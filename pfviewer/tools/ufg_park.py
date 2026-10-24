"""ufg_park.py — Upper Fort Garry Provincial Park from OSM, coloured from Mike's satellite shot.

    ~/.venvs/pfgis/bin/python tools/ufg_park.py [--extract]   (--extract: re-read the park area from manitoba-latest.osm.pbf)

Mike, 2026-10-23 (top-down satellite shot, north up): the park as it is, plus the remnant bastion foundation south of
Assiniboine Ave, shown from the fort's demolition (the bastions died 1881-06-01 in building_history).
OSM maps the park in detail (way/97051564 and what's inside it):
  man_made=planter        → raised limestone beds (the park map: building sites and gardens of the old fort "are
                            demarcated by raised limestone walls"); way/1385821203 (limestone, 0.5 m, a 4.4 m circle
                            south of Assiniboine Ave) is the bastion remnant
  landuse=grass           → lawn (data/early_yards.json)
  barrier=wall steel      → the Heritage Wall (Corten, 4 m) on the line of the fort's west wall
  man_made=structure steel → the trellis on the line of the 1835 north wall (posts + a top beam) and the steel ring
                            marking the NW bastion where the two meet (height a guess)
  barrier=wall wood       → the replica wooden wall by the gate (1980s per the park map; year a guess)
  natural=tree            → trees: under a big canopy in the satellite shot → mature (born MATURE), else planted 2014
Paving: the park less the Manitoba Club and the gate, pale concrete, with the red (crushed brick) areas traced from the
satellite shot. The shot is fitted to OSM by the lawns/beds (FIT: px per m, the steel ring's centre in px; IoU 0.48).
Writes the 'Upper Fort Garry Provincial Park' entry of data/park_features.json and its lawn in data/early_yards.json."""
import sys, os, json, math
import numpy as np
from PIL import Image
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
GIS = os.path.expanduser('~/gisdata/ufg'); OSM = os.path.join(GIS, 'ufg_osm.json'); SAT = os.path.join(GIS, 'ufg_satellite_mike.webp')
PARK, CLUB, GATE = 'way/97051564', 'way/33068156', 'way/97051561'
BASTION_REMNANT, BASTION_RING = 'way/1385821203', 'way/1385842444'
TRELLIS = ['way/1385842445']
HERITAGE = ['way/1383853375', 'way/1385842443']
WOOD_WALLS = ['way/308443449', 'way/308443450']
FIT = dict(s=4.04, tx=391.0, ty=672.0)          # px per m; the steel ring's centre in the shot (tools: fit by grass IoU)
BORN, WALL_BORN, WOOD_BORN, MATURE = '2014-10-18', '2015-08-01', '1985-01-01', '1950-01-01'
DEMOLISHED = '1881-06-01'
K = math.cos(math.radians(49.887)) * 111320; KY = 110574

def extract():
    import osmium
    W, S, E, N = -97.1375, 49.8855, -97.1325, 49.8885
    out = []
    class H(osmium.SimpleHandler):
        def way(self, w):
            try: pts = [(n.lon, n.lat) for n in w.nodes]
            except Exception: return
            if any(W < x < E and S < y < N for x, y in pts): out.append({'id': 'way/%d' % w.id, 'tags': dict(w.tags), 'pts': pts})
        def node(self, n):
            if len(n.tags) and W < n.location.lon < E and S < n.location.lat < N:
                out.append({'id': 'node/%d' % n.id, 'tags': dict(n.tags), 'pts': [(n.location.lon, n.location.lat)]})
    H().apply_file(os.path.expanduser('~/gisdata/osm/manitoba-latest.osm.pbf'), locations=True)
    os.makedirs(GIS, exist_ok=True); json.dump(out, open(OSM, 'w'))

if '--extract' in sys.argv: extract()
O = {o['id']: o for o in json.load(open(OSM))}
ring0 = Polygon(O[BASTION_RING]['pts']).centroid
LON0, LAT0 = ring0.x, ring0.y
to_m = lambda x, y: ((x - LON0) * K, (y - LAT0) * KY)
to_ll = lambda a, b: (round(LON0 + a / K, 7), round(LAT0 + b / KY, 7))
def mpoly(pts): return Polygon([to_m(*q) for q in pts])
def ll_ring(g): return [list(to_ll(*q)) for q in g.exterior.coords]
def ll_polys(g):   # [[outer, hole…], …] in lon/lat
    gs = [g] if g.geom_type == 'Polygon' else list(g.geoms)
    return [[ll_ring(p)] + [[list(to_ll(*q)) for q in h.coords] for h in p.interiors] for p in gs if p.area > 0.5]

park = mpoly(O[PARK]['pts'])
inside = lambda o: any(park.buffer(0.5).contains(Point(to_m(*q))) for q in o['pts'])

# ── paving: the park less the club and the gate; red where the shot is red ──
ground = park.difference(mpoly(O[CLUB]['pts']).buffer(0.3)).difference(mpoly(O[GATE]['pts']).buffer(0.2))
im = np.asarray(Image.open(SAT).convert('RGB')).astype(int)
r, g, b = im[..., 0], im[..., 1], im[..., 2]
red = (r > g + 28) & (r > b + 45) & (r > 120)
s, tx, ty = FIT['s'], FIT['tx'], FIT['ty']
cells = []
for py in range(red.shape[0]):
    row = red[py]; px = 0
    while px < row.size:
        if row[px]:
            q = px
            while q < row.size and row[q]: q += 1
            cells.append(box((px - tx) / s, -(py + 1 - ty) / s, (q - tx) / s, -(py - ty) / s)); px = q
        else: px += 1
redm = unary_union(cells).buffer(0.6).buffer(-1.0).buffer(0.4).simplify(0.35).intersection(ground)
lawns = [o for o in O.values() if o['tags'].get('landuse') == 'grass' and inside(o) and len(o['pts']) > 3]
planters = [o for o in O.values() if o['tags'].get('man_made') == 'planter' and inside(o) and len(o['pts']) > 3]
soft = unary_union([mpoly(o['pts']) for o in lawns + planters])
redm = redm.difference(soft).difference(unary_union([LineString([to_m(*q) for q in O[i]["pts"]]).buffer(3.4) for i in HERITAGE]))   # the rusty wall itself
redm = unary_union([p for p in (redm.geoms if redm.geom_type != 'Polygon' else [redm]) if p.area >= 4])

# ── structures ──
def strip(line, w):   # a line as a w-wide flat-ended strip
    return LineString([to_m(*q) for q in line]).buffer(w / 2, cap_style=2, join_style=2)
St = []
for o in planters:
    St.append({'kind': 'limestone', 'h': float(o['tags'].get('height', 0.45)), 'ring': ll_ring(mpoly(o['pts'])), 'osm': o['id']})
St.append({'kind': 'limestone', 'h': 0.5, 'born': DEMOLISHED, 'ring': ll_ring(mpoly(O[BASTION_REMNANT]['pts'])), 'osm': BASTION_REMNANT,
           'note': "remnant foundation of the fort's south bastion (Mike, 2026-10-23), shown from the demolition"})
for i in HERITAGE:
    St.append({'kind': 'corten', 'h': 4.0, 'born': WALL_BORN, 'ring': ll_ring(strip(O[i]['pts'], 0.6)), 'osm': i,
               'note': 'Heritage Wall (Corten, 4 m; official opening Aug 2015)'})
for i in TRELLIS:   # posts every 3 m, a beam along the top
    L = LineString([to_m(*q) for q in O[i]['pts']]); n = max(2, round(L.length / 3))
    for j in range(n + 1):
        p = L.interpolate(j / n, normalized=True)
        St.append({'kind': 'trellis', 'h': 4.0, 'ring': ll_ring(box(p.x - 0.1, p.y - 0.1, p.x + 0.1, p.y + 0.1)), 'osm': i})
    St.append({'kind': 'trellis', 'h': 4.0, 'base': 3.75, 'ring': ll_ring(L.buffer(0.12, cap_style=2)), 'osm': i,
               'note': 'trellis on the line of the 1835–1851 north stone wall'})
ringp = mpoly(O[BASTION_RING]['pts'])
St.append({'kind': 'corten', 'h': 4.0, 'base': 3.7, 'ring': ll_ring(ringp), 'hole': ll_ring(ringp.buffer(-0.2)), 'osm': BASTION_RING,
           'note': 'steel ring marking the NW bastion (height a guess)'})
c = ringp.centroid; R = math.sqrt(ringp.area / math.pi)
for j in range(6):
    a = j * math.pi / 3; x, y = c.x + (R - 0.1) * math.cos(a), c.y + (R - 0.1) * math.sin(a)
    St.append({'kind': 'corten', 'h': 3.7, 'ring': ll_ring(box(x - 0.08, y - 0.08, x + 0.08, y + 0.08)), 'osm': BASTION_RING})
for i in WOOD_WALLS:
    St.append({'kind': 'woodwall', 'h': float(O[i]['tags'].get('height', 3)), 'born': WOOD_BORN, 'ring': ll_ring(mpoly(O[i]['pts'])), 'osm': i,
               'note': 'replica wooden wall (the park map: erected in the 1980s; year a guess)'})

# ── trees: mature where the shot shows a big canopy round them ──
dark = (g > r - 4) & ((r + g + b) < 300)
trees = []; nm = 0
for o in O.values():
    if o['tags'].get('natural') != 'tree' or not park.contains(Point(to_m(*o['pts'][0]))): continue
    a, bm = to_m(*o['pts'][0]); px, py = tx + a * s, ty - bm * s
    yy, xx = np.ogrid[:dark.shape[0], :dark.shape[1]]
    disk = (xx - px) ** 2 + (yy - py) ** 2 <= (4.5 * s) ** 2
    mature = dark[disk].mean() > 0.75
    nm += mature
    trees.append([*to_ll(a, bm), MATURE] if mature else [*to_ll(a, bm)])

entry = {
    'name': 'Upper Fort Garry Provincial Park', 'born': BORN, 'died': None,
    'source': 'tools/ufg_park.py: OSM (way/97051564 and its contents) with the red paving traced from Mike\'s satellite shot (2026-10-23)',
    'sources': ['https://www.upperfortgarry.com/wp-content/uploads/2016/11/ufg_park_map.pdf (park map: limestone beds, Heritage Wall, trellis, bastion, wooden wall)',
                'https://worldlandscapearchitect.com/upper-fort-garry-provincial-park-winnipeg-canada-htfc-planning-design/ (Heritage Wall: Corten steel, 400 ft, up to 13 ft)',
                'https://news.umanitoba.ca/?p=16843 (first phase opened 18 Oct 2014); https://news.gov.mb.ca/news/print,index.html?item=35796 (official opening Aug 2015)'],
    'paving': [{'born': BORN, 'color': '#BDB6A6', 'polys': ll_polys(ground)},
               {'born': BORN, 'color': '#A65A3E', 'lift': 0.045, 'polys': ll_polys(redm)}],
    'structures': St, 'trees': trees}
pf = json.load(open(os.path.join(DATA, 'park_features.json')))
pf['parks'] = [p for p in pf['parks'] if p['name'] != entry['name']] + [entry]
json.dump(pf, open(os.path.join(DATA, 'park_features.json'), 'w'), indent=1, ensure_ascii=False)

ey = json.load(open(os.path.join(DATA, 'early_yards.json')))
L = [y for y in (ey if isinstance(ey, list) else ey['yards']) if not y['name'].startswith('Upper Fort Garry Provincial Park')]
L.append({'name': 'Upper Fort Garry Provincial Park: lawn', 'kind': 'lawn', 'born': BORN, 'died': None,
          'source': 'OSM landuse=grass inside way/97051564 (tools/ufg_park.py)',
          'polys': ll_polys(unary_union([mpoly(o['pts']) for o in lawns]).intersection(park))})
if isinstance(ey, list): ey = L
else: ey['yards'] = L
json.dump(ey, open(os.path.join(DATA, 'early_yards.json'), 'w'), indent=1, ensure_ascii=False)
print(f'paving red {redm.area:.0f} m² of {ground.area:.0f}; lawns {len(lawns)}; beds {len(planters)}; structures {len(St)}; trees {len(trees)} ({nm} mature)')
