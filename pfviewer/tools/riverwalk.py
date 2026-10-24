"""riverwalk.py — the Assiniboine River Walk and the Forks Historic Port, as ground in data/early_yards.json.

    ~/.venvs/pfgis/bin/python tools/riverwalk.py

Mike, 2026-10-23: add the Forks historic port and the river walk. OSM's 'River Walk' ways (~/gisdata/osm/feat/
wpg_paths.json) buffered WIDTH_M wide, dated by stage (winnipegarchitecture.ca, The Forks tour): from the rivers'
junction to the Main Street railway bridge in 1989, on west to the Legislature in the early 1990s (STAGE2, a guess
within that). The Historic Port — the landing at the junction where the boats (and today's water taxis) tie up —
is a paved landing PORT, 1989 (its outline a guess). Re-running replaces its own entries."""
import os, json, math
from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union
from shapely import affinity
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
PATHS = os.path.expanduser('~/gisdata/osm/feat/wpg_paths.json')
WIDTH_M, MAIN_ST_LON, STAGE1, STAGE2 = 3.5, -97.1330, '1989-06-01', '1992-06-01'
PORT = (-97.12985, 49.88625, 34, 12, 25)   # lon, lat, length m, width m, rotation ° — the landing at the junction (a guess)
C_LAT = 49.886; K = math.cos(math.radians(C_LAT)) * 111320; KY = 110574
m = lambda q: ((q[0] + 97.13) * K, (q[1] - C_LAT) * KY)
ll = lambda q: [round(q[0] / K - 97.13, 7), round(q[1] / KY + C_LAT, 7)]
W = [w for w in json.load(open(PATHS))['paths'] if w['t'].get('name') == 'River Walk']
mx = m((MAIN_ST_LON, C_LAT))[0]
east, west = [], []
for w in W:
    L = LineString([m(q) for q in w['p']])
    e = L.intersection(box(mx, -1e5, 1e5, 1e5)); wst = L.intersection(box(-1e5, -1e5, mx, 1e5))
    if not e.is_empty: east.append(e.buffer(WIDTH_M / 2, cap_style=1))
    if not wst.is_empty: west.append(wst.buffer(WIDTH_M / 2, cap_style=1))
def polys(g): return [[[ll(q) for q in p.exterior.coords]] for p in (getattr(g, 'geoms', None) or [g]) if p.area > 1]
x, y = m(PORT[:2]); port = affinity.rotate(box(x - PORT[2] / 2, y - PORT[3] / 2, x + PORT[2] / 2, y + PORT[3] / 2), PORT[4])
ey = json.load(open(os.path.join(DATA, 'early_yards.json')))
ey['yards'] = [Y for Y in ey['yards'] if not Y.get('source', '').startswith('tools/riverwalk.py')]
src = 'tools/riverwalk.py: OSM River Walk ways; stages from https://winnipegarchitecture.ca/digital-tours/the-forks/'
ey['yards'] += [
    {'name': 'River Walk (the Forks to the Main Street railway bridge)', 'kind': 'riverwalk', 'born': STAGE1, 'died': None, 'source': src, 'polys': polys(unary_union(east))},
    {'name': 'River Walk (on to the Legislature)', 'kind': 'riverwalk', 'born': STAGE2, 'died': None, 'source': src + ' (early 1990s; year a guess)', 'polys': polys(unary_union(west))},
    {'name': 'Forks Historic Port', 'kind': 'riverwalk', 'born': STAGE1, 'died': None, 'source': src + ' (outline a guess)', 'polys': polys(port)}]
json.dump(ey, open(os.path.join(DATA, 'early_yards.json'), 'w'), indent=1, ensure_ascii=False)
print('river walk', round(unary_union(east).area), '+', round(unary_union(west).area), 'm²; port', round(port.area), 'm²')
