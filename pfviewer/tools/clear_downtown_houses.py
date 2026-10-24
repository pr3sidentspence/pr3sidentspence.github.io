"""clear_downtown_houses.py — houses, sheds and stables downtown die a year before a larger building goes up nearby.

    ~/.venvs/pfgis/bin/python tools/clear_downtown_houses.py [--area north|south] [--apply] [--blocks] [--why]   (WHY=1987,2015: reasons per died year)

Mike, 2026-10-23: by today there are no houses, sheds, stables or garages in the area north of Broadway, east of
Memorial Blvd (Route 62), west of Main and south of Portage (the polygon those four street centrelines in
data/wpg_roads.geojson close). Every standing pfviewer piece there that is house-like (HOUSE_NAMES, or unnamed and wood,
or unnamed, small and at most 1.5 storeys) gets died = during the year before the nearest larger, later building:
  larger = at least BIG_M2 and BIG_RATIO × its own area, from pfviewer's own buildings (dead or alive) or the outer-city
           tiles (data/tiles/b, OSM with roll / Wikidata / hand years); later = built at least 2 years after it was born;
  nearest = edge distance <= NEAR_M; among those within TIE_M of the nearest, the earliest.
Fences (LineStrings) die with the nearest cleared house within FENCE_M, else by the same rule. The rest (mostly on
blocks whose modern building has no year here) go with the nearest dated piece on the same city block (faces of the
road centrelines), else that block's earliest larger later building; pieces on a block with none are listed and left alone. Written to data/building_history.json (set.died, died_basis replaced_by_later_building,
replaced_by), so regenerating the building files keeps them. Only pieces with no died date are touched.

--area south (Mike, same day): Broadway down to the Assiniboine, Osborne St (Route 62 south of Broadway) to Main — the
same, except the houses at KEEP points, which still stand."""
import sys, os, re, ast, json, math, glob
from collections import Counter
import numpy as np
from shapely import STRtree
from shapely import transform as sh_transform
from shapely.geometry import shape, Polygon, Point
from shapely.ops import polygonize, unary_union
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
sys.path.insert(0, os.path.join(HERE, '..', 'matching'))
from merge_assessment import iso_in_years

OLD_FILES = ['pastforward_2026_assessment.geojson', 'pastforward_2026_osm.geojson', 'pastforward_2026_mcphillips1910.geojson',
             'pastforward_2026_stb1880.geojson', 'pastforward_2026_legislature_osm.geojson', 'pastforward_2026_ogilvie_stack.geojson',
             'pastforward_2026_additions.geojson', 'pastforward_2026_ufg_walls.geojson', 'pastforward_2026_fort_douglas.geojson']
AREAS = {   # streets (centrelines in data/wpg_roads.geojson) + rivers that close the area, a point inside it, houses that stay
    'north': {'streets': ('Portage Ave', 'Main St', 'Broadway', 'Memorial Blvd'), 'rivers': False, 'inside': (-97.1415, 49.8925), 'keep': []},
    'south': {'streets': ('Broadway', 'Osborne St N', 'Osborne St Bridge', 'Main St', 'Main Street Bridge'), 'rivers': True,
              'inside': (-97.1405, 49.8855),
              'keep': [(49.886096258302274, -97.13976987658887), (49.88355175683411, -97.14252572134018), (49.883441253029545, -97.14272507495838),
                       (49.88406461865855, -97.14356809143389), (49.88401518203148, -97.14378307869723), (49.88439663877216, -97.14329497553908),
                       (49.88449510108972, -97.14332234746463), (49.88481571725826, -97.14269806774294), (49.88505166807853, -97.14285929628042),
                       (49.88299963718971, -97.14244608752465)]},   # Mike, 2026-10-23: pitched-roof houses (and an outbuilding) still there
}
AREA_NAME = sys.argv[sys.argv.index('--area') + 1] if '--area' in sys.argv else 'north'
CFG = AREAS[AREA_NAME]
KEEP_M = 2
KEEP_UIDS = {'77c2902b-5b96-457d-a90b-5f6c9c0c4907', '913ae155-b39e-4d9b-b715-9a41f3ad3ae4', '8cc8d66c-e8ae-4c76-8511-db431542e800',
             '73416d38-97f8-44e3-bf10-e11db7c558d4'}   # Dalnavert (Macdonald House, a museum) and its wing, mudroom and sunroom
HOUSE_PART = re.compile(r'^(dwg|dwellings?( over)?|(livery )?stables?( office)?|livery|drive shed|shed|lumber shed|garage|ice house|'
                        r'coach house|carriage house|greenhouse)$', re.I)
SMALL_M2 = 80
BIG_M2, BIG_RATIO = 250, 2.0
NEAR_M, TIE_M, FENCE_M = 40, 3, 15
TAG = 'tools/clear_downtown_houses.py'
NOTE = 'Downtown house / shed / stable cleared a year before a larger building nearby (placeholder).'
GOAD_YEAR, GOAD_SURVEY_ISO = 1906, '1906-07-02'   # a piece the 1906 survey drew stood until after it
C_LON, C_LAT = -97.135515, 49.895396
MLON = 111320*math.cos(math.radians(C_LAT)); MLAT = 111320
to_m = lambda g: sh_transform(g, lambda c: np.column_stack([(c[:, 0]-C_LON)*MLON, (c[:, 1]-C_LAT)*MLAT]))

roads = [to_m(shape(f['geometry'])) for f in json.load(open(os.path.join(DATA, 'wpg_roads.geojson')))['features']
         if f['properties'].get('full_name') in CFG['streets']]
if CFG['rivers']: roads += [to_m(shape(f['geometry'])).boundary for f in json.load(open(os.path.join(DATA, 'wpg_rivers.geojson')))['features']]
pin = to_m(Point(*CFG['inside']))
AREA = [p for p in polygonize(unary_union(roads)) if p.contains(pin)][0]
KEEP = [to_m(Point(lon, lat)) for lat, lon in CFG['keep']]
print(f'area {AREA_NAME}: {AREA.area/1e6:.2f} km², bounds {[round(v) for v in AREA.bounds]}')

NAMED_HOUSE = re.compile(r"\b(house|cottage|residence|villa)\b(?! of )", re.I)
def house_like(pr, g):
    n = (pr.get('name') or '').strip()
    if NAMED_HOUSE.search(n) and not re.search(r'apartment|block|hotel|hall|school|club|lodge', n, re.I) and not re.search(r'government', n, re.I): return True
    if n: return all(HOUSE_PART.match(s.strip()) for s in re.split(r'\s+and\s+', n, flags=re.I))
    if (pr.get('material') or '').startswith('wood'): return True
    return g.area < SMALL_M2 and (pr.get('floors') or 1) <= 1.5

hist = json.load(open(os.path.join(DATA, 'building_history.json'))); H = hist['buildings']
houses, fences, kept, big, big_y, big_name = [], [], [], [], [], []
for fn in OLD_FILES:
    p = os.path.join(DATA, fn)
    if not os.path.exists(p): continue
    for f in json.load(open(p))['features']:
        pr = f['properties']; g = f.get('geometry')
        h = H.get(pr.get('pf_uid')) or {}
        if not g or h.get('remove') or not pr.get('born'): continue
        mine = any(TAG in x for x in h.get('sources', []))   # dated by an earlier run: redo
        died = None if mine else (h.get('set') or {}).get('died', pr.get('died'))
        try: gm = to_m(shape(g))
        except Exception: continue
        if gm.is_empty: continue
        by = int(((h.get('set') or {}).get('born') or pr['born'])[:4])
        if g['type'] in ('Polygon', 'MultiPolygon'):
            gm = gm.buffer(0)
            if gm.area >= BIG_M2: big.append(gm); big_y.append(by); big_name.append(pr.get('name') or pr.get('address') or pr.get('pf_uid'))
        if died or not AREA.contains(gm.representative_point()): continue
        if g['type'] == 'LineString': fences.append((pr['pf_uid'], gm, by))
        elif pr.get('pf_uid') in KEEP_UIDS or any(gm.distance(k) <= KEEP_M for k in KEEP): kept.append((pr['pf_uid'], pr.get('name') or '', by, round(gm.area), mine))
        elif house_like(pr, gm):
            houses.append((pr['pf_uid'], gm, by, pr.get('name') or ''))
            if pr.get('name') and NAMED_HOUSE.search(pr['name']): print('  named house:', pr['name'], by, round(gm.area))
for fp in glob.glob(os.path.join(DATA, 'tiles', 'b', '*_*.json')):
    t = json.load(open(fp)); ox, oz = t['o']
    for r in t['b']:
        if not r[0]: continue
        q = r[8:]
        ring = Polygon([(ox + q[i]/10, -(oz + q[i+1]/10)) for i in range(0, len(q) - 1, 2)]).buffer(0)
        if ring.area >= BIG_M2: big.append(ring); big_y.append(int(r[0])); big_name.append('OSM tile building')
for lm in json.load(open(os.path.join(DATA, 'tiles', 'b', 'landmarks.json')))['landmarks'].values():   # tall ones aren't in the tiles
    if not lm.get('born'): continue
    vols = lm['volumes'] if isinstance(lm['volumes'], list) else ast.literal_eval(lm['volumes'])
    g = unary_union([Polygon([(x, -z) for x, z in v['ring']]).buffer(0) for v in vols])
    if g.area >= BIG_M2: big.append(g); big_y.append(int(lm['born'])); big_name.append(lm.get('name') or lm.get('address') or lm.get('osm_id'))
btree = STRtree(big)
print(len(kept), 'kept (KEEP points):', kept)
print(len(houses), 'house-like pieces,', len(fences), 'fences standing in the area;', len(big), 'larger buildings')

def replacer(g, born, area):
    cands = []
    for i in btree.query(g.buffer(NEAR_M)):
        if big_y[i] < max(born + 2, GOAD_YEAR + 1) or big[i].area < BIG_RATIO*area: continue
        d = g.distance(big[i])
        if d <= NEAR_M: cands.append((d, big_y[i], i))
    if not cands: return None
    d0 = min(c[0] for c in cands)
    return min((c for c in cands if c[0] <= d0 + TIE_M), key=lambda c: c[1])

out, left = {}, []
for uid, g, by, name in houses:
    r = replacer(g, by, g.area)
    if r: out[uid] = (r[1], big_name[r[2]], f'the larger building {r[0]:.0f} m away, built {r[1]}')
    else: left.append((uid, g, by, name or 'house-like'))
cleared = [(g, out[uid]) for uid, g, by, _ in houses if uid in out]
ctree = STRtree([c[0] for c in cleared]) if cleared else None
for uid, g, by in fences:
    near = sorted((g.distance(cleared[i][0]), i) for i in ctree.query(g.buffer(FENCE_M))) if ctree else []
    if near and near[0][0] <= FENCE_M and cleared[near[0][1]][1][0] >= by + 2: out[uid] = cleared[near[0][1]][1]; continue
    r = replacer(g, by, 0)
    if r: out[uid] = (r[1], big_name[r[2]], f'the larger building {r[0]:.0f} m away, built {r[1]}')
    else: left.append((uid, g, by, 'fence'))
n_near = len(out)
# The rest (mostly blocks whose modern building has no year): the nearest piece on the same city block that got a date.
blocks = list(polygonize(unary_union([to_m(shape(f['geometry'])) for f in json.load(open(os.path.join(DATA, 'wpg_roads.geojson')))['features']
                                      if shape(f['geometry']).length > 0])))
bltree = STRtree(blocks)
def block_of(g):
    pt = g.representative_point()
    return next((int(i) for i in bltree.query(pt, predicate='within')), None)
dated = [(g, out[uid], block_of(g)) for uid, g, *_ in [(u, g) for u, g, *_ in houses] + [(u, g) for u, g, _ in fences] if uid in out]
none = []
for uid, g, by, what in left:
    b = block_of(g)
    near = sorted((g.distance(dg), v) for dg, v, db in dated if db is not None and db == b and v[0] >= max(by + 2, GOAD_YEAR + 1))
    if near: Y, nm, _ = near[0][1]; out[uid] = (Y, nm, f'with its block: the nearest dated piece on it ({near[0][0]:.0f} m) goes for {nm}, built {Y}'); continue
    on = [i for i in btree.query(blocks[b]) if big_y[i] >= max(by + 2, GOAD_YEAR + 1) and blocks[b].contains(big[i].representative_point())] if b is not None else []
    if on: i = min(on, key=lambda i: big_y[i]); out[uid] = (big_y[i], big_name[i], f'with its block: its earliest larger building ({big_name[i]}) built {big_y[i]}')
    else: none.append((uid, what, by))
print(n_near, 'dated by a building within', NEAR_M, 'm;', len(out) - n_near, 'by their block;', len(none), 'left alone')
print('died years:', sorted(Counter(v[0] - 1 for v in out.values()).items()))
for n in none: print('  none:', n)

if '--apply' in sys.argv:
    for uid, (Y, by_name, d) in out.items():
        e = H.setdefault(uid, {})
        e['sources'] = [x for x in e.get('sources', []) if TAG not in x]
        e['notes'] = e.get('notes', '').replace(NOTE, '').strip()
        e['notes'] = (e['notes'] + ' ' if e['notes'] else '') + NOTE
        e['sources'].append(f'tools/clear_downtown_houses.py (Mike, 2026-10-23: no houses / sheds / stables left between '
                                           f'{"Broadway, Memorial, Portage and Main" if AREA_NAME == "north" else "Broadway, Osborne, the Assiniboine and Main"}): {d}')
        died = max(iso_in_years(uid, 'downtown_cleared', Y - 1, Y - 1), GOAD_SURVEY_ISO)
        s = e.setdefault('set', {})
        s.update(died=died, died_low=str(Y - 1), died_high=str(Y), died_basis='replaced_by_later_building', replaced_by=by_name)
        s.setdefault('date_precision', {})['died'] = 'year'
    for uid, *_, mine in kept:   # dated by an earlier run before it was on the keep list
        if mine:
            e = H[uid]; e['sources'] = [x for x in e['sources'] if TAG not in x]; e['notes'] = e.get('notes', '').replace(NOTE, '').strip()
            for k in ('died', 'died_low', 'died_high', 'died_basis', 'replaced_by'): e.get('set', {}).pop(k, None)
    json.dump(hist, open(os.path.join(DATA, 'building_history.json'), 'w'), indent=1, ensure_ascii=False)
    print('written', len(out))
if '--blocks' in sys.argv:
    rn = [(to_m(shape(f['geometry'])), f['properties'].get('full_name')) for f in json.load(open(os.path.join(DATA, 'wpg_roads.geojson')))['features']]
    left_g = {u: g for u, g, *_ in left}
    per = Counter(block_of(left_g[u]) for u, *_ in none)
    for b, n in per.most_common():
        if b is None: print(n, 'no block'); continue
        print(n, round(blocks[b].area), sorted({nm for g, nm in rn if g.distance(blocks[b]) < 1 and nm}))
    und = {f['properties']['osm_id']: f['properties'] for f in json.load(open(os.path.join(DATA, 'review_undated_footprints.geojson')))['features']}
    for b, n in per.most_common():
        if b is None: continue
        print('--', sorted({nm for g, nm in rn if g.distance(blocks[b]) < 1 and nm}))
        for line in open(os.path.expanduser('~/gisdata/osm/wpg40_buildings.ndjson')):
            r = json.loads(line); p = r['p']
            if not (-97.15 < r['g'][0][0][0][0] < -97.13): continue
            g = to_m(shape({'type': 'MultiPolygon', 'coordinates': r['g']})).buffer(0)
            if g.area < 300 or not blocks[b].contains(g.representative_point()): continue
            oid = 'way/' + p['id'][1:]
            print('  ', oid, round(g.area), p.get('name'), p.get('addr:housenumber'), p.get('addr:street'), p.get('building:levels'), 'UNDATED' if oid in und else '', (und.get(oid) or {}).get('address'))
if '--why' in sys.argv:
    for yr in map(int, os.environ.get('WHY', '').split(',')):
        print(yr, Counter(v[2].split(' (')[0] if 'nearest dated' in v[2] else v[2] for v in out.values() if v[0] - 1 == yr).most_common(6))
