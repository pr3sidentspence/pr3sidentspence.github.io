"""osm_trees.py — OpenStreetMap's trees and woods for pfviewer's city tree layer (initCityTrees).

    ~/.venvs/pfgis/bin/python tools/osm_trees.py

Mike, 2026-10-23: use OSM's individual trees and woods — noting that where none are mapped (private yards) that does
not mean there are none. Input ~/gisdata/osm/feat/wpg_features.json (tools: the Winnipeg feature extract):
  natural=tree nodes                  → one tree each (leaf_type / genus → conifer 'cone' or a broadleaf shape)
  natural=tree_row ways               → a tree every ROW_M
  natural=wood, landuse=forest areas  → trees scattered WOOD_PER_M2 (natural=scrub: SCRUB_PER_M2, smaller)
Skipped: inside the hand-made tree sets (Elmwood's surveyed trees, the park_features parks) and, for woods, within
RIVER_BAND_M of the rivers where buildRiverTrees already plants the banks (inside its CONFIG.trees.maxRadius).
Planting year (the tree grows from it in the viewer):
  - stands where a building stood (pfviewer's dated pieces; the outer-city tiles): RESET_Y after the last one went
  - a street / yard tree: STREET_DELAY + 0..STREET_SPREAD years after the first building within NEAR_M went up
  - woods (not built over): always there (natural), from before the viewer's first year
  - a lone tree with nothing near: LONE_Y + 0..LONE_SPREAD
Output: data/trees/osm_trees.bin (12 bytes per tree: int16 x, z in dm from its tile's origin, int16 plant year,
uint16 scale×1000, uint8 rotation, height jitter, shape (0 vase 1 round 2 tall 3 cone), colour) + osm_trees.json
(tiles {key: [first, count, origin x, origin z]}), trees shuffled within each tile so the viewer can draw a share."""
import os, json, math, struct, glob
import numpy as np
from shapely.geometry import Polygon, Point, LineString, shape
from shapely.ops import unary_union
from shapely import STRtree
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
FEAT = os.path.expanduser('~/gisdata/osm/feat/wpg_features.json')
C_LON, C_LAT = -97.135515, 49.895396
KX = math.cos(math.radians(C_LAT)) * 111320; KY = 110574
TILE_M, ROW_M, WOOD_PER_M2, SCRUB_PER_M2 = 500, 8, 1 / 110, 1 / 200
WOODS_WITHIN_M = 10000   # woods further out than this from downtown are left out (the viewer draws trees within a few km anyway)
RIVER_BAND_M, RIVER_RADIUS_M = 35, 3500
NEAR_M, STREET_DELAY, STREET_SPREAD, RESET_Y, LONE_Y, LONE_SPREAD = 45, 3, 12, 3, 1955, 40
NATURAL = 1700
CONIFER_GENUS = {'Picea', 'Pinus', 'Abies', 'Larix', 'Juniperus', 'Thuja', 'Pseudotsuga', 'Tsuga'}
rng = np.random.default_rng(20261023)
to_xz = lambda lon, lat: ((lon - C_LON) * KX, -(lat - C_LAT) * KY)

F = json.load(open(FEAT))
def poly_xz(p): return Polygon([to_xz(*q) for q in p[0]], [[to_xz(*q) for q in h] for h in p[1:]])

# ── where trees are already planted by hand-made sets ──
skip = []
for c in [a for a in F['areas'] if 'Elmwood' in a['t'].get('name', '') and a['t'].get('landuse') == 'cemetery']:
    skip += [poly_xz(p) for p in c['polys']]
for P in json.load(open(os.path.join(DATA, 'park_features.json')))['parks']:
    if P.get('trees'):
        pts = [to_xz(t[0], t[1]) for t in P['trees']]
        skip.append(unary_union([Point(q).buffer(25) for q in pts]).convex_hull)
skip = unary_union(skip)
rivers = []
for f in json.load(open(os.path.join(DATA, 'wpg_rivers.geojson')))['features']:
    g = shape(f['geometry'])
    for p in getattr(g, 'geoms', [g]):
        if p.geom_type == 'Polygon': rivers.append(Polygon([to_xz(*q) for q in p.exterior.coords]))
river_band = unary_union([r.boundary.buffer(RIVER_BAND_M) for r in rivers]).intersection(Point(0, 0).buffer(RIVER_RADIUS_M))

# ── buildings with years: pfviewer pieces and the outer-city tiles ──
hist = json.load(open(os.path.join(DATA, 'building_history.json')))['buildings']
bl, by, bd = [], [], []
def yr(v):
    try: return float(str(v)[:4])
    except Exception: return None
for fn in ['pastforward_2026_assessment.geojson', 'pastforward_2026_osm.geojson', 'pastforward_2026_additions.geojson', 'pastforward_2026_stb1880.geojson', 'pastforward_2026_mcphillips1910.geojson']:
    pth = os.path.join(DATA, fn)
    if not os.path.exists(pth): continue
    for x in json.load(open(pth))['features']:
        p = x['properties']; h = hist.get(p.get('uid'), {})
        if h.get('remove') or not x.get('geometry'): continue
        s = h.get('set', {}); b, d = yr(s.get('born', p.get('born'))), yr(s.get('died', p.get('died')))
        try: g = shape(x['geometry'])
        except Exception: continue
        if g.is_empty or g.geom_type not in ('Polygon', 'MultiPolygon'): continue
        bl.append(Polygon([to_xz(*q) for q in (g.geoms[0] if g.geom_type == 'MultiPolygon' else g).exterior.coords])); by.append(b or 1880); bd.append(d)
for fn in glob.glob(os.path.join(DATA, 'tiles', 'b', '*_*.json')):
    T = json.load(open(fn)); ox, oz = T['o']
    for rec in T['b']:
        b, d, ring = rec[0], rec[1], rec[8:]
        pts = [(ox + ring[i] / 10, oz + ring[i + 1] / 10) for i in range(0, len(ring) - 1, 2)]
        if len(pts) >= 3:
            q = Polygon(pts)
            if q.is_valid and q.area > 4: bl.append(q); by.append(b or 1950); bd.append(d or None)
tree = STRtree(bl); print('buildings', len(bl))

def plant_year(x, z, wood):
    P = Point(x, z)
    under = [i for i in tree.query(P) if bl[i].contains(P)]
    if any(bd[i] is None for i in under): return None                 # a building stands there now
    if under: return int(max(bd[i] for i in under) + RESET_Y + rng.integers(0, 6))
    if wood: return NATURAL                                             # woods: there all along, unless built over
    near = tree.query(P.buffer(NEAR_M))
    if len(near): return int(max(1872, min(by[i] for i in near)) + STREET_DELAY + rng.integers(0, STREET_SPREAD + 1))
    return NATURAL if wood else int(LONE_Y + rng.integers(0, LONE_SPREAD + 1))

def shape_of(t, wood):
    lt, ge = t.get('leaf_type', ''), (t.get('genus') or t.get('species', '').split(' ')[0])
    if lt == 'needleleaved' or ge in CONIFER_GENUS: return 3
    if wood: return int(rng.choice([1, 2, 0, 3], p=[0.45, 0.3, 0.15, 0.1]))
    return int(rng.choice([0, 1, 2], p=[0.4, 0.45, 0.15]))

out = []   # x, z, plant, scale, shape
def add(x, z, t, wood, sc=None):
    if skip.contains(Point(x, z)): return
    py = plant_year(x, z, wood)
    if py is None: return
    out.append((x, z, py, sc or float(rng.uniform(0.7, 1.15)), shape_of(t, wood)))
for n in F['nodes']:
    if n['t'].get('natural') == 'tree': add(*to_xz(*n['p']), n['t'], False)
for w in F['ways']:
    if w['t'].get('natural') != 'tree_row': continue
    L = LineString([to_xz(*q) for q in w['p']])
    for k in range(int(L.length // ROW_M) + 1):
        p = L.interpolate(k * ROW_M); add(p.x, p.y, w['t'], False)
nw = 0
for a in F['areas']:
    t = a['t']; kind = 'wood' if (t.get('natural') == 'wood' or t.get('landuse') == 'forest') else ('scrub' if t.get('natural') == 'scrub' else None)
    if not kind: continue
    for p in a['polys']:
        g = poly_xz(p)
        if not g.is_valid: g = g.buffer(0)
        g = g.difference(river_band) if kind == 'wood' else g
        g = g.intersection(Point(0, 0).buffer(WOODS_WITHIN_M))
        if g.is_empty: continue
        n = int(g.area * (WOOD_PER_M2 if kind == 'wood' else SCRUB_PER_M2)); x0, z0, x1, z1 = g.bounds; got = 0
        from shapely import contains_xy
        while got < n:
            xs = rng.uniform(x0, x1, n * 2); zs = rng.uniform(z0, z1, n * 2); ok = contains_xy(g, xs, zs)
            for x, z in zip(xs[ok][:n - got], zs[ok][:n - got]):
                add(float(x), float(z), t, True, float(rng.uniform(0.5, 0.85)) if kind == 'scrub' else None); got += 1
        nw += got
print('trees', len(out), '(woods/scrub points tried', nw, ')')

tiles = {}
for rec in out:
    k = (math.floor(rec[0] / TILE_M), math.floor(rec[1] / TILE_M)); tiles.setdefault(k, []).append(rec)
os.makedirs(os.path.join(DATA, 'trees'), exist_ok=True)
buf = bytearray(); idx = {}; first = 0
for (i, j), L in sorted(tiles.items()):
    L = [L[q] for q in rng.permutation(len(L))]; ox, oz = i * TILE_M, j * TILE_M
    for x, z, py, sc, sh in L:
        col = int(rng.integers(0, 3)) + 5 if sh == 3 else int(rng.integers(0, 5))   # crown palette: CONFIG.trees.crownColors then the conifer colours
        buf += struct.pack('<hhhHBBBB', int(round((x - ox) * 10)), int(round((z - oz) * 10)), py, int(sc * 1000), int(rng.integers(0, 256)), int(rng.integers(0, 256)), sh, col)
    idx[f'{i},{j}'] = [first, len(L), ox, oz]; first += len(L)
open(os.path.join(DATA, 'trees', 'osm_trees.bin'), 'wb').write(buf)
json.dump({'source': 'tools/osm_trees.py from OpenStreetMap (© OpenStreetMap contributors, ODbL)', 'recordBytes': 12, 'tileM': TILE_M,
           'count': len(out), 'tiles': idx}, open(os.path.join(DATA, 'trees', 'osm_trees.json'), 'w'))
from collections import Counter
print('written', len(out), 'trees in', len(idx), 'tiles;', len(buf) // 1024, 'KB; shapes', Counter(r[4] for r in out),
      '; natural', sum(r[2] == NATURAL for r in out))
