#!/usr/bin/env python3
"""OSM railway lines that pfviewer's rail data (wpg_rails_1906 + rail_history extras) doesn't have, inside the inner
terrain, for grading their embankments out of the LiDAR until built (CONFIG.terrain.embankments.extraRailsFile).
Not drawn as track. Every line gets DEFAULT_BORN — a guess (most are the GTP/NTR, CN and CP lines and spurs of
1906–1914; later yards and spurs too, which this dates too early).

  python3 tools/osm_rails.py ~/gisdata/osm/feat/wpg_rails_osm.json data/osm_rails_extra.json
(the input comes from ~/gisdata/scripts/osm_rails_extract.py over the Manitoba pbf)"""
import json, math, re, sys
from shapely.geometry import LineString, MultiLineString
from shapely.ops import unary_union

DEFAULT_BORN = 1910
HALF = 6000          # inner terrain ±m
MIN_LEN = 60

src = open('index.html').read()
C_LON = float(re.search(r'const C_LON\s*=\s*([-\d.]+)', src).group(1))
C_LAT = float(re.search(r'const C_LAT\s*=\s*([-\d.]+)', src).group(1))
ML = 111320 * math.cos(math.radians(C_LAT))
P = lambda c: [((x - C_LON) * ML, (y - C_LAT) * 111320) for x, y in c]
U = lambda c: [[round(C_LON + x / ML, 6), round(C_LAT + y / 111320, 6)] for x, y in c]

have = []
for f in json.load(open('data/wpg_rails_1906.geojson'))['features']:
    g = f['geometry']
    for l in (g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]):
        if len(l) > 1: have.append(LineString(P(l)))
for x in json.load(open('data/rail_history.json')).get('extras', []):
    have.append(LineString(P(x['coordinates'])))
have = unary_union(have).buffer(30)
box = LineString([(-HALF, -HALF), (HALF, -HALF), (HALF, HALF), (-HALF, HALF), (-HALF, -HALF)]).convex_hull

out = []
for f in json.load(open(sys.argv[1]))['features']:
    p = f['properties']
    rest = LineString(P(f['geometry']['coordinates'])).intersection(box).difference(have)
    parts = [rest] if isinstance(rest, LineString) else list(getattr(rest, 'geoms', []))
    for g in parts:
        if not isinstance(g, LineString) or g.length < MIN_LEN: continue
        out.append({'type': 'Feature', 'geometry': {'type': 'LineString', 'coordinates': U(g.simplify(1.5).coords)},
                    'properties': {'osm': p['id'], 'railway': p.get('railway'), 'name': p.get('name') or p.get('service') or '',
                                   'born': DEFAULT_BORN, 'born_basis': 'guess'}})
json.dump({'type': 'FeatureCollection', 'note': __doc__.split('\n\n')[0], 'features': out},
          open(sys.argv[2], 'w'), separators=(',', ':'))
print(len(out), 'lines,', round(sum(LineString(P(f['geometry']['coordinates'])).length for f in out) / 1000, 1), 'km')
