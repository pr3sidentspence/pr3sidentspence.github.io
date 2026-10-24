"""OSM building footprints in a box around the Forks → newline-delimited JSON (one building per line).
python extract_buildings.py manitoba.osm.pbf OUT.ndjson W,E,S,N (metres from the Forks)"""
import sys, json, math, osmium
from shapely import wkb as shwkb
from shapely.geometry import box, mapping
C_LON, C_LAT = -97.135515, 49.895396
kx = 111320*math.cos(math.radians(C_LAT)); ky = 111320
W, E, S, N = [float(v) for v in sys.argv[3].split(',')]
x0, x1, y0, y1 = C_LON+W/kx, C_LON+E/kx, C_LAT+S/ky, C_LAT+N/ky
KEEP = ('building', 'building:levels', 'height', 'roof:shape', 'roof:levels', 'start_date', 'name', 'amenity', 'shop', 'addr:housenumber', 'addr:street',
        'wikidata', 'wikipedia', 'heritage', 'construction_date', 'building:start_date', 'old_name',
        'layer', 'location', 'level', 'min_height', 'building:min_level')
fab = osmium.geom.WKBFactory(); out = open(sys.argv[2], 'w'); n = 0; from collections import Counter; kinds = Counter()
class H(osmium.SimpleHandler):
    def area(self, a):
        global n
        t = a.tags; b = t.get('building')
        if not b or b == 'no': return
        try: g = shwkb.loads(fab.create_multipolygon(a), hex=True)
        except Exception: return
        c = g.centroid
        if not (x0 <= c.x <= x1 and y0 <= c.y <= y1): return
        props = {k: t.get(k) for k in KEEP if t.get(k) is not None}
        props['id'] = ('w' if a.from_way() else 'r') + str(a.orig_id())
        geom = mapping(g)
        out.write(json.dumps({'p': props, 'g': json.loads(json.dumps(geom['coordinates'], separators=(',', ':')), parse_float=lambda s: round(float(s), 7))}, separators=(',', ':')) + '\n')
        n += 1; kinds[b] += 1
H().apply_file(sys.argv[1], locations=True)
print(n, 'buildings', kinds.most_common(15))
