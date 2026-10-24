"""ballpark.py — Blue Cross Park (CanWest Global Park 1999, then Shaw Park, now Blue Cross Park) at the Forks.

    ~/.venvs/pfgis/bin/python tools/ballpark.py

Mike, 2026-10-23: add the ballpark. OSM has the stadium's outline (way/250698229, leisure=stadium) and the field
(way/250698235, leisure=pitch baseball) but no building. The stands: the outline less the field (and a STANDS_GAP
apron), each piece of at least MIN_M2 a concrete grandstand STANDS_FLOORS high; the field: grass (early_yards,
kind ballfield). Built 1998 for the 1999 Pan American Games (winnipegarchitecture.ca, The Forks tour). Names by period
(names: [[from, to, name]…]): CanWest Global Park 1999–2010 (guess for the change), Shaw Park 2010–2019, Blue Cross Park
from 2019 (the last two from memory — check). Writes into data/pastforward_2026_additions.geojson (replacing its own
features) and data/early_yards.json."""
import os, json, math, uuid
from shapely.geometry import Polygon
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
D = json.load(open(os.path.expanduser('~/gisdata/osm/feat/wpg_more.json')))
C_LAT = 49.8944; K = math.cos(math.radians(C_LAT)) * 111320; KY = 110574
m = lambda q: ((q[0] + 97.1325) * K, (q[1] - C_LAT) * KY)
ll = lambda q: [round(q[0] / K - 97.1325, 7), round(q[1] / KY + C_LAT, 7)]
STANDS_GAP, MIN_M2, STANDS_FLOORS, BORN = 3, 250, 2, '1999-05-01'
NAMES = [[1999, 2010, 'CanWest Global Park'], [2010, 2019, 'Shaw Park'], [2019, None, 'Blue Cross Park']]
S = Polygon([m(q) for q in next(w for w in D['misc'] if w['id'] == 'way/250698229')['p']]).buffer(0)
F = Polygon([m(q) for q in next(w for w in D['misc'] if w['id'] == 'way/250698235')['p']]).buffer(0)
# home plate: where the field's two longest straight edges (the foul lines) meet; the stands are the part of the ring
# within HOME_M of it (behind home and down the lines; the outfield has no stands)
def home_plate(P):
    c = list(P.exterior.coords); e = sorted(((math.dist(c[i], c[i + 1]), c[i], c[i + 1]) for i in range(len(c) - 1)), reverse=True)[:2]
    (_, a1, a2), (_, b1, b2) = e
    d1 = (a2[0] - a1[0], a2[1] - a1[1]); d2 = (b2[0] - b1[0], b2[1] - b1[1]); den = d1[0] * d2[1] - d1[1] * d2[0]
    t = ((b1[0] - a1[0]) * d2[1] - (b1[1] - a1[1]) * d2[0]) / den
    return math.degrees(math.acos(abs(d1[0] * d2[0] + d1[1] * d2[1]) / (math.hypot(*d1) * math.hypot(*d2)))), (a1[0] + d1[0] * t, a1[1] + d1[1] * t)
HOME_M = 70
ang, hp = home_plate(F)
from shapely.geometry import Point
stands = S.difference(F.buffer(STANDS_GAP)).intersection(Point(hp).buffer(HOME_M))
print('home plate corner', round(ang), 'deg at', [round(v) for v in hp])
pieces = [p for p in (getattr(stands, 'geoms', None) or [stands]) if p.geom_type == 'Polygon' and p.area >= MIN_M2]
NS = uuid.UUID('2b7d9a10-55a1-4f0e-9c3b-1f4a6c8e0d21'); TAG = 'tools/ballpark.py'
add = json.load(open(os.path.join(DATA, 'pastforward_2026_additions.geojson')))
add['features'] = [f for f in add['features'] if f['properties'].get('source_file') != TAG]
for i, p in enumerate(pieces):
    q = p.simplify(0.5); uid = str(uuid.uuid5(NS, f'stands {i}'))
    add['features'].append({'type': 'Feature', 'properties': {
        'uid': uid, 'pf_uid': uid, 'name': 'Blue Cross Park grandstand', 'names': NAMES, 'material': 'concrete', 'floors': STANDS_FLOORS,
        'roof_type': 'flat', 'no_windows': True, 'born': BORN, 'construction_months': 12, 'born_basis': 'built 1998 for the 1999 Pan Am Games',
        'died_basis': 'still_standing', 'cohort': 'manual', 'source_file': TAG,
        'footprint_source': 'OSM stadium outline (way/250698229) less the field (way/250698235)', 'area_m2': round(p.area, 1)},
        'geometry': {'type': 'Polygon', 'coordinates': [[ll(c) for c in q.exterior.coords]]}})
json.dump(add, open(os.path.join(DATA, 'pastforward_2026_additions.geojson'), 'w'), ensure_ascii=False)
ey = json.load(open(os.path.join(DATA, 'early_yards.json')))
ey['yards'] = [Y for Y in ey['yards'] if not Y.get('source', '').startswith(TAG)]
ey['yards'].append({'name': 'Blue Cross Park: field', 'kind': 'ballfield', 'born': BORN, 'died': None, 'source': TAG + ' (OSM way/250698235)',
                    'polys': [[[ll(c) for c in F.exterior.coords]]]})
json.dump(ey, open(os.path.join(DATA, 'early_yards.json'), 'w'), indent=1, ensure_ascii=False)
print(len(pieces), 'stand pieces', [round(p.area) for p in pieces], 'field', round(F.area))
