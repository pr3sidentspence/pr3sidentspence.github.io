"""outer_roads.py — a year for every street beyond the hand-built (Goad / McPhillips) city, from the buildings beside it.

    ~/.venvs/pfgis/bin/python tools/outer_roads.py

Mike, 2026-10-23: streets (and their street lights) are missing outside the original area. The viewer only draws a
street where pfviewer's own dated buildings stand within ROAD_NEAR_M, and only within ~3 km of downtown. This writes
road_born (a year) onto each feature of data/wpg_roads_streetcar.geojson: the earliest outer-city tile building
(data/tiles/b, years from the assessment roll / OSM / hand lists) within NEAR_M of the street, sampled every STEP_M,
less LEAD years (the street goes in first); a street with no building near gets NO_BLDG_YEAR by its type (a guess:
highways and the like are post-war). The viewer uses road_born where its own buildings give no date (index.html
buildRoads: outer streets, drawn simpler, with modern street lights)."""
import os, json, math, glob
import numpy as np
from shapely.geometry import Point, LineString
from shapely import STRtree
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
C_LON, C_LAT = -97.135515, 49.895396
KX = math.cos(math.radians(C_LAT)) * 111320; KY = 110574
NEAR_M, STEP_M, LEAD = 70, 30, 1
NO_BLDG_YEAR = {'HWY': 1958, 'RD': 1950, 'BLVD': 1960, 'DR': 1965, 'WAY': 1975, 'TRAIL': 1975}
DEFAULT = 1970
pts, yrs = [], []
for fn in glob.glob(os.path.join(DATA, 'tiles', 'b', '*_*.json')):
    T = json.load(open(fn)); ox, oz = T['o']
    for r in T['b']:
        if not r[0]: continue
        ring = r[8:]; n = len(ring) // 2
        if n < 3: continue
        pts.append(Point(ox + sum(ring[0::2]) / n / 10, oz + sum(ring[1::2]) / n / 10)); yrs.append(r[0])
for L in json.load(open(os.path.join(DATA, 'tiles', 'b', 'landmarks.json')))['landmarks'].values():
    if L.get('born') and L.get('volumes'):
        r = L['volumes'][0]['ring']; pts.append(Point(sum(p[0] for p in r) / len(r), sum(p[1] for p in r) / len(r))); yrs.append(L['born'])
yrs = np.array(yrs); tree = STRtree(pts); print('dated buildings', len(pts))
path = os.path.join(DATA, 'wpg_roads_streetcar.geojson'); G = json.load(open(path))
from collections import Counter
c = Counter()
for f in G['features']:
    lines = f['geometry']['coordinates'] if f['geometry']['type'] == 'MultiLineString' else [f['geometry']['coordinates']]
    best = None
    for line in lines:
        L = LineString([((x - C_LON) * KX, -(y - C_LAT) * KY) for x, y in line])
        for d in np.arange(0, L.length + 1, STEP_M):
            p = L.interpolate(min(d, L.length)); near = tree.query(p.buffer(NEAR_M))
            if len(near): y = int(yrs[near].min()); best = y if best is None else min(best, y)
    st = f['properties'].get('st_type')
    f['properties']['road_born'] = (best - LEAD) if best else NO_BLDG_YEAR.get(st, DEFAULT)
    c['near' if best else 'none'] += 1
json.dump(G, open(path, 'w'), separators=(',', ':'))
print(c, 'decades', sorted(Counter(f['properties']['road_born'] // 10 * 10 for f in G['features']).items()))
