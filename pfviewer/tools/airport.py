"""airport.py — Winnipeg's airport (Stevenson Field 1928, Winnipeg International 1962, Richardson International) for the
viewer's airport layer: data/airport.json.

    ~/.venvs/pfgis/bin/python tools/airport.py

Mike, 2026-10-23: runways, the old control tower and terminal, the new terminal, hotels, landing lights, and the beacon
that revolved on top of the tower until at least the 1980s (in fog or snow you could see it sweep across the sky).
From OSM (~/gisdata/osm/feat/wpg_more.json): the YWG runways (18/36, 13/31: ends and width), taxiways (lines, drawn
TAXI_W wide) and aprons → pavement (ground in the viewer, kinds runway / taxiway / apron) and the lights the viewer
lays out along them; the beacon on the 1964 control tower (OSM way/312490411, 40 m). Buildings are city tiles with
years in tools/building_years.json. Years: RUNWAYS_PAVED etc. (guesses unless sourced)."""
import os, json, math
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
D = json.load(open(os.path.expanduser('~/gisdata/osm/feat/wpg_more.json')))
C_LAT = 49.90; K = math.cos(math.radians(C_LAT)) * 111320; KY = 110574
m = lambda q: ((q[0] + 97.22) * K, (q[1] - C_LAT) * KY)
ll = lambda q: [round(q[0] / K - 97.22, 7), round(q[1] / KY + C_LAT, 7)]
RUNWAYS_PAVED, TAXIWAYS, APRONS_OLD, NEW_TERMINAL = '1940-06-01', '1945-06-01', '1963-11-12', '2011-10-30'   # paving years: guesses (BCATP wartime paving); the 1963 airport opening; the new terminal
TAXI_W, APPROACH_FROM = 23, '1965-06-01'
FIELD_OPENED = '1928-05-27'   # Stevenson Field opened (Mike, 2026-10-24); the whole of today's boundary is grass from then (a simplification)
YWG = next(Polygon([m(q) for q in w['p']]) for w in D['aero'] if w['t'].get('name') == 'Winnipeg Richardson International Airport')
def polys(g): return [[[ll(q) for q in p.exterior.coords]] for p in (getattr(g, 'geoms', None) or [g]) if p.geom_type == 'Polygon' and p.area > 4]
runways, pave, taxi, shapes = [], [], [], []   # shapes: (priority, kind, born, name, geometry) → disjoint pavement at the end
for w in D['aero']:
    t = w['t']; L = LineString([m(q) for q in w['p']])
    if not YWG.buffer(200).intersects(L): continue
    if t.get('aeroway') == 'runway':
        wd = float(t.get('width', 45))
        runways.append({'ref': t.get('ref'), 'ends': [ll(L.coords[0]), ll(L.coords[-1])], 'width': wd, 'born': RUNWAYS_PAVED, 'lightsFrom': RUNWAYS_PAVED, 'approachFrom': APPROACH_FROM, 'approachM': 900})
        shapes.append((0, 'runway', RUNWAYS_PAVED, f"YWG runway {t.get('ref')}", L.buffer(wd / 2, cap_style=2)))
    elif t.get('aeroway') == 'taxiway':
        taxi.append(L)
    elif t.get('aeroway') == 'apron' and len(w['p']) > 3:
        A = Polygon([m(q) for q in w['p']]).buffer(0)
        new = A.centroid.y > m((0, 49.9045))[1]   # north of the old field side: the new terminal's apron
        shapes.append((3 if new else 2, 'apron', NEW_TERMINAL if new else APRONS_OLD, 'YWG apron', A))
T = unary_union([L.buffer(TAXI_W / 2, cap_style=2) for L in taxi])
shapes.append((1, 'taxiway', TAXIWAYS, 'YWG taxiways', T))
tower = next(w for w in D['aero'] if w['id'] == 'way/312490411'); tp = Polygon(tower['p']).centroid
out = {'source': 'tools/airport.py from OpenStreetMap (© OpenStreetMap contributors, ODbL); years guesses unless noted',
       'runways': runways, 'taxiwayLines': [{'line': [ll(q) for q in L.coords], 'width': TAXI_W, 'born': TAXIWAYS} for L in taxi],
       'beacon': {'lon': round(tp.x, 7), 'lat': round(tp.y, 7), 'heightM': 41.5, 'born': '1964-01-17', 'died': '1990-01-01', 'rpm': 6, 'beamM': 2500, 'beamEndR': 90, 'tiltDeg': 4,
                  'note': "on the 1964 control tower; 'until at least the 80s' (Mike) — the end year a guess"},
       'pavement': pave}

# ── the 1964 terminal (gone) and the control tower (standing), as landmarks in tools/landmarks.json ──────────────────
# Where: OSM as of 2012-09-13 (Overpass attic query, saved as ~/gisdata/osm/feat/ywg_2012-09-13_overpass.json) still had
# the old terminal, way/82348116, a 191 x ~50 m block immediately west of the tower, its long axis ~18° east of north.
# What: Mike's postcard (2026-10-24, "Winnipeg International Airport", looking NNE along the block): solid white south end,
# black glass long faces (archiseek / westenddumplings: a 58,000 sq ft glass wall with a near-black coating; glazed east and
# west, solid north and south ends — winnipegarchitecture.ca), two rows of round roof drums, a low glass link east to the
# Tyndall-stone administration building with the 125 ft tower, and a one-storey gate wing west at the south end.
# Heights: 58,000 sq ft over the two long faces → ~14 m. Drums, link and gate wing sizes from the postcard (guesses).
# Years: first flights 12 Nov 1963 (westenddumplings); closed 30 Oct 2011, demolished 2011–12 (Mike) — the end a guess.
OLD = json.load(open(os.path.expanduser('~/gisdata/osm/feat/ywg_2012-09-13_overpass.json')))['elements']
OT = next(e for e in OLD if e['id'] == 82348116)
OTP = Polygon([m((q['lon'], q['lat'])) for q in OT['geometry']])
TERM_BORN, TERM_DIED, TERM_H = 1963.87, 2012.5, 14.0
th = math.radians(71.6); AX = (math.cos(th), math.sin(th)); AV = (-AX[1], AX[0])     # u: along the block (NNE), v: across (west +)
uv = lambda q: ((q[0]*AX[0] + q[1]*AX[1]), (q[0]*AV[0] + q[1]*AV[1]))
xy = lambda u, v: (u*AX[0] + v*AV[0], u*AX[1] + v*AV[1])
U = [uv(q)[0] for q in OTP.exterior.coords]; V = sorted(uv(q)[1] for q in OTP.exterior.coords)
U0, U1 = min(U), max(U)
# the outline is the 50 m block (airside, west) plus a 23 m strip along its landside face, short of both ends
VS, VW = V[0], V[-1]; VE = min(v for v in V if v > VS + 5)
SU = [uv(q)[0] for q in OTP.exterior.coords if uv(q)[1] < VS + 1]
def box(u0, u1, v0, v1): return [ll(xy(u, v)) for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1))]
vols = [{'ring': box(U0, U1, VE, VW), 'min': 0, 'max': TERM_H, 'type': 'curtain'}]
for u in (U0 - 0.3, U1 - 1.2):                # solid stone ends, a hair proud of the glass
    vols.append({'ring': box(u, u + 1.5, VE - 0.3, VW + 0.3), 'min': 0, 'max': TERM_H + 0.4, 'type': 'blank'})
vols.append({'ring': box(U0 - 0.3, U1 + 0.3, VE - 0.3, VW + 0.3), 'min': TERM_H - 1.0, 'max': TERM_H + 0.4, 'type': 'blank'})   # white fascia
for i in range(4):                            # roof drums (round skylights): two rows of four
    for f in (0.27, 0.73):
        c = xy(U0 + (U1 - U0)*(i + 0.5)/4, VE + (VW - VE)*f)
        vols.append({'circle': ll(c), 'r': 5.5, 'n': 14, 'min': TERM_H + 0.4, 'max': TERM_H + 2.2, 'type': 'blank',
                     'roof': {'h': 0.8, 'k': 0.55, 'colour': '#B9C3C6'}})
vols.append({'ring': box(min(SU), max(SU), VS, VE + 0.5), 'min': 0, 'max': 6.0, 'type': 'curtain'})   # landside strip: low glass frontage
ADM = next(Polygon([m(q) for q in json.loads(l)['g'][0][0]]) for l in open(os.path.expanduser('~/gisdata/osm/wpg40_buildings.ndjson')) if '"r4189076"' in l)
AU = [uv(q)[0] for q in ADM.exterior.coords]; AVv = [uv(q)[1] for q in ADM.exterior.coords]
vols.append({'ring': box(min(AU) + 8, max(AU) - 8, max(AVv) - 0.5, VS + 0.5), 'min': 0, 'max': 5.5, 'type': 'curtain'})   # glass link to the admin building
vols.append({'ring': box(U0 + 1, U0 + 23, VW - 0.5, VW + 72), 'min': 0, 'max': 5.0, 'type': 'band'})                     # gate wing (guess)
TOWER = next(json.loads(l)['g'][0][0] for l in open(os.path.expanduser('~/gisdata/osm/wpg40_buildings.ndjson')) if '"w312490411"' in l)
LM = json.load(open(os.path.join(HERE, 'landmarks.json')))
LM['landmarks']['lost/ywg_terminal_1964'] = {
    'name': 'Winnipeg International Airport terminal', 'lost': True, 'born': TERM_BORN, 'died': TERM_DIED, 'kind': 'institutional',
    'footprint': 'drawn', 'floors': 3, 'facade': {'type': 'curtain', 'curtainBayM': 1.8, 'floorH': 4.6},
    'wall': '#E4DDCB', 'curtain': '#1E2329', 'glass': '#1E2329', 'roof': '#D9D7D0',
    'sources': ['OSM way/82348116 as of 2012-09-13 (Overpass attic)', 'https://www.archiseek.com/1960-winnipeg-airport/',
                'http://westenddumplings.blogspot.com/2011/10/looking-back-at-winnipegs-airports-part_30.html',
                'https://winnipegarchitecture.ca/?p=17525', "Mike's postcard, 2026-10-24"],
    'note': 'generated by tools/airport.py — edit there. Green Blankstein Russell, 1960–63; drums, link and gate wing from the postcard (guesses); demolition year a guess.',
    'volumesLL': vols}
LM['landmarks']['way/312490411'] = {
    'name': 'Winnipeg International Airport control tower', 'born': 1963.7, 'kind': 'institutional', 'footprint': 'drawn',
    'wall': '#E4DDCB', 'glass': '#1C2228', 'roof': '#5A5E62',
    'sources': ['OSM way/312490411 (40 m)', 'westenddumplings: 125 ft, Manitoba Tyndall stone', "Mike's postcard, 2026-10-24 (dark cab band near the top)"],
    'note': 'generated by tools/airport.py — edit there. Cab band heights from the postcard (guess). The beacon is in data/airport.json.',
    'volumesLL': [{'ring': TOWER, 'min': 0, 'max': 33.0, 'type': 'blank'},
                  {'ring': TOWER, 'min': 33.0, 'max': 38.0, 'type': 'band'},
                  {'ring': TOWER, 'min': 38.0, 'max': 39.5, 'type': 'blank', 'roof': {'h': 0.8, 'k': 0.4, 'colour': '#5A5E62'}}]}
json.dump(LM, open(os.path.join(HERE, 'landmarks.json'), 'w'), indent=2, ensure_ascii=False)
# the old apron in front of it (2012's one big apron, less the buildings on it), paved from the 1963 opening
OA = Polygon([m((q['lon'], q['lat'])) for q in next(e for e in OLD if e['id'] == 96605892)['geometry']]).buffer(0)
OA = OA.difference(unary_union([OTP.buffer(2), ADM.buffer(2)] + [Polygon([m((q['lon'], q['lat'])) for q in e['geometry']]).buffer(2)
                   for e in OLD if e.get('tags', {}).get('building') and len(e.get('geometry') or []) > 3]))
shapes.append((2, 'apron', APRONS_OLD, 'YWG apron (1963 terminal)', OA))
# Disjoint ground (Mike, 2026-10-24: grass between the runways and taxiways; the paving shimmered where pieces overlapped —
# the viewer's log depth buffer ignores polygon offsets, so overlapping patches z-fight). Each piece keeps only what no
# higher-priority piece covers (runway > taxiway > old apron > newer aprons). Grass: the airport's OSM boundary less all of
# that, from FIELD_OPENED, plus grass under each paved piece until the year it was paved.
taken = None
for pri, kind, born, name, G in sorted(shapes, key=lambda r: r[0]):
    G = G.buffer(0) if taken is None else G.buffer(0).difference(taken)
    if G.is_empty or G.area < 4: continue
    pave.append({'name': name, 'kind': kind, 'born': born, 'died': None, 'polys': polys(G.simplify(0.3))})
    pave.append({'name': 'YWG grass (before ' + name + ')', 'kind': 'airfield', 'born': FIELD_OPENED, 'died': born, 'polys': polys(G.simplify(0.3))})
    taken = G if taken is None else unary_union([taken, G])
# less the streets inside the boundary (drawn by the viewer ROAD_W x 2 wide — CONFIG.roadWidths), so they don't z-fight either
RW = {'BLVD': 18, 'HWY': 16, 'AVE': 12, 'ST': 10, 'RD': 10, 'DR': 10, 'CRES': 9, 'WAY': 9, 'ROW': 8, 'LANE': 6, 'PL': 9, 'BAY': 9, 'PATH': 5, 'TRAIL': 5}
streets = []
for f in json.load(open(os.path.join(DATA, 'wpg_roads_streetcar.geojson')))['features']:
    g = f['geometry']
    for line in (g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]):
        L = LineString([m(q) for q in line])
        if L.length > 0 and YWG.intersects(L): streets.append(L.buffer(RW.get(f['properties'].get('st_type'), 9) + 1.0))
grass = YWG.buffer(0).difference(unary_union([taken] + streets))
print(len(streets), 'street pieces cut from the grass')
pave.append({'name': 'YWG grass', 'kind': 'airfield', 'born': FIELD_OPENED, 'died': None, 'polys': polys(grass.simplify(1.0))})
print('old terminal', round(U1 - U0), 'x', round(VW - VE), 'm + strip', round(max(SU) - min(SU)), 'x', round(VE - VS), 'm; link', round(VS - max(AVv)), 'm; old apron', round(OA.area), 'm2')
json.dump(out, open(os.path.join(DATA, 'airport.json'), 'w'), separators=(',', ':'))
print(len(runways), 'runways', [r['ref'] for r in runways], len(taxi), 'taxiway lines', len(pave), 'pavement pieces')
