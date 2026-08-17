"""
match_buildings.py — McPhillips 1880 <-> Goad's 1906 building-match pipeline.

Usage:
    python match_buildings.py [--in1880 PATH] [--in1906 PATH] [--out PATH]

Defaults read/write relative to pfviewer/data/:
    data/mcphillips_1880.geojson
    data/goad_1906.geojson
    -> data/mcphillips_goad_1906.matches.json   (the review queue)

Pipeline (see reconstruct.py for the fit/reconstruction math):
  1. Load + filter to real building footprints (Polygon/MultiPolygon,
     properties.type unset — this drops fence/walkway/bridge/lumber/
     shantytown, and LineString railways are excluded by geometry type).
  2. Project lon/lat to local metres (equirectangular approx, matches
     pfviewer's index.html project()).
  3. Spatial-index 1906 footprints (STRtree); for each 1880 footprint, find
     1906 candidates whose padded bbox overlaps.
  4. Compute per-pair metrics; build a bipartite 1880<->1906 graph from
     candidates that show *real* overlap; connected components become match
     groups (handles many->one merges and one->many splits).
  5. Classify each group (continuation / base_addition / shrink / ambiguous /
     no_match); fit + reconstruct base_addition and shrink groups.
  6. Write every group (not just the ones needing review) to matches.json as
     a full audit trail, with needs_review/status fields gating what
     Planimetro's review UI actually steps through.
"""

import sys
import os
import json
import math
import argparse
import datetime

import numpy as np
from shapely.geometry import shape, mapping, box
from shapely.ops import unary_union
from shapely.strtree import STRtree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reconstruct as rc

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')

# ── Tunable constants (also written into matches.json's "params" block) ────
# SEARCH_PAD_M and the EDGE_* thresholds were tuned down from an initial pass
# (15m / 0.02 / 0.05) that let dense rowhouse blocks chain-merge transitively
# through weak sliver overlaps with neighboring, unrelated buildings into a
# single 48-vs-27-feature "match" — real overlap, just not a coherent event.
SEARCH_PAD_M = 4.0               # candidate-search bbox padding & fit translation bound
CONTIGUITY_TOL_M = 0.5          # buffer tolerance for "extra area touches footprint"
EDGE_IOU_MIN = 0.08              # minimum IoU to keep a candidate edge
EDGE_CONTAINMENT_MIN = 0.2      # ...or minimum containment (either direction)
CONTINUATION_IOU_MIN = 0.75
BASE_ADDITION_CONTAINMENT_1880_MIN = 0.85
BASE_ADDITION_AREA_RATIO_MIN = 1.15
BASE_ADDITION_AREA_RATIO_MAX = 4.0   # beyond this it reads as redevelopment, not an addition
SHRINK_CONTAINMENT_1906_MIN = 0.85
SHRINK_AREA_RATIO_MAX = 0.87
SHRINK_AREA_RATIO_MIN = 0.25         # mirrors BASE_ADDITION_AREA_RATIO_MAX
FIT_MAX_ROTATION_DEG = 12.0
FIT_SCALE_BOUNDS = (0.85, 1.15)
# A connected component bigger than this is almost certainly several distinct
# real-world events chained together by transitive neighbor overlap (rather
# than one coherent merge/split) — force it to ambiguous for human review
# instead of guessing, and skip the (meaningless for a 48-building blob)
# rigid-transform fit.
MAX_GROUP_SIZE = 6   # len(ids_1880) + len(ids_1906)

NON_BUILDING_TYPES = {'fence', 'walkway', 'bridge', 'lumber', 'shantytown', 'railway'}


class NpEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def load_buildings(path):
    """Load a FeatureCollection, keep only real building footprints."""
    with open(path, encoding='utf-8') as f:
        fc = json.load(f)
    out = []
    skipped_type, skipped_geom, skipped_empty = 0, 0, 0
    for ft in fc['features']:
        props = ft.get('properties') or {}
        if props.get('type') in NON_BUILDING_TYPES:
            skipped_type += 1
            continue
        geom_type = ft['geometry']['type']
        if geom_type not in ('Polygon', 'MultiPolygon'):
            skipped_geom += 1
            continue
        geom_ll = rc.fix_geom(shape(ft['geometry']))
        if geom_ll.is_empty or geom_ll.area <= 0:
            skipped_empty += 1
            continue
        out.append({
            'id': props['id'],
            'props': props,
            'geom_ll': geom_ll,
            'geom_m': rc.fix_geom(rc.project_geom(geom_ll)),
        })
    print(f"  {os.path.basename(path)}: {len(out)} buildings kept "
          f"({skipped_type} non-building type, {skipped_geom} non-polygon geom, "
          f"{skipped_empty} empty/degenerate skipped)")
    return out


def pair_metrics(geom_a, geom_b):
    inter = geom_a.intersection(geom_b).area
    union_area = geom_a.area + geom_b.area - inter
    iou = inter / union_area if union_area > 0 else 0.0
    containment_a = inter / geom_a.area if geom_a.area > 0 else 0.0
    containment_b = inter / geom_b.area if geom_b.area > 0 else 0.0
    area_ratio = geom_b.area / geom_a.area if geom_a.area > 0 else float('inf')

    inter_geom = geom_a.intersection(geom_b)
    if geom_b.area >= geom_a.area:
        extra = rc.fix_geom(geom_b.difference(inter_geom))
        contiguous = extra.is_empty or geom_a.buffer(CONTIGUITY_TOL_M).intersects(extra)
    else:
        extra = rc.fix_geom(geom_a.difference(inter_geom))
        contiguous = extra.is_empty or geom_b.buffer(CONTIGUITY_TOL_M).intersects(extra)

    return {
        'intersection_area': inter,
        'iou': iou,
        'containment_1880': containment_a,
        'containment_1906': containment_b,
        'area_ratio': area_ratio,
        'contiguous': bool(contiguous),
    }


def classify(n_1880, n_1906, metrics):
    if n_1880 == 1 and n_1906 == 1 and metrics['iou'] >= CONTINUATION_IOU_MIN:
        return 'continuation'
    if (metrics['containment_1880'] >= BASE_ADDITION_CONTAINMENT_1880_MIN and
            BASE_ADDITION_AREA_RATIO_MIN <= metrics['area_ratio'] <= BASE_ADDITION_AREA_RATIO_MAX and
            metrics['contiguous']):
        return 'base_addition'
    if (metrics['containment_1906'] >= SHRINK_CONTAINMENT_1906_MIN and
            SHRINK_AREA_RATIO_MIN <= metrics['area_ratio'] <= SHRINK_AREA_RATIO_MAX and
            metrics['contiguous']):
        return 'shrink'
    return 'ambiguous'


def bbox_of(*geoms_ll, pad_m=8.0):
    minx = min(g.bounds[0] for g in geoms_ll) - pad_m / rc.M_PER_LON
    miny = min(g.bounds[1] for g in geoms_ll) - pad_m / rc.M_PER_LAT
    maxx = max(g.bounds[2] for g in geoms_ll) + pad_m / rc.M_PER_LON
    maxy = max(g.bounds[3] for g in geoms_ll) + pad_m / rc.M_PER_LAT
    return [minx, miny, maxx, maxy]


def build_matches(b1880, b1906):
    tree = STRtree([b['geom_m'] for b in b1906])

    uf = UnionFind()
    edges_by_1880 = {}  # id_1880 -> list of b1906 dicts that passed the edge test
    for a in b1880:
        node_a = ('1880', a['id'])
        minx, miny, maxx, maxy = a['geom_m'].bounds
        query_geom = box(minx - SEARCH_PAD_M, miny - SEARCH_PAD_M,
                          maxx + SEARCH_PAD_M, maxy + SEARCH_PAD_M)
        cand_idx = tree.query(query_geom)
        kept = []
        for i in cand_idx:
            b = b1906[int(i)]
            m = pair_metrics(a['geom_m'], b['geom_m'])
            if m['iou'] > EDGE_IOU_MIN or m['containment_1880'] > EDGE_CONTAINMENT_MIN \
                    or m['containment_1906'] > EDGE_CONTAINMENT_MIN:
                kept.append(b)
                uf.union(node_a, ('1906', b['id']))
        if not kept:
            uf.find(node_a)  # register as its own singleton component
        edges_by_1880[a['id']] = kept

    by_id_1880 = {b['id']: b for b in b1880}
    by_id_1906 = {b['id']: b for b in b1906}

    groups = {}  # root -> {'1880': set(ids), '1906': set(ids)}
    for a in b1880:
        root = uf.find(('1880', a['id']))
        g = groups.setdefault(root, {'1880': set(), '1906': set()})
        g['1880'].add(a['id'])
        for b in edges_by_1880[a['id']]:
            g['1906'].add(b['id'])

    matches = []
    counts = {}
    for gi, (root, g) in enumerate(sorted(groups.items(), key=lambda kv: min(kv[1]['1880'])), start=1):
        ids_1880 = sorted(g['1880'])
        ids_1906 = sorted(g['1906'])
        geoms_1880_m = [by_id_1880[i]['geom_m'] for i in ids_1880]
        geoms_1880_ll = [by_id_1880[i]['geom_ll'] for i in ids_1880]
        src_union_m = rc.fix_geom(unary_union(geoms_1880_m))

        oversized = (len(ids_1880) + len(ids_1906)) > MAX_GROUP_SIZE

        fit = None
        if not ids_1906:
            classification = 'no_match'
            metrics = {'intersection_area': 0.0, 'iou': 0.0, 'containment_1880': 0.0,
                       'containment_1906': 0.0, 'area_ratio': None, 'contiguous': None}
            tgt_union_m = None
            geoms_1906_ll = []
        else:
            geoms_1906_m = [by_id_1906[i]['geom_m'] for i in ids_1906]
            geoms_1906_ll = [by_id_1906[i]['geom_ll'] for i in ids_1906]
            tgt_union_m = rc.fix_geom(unary_union(geoms_1906_m))
            metrics = pair_metrics(src_union_m, tgt_union_m)

            is_continuation = (len(ids_1880) == 1 and len(ids_1906) == 1
                               and metrics['iou'] >= CONTINUATION_IOU_MIN)
            if oversized:
                classification = 'ambiguous'
            elif is_continuation:
                classification = 'continuation'
            else:
                # Fit BEFORE classifying, and classify on the FITTED footprint's
                # containment, not the raw one. A clean base+addition often has
                # its raw 1880 footprint poking slightly outside 1906 (so raw
                # containment < 0.85 → ambiguous) purely because it hasn't been
                # aligned yet; once the corner fit nudges it into place the real
                # containment is what matters. The fitter falls back to identity
                # when it can't align confidently, so this can't manufacture a
                # false base_addition out of a genuinely poor overlap.
                fit = rc.fit_corner_anchored(
                    src_union_m, tgt_union_m,
                    max_rotation_deg=FIT_MAX_ROTATION_DEG,
                    scale_bounds=FIT_SCALE_BOUNDS,
                )
                class_metrics = dict(metrics)
                if fit is not None:
                    fs = fit['fitted_geom']
                    inter = fs.intersection(tgt_union_m).area
                    class_metrics['containment_1880'] = inter / fs.area if fs.area > 0 else 0.0
                    class_metrics['containment_1906'] = inter / tgt_union_m.area if tgt_union_m.area > 0 else 0.0
                    metrics['containment_1880_fitted'] = class_metrics['containment_1880']
                    metrics['containment_1906_fitted'] = class_metrics['containment_1906']
                classification = classify(len(ids_1880), len(ids_1906), class_metrics)

        metrics['oversized_group'] = oversized
        needs_review = classification in ('base_addition', 'shrink', 'ambiguous')
        counts[classification] = counts.get(classification, 0) + 1

        transform = None
        geometry_1880_fitted = None
        reconstruction = None
        # Reuse the fit computed above (base_addition / shrink / ambiguous all
        # get one so the reviewer always has an amber overlay to judge).
        if fit is not None:
            transform = fit['transform']
            geometry_1880_fitted = mapping(rc.unproject_geom(fit['fitted_geom']))
            base_m, addition_m = rc.reconstruct_base_addition(fit['fitted_geom'], tgt_union_m)
            reconstruction = {
                'base': mapping(rc.unproject_geom(base_m)),
                'addition': mapping(rc.unproject_geom(addition_m)),
            }

        all_geoms_ll = geoms_1880_ll + geoms_1906_ll
        matches.append({
            'match_id': f'm{gi:04d}',
            'classification': classification,
            'needs_review': needs_review,
            'status': 'pending' if needs_review else 'auto',
            'ids_1880': ids_1880,
            'ids_1906': ids_1906,
            # Stable identity: pf_uid survives Planimetro edits/renumbering, so
            # downstream (build_pastforward) keys on these, not the volatile ids.
            'uids_1880': [by_id_1880[i]['props'].get('pf_uid') for i in ids_1880],
            'uids_1906': [by_id_1906[i]['props'].get('pf_uid') for i in ids_1906],
            'metrics': metrics,
            'transform': transform,
            'bbox': bbox_of(*all_geoms_ll),
            'geometry_1880_orig': mapping(unary_union(geoms_1880_ll)) if len(geoms_1880_ll) > 1 else mapping(geoms_1880_ll[0]),
            'geometry_1880_fitted': geometry_1880_fitted,
            'geometry_1906': (mapping(unary_union(geoms_1906_ll)) if len(geoms_1906_ll) > 1
                               else (mapping(geoms_1906_ll[0]) if geoms_1906_ll else None)),
            'reconstruction': reconstruction,
        })

    return matches, counts


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--in1880', default=os.path.join(DATA_DIR, 'mcphillips_1880.geojson'))
    ap.add_argument('--in1906', default=os.path.join(DATA_DIR, 'goad_1906.geojson'))
    ap.add_argument('--out', default=os.path.join(DATA_DIR, 'mcphillips_goad_1906.matches.json'))
    args = ap.parse_args()

    print('Loading buildings...')
    b1880 = load_buildings(args.in1880)
    b1906 = load_buildings(args.in1906)

    print('Matching...')
    matches, counts = build_matches(b1880, b1906)

    out = {
        'generated': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source_1880': os.path.basename(args.in1880),
        'source_1906': os.path.basename(args.in1906),
        'params': {
            'search_pad_m': SEARCH_PAD_M,
            'contiguity_tol_m': CONTIGUITY_TOL_M,
            'edge_iou_min': EDGE_IOU_MIN,
            'edge_containment_min': EDGE_CONTAINMENT_MIN,
            'continuation_iou_min': CONTINUATION_IOU_MIN,
            'base_addition_containment_1880_min': BASE_ADDITION_CONTAINMENT_1880_MIN,
            'base_addition_area_ratio_min': BASE_ADDITION_AREA_RATIO_MIN,
            'shrink_containment_1906_min': SHRINK_CONTAINMENT_1906_MIN,
            'shrink_area_ratio_max': SHRINK_AREA_RATIO_MAX,
            'fit_max_rotation_deg': FIT_MAX_ROTATION_DEG,
            'fit_scale_bounds': list(FIT_SCALE_BOUNDS),
        },
        'matches': matches,
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(out, f, cls=NpEncoder)

    print(f"\nWrote {len(matches)} match groups -> {args.out}")
    total = sum(counts.values())
    for cls, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {cls:16s} {n:5d}  ({100*n/total:.1f}%)")


if __name__ == '__main__':
    main()
