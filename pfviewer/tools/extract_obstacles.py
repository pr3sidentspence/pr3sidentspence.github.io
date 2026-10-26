"""extract_obstacles.py — tall masts, towers and chimneys from OSM, for pfviewer's aviation obstruction lights.

    python tools/extract_obstacles.py manitoba.osm.pbf OUT.json [W,E,S,N]   (metres from the Forks; default ±19.6 km)

man_made = mast | tower | communications_tower | chimney (and tower:type = communication) with a height tag of at
least MIN_H metres; nodes and closed ways (centroid). Output {fields, items: [[x, z, heightDm, kind, born, name], ...]}
in the viewer frame (x east, z south). born = start_date year, else 0 (the viewer's placeholder)."""
import sys, json, math, re, osmium
C_LON, C_LAT = -97.135515, 49.895396
MLON = 111320*math.cos(math.radians(C_LAT)); MLAT = 111320
MIN_H = 30
KINDS = ['mast', 'tower', 'chimney']
W, E, S, N = [float(v) for v in (sys.argv[3] if len(sys.argv) > 3 else '-19600,19600,-19600,19600').split(',')]

def height(t):
    """OSM height → metres ("30", "30 m", "30'", "98 ft", "12'6\""); unreadable = 0. Feet matter: way/502520305
    (height=30', a small tower by the Red) was read as a 30 m obstruction."""
    s = str(t.get('height') or '').strip().lower().split(';')[0]
    m = re.match(r"^\s*([0-9.]+)\s*'\s*(?:([0-9.]+)\s*\")?\s*$", s)
    if m: return float(m.group(1))*0.3048 + (float(m.group(2))*0.0254 if m.group(2) else 0)
    m = re.match(r'^\s*([0-9.]+)\s*(m|ft|feet)?\s*$', s)
    if not m: return 0
    v = float(m.group(1)); return v*0.3048 if m.group(2) in ('ft', 'feet') else v

def kind(t):
    m = t.get('man_made')
    if m in ('mast', 'communications_tower') or t.get('tower:type') == 'communication': return 'mast'
    if m == 'chimney': return 'chimney'
    if m == 'tower': return 'tower'

items = []
class H(osmium.SimpleHandler):
    def add(self, t, lon, lat):
        k = kind(t); h = height(t)
        if not k or h < MIN_H: return
        x, z = (lon - C_LON)*MLON, -(lat - C_LAT)*MLAT
        if not (W <= x <= E and S <= -z <= N): return
        m = re.match(r'\s*~?(\d{4})', t.get('start_date') or '')
        items.append([round(x, 1), round(z, 1), int(round(h*10)), KINDS.index(k), int(m.group(1)) if m else 0, t.get('name') or t.get('operator')])
    def node(self, n): self.add(n.tags, n.location.lon, n.location.lat)
    def way(self, w):
        if not w.is_closed() or not kind(w.tags): return
        try: pts = [(nd.lon, nd.lat) for nd in w.nodes][:-1]
        except osmium.InvalidLocationError: return
        self.add(w.tags, sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))
H().apply_file(sys.argv[1], locations=True)
HAND = {(267.5, 785.9): (1947, 'CN steam plant stack (Citytv), 1947')}   # hand years by position (winnipegarchitecture.ca, The Forks tour)
for r in items:
    if (r[0], r[1]) in HAND: r[4], r[5] = HAND[(r[0], r[1])]
items.sort(key=lambda r: -r[2])
json.dump({'fields': 'x, z (m, viewer frame), heightDm, kind (index into kinds), born (0 = unknown), name',
           'kinds': KINDS, 'source': 'tools/extract_obstacles.py', 'attribution': '© OpenStreetMap contributors (ODbL)', 'items': items},
          open(sys.argv[2], 'w'), separators=(',', ':'), ensure_ascii=False)
print(len(items), 'obstacles'); [print(' ', r) for r in items[:25]]
