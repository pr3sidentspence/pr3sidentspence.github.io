"""twin_bridges.py — the 1996–98 twin spans of the Main Street (Assiniboine) and Norwood (Red) bridges.

    ~/.venvs/pfgis/bin/python tools/twin_bridges.py

Mike, 2026-10-23: Main's Assiniboine bridge becomes twinned at some point. The City's chronology (Rev. 2003/2005):
Main Street Bridge — 1881, 1897, 1931, "Fourth Bridge (twin)" 1996/98; Norwood Bridge — 1890, 1931, "Third Bridge
(twin)" 1996/98. Each twin is the 1931 deck (data/pastforward_2026_bridges.geojson) moved square across onto OSM's
other carriageway (~/gisdata/osm/feat/wpg_more.json), born 1998-06-01. Written into the same bridges file (its own
features replaced on a re-run)."""
import os, json, math, uuid
from shapely.geometry import Polygon, LineString
from shapely import affinity
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
SRC = 'https://legacy.winnipeg.ca/publicworks/construction/pdf/Chronology-of-Major-Bridge-Construction-in-Winnipeg-Rev2005.pdf'
PAIRS = [('Main Street Bridge (3rd)', 'way/5001933', 'Main Street Bridge (4th, twin)'),
         ('Norwood Bridge (2nd)', 'way/151734188', 'Norwood Bridge (3rd, twin)')]
C_LAT = 49.885; K = math.cos(math.radians(C_LAT)) * 111320; KY = 110574
m = lambda q: ((q[0] + 97.132) * K, (q[1] - C_LAT) * KY)
ll = lambda q: [round(q[0] / K - 97.132, 9), round(q[1] / KY + C_LAT, 9)]
D = {w['id']: w for w in json.load(open(os.path.expanduser('~/gisdata/osm/feat/wpg_more.json')))['roads']}
path = os.path.join(DATA, 'pastforward_2026_bridges.geojson'); B = json.load(open(path))
B['features'] = [f for f in B['features'] if 'tools/twin_bridges.py' not in f['properties'].get('source_file', '')]
NS = uuid.UUID('9d3e2c41-7b5a-4c8e-a1f0-3e6b2d7c9a55')
for old, osm, name in PAIRS:
    f = next(f for f in B['features'] if f['properties']['name'] == old)
    P = Polygon([m(q) for q in f['geometry']['coordinates'][0]])
    r = P.minimum_rotated_rectangle; c = list(r.exterior.coords)
    e = max(((c[i], c[i + 1]) for i in range(4)), key=lambda q: math.dist(*q)); ux, uz = (e[1][0] - e[0][0]) / math.dist(*e), (e[1][1] - e[0][1]) / math.dist(*e)
    nx, nz = -uz, ux   # square across the deck
    L = LineString([m(q) for q in D[osm]['p']]); d = (L.centroid.x - P.centroid.x) * nx + (L.centroid.y - P.centroid.y) * nz
    T = affinity.translate(P, d * nx, d * nz)
    props = dict(f['properties']); uid = str(uuid.uuid5(NS, name))
    props.update(id=uid, uid=uid, pf_uid=uid, name=name, born='1998-06-01', born_basis='documented', source_file='tools/twin_bridges.py: ' + SRC,
                 notes=f'The 1996–98 twin beside the 1931 bridge (City chronology); placed on OSM {osm}, {abs(d):.0f} m across.')
    props.pop('died', None)
    B['features'].append({'type': 'Feature', 'properties': props, 'geometry': {'type': 'Polygon', 'coordinates': [[ll(q) for q in T.exterior.coords]]}})
    print(name, f'{d:+.1f} m across')
# the CN (Rivers subdivision) double-track bridge over the Assiniboine just east of Main St, carrying the high line into
# Union Station (Mike: "the railway bridge closer to Main St never appears"). Built with the station's approaches
# (winnipegarchitecture.ca: the High-Line Bridge, 1905; Union Station 1908–11) — the year here a guess within that.
M = {w['id']: w for w in json.load(open(os.path.expanduser('~/gisdata/osm/feat/wpg_more.json')))['misc']}
from shapely.ops import unary_union
deck = unary_union([LineString([m(q) for q in M[i]['p']]).buffer(5.5, cap_style=2) for i in ('way/13800808', 'way/106475554')]).minimum_rotated_rectangle
uid = str(uuid.uuid5(NS, 'CN Assiniboine bridge'))
B['features'].append({'type': 'Feature', 'properties': {'id': uid, 'uid': uid, 'pf_uid': uid, 'name': 'CN Assiniboine River bridge (Main Street railway bridge)',
    'type': 'bridge', 'material': 'iron', 'bridge_style': 'truss', 'floors': 1, 'born': '1908-06-01', 'born_basis': 'guess: with the high line into Union Station (1905–1911)',
    'source_file': 'tools/twin_bridges.py: OSM way/13800808 + way/106475554 (CN Rivers subdivision, bridge=yes)', 'cohort': 'bridges', 'bridge_fit': True},
    'geometry': {'type': 'Polygon', 'coordinates': [[ll(q) for q in deck.exterior.coords]]}})
print('CN rail bridge', round(deck.area), 'm²')
json.dump(B, open(path, 'w'))
