"""build_building_tiles.py — the city beyond pfviewer's hand-built buildings, as 1 km tiles for the lightweight renderer.

    python tools/build_building_tiles.py ASSESSMENT_CSV OSM_BUILDINGS_NDJSON [OUT_DIR] [PARTS_NDJSON]
                                        (default data/tiles/b; parts: OSM_BUILDINGS_NDJSON with _buildings → _parts)

Every OSM footprint in the extract (tools/extract_buildings.py) EXCEPT ones pfviewer already draws:
  - the same OSM id as a building in the autoloaded files;
  - landmarks (tools/landmarks.json): written with their footprint to OUT_DIR/landmarks.json for the viewer's
    landmark renderer instead;
  - underground ones (location=underground, or a negative layer / level — e.g. the Winnipeg Square concourse); they
    still count as replacements in tools/died_upper_bounds.py, the dig took out what stood there;
  - overlapping a pfviewer building that is still standing (no died date) by >= 50% of the larger of the two — the
    same building;
  - containing standing pfviewer buildings (>= 50% of theirs) when its own year isn't known: one OSM outline over
    several Goad pieces is either the same old building or a later one whose predecessors were never given died
    dates, and only a year tells which. Known (roll, building_years.json, Wikidata, OSM date) and after 1910 and the
    pieces' born years: kept. Otherwise listed, biggest first, in data/review_undated_footprints.geojson for a year to
    go into tools/building_years.json (then tools/died_upper_bounds.py → apply_died_bounds.py → this);
  - inside the merge_assessment.py circle (RADIUS_M) and dated <= MERGE_CUTOFF — that pipeline already took or
    deliberately left those.
Born year, in order: building_years.json; Wikidata (osm_years.py); the parcel's assessment Year Built (residential +
condo parcels only); OSM start_date / construction_date; for a
footprint on ground a pfviewer building left, the year after it died (at the earliest — still checked against the
neighbours); the median year of the NEAR_K nearest dated buildings within NEAR_M; else PLACEHOLDER_YEAR (towns
outside Winnipeg have no roll). Each building keeps a code for which (BASIS).

Height (metres): OSM height; OSM building:levels; the roll's Building Type (storeys) for the parcel's main building;
else a default by kind and size. Pitched roofs (ridge bearing given) on houses and garages under 400 m², flat otherwise. building_years.json `died` ends one.

Kind: OSM building tag; a generic tag (building=yes, residential, ...) takes the parcel's Property Use Code instead.

Output (JSON, gzip-served): index.json {tileM, tiles: {"tx,tz": count}, kinds, basis, ...} and one file per tile
"tx_tz.json": {o:[x0,z0], b:[[born, died, heightDm, kind, basis, roof, minDm, colour, ringXZ...], ...]} — ring in
decimetres from the tile's corner (world x east, z south, viewer project()); roof = 0 flat, else the ridge bearing in
degrees + 1; minDm = where the walls start (building parts over others); colour = 0xRRGGBB + 1, 0 = by kind.
grp (optional): [[first record, count], ...] — records that are one building's parts, to stand on one ground height.

Building parts (OSM building:part, PARTS_NDJSON from the same extract): a building with parts is drawn as its parts
(each with its own height / min_height, levels, colour, glass for building:material mirror|glass) plus whatever of its
outline no part covers, at the building's height — OSM often maps only the podium as parts. Heights in feet (200', 61 ft)
are converted.
Hover details, fetched only when a building in the tile is hovered: m/tx_tz.json [[osm_id, osm building tag, name,
address, property use, height source], ...] in the same order.
ODbL: footprints are OpenStreetMap data (index.json carries the attribution)."""
import sys, os, csv, json, math, re
from collections import defaultdict, Counter
import numpy as np
from scipy.spatial import cKDTree
from shapely import wkt, STRtree
from shapely.geometry import shape, Polygon
from shapely.ops import unary_union
from shapely import transform as sh_transform
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osm_years import known_year

csv.field_size_limit(1 << 30)
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
OLD_FILES = ['pastforward_2026_assessment.geojson', 'pastforward_2026_osm.geojson', 'pastforward_2026_mcphillips1910.geojson',
             'pastforward_2026_stb1880.geojson', 'pastforward_2026_legislature_osm.geojson', 'pastforward_2026_ogilvie_stack.geojson', 'pastforward_2026_additions.geojson',
             'pastforward_2026_ufg_walls.geojson', 'pastforward_2026_fort_douglas.geojson']
TILE_M = 1000
RADIUS_M, MERGE_CUTOFF = 6000, 1939          # matching/merge_assessment.py --max-radius-m / --cutoff
SAME_COVER = 0.5
NEAR_K, NEAR_M = 15, 400
PLACEHOLDER_YEAR = 1970
CONTAINER_MIN_YEAR = 1910                     # a container's year must be after this (Goad 1906/1917 pieces) ...
CONTAINER_MARGIN = 3                          # ... and this many years after the youngest piece inside it
SKIP_TAGS = {'proposed', 'construction', 'demolished', 'destroyed', 'abandoned', 'no'}
MIN_AREA = 12
def underground(p):
    if p.get('location') == 'underground': return True
    for k in ('layer', 'level'):
        try:
            if float(str(p.get(k, '0')).split(';')[0]) < 0: return True
        except ValueError: pass
    return False                                 # m² — skips sheds and slivers
C_LON, C_LAT = -97.135515, 49.895396
MLON = 111320*math.cos(math.radians(C_LAT)); MLAT = 111320
to_m = lambda g: sh_transform(g, lambda c: np.column_stack([(c[:, 0]-C_LON)*MLON, (c[:, 1]-C_LAT)*MLAT]))   # x east, y north

KINDS = ['house', 'garage', 'apartments', 'commercial', 'industrial', 'institutional', 'other']
KIND_OF = {**{k: 'house' for k in ('house', 'detached', 'semidetached_house', 'semidetached', 'terrace', 'residential', 'bungalow', 'farm', 'cabin', 'duplex')},
           **{k: 'garage' for k in ('garage', 'garages', 'shed', 'carport', 'hut')},
           **{k: 'apartments' for k in ('apartments', 'dormitory', 'hotel')},
           **{k: 'commercial' for k in ('retail', 'commercial', 'office', 'supermarket', 'kiosk')},
           **{k: 'industrial' for k in ('industrial', 'warehouse', 'manufacture', 'barn', 'farm_auxiliary', 'storage_tank', 'silo', 'hangar', 'service')},
           **{k: 'institutional' for k in ('school', 'church', 'hospital', 'university', 'college', 'public', 'civic', 'government', 'chapel', 'mosque', 'synagogue', 'temple', 'fire_station', 'sports_centre', 'stadium', 'train_station', 'transportation')}}
GENERIC = {None, 'yes', 'residential', 'building', 'roof'}
USE_KIND = [('RESAP', 'apartments'), ('RESAM', 'apartments'), ('RESGC', 'apartments'), ('CNAPT', 'apartments'),
            ('CNCOM', 'commercial'), ('CNIND', 'industrial'), ('CM', 'commercial'), ('PI', 'institutional'),
            ('IN', 'industrial'), ('VIN', 'industrial'), ('RAI', 'industrial'), ('HYD', 'industrial'), ('MTS', 'industrial'),
            ('ARP', 'industrial'), ('STA', 'industrial'), ('AGR', 'industrial'), ('RES', 'house'), ('CNR', 'house')]
def use_kind(use):
    for pre, k in USE_KIND:
        if use.startswith(pre): return k
HSRC = ['osm_height', 'osm_levels', 'roll_storeys', 'default']
BASIS = ['roll', 'osm_start_date', 'after_predecessor', 'neighbours', 'placeholder', 'wikidata', 'manual']
STOREYS = {'ONE STOREY': 1, 'ONE & 1/2 STOREY': 1.5, 'ONE & 3/4 STOREY': 1.75, 'TWO STOREY': 2, 'TWO & 1/2 STOREY': 2.5,
           'TWO/ONE STOREY': 2, 'BI-LEVEL': 1.5, '4 LEVEL SPLIT': 2, '3 LEVEL SPLIT': 1.5, 'CABOVER': 1.5, 'THREE STOREY': 3}

csv_path, osm_path = sys.argv[1:3]
out_dir = sys.argv[3] if len(sys.argv) > 3 else os.path.join(DATA, 'tiles', 'b')
parts_path = sys.argv[4] if len(sys.argv) > 4 else osm_path.replace('_buildings', '_parts')
CONCRETE = 0xA8A49B
GLASS = 0x5E7A8E

def parse_len(s):
    """OSM height / min_height → metres ("12", "12 m", "200'", "61 ft", "12'6\"")."""
    if not s: return None
    s = str(s).strip().lower().split(';')[0]
    m = re.match(r"^\s*([0-9.]+)\s*'\s*(?:([0-9.]+)\s*\")?\s*$", s)
    if m: return float(m.group(1))*0.3048 + (float(m.group(2))*0.0254 if m.group(2) else 0)
    m = re.match(r'^\s*([0-9.]+)\s*(m|ft|feet)?\s*$', s)
    if not m: return None
    v = float(m.group(1)); return v*0.3048 if m.group(2) in ('ft', 'feet') else v

def colour_of(p):
    if (p.get('building:material') or '') in ('mirror', 'glass'): return GLASS + 1
    c = p.get('building:colour') or p.get('colour')
    if c and re.match(r'^#[0-9a-fA-F]{6}$', c): return int(c[1:], 16) + 1
    if (p.get('building:material') or '') == 'concrete': return CONCRETE + 1
    return 0
os.makedirs(out_dir, exist_ok=True)

# ── pfviewer's own buildings ─────────────────────────────────────────────
hist = json.load(open(os.path.join(DATA, 'building_history.json'))).get('buildings', {})
old_ids, standing, standing_born, dead, dead_year = set(), [], [], [], []
for fn in OLD_FILES:
    p = os.path.join(DATA, fn)
    if not os.path.exists(p): continue
    for f in json.load(open(p))['features']:
        pr = f['properties']; g = f.get('geometry')
        if pr.get('osm_id'): old_ids.add(pr['osm_id'])
        if not g or g['type'] not in ('Polygon', 'MultiPolygon'): continue
        died = ((hist.get(pr.get('pf_uid')) or {}).get('set') or {}).get('died', pr.get('died'))
        try: gm = to_m(shape(g)).buffer(0)
        except Exception: continue
        if gm.is_empty or gm.area < 4: continue
        if died: dead.append(gm); dead_year.append(int(died[:4]))
        else: standing.append(gm); standing_born.append(int(pr['born'][:4]) if pr.get('born') else 0)
stree, dtree = STRtree(standing), STRtree(dead)
print(len(standing), 'standing and', len(dead), 'dead pfviewer buildings')

# ── Parcels ───────────────────────────────────────────────────────────────
parcels, prec = [], []
seen = {}
with open(csv_path, newline='') as fh:
    for r in csv.DictReader(fh):
        gw = r['Geometry']
        if not gw: continue
        y = int(r['Year Built']) if r['Year Built'].strip() else None
        st = STOREYS.get(r['Building Type'])
        k = gw[:200]
        if k in seen:   # condo units / several rolls on one lot: earliest year, tallest storeys
            p = prec[seen[k]]
            if y and (not p['y'] or y < p['y']): p['y'] = y
            if st and (not p['st'] or st > p['st']): p['st'] = st
            continue
        try: g = to_m(wkt.loads(gw)).buffer(0)
        except Exception: continue
        seen[k] = len(parcels); parcels.append(g); prec.append({'y': y, 'st': st, 'use': r['Property Use Code'] or '', 'addr': r['Full Address'] or None})
ptree = STRtree(parcels)
print(len(parcels), 'parcels')

# ── OSM footprints ────────────────────────────────────────────────────────
blds = []
with open(osm_path) as fh:
    for line in fh:
        b = json.loads(line); p = b['p']
        if p.get('building') in SKIP_TAGS or underground(p): continue
        oid = ('way/' if p['id'][0] == 'w' else 'relation/') + p['id'][1:]
        coords = b['g']
        polys = coords if isinstance(coords[0][0][0], list) else [coords]
        for poly in polys:
            try: g = to_m(Polygon(poly[0])).buffer(0)
            except Exception: continue
            if g.is_empty or g.area < MIN_AREA: continue
            if g.geom_type == 'MultiPolygon': g = max(g.geoms, key=lambda q: q.area)
            blds.append({'oid': oid, 'p': p, 'g': g})
print(len(blds), 'OSM footprints')

# ── Building parts → the building they belong to (most of the part inside it) ─
parts = []
if os.path.exists(parts_path):
    with open(parts_path) as fh:
        for line in fh:
            q = json.loads(line); co = q['g']
            for poly in (co if isinstance(co[0][0][0], list) else [co]):
                try: g = to_m(Polygon(poly[0])).buffer(0)
                except Exception: continue
                if g.is_empty or g.area < 2 or q['p'].get('building:part') in ('roof', 'no'): continue
                if g.geom_type == 'MultiPolygon': g = max(g.geoms, key=lambda r: r.area)
                parts.append({'p': q['p'], 'g': g})
btree = STRtree([b['g'] for b in blds])
for q in parts:
    best, ba = None, 0
    for i in btree.query(q['g']):
        a = q['g'].intersection(blds[i]['g']).area
        if a > ba: best, ba = i, a
    if best is not None and ba >= 0.5*q['g'].area: blds[best].setdefault('parts', []).append(q)
print(len(parts), 'building parts,', sum(1 for b in blds if b.get('parts')), 'buildings with parts')

# parcel → its buildings, so the roll's storeys go to the main one
by_parcel = defaultdict(list)
for i, b in enumerate(blds):
    hit = ptree.query(b['g'].representative_point(), predicate='within')
    b['parcel'] = int(hit[0]) if len(hit) else None
    if b['parcel'] is not None: by_parcel[b['parcel']].append(i)
for pi, ids in by_parcel.items():
    main = max(ids, key=lambda i: (KIND_OF.get(blds[i]['p'].get('building'), 'other') != 'garage', blds[i]['g'].area))
    blds[main]['main'] = True

# dated buildings, for the neighbour median
dated_xy, dated_y = [], []
for b in blds:
    pr = prec[b['parcel']] if b['parcel'] is not None else None
    b['year'] = pr['y'] if pr and pr['y'] else None
    if b['year']: c = b['g'].centroid; dated_xy.append((c.x, c.y)); dated_y.append(b['year'])
kd = cKDTree(np.array(dated_xy)); dated_y = np.array(dated_y)

def make_landmark(b, g, p, h, y, basis, kind, pr):
    """A landmark entry: tools/landmarks.json's hand-kept settings over defaults guessed from OSM, with its volumes."""
    hand = LANDMARKS.get(b['oid'], {})
    L = {'style': 'tower', 'born': y, 'basis': basis, 'kind': kind, 'name': NAMES.get(b['oid'], p.get('name')),
         'address': pr['addr'] if pr else None, 'use': pr['use'] if pr and pr['use'] else None, 'osm_building': p.get('building'),
         'footprint': 'parts' if b.get('parts') else 'outline', 'heightM': h, 'auto': not hand}
    lv = p.get('building:levels')
    try: L['floors'] = float(lv) if lv else None
    except ValueError: L['floors'] = None
    if (p.get('building:material') or '') in ('glass', 'mirror'): L['facade'] = {'type': 'curtain'}
    elif kind == 'apartments': L['facade'] = {'type': 'punched', 'bayM': 3.0, 'winW': 0.55, 'winH': 0.5, 'cornerM': 1.2}
    c = colour_of(p)
    if c and c - 1 != GLASS: L['wall'] = '#%06x' % (c - 1)
    L.update(hand)
    fp = L['footprint']
    def ringxz(q):
        ring = list(q.exterior.coords)[:-1]
        if q.exterior.is_ccw: ring = ring[::-1]          # counter-clockwise seen from above in (x, z), like the tiles
        return [[round(x, 2), round(-yn, 2)] for x, yn in ring]
    vols = []
    if fp == 'parts' and b.get('parts'):
        lvh = 3.0 if kind in ('house', 'apartments') else 4.0
        for q in b['parts']:
            qp = q['p']; top = parse_len(qp.get('height'))
            if not top and qp.get('building:levels'):
                try: top = float(qp['building:levels'])*lvh
                except ValueError: top = None
            bottom = parse_len(qp.get('min_height'))
            if bottom is None and qp.get('building:min_level'):
                try: bottom = float(qp['building:min_level'])*lvh
                except ValueError: bottom = None
            top = top or h
            if bottom is None and qp.get('building:part') == 'roof': bottom = top - 1.0   # a canopy, not a volume to the ground
            bottom = bottom or 0
            if top <= bottom + 0.3: continue
            vols.append({'ring': ringxz(q['g']), 'min': bottom, 'max': top, 'osm': qp['id'],
                         'glass': (qp.get('building:material') or '') in ('mirror', 'glass')})
        rest = g.difference(unary_union([q['g'] for q in b['parts']]))
        for poly in (getattr(rest, 'geoms', None) or [rest]):
            if poly.geom_type == 'Polygon' and poly.area >= 20 and not poly.buffer(-1.0).is_empty:
                vols.append({'ring': ringxz(poly), 'min': 0, 'max': h, 'osm': 'rest'})
    elif fp == 'drawn':
        vols = drawn_volumes(L, ringxz)
    else:
        vols.append({'ring': ringxz(g.minimum_rotated_rectangle if fp == 'rect' else g), 'min': 0, 'max': L.get('heightM') or h})
    for v in vols: v.update(L.get('volumeStyles', {}).get(v.get('osm'), {}))   # per-part overrides
    vols = [v for v in vols if not v.pop('skip', False)]                     # {"skip": true}: a part left out
    L['volumes'] = vols; L['osm_id'] = b['oid']; L['heightM'] = max(v['max'] for v in vols)
    return L

def drawn_volumes(L, ringxz):
    """footprint 'drawn': volumes given by hand in lon/lat (L['volumesLL']: [{ring: [[lon, lat], …], min, max, …styles}]),
    or a ring of n sides round a point ({circle: [lon, lat], r: metres, n}) — a building OSM doesn't have (any more)."""
    vols = []
    for v in L['volumesLL']:
        v = dict(v)
        if 'circle' in v:
            (lon, lat), r, n = v.pop('circle'), v.pop('r'), v.pop('n', 12)
            v['ring'] = [[lon + r*math.cos(2*math.pi*k/n)/MLON, lat + r*math.sin(2*math.pi*k/n)/MLAT] for k in range(n)]
        v['ring'] = ringxz(to_m(Polygon(v['ring'])))
        vols.append(v)
    return vols

AUTO_LANDMARK_M = 45     # every building at least this tall gets the landmark renderer (windows, night lights)
stats = Counter(); tiles = defaultdict(list); metas = defaultdict(list); groups = defaultdict(list); undated = []
LANDMARKS = json.load(open(os.path.join(HERE, 'landmarks.json')))['landmarks']; landmarks_out = {}
HEIGHTS = {k: v['m'] for k, v in json.load(open(os.path.join(HERE, 'building_years.json'))).get('heights', {}).items()}
TRACE = set(os.environ.get('TRACE_IDS', '').split(','))   # TRACE_IDS=way/1,way/2: print why each is skipped
def _names(v):   # a name, or [[from, to, name], …] when it changed (periods: the earlier names; name: the current one)
    if not v.get('periods'): return v['name']
    return [list(q) for q in v['periods']] + [[v['periods'][-1][1], None, v['name']]]
NAMES = {k: _names(v) for k, v in json.load(open(os.path.join(HERE, 'building_years.json'))).get('names', {}).items()}
COLOURS = {k: int(v['colour'][1:], 16) + 1 for k, v in json.load(open(os.path.join(HERE, 'building_years.json'))).get('colours', {}).items()}
DIED = {k: int(v['year']) for k, v in json.load(open(os.path.join(HERE, 'building_years.json'))).get('died', {}).items()}   # demolished since OSM mapped them
for b in blds:
    g, p = b['g'], b['p']; c = g.centroid
    if b['oid'] in old_ids:
        if b['oid'] in TRACE: print('TRACE', b['oid'], 'same osm id as a pfviewer building')
        stats['skip_same_osm_id'] += 1; continue
    ky, kb = known_year(b['oid'], p)
    if kb in ('manual', 'wikidata'): b['year'], b['basis'] = ky, kb
    elif b['year']: b['basis'] = 'roll'
    elif ky: b['year'], b['basis'] = ky, kb
    over = [(i, g.intersection(standing[i]).area) for i in stree.query(g)]
    if any(a >= SAME_COVER*max(g.area, standing[i].area) for i, a in over):
        if b['oid'] in TRACE: print('TRACE', b['oid'], 'same as a standing pfviewer building')
        stats['skip_standing_pfviewer'] += 1; continue
    inner = [i for i, a in over if a >= SAME_COVER*min(g.area, standing[i].area)]
    if inner:
        yb = max(standing_born[i] for i in inner)
        if not (b['year'] and b['year'] > CONTAINER_MIN_YEAR and b['year'] >= yb + CONTAINER_MARGIN):
            if b['oid'] in TRACE: print('TRACE', b['oid'], 'container', b['year'], yb, len(inner))
            stats['skip_container_' + ('undated' if not b['year'] else 'early')] += 1
            if not b['year']: undated.append((g, b, len(inner), yb))
            continue
        stats['kept_container'] += 1
    inside = math.hypot(c.x, c.y) <= RADIUS_M
    pr = prec[b['parcel']] if b['parcel'] is not None else None
    kind = KIND_OF.get(p.get('building'), 'other')
    if p.get('building') in GENERIC and pr and use_kind(pr['use']): kind = use_kind(pr['use'])
    # born
    y, basis = b['year'], b.get('basis')
    if not y:
        d, ii = kd.query((c.x, c.y), k=NEAR_K, distance_upper_bound=NEAR_M)
        ok = np.isfinite(d)
        if ok.sum() >= 3: y, basis = int(np.median(dated_y[ii[ok]])), 'neighbours'
        pred = [dead_year[i] for i in dtree.query(g) if g.intersection(dead[i]).area >= 0.3*min(g.area, dead[i].area)]
        if pred and (not y or y <= max(pred)): y, basis = max(pred) + 1, 'after_predecessor'
        if not y: y, basis = PLACEHOLDER_YEAR, 'placeholder'
    if inside and y <= MERGE_CUTOFF and basis != 'manual':   # a hand-set year means pfviewer's own merge missed it
        if b['oid'] in TRACE: print('TRACE', b['oid'], 'merge circle', y, basis)
        stats['skip_merge_circle'] += 1; continue
    # height
    h, hs = parse_len(p.get('height')), 'osm_height'
    if b['oid'] in HEIGHTS: h, hs = HEIGHTS[b['oid']], 'manual'
    if not h and p.get('building:levels'):
        try: h, hs = float(p['building:levels'])*(3.0 if kind in ('house', 'apartments') else 4.0) + 0.6, 'osm_levels'
        except ValueError: h = None
    if not h and b.get('main') and kind == 'house' and pr and pr['st']:
        h, hs = pr['st']*2.8 + 0.6, 'roll_storeys'
    if not h:
        a = g.area; hs = 'default'
        h = {'house': 4.0, 'garage': 2.6, 'apartments': 10.0 if a < 1500 else 13.0, 'commercial': 5.0 if a < 3000 else 7.0,
             'industrial': 7.0 if a < 3000 else 9.0, 'institutional': 8.0, 'other': 4.0 if a < 400 else 6.0}[kind]
    # roof
    roof = 0
    if kind in ('house', 'garage') and g.area < 400 and h < 12:   # any shape: the viewer splits it into rectangles (or hips the outline)
        r = g.minimum_rotated_rectangle
        if True:
            q = list(r.exterior.coords)
            e1 = (q[1][0]-q[0][0], q[1][1]-q[0][1]); e2 = (q[2][0]-q[1][0], q[2][1]-q[1][1])
            L = e1 if math.hypot(*e1) >= math.hypot(*e2) else e2
            roof = int(round(math.degrees(math.atan2(L[0], L[1])))) % 180 + 1   # ridge bearing from north, +1 so 0 = flat
    def part_top(qp):
        t = parse_len(qp.get('height'))
        try: return t or (float(qp['building:levels'])*(3.0 if kind in ('house', 'apartments') else 4.0) if qp.get('building:levels') else 0)
        except ValueError: return 0
    tallest = max([h] + [part_top(q['p']) for q in b.get('parts', [])])
    if b['oid'] in LANDMARKS or tallest >= AUTO_LANDMARK_M:
        landmarks_out[b['oid']] = make_landmark(b, g, p, h, y, basis, kind, pr)
        stats['landmark_' + ('hand' if b['oid'] in LANDMARKS else 'auto')] += 1; continue
    tx, tz = math.floor(c.x/TILE_M), math.floor(-c.y/TILE_M)
    x0, z0 = tx*TILE_M, tz*TILE_M
    bcol = COLOURS.get(b['oid']) or colour_of(p)
    meta = [b['oid'], p.get('building'), NAMES.get(b['oid'], p.get('name')), pr['addr'] if pr else None, pr['use'] if pr and pr['use'] else None, hs]
    def emit(poly, top, bottom, rf, col):
        ring = list(poly.exterior.coords)[:-1]
        if len(ring) < 3: return
        if poly.exterior.is_ccw: ring = ring[::-1]  # clockwise in (x, north) = counter-clockwise seen from above in (x, z south)
        flat = []
        for x, yn in ring: flat += [int(round((x - x0)*10)), int(round((-yn - z0)*10))]
        metas[(tx, tz)].append(meta)
        tiles[(tx, tz)].append([y, DIED.get(b['oid'], 0), int(round(top*10)), KINDS.index(kind), BASIS.index(basis), rf, int(round(bottom*10)), col] + flat)
    first = len(tiles[(tx, tz)])
    if b.get('parts'):
        lv = 3.0 if kind in ('house', 'apartments') else 4.0
        for q in b['parts']:
            qp = q['p']
            top = parse_len(qp.get('height'))
            if not top and qp.get('building:levels'):
                try: top = float(qp['building:levels'])*lv
                except ValueError: top = None
            bottom = parse_len(qp.get('min_height'))
            if bottom is None and qp.get('building:min_level'):
                try: bottom = float(qp['building:min_level'])*lv
                except ValueError: bottom = None
            top = top or h
            if bottom is None and qp.get('building:part') == 'roof': bottom = top - 1.0   # a canopy, not a volume to the ground
            bottom = bottom or 0
            if top <= bottom + 0.3: continue
            emit(q['g'], top, bottom, 0, colour_of(qp) or bcol); stats['part'] += 1
        rest = g.difference(unary_union([q['g'] for q in b['parts']]))
        for poly in (getattr(rest, 'geoms', None) or [rest]):
            if poly.geom_type == 'Polygon' and poly.area >= 20 and not poly.buffer(-1.0).is_empty: emit(poly, h, 0, 0, bcol); stats['part_rest'] += 1
    else:
        emit(g, h, 0, roof, bcol)
    if len(tiles[(tx, tz)]) - first > 1: groups[(tx, tz)].append([first, len(tiles[(tx, tz)]) - first])   # one building: one ground height
    stats['kept'] += 1; stats['basis_' + basis] += 1; stats['kind_' + kind] += 1

# lost buildings: hand landmarks with no OSM footprint (demolished before anyone mapped them, or since), drawn volumes only
for oid, hand in LANDMARKS.items():
    if not hand.get('lost') or oid in landmarks_out: continue
    L = {'style': 'tower', 'basis': 'manual', 'kind': 'commercial', 'auto': False, 'footprint': 'drawn', 'osm_building': None, **hand}
    def ringxz(q):
        ring = list(q.exterior.coords)[:-1]
        if q.exterior.is_ccw: ring = ring[::-1]
        return [[round(x, 2), round(-yn, 2)] for x, yn in ring]
    L['volumes'] = drawn_volumes(L, ringxz); L['osm_id'] = oid; L['heightM'] = max(v['max'] for v in L['volumes'])
    landmarks_out[oid] = L; stats['landmark_lost'] += 1

os.makedirs(os.path.join(out_dir, 'm'), exist_ok=True)
for (tx, tz), bl in tiles.items():
    json.dump({'o': [tx*TILE_M, tz*TILE_M], 'b': bl, **({'grp': groups[(tx, tz)]} if groups[(tx, tz)] else {})}, open(os.path.join(out_dir, f'{tx}_{tz}.json'), 'w'), separators=(',', ':'))
    json.dump(metas[(tx, tz)], open(os.path.join(out_dir, 'm', f'{tx}_{tz}.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
json.dump({'tileM': TILE_M, 'tiles': {f'{tx},{tz}': len(bl) for (tx, tz), bl in sorted(tiles.items())}, 'kinds': KINDS, 'basis': BASIS,
           'fields': 'born, died, heightDm, kind, basis, roof (0 flat, else ridge bearing+1), minDm, colour (0xRRGGBB+1, 0 = by kind), then ring x,z in dm from the tile corner',
           'attribution': '© OpenStreetMap contributors (ODbL); years: City of Winnipeg Assessment Parcels (Open Government Licence – Winnipeg)',
           'source': 'tools/build_building_tiles.py'}, open(os.path.join(out_dir, 'index.json'), 'w'), separators=(',', ':'))
json.dump({'note': 'tools/landmarks.json with footprints (tools/build_building_tiles.py)', 'landmarks': landmarks_out},
          open(os.path.join(out_dir, 'landmarks.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
to_ll = lambda g: sh_transform(g, lambda c: np.column_stack([C_LON + c[:, 0]/MLON, C_LAT + c[:, 1]/MLAT]))
undated.sort(key=lambda u: -u[0].area)
json.dump({'type': 'FeatureCollection', 'note': 'OSM footprints over standing pfviewer buildings with no known year, biggest first '
           '(tools/build_building_tiles.py). A year for one goes into tools/building_years.json.',
           'features': [{'type': 'Feature', 'properties': {'osm_id': b['oid'], 'name': b['p'].get('name'), 'osm_building': b['p'].get('building'),
                         'address': prec[b['parcel']]['addr'] if b['parcel'] is not None else None,
                         'use': prec[b['parcel']]['use'] if b['parcel'] is not None else None,
                         'area_m2': round(g.area), 'pfviewer_inside': n, 'youngest_inside_born': yb},
                         'geometry': json.loads(json.dumps(to_ll(g).__geo_interface__), parse_float=lambda s: round(float(s), 7))}
                        for g, b, n, yb in undated]},
          open(os.path.join(DATA, 'review_undated_footprints.geojson'), 'w'), separators=(',', ':'))
for k in sorted(stats): print(f'  {k:28} {stats[k]}')
print(len(tiles), 'tiles ->', out_dir)
