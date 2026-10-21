"""Water polygons + waterway lines from a Manitoba .osm.pbf, clipped to a box around the Forks."""
import sys, json, math, osmium
from shapely.geometry import shape, box, mapping
from shapely import wkb as shwkb
C_LON, C_LAT = -97.135515, 49.895396
kx = 111320*math.cos(math.radians(C_LAT)); ky = 111320
W, E, S, N = [float(v) for v in sys.argv[3].split(',')]   # metres from the Forks
bb = box(C_LON+W/kx, C_LAT+S/ky, C_LON+E/kx, C_LAT+N/ky)
fab = osmium.geom.WKBFactory()
polys, lines = [], []
class H(osmium.SimpleHandler):
    def area(self, a):
        t = a.tags
        if not (t.get('natural') == 'water' or t.get('waterway') == 'riverbank' or t.get('landuse') == 'reservoir'): return
        try: g = shwkb.loads(fab.create_multipolygon(a), hex=True)
        except Exception: return
        if not g.intersects(bb): return
        g = g.intersection(bb)
        if g.is_empty or g.area*kx*ky < 400: return
        polys.append({'type':'Feature','geometry':mapping(g),'properties':{'id':('w' if a.from_way() else 'r')+str(a.orig_id()),'name':t.get('name'),'water':t.get('water') or t.get('waterway'),'natural':t.get('natural')}})
    def way(self, w):
        t = w.tags
        ww = t.get('waterway')
        if ww not in ('river','stream','canal','drain','ditch'): return
        try: g = shwkb.loads(fab.create_linestring(w), hex=True)
        except Exception: return
        if not g.intersects(bb): return
        g = g.intersection(bb)
        lines.append({'type':'Feature','geometry':mapping(g),'properties':{'id':'w'+str(w.id),'name':t.get('name'),'waterway':ww,'intermittent':t.get('intermittent'),'width':t.get('width')}})
H().apply_file(sys.argv[1], locations=True)
out = sys.argv[2]
json.dump({'type':'FeatureCollection','features':polys}, open(out+'_polys.geojson','w'))
json.dump({'type':'FeatureCollection','features':lines}, open(out+'_lines.geojson','w'))
from collections import Counter
print(len(polys), 'polys', Counter(p['properties']['water'] for p in polys).most_common(8))
print(len(lines), 'lines', Counter(l['properties']['waterway'] for l in lines))
print('named rivers:', sorted({p['properties']['name'] for p in polys if p['properties']['water']=='river' and p['properties']['name']}))
