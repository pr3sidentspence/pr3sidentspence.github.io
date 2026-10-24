"""elmwood_rows.py — Elmwood Cemetery's burial layout from Mike's drawing.

    ~/.venvs/pfgis/bin/python tools/elmwood_rows.py [--fit] [--preview out.png]

Mike, 2026-10-23: a drawing (black background, north up) traced over the cemetery:
  green  — rows of larger headstones, the stones facing both ways away from the line (graves on both sides), except
           on the cemetery's edges, where they face inward
  red    — rows of flush-with-the-ground stones
  blue   — larger, densely packed stones (concrete along them)
  yellow — flower beds (not raised)
The drawing is fitted to the cemetery (FIT: px per m, rotation, offset — --fit searches it again): its rows must lie
inside OSM's cemetery outline and off the paths. Stones go along each line every GAP[kind] m (Poisson-disk over the
line's pixels, each facing square to the line's local direction). Writes data/elmwood_rows.json:
  {stones: [[lon, lat, facing° (compass), kind 0 upright / 1 flush / 2 dense], …], beds: [[outer ring]…], strips: [[ring]…]}
in fill order: the 1910 plots (data/cemeteries.json) first, then the rest, shuffled within each."""
import sys, os, json, math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from shapely.geometry import Polygon, LineString, Point, MultiPoint
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
DRAWING = os.path.expanduser('~/gisdata/elmwood/elmwood_rows_mike.webp')
OSM = os.path.expanduser('~/gisdata/osm/feat/wpg_paths.json'); FEAT = os.path.expanduser('~/gisdata/osm/feat/wpg_features.json')
LAT0 = 49.912; K = math.cos(math.radians(LAT0)) * 111320; KY = 110574
GAP = {0: 1.3, 1: 1.0, 2: 0.8}        # m between stones along a line
EDGE_M = 4.0                          # a green line this close to the outline: one stone, facing inward
FIT = json.load(open(os.path.join(HERE, 'elmwood_fit.json'))) if os.path.exists(os.path.join(HERE, 'elmwood_fit.json')) else None

im = np.asarray(Image.open(DRAWING).convert('RGB')).astype(int); H, W, _ = im.shape
r, g, b = im[..., 0], im[..., 1], im[..., 2]
MASKS = {0: (g > 110) & (g > r + 40) & (g > b + 40),
         1: (r > 130) & (r > g + 60) & (r > b + 60),
         2: (b > 70) & (b > r + 35) & (b > g + 25),
         3: (r > 160) & (g > 160) & (b < 120)}

def px_to_m(x, y, fit):   # drawing px → metres east/north of (lon0, LAT0)
    s, rot, tx, ty = fit['s'], math.radians(fit['rot']), fit['tx'], fit['ty']
    u, v = (x - W / 2) / s, -(y - H / 2) / s
    return u * math.cos(rot) - v * math.sin(rot) + tx, u * math.sin(rot) + v * math.cos(rot) + ty
LON0 = -97.12
m_to_ll = lambda X, Y: (round(LON0 + X / K, 7), round(LAT0 + Y / KY, 7))
ll_to_m = lambda lon, lat: ((lon - LON0) * K, (lat - LAT0) * KY)

def outline_and_paths():
    P = json.load(open(OSM))
    cem = [w for w in P['elm'] if 'Elmwood' in w['t'].get('name', '') and w['t'].get('landuse') == 'cemetery']   # way/32263535
    out = unary_union([Polygon([ll_to_m(*q) for q in w['p']]) for w in cem])
    paths = []
    for w in P['elm']:
        t = w['t']
        if t.get('highway') in ('footway', 'path', 'service', 'track', 'pedestrian', 'unclassified', 'residential'):
            L = LineString([ll_to_m(*q) for q in w['p']])
            if L.intersects(out): paths.append(L.buffer(2.5 if t.get('highway') in ('service', 'track', 'unclassified', 'residential') else 1.2))
    return out, unary_union(paths) if paths else Polygon()

def fit_drawing(out, paths):
    ys, xs = np.nonzero(MASKS[0] | MASKS[1] | MASKS[2])
    sel = np.random.default_rng(0).choice(len(xs), min(15000, len(xs)), replace=False); xs, ys = xs[sel].astype(float), ys[sel].astype(float)
    x0, y0, x1, y1 = out.bounds; M = 1.0; MW, MH = int((x1 - x0) / M) + 40, int((y1 - y0) / M) + 40
    def raster(geom):
        m = Image.new('L', (MW, MH), 0); d = ImageDraw.Draw(m)
        for p in getattr(geom, 'geoms', [geom]):
            if p.is_empty: continue
            d.polygon([((x - x0) / M + 20, (y1 - y) / M + 20) for x, y in p.exterior.coords], fill=1)
            for h in p.interiors: d.polygon([((x - x0) / M + 20, (y1 - y) / M + 20) for x, y in h.coords], fill=0)
        return np.asarray(m).astype(bool)
    good, bad = raster(out.difference(paths)), raster(paths) | ~raster(out)
    CS = 6; good6 = good[:good.shape[0] // CS * CS, :good.shape[1] // CS * CS].reshape(good.shape[0] // CS, CS, -1, CS).mean((1, 3)) > 0.5
    def score(s, rd, tx, ty):   # rows inside the grounds and off the paths, and covering them (6 m cells)
        rot = math.radians(rd); u, v = (xs - W / 2) / s, -(ys - H / 2) / s
        X = u * math.cos(rot) - v * math.sin(rot) + tx; Y = u * math.sin(rot) + v * math.cos(rot) + ty
        j = ((X - x0) / M + 20).astype(int); i = ((y1 - Y) / M + 20).astype(int); ok = (i >= 0) & (i < MH) & (j >= 0) & (j < MW)
        gg = np.zeros(len(xs)); bb = np.ones(len(xs)); gg[ok] = good[i[ok], j[ok]]; bb[ok] = bad[i[ok], j[ok]]
        hit = np.zeros(good6.shape, bool); ii, jj = i[ok] // CS, j[ok] // CS; k2 = (ii < hit.shape[0]) & (jj < hit.shape[1]); hit[ii[k2], jj[k2]] = True
        return gg.mean() - 1.5 * bb.mean() + (hit & good6).sum() / max(1, good6.sum())
    cx, cy = out.centroid.x, out.centroid.y; best = None
    for s in np.arange(2.4, 4.21, 0.1):
        for rd in range(-9, 10, 3):
            for tx in np.arange(cx - 80, cx + 81, 10):
                for ty in np.arange(cy - 80, cy + 81, 10):
                    q = score(s, rd, tx, ty)
                    if best is None or q > best[0]: best = (q, s, rd, tx, ty)
    print('coarse', best)
    for step in (0.025, 0.01):
        q0, s0, r0, tx0, ty0 = best
        for s in np.arange(s0 - 4 * step, s0 + 4.1 * step, step):
            for rd in np.arange(r0 - 2, r0 + 2.01, 0.5 if step > 0.02 else 0.2):
                for tx in np.arange(tx0 - 6, tx0 + 6.1, 2 if step > 0.02 else 0.5):
                    for ty in np.arange(ty0 - 6, ty0 + 6.1, 2 if step > 0.02 else 0.5):
                        q = score(s, rd, tx, ty)
                        if q > best[0]: best = (q, s, rd, tx, ty)
        print('fine', step, best)
    q, s, rd, tx, ty = best
    return {'s': float(s), 'rot': float(rd), 'tx': float(tx), 'ty': float(ty), 'score': float(q), 'lon0': LON0, 'lat0': LAT0}

def stations(mask, gap_px):
    """points along the mask's lines, gap_px apart (greedy over a grid), each with the local line direction (radians, px frame)"""
    lab, n = ndimage.label(mask, structure=np.ones((3, 3)))
    out = []
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        if len(xs) < 4: continue
        P = np.stack([xs, ys], 1).astype(float)
        c = P.mean(0); u, sv, vt = np.linalg.svd(P - c, full_matrices=False); ax = vt[0]
        order = np.argsort((P - c) @ ax); P = P[order]
        last = None
        for p in P:
            if last is not None and np.hypot(*(p - last)) < gap_px: continue
            near = P[np.hypot(*(P - p).T) < max(6, gap_px * 3)]
            if len(near) >= 3:
                cc = near.mean(0); _, _, v2 = np.linalg.svd(near - cc, full_matrices=False); d = v2[0]
            else: d = ax
            out.append((p[0], p[1], math.atan2(d[1], d[0]), k)); last = p
    return out

def main():
    out, paths = outline_and_paths()
    fit = FIT
    if '--fit' in sys.argv or fit is None:
        fit = fit_drawing(out, paths); json.dump(fit, open(os.path.join(HERE, 'elmwood_fit.json'), 'w'), indent=1)
    s = fit['s']
    plots1910 = unary_union([Polygon([ll_to_m(*q) for q in p[0]]) for p in json.load(open(os.path.join(DATA, 'cemeteries.json')))['plots']])
    edge = out.exterior if out.geom_type == 'Polygon' else unary_union([p.exterior for p in out.geoms])
    rng = np.random.default_rng(7); stones = []
    for kind in (0, 1, 2):
        for x, y, ang, comp in stations(MASKS[kind], GAP[kind] * s):
            X, Y = px_to_m(x, y, fit)
            if not out.buffer(1.0).contains(Point(X, Y)) or paths.contains(Point(X, Y)): continue
            # the line's direction in metres (y down in the drawing → north up), then the two faces square to it
            dx, dy = math.cos(ang), -math.sin(ang); rot = math.radians(fit['rot'])
            ex, ey = dx * math.cos(rot) - dy * math.sin(rot), dx * math.sin(rot) + dy * math.cos(rot)
            nx, ny = -ey, ex
            faces = [(nx, ny), (-nx, -ny)] if kind != 1 else [(nx, ny)]
            if kind == 0 and edge.distance(Point(X, Y)) < EDGE_M:   # on the edge: one stone, facing inward
                inward = max(faces, key=lambda f: out.contains(Point(X + f[0] * 3, Y + f[1] * 3)) - 0)
                faces = [inward]
            for fx, fy in faces:
                off = 0.18 if len(faces) == 2 else 0
                bx, by = X + fx * off, Y + fy * off
                stones.append([*m_to_ll(bx, by), round((math.degrees(math.atan2(fx, fy)) + 360) % 360, 1), kind, plots1910.contains(Point(bx, by))])
    order = rng.permutation(len(stones)); stones = [stones[i] for i in order]
    stones.sort(key=lambda q: not q[4])           # 1910 plots first (stable: shuffled within)
    stones = [q[:4] for q in stones]
    beds = []
    lab, n = ndimage.label(ndimage.binary_closing(MASKS[3], iterations=2))
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        if len(xs) < 8: continue
        hull = MultiPoint([px_to_m(x, y, fit) for x, y in zip(xs, ys)]).convex_hull.buffer(0.3)
        beds.append([list(m_to_ll(*q)) for q in hull.exterior.coords])
    strips = []
    lab, n = ndimage.label(MASKS[2], structure=np.ones((3, 3)))
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        if len(xs) < 6: continue
        pts = np.array([px_to_m(x, y, fit) for x, y in zip(xs, ys)]); c = pts.mean(0); _, _, vt = np.linalg.svd(pts - c, full_matrices=False)
        t = (pts - c) @ vt[0]; L = LineString([c + vt[0] * t.min(), c + vt[0] * t.max()]).buffer(0.45, cap_style=2)
        strips.append([list(m_to_ll(*q)) for q in L.exterior.coords])
    res = {'source': "Mike's drawing of the burial rows (2026-10-23), fitted by tools/elmwood_rows.py", 'fit': fit,
           'kinds': ['upright headstone', 'flush stone', 'dense larger stones'], 'stones': stones, 'beds': beds, 'strips': strips}
    json.dump(res, open(os.path.join(DATA, 'elmwood_rows.json'), 'w'), separators=(',', ':'))
    from collections import Counter
    print('stones', len(stones), Counter(q[3] for q in stones), 'beds', len(beds), 'strips', len(strips), 'fit', fit)
    if '--preview' in sys.argv:
        pv = Image.new('RGB', (1400, 900), 'black'); d = ImageDraw.Draw(pv); x0, y0, x1, y1 = out.bounds; sc = min(1380 / (x1 - x0), 880 / (y1 - y0))
        P = lambda X, Y: ((X - x0) * sc + 10, (y1 - Y) * sc + 10)
        for p in getattr(out, 'geoms', [out]): d.line([P(*q) for q in p.exterior.coords], fill='white')
        for p in getattr(paths, 'geoms', [paths]):
            if not p.is_empty: d.polygon([P(*q) for q in p.exterior.coords], outline=(255, 140, 0))
        for lon, lat, f, kd in stones:
            X, Y = ll_to_m(lon, lat); d.point(P(X, Y), fill=[(0, 255, 0), (255, 0, 0), (60, 120, 255)][kd])
        pv.save(sys.argv[sys.argv.index('--preview') + 1])

if __name__ == '__main__': main()
