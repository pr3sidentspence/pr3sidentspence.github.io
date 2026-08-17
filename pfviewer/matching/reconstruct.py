"""
reconstruct.py — rigid-transform fitting and base/addition reconstruction for
the McPhillips 1880 -> Goad's 1906 building-match pipeline.

Imported by match_buildings.py. All fitting/reconstruction geometry here is in
the local metric projection (see project_point/project_geom below, which
mirror the C_LON/C_LAT/M_PER_LON/M_PER_LAT constants pfviewer's index.html
already uses) — callers project inputs before calling in, and un-project
results before writing them out as GeoJSON.
"""

import math
import numpy as np
from shapely.ops import transform as shapely_transform
from shapely.affinity import affine_transform as shapely_affine

# ── Local metric projection (matches pfviewer index.html's project()) ──────
C_LON = -97.135515
C_LAT = 49.895396
_COS_LAT = math.cos(math.radians(C_LAT))
M_PER_LON = 111320 * _COS_LAT
M_PER_LAT = 111320


def project_point(x, y):
    return ((x - C_LON) * M_PER_LON, (y - C_LAT) * M_PER_LAT)


def unproject_point(x, y):
    return (x / M_PER_LON + C_LON, y / M_PER_LAT + C_LAT)


def project_geom(geom):
    return shapely_transform(project_point, geom)


def unproject_geom(geom):
    return shapely_transform(unproject_point, geom)


def fix_geom(geom):
    """Repair a self-intersecting polygon the cheap, standard way."""
    if geom.is_empty:
        return geom
    if not geom.is_valid:
        geom = geom.buffer(0)
    return geom


def _angle_diff(a, b):
    """Minimal signed difference between two angles that are only meaningful
    mod pi (undirected edges/walls), wrapped to (-pi/2, pi/2]."""
    d = (a - b) % math.pi
    return d - math.pi if d > math.pi / 2 else d


def _wrap_pi(x):
    """Wrap a directed angle to (-pi, pi]."""
    return (x + math.pi) % (2 * math.pi) - math.pi


def _iter_exteriors(geom):
    if geom.geom_type == 'Polygon':
        yield geom.exterior
    elif geom.geom_type == 'MultiPolygon':
        for p in geom.geoms:
            yield p.exterior


def _corners(geom, min_turn_deg=25.0, min_edge_len=0.6):
    """
    Extract real corners (not near-collinear vertices) from a polygon's
    exterior ring(s). Each corner records its position, the undirected
    directions of its two incident walls (mod pi), and the signed turn
    angle (magnitude ≈ how sharp, sign ≈ convex vs reflex) — enough to pair
    a source corner with a geometrically-similar target corner and to build
    a pin+rotate+scale transform around it.
    """
    out = []
    min_turn = math.radians(min_turn_deg)
    for ring in _iter_exteriors(geom):
        pts = list(ring.coords)
        if len(pts) < 4:  # closed ring needs ≥4 coords (triangle + dup close)
            continue
        pts = pts[:-1]  # drop the closing duplicate
        n = len(pts)
        for i in range(n):
            p = np.asarray(pts[(i - 1) % n], dtype=float)
            v = np.asarray(pts[i], dtype=float)
            q = np.asarray(pts[(i + 1) % n], dtype=float)
            e_in = v - p
            e_out = q - v
            len_in = math.hypot(*e_in)
            len_out = math.hypot(*e_out)
            if len_in < min_edge_len or len_out < min_edge_len:
                continue
            a_in = math.atan2(e_in[1], e_in[0])
            a_out = math.atan2(e_out[1], e_out[0])
            turn = _wrap_pi(a_out - a_in)
            if abs(turn) < min_turn:
                continue  # near-collinear — not a real corner
            out.append({
                'pos': v,
                'walls': (a_in % math.pi, a_out % math.pi),  # undirected
                'turn': turn,
            })
    return out


def _corner_transform(cs, ct, corr, scale_u, scale_v, max_rotation_rad):
    """
    Build the affine map (2x2 linear A, offset) that pins source corner cs
    onto target corner ct, rotates so cs's walls align to ct's, and scales
    by scale_u/scale_v along ct's two wall axes. `corr` picks which source
    wall maps to which target wall (0 = in→in/out→out, 1 = crossed).
    Returns (A, offset) or None if the rotation exceeds the cap or the
    target axes are degenerate.
    """
    sw_in, sw_out = cs['walls']
    tw_in, tw_out = ct['walls']
    if corr == 0:
        pair = [(sw_in, tw_in), (sw_out, tw_out)]
        ax1, ax2 = tw_in, tw_out
    else:
        pair = [(sw_in, tw_out), (sw_out, tw_in)]
        ax1, ax2 = tw_out, tw_in

    t1 = _angle_diff(pair[0][1], pair[0][0])
    t2 = _angle_diff(pair[1][1], pair[1][0])
    # The two walls must agree on the rotation, else this is a wrong pairing.
    if abs(_wrap_pi(t1 - t2)) > math.radians(12.0):
        return None
    theta = 0.5 * (t1 + t2)
    if abs(theta) > max_rotation_rad:
        return None

    u1 = np.array([math.cos(ax1), math.sin(ax1)])
    u2 = np.array([math.cos(ax2), math.sin(ax2)])
    U = np.column_stack([u1, u2])
    if abs(np.linalg.det(U)) < 0.15:  # walls nearly parallel → unusable basis
        return None
    S = U @ np.diag([scale_u, scale_v]) @ np.linalg.inv(U)
    R = np.array([[math.cos(theta), -math.sin(theta)],
                  [math.sin(theta),  math.cos(theta)]])
    A = S @ R
    offset = ct['pos'] - A @ cs['pos']
    return A, offset, theta


def _apply_affine(geom, A, offset):
    return shapely_affine(geom, [A[0, 0], A[0, 1], A[1, 0], A[1, 1], offset[0], offset[1]])


def fit_corner_anchored(source_geom, target_geom,
                        max_rotation_deg=15.0, scale_bounds=(0.85, 1.15),
                        wall_eps=1.0, corner_max_dist=12.0,
                        turn_tol_deg=30.0, conf_threshold=0.45,
                        top_k=5, scale_steps=5):
    """
    Fit source_geom onto target_geom by CORNER CORRESPONDENCE rather than by
    optimizing an area score.

    Motivation: every area-based objective tried before this (IoU, and two
    containment variants) was gameable — the continuous optimizer would
    shrink to the scale floor, grow to the ceiling, or rotate a hair off-
    parallel, whenever doing so nudged the area score, producing fits that
    scored well but looked wrong (walls not parallel, corners not meeting).
    Regularizing each dimension only moved the gaming to the next one.

    This instead ENUMERATES geometrically-sane candidate transforms and uses
    overlap only to SELECT among them (discrete selection over sane options
    can't "wander" to a bad answer the way continuous optimization can):

      1. Extract real corners from both shapes (position + two wall angles +
         turn/convexity).
      2. For every source-corner × target-corner pair that is close enough,
         of similar sharpness, and same convexity: pin the source corner
         onto the target corner and rotate so their walls become parallel
         (rotation is DETERMINED by the walls, not free — this is what fixes
         the rotate-to-max-area failure; the pin fixes the centroid-translate
         failure).
      3. For the most promising pins, grid-search a bounded anisotropic
         scale along the pinned corner's two wall axes (width and length
         independently — handles "only the notch depth changed").
      4. Score each candidate by wall coincidence (how much of the fitted
         boundary lies on the target boundary) plus containment — NOT by
         area/IoU — and keep the best.
      5. Always include the identity (no transform) as a candidate, and if
         no real candidate clears a confidence threshold, RETURN THE IDENTITY
         so the reviewer sees the untransformed original rather than a
         confidently-wrong fit. `confident` in the returned transform says
         which happened.

    Returns None only if source_geom is empty; otherwise a dict with
    'fitted_geom' (in projected metres) and 'transform' (a JSON-ready dict
    including the exact affine 'matrix' plus human-readable display fields).
    """
    source_geom = fix_geom(source_geom)
    target_geom = fix_geom(target_geom)
    if source_geom.is_empty or source_geom.area <= 0:
        return None

    max_rot = math.radians(max_rotation_deg)
    tgt_boundary_buf = target_geom.boundary.buffer(wall_eps)
    tgt_area = target_geom.area
    src_centroid = np.array([source_geom.centroid.x, source_geom.centroid.y])

    def wall_coincidence(fitted):
        b = fitted.boundary
        L = b.length
        if L <= 0:
            return 0.0
        return b.intersection(tgt_boundary_buf).length / L

    def containment(fitted):
        if fitted.area <= 0:
            return 0.0
        return fitted.intersection(target_geom).area / fitted.area

    def iou(fitted):
        if fitted.area <= 0:
            return 0.0
        inter = fitted.intersection(target_geom).area
        union = fitted.area + tgt_area - inter
        return inter / union if union > 0 else 0.0

    def score_of(fitted):
        return 0.6 * wall_coincidence(fitted) + 0.4 * containment(fitted)

    scs = _corners(source_geom)
    tcs = _corners(target_geom)

    # ── Candidate pins at scale 1, pre-filtered on geometry, pre-scored ──
    turn_tol = math.radians(turn_tol_deg)
    prelim = []
    for cs in scs:
        for ct in tcs:
            if np.hypot(*(cs['pos'] - ct['pos'])) > corner_max_dist:
                continue
            if (cs['turn'] > 0) != (ct['turn'] > 0):
                continue  # convex must match convex, reflex reflex
            if abs(abs(cs['turn']) - abs(ct['turn'])) > turn_tol:
                continue  # corner sharpness must be similar
            for corr in (0, 1):
                built = _corner_transform(cs, ct, corr, 1.0, 1.0, max_rot)
                if built is None:
                    continue
                A, offset, theta = built
                fitted = fix_geom(_apply_affine(source_geom, A, offset))
                if fitted.is_empty or fitted.area <= 0:
                    continue
                prelim.append((score_of(fitted), cs, ct, corr, theta))

    prelim.sort(key=lambda r: r[0], reverse=True)

    # Identity (no transform) is always a candidate and the safe fallback.
    identity_fitted = source_geom
    best = {
        'score': score_of(identity_fitted),
        'fitted': identity_fitted,
        'A': np.eye(2), 'offset': np.zeros(2),
        'theta': 0.0, 'su': 1.0, 'sv': 1.0, 'kind': 'identity',
    }

    # ── Refine the top few pins with a bounded anisotropic scale grid ──
    scale_grid = np.linspace(scale_bounds[0], scale_bounds[1], scale_steps)
    for _, cs, ct, corr, _theta in prelim[:top_k]:
        for su in scale_grid:
            for sv in scale_grid:
                built = _corner_transform(cs, ct, corr, float(su), float(sv), max_rot)
                if built is None:
                    continue
                A, offset, theta = built
                fitted = fix_geom(_apply_affine(source_geom, A, offset))
                if fitted.is_empty or fitted.area <= 0:
                    continue
                sc = score_of(fitted)
                if sc > best['score']:
                    best = {'score': sc, 'fitted': fitted, 'A': A, 'offset': offset,
                            'theta': theta, 'su': float(su), 'sv': float(sv), 'kind': 'corner'}

    confident = best['kind'] == 'corner' and best['score'] >= conf_threshold
    if not confident:
        # Fall back to showing the untransformed original.
        best = {'score': score_of(identity_fitted), 'fitted': identity_fitted,
                'A': np.eye(2), 'offset': np.zeros(2),
                'theta': 0.0, 'su': 1.0, 'sv': 1.0, 'kind': 'identity'}

    fitted = best['fitted']
    A, offset = best['A'], best['offset']
    fit_centroid = np.array([fitted.centroid.x, fitted.centroid.y])
    disp_dx, disp_dy = (fit_centroid - src_centroid).tolist()

    transform = {
        'kind': best['kind'],
        'confident': bool(confident),
        'theta_deg': math.degrees(best['theta']),
        'scale_u': best['su'],
        'scale_v': best['sv'],
        'scale': 0.5 * (best['su'] + best['sv']),  # legacy single-scale display
        'dx': disp_dx,
        'dy': disp_dy,
        'wall_coincidence': wall_coincidence(fitted),
        'containment': containment(fitted),
        'iou': iou(fitted),
        'objective_value': best['score'],
        # Exact affine in the projected-metre frame (project_point space),
        # for reapplying to a subset during partial-accept in Planimetro.
        'matrix': [A[0, 0], A[0, 1], A[1, 0], A[1, 1], offset[0], offset[1]],
    }
    return {'fitted_geom': fitted, 'transform': transform}


def reconstruct_base_addition(fitted_geom, target_geom):
    """
    base = fitted_geom clipped to target_geom's boundary.
    addition = target_geom minus base.
    base ∪ addition == target_geom by construction (asserted to a tight
    numeric tolerance, not a tunable threshold — this is a sanity check on
    the geometry math, not a modelling choice).
    """
    fitted_geom = fix_geom(fitted_geom)
    target_geom = fix_geom(target_geom)
    base = fix_geom(fitted_geom.intersection(target_geom))
    addition = fix_geom(target_geom.difference(base))
    total = base.area + addition.area
    assert abs(total - target_geom.area) < 0.01, (
        f"reconstruction area mismatch: base+addition={total:.4f} vs target={target_geom.area:.4f}"
    )
    return base, addition
