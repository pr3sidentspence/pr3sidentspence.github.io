#!/usr/bin/env python3
"""Surface parking lots from OSM (amenity=parking; not multi-storey / underground / street-side / lane) → data/parking.json,
drawn as paved ground (kind 'parking', gravel ones 'parking_gravel') from a born year:

  - the lot serves the biggest non-house building within SERVE_M of it (city tiles, landmarks, pfviewer buildings):
    born = that building's year, but not before MIN_YEAR (cars);
  - pfviewer buildings that stood on the lot (≥ COVER of their area) and have died: not before the last of them went;
  - nothing near: FALLBACK_YEAR (a guess).
Lots are grouped into BUCKET_M squares (one ground mesh each, every lot keeping its own year).

  python3 tools/osm_parking.py ~/gisdata/osm/feat/wpg_parking_osm.json data/parking.json
(input from ~/gisdata/scripts/osm_parking_extract.py over the Manitoba pbf; ODbL — © OpenStreetMap contributors)"""
import sys, os, json, math, glob
from collections import defaultdict, Counter
import numpy as np
from shapely import STRtree
from shapely.geometry import shape, Polygon, mapping
from shapely import transform as sh_transform

HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
C_LON, C_LAT = -97.135515, 49.895396
MLON = 111320*math.cos(math.radians(C_LAT)); MLAT = 111320
to_m = lambda g: sh_transform(g, lambda c: np.column_stack([(c[:, 0]-C_LON)*MLON, (c[:, 1]-C_LAT)*MLAT]))
to_ll = lambda g: sh_transform(g, lambda c: np.column_stack([C_LON + c[:, 0]/MLON, C_LAT + c[:, 1]/MLAT]))
SERVE_M, COVER, MIN_YEAR, FALLBACK_YEAR, BUCKET_M, MIN_AREA = 40, 0.3, 1930, 1960, 2000, 60
SKIP_PARKING = {'multi-storey', 'underground', 'street_side', 'lane', 'rooftop', 'carports', 'garage_boxes'}
GRAVEL = {'gravel', 'unpaved', 'compacted', 'ground', 'dirt', 'fine_gravel', 'grass'}
OLD_FILES = ['pastforward_2026_assessment.geojson', 'pastforward_2026_osm.geojson', 'pastforward_2026_mcphillips1910.geojson',
             'pastforward_2026_stb1880.geojson', 'pastforward_2026_legislature_osm.geojson', 'pastforward_2026_additions.geojson']

# buildings: (geometry in m, born, died, big) — big = not a house or garage
geoms, borns, dieds, bigs = [], [], [], []
hist = json.load(open(os.path.join(DATA, 'building_history.json'))).get('buildings', {})
for fn in OLD_FILES:
    p = os.path.join(DATA, fn)
    if not os.path.exists(p): continue
    for f in json.load(open(p))['features']:
        pr = f['properties']; g = f.get('geometry')
        if not g or g['type'] not in ('Polygon', 'MultiPolygon') or not pr.get('born'): continue
        s = (hist.get(pr.get('pf_uid')) or {}).get('set') or {}
        died = s.get('died', pr.get('died'))
        try: gm = to_m(shape(g)).buffer(0)
        except Exception: continue
        if gm.is_empty: continue
        geoms.append(gm); borns.append(int(str(pr['born'])[:4])); dieds.append(int(str(died)[:4]) if died else None)
        bigs.append(gm.area >= 250)
T = os.path.join(DATA, 'tiles', 'b'); I = json.load(open(os.path.join(T, 'index.json')))
for fn in glob.glob(os.path.join(T, '*_*.json')):
    J = json.load(open(fn)); ox, oz = J['o']
    for b in J['b']:
        ring = [(ox + b[8+2*i]/10, -(oz + b[9+2*i]/10)) for i in range((len(b)-8)//2)]
        if len(ring) < 3: continue
        g = Polygon(ring).buffer(0)
        if g.is_empty: continue
        geoms.append(g); borns.append(int(b[0])); dieds.append(int(b[1]) or None)
        bigs.append(I['kinds'][b[3]] not in ('house', 'garage') and g.area >= 150)
for L in json.load(open(os.path.join(T, 'landmarks.json')))['landmarks'].values():
    for v in L.get('volumes') or []:
        g = Polygon([(x, -z) for x, z in v['ring']]).buffer(0)
        if g.is_empty: continue
        geoms.append(g); borns.append(int(L.get('born') or FALLBACK_YEAR)); dieds.append(int(L['died']) if L.get('died') else None); bigs.append(True)
tree = STRtree(geoms)
print(len(geoms), 'buildings')

buckets = defaultdict(list); stats = Counter(); seen = set()
for f in json.load(open(sys.argv[1]))['features']:
    p = f['properties']
    if p.get('parking') in SKIP_PARKING: stats['skip_' + p['parking']] += 1; continue
    if p['id'] in seen: continue
    seen.add(p['id'])
    try: lot = to_m(shape(f['geometry'])).buffer(0)
    except Exception: continue
    if lot.is_empty or lot.area < MIN_AREA: continue
    served, gone = None, []
    for i in tree.query(lot.buffer(SERVE_M)):
        g = geoms[i]
        inter = g.intersection(lot).area if g.intersects(lot) else 0
        if inter >= COVER*g.area:   # stood on the lot
            if dieds[i]: gone.append(dieds[i])
            continue
        if bigs[i] and (dieds[i] is None) and g.distance(lot) <= SERVE_M and (served is None or g.area > geoms[served].area): served = i
    if served is not None: y, basis = max(MIN_YEAR, borns[served]), 'served_building'
    else: y, basis = FALLBACK_YEAR, 'guess'
    if gone and max(gone) >= y: y, basis = max(gone), 'after_demolition'
    stats['basis_' + basis] += 1
    kind = 'parking_gravel' if (p.get('surface') or '') in GRAVEL else 'parking'
    c = lot.centroid
    ll = to_ll(lot.simplify(0.5))
    polys = [ll] if ll.geom_type == 'Polygon' else list(ll.geoms)
    for q in polys:
        rings = [[[round(x, 7), round(yy, 7)] for x, yy in q.exterior.coords]] + [[[round(x, 7), round(yy, 7)] for x, yy in r.coords] for r in q.interiors]
        buckets[(kind, math.floor(c.x/BUCKET_M), math.floor(c.y/BUCKET_M))].append((y, rings))
    stats[kind] += 1
out = [{'kind': k, 'name': f'parking {bx},{by}', 'born': [y for y, _ in L], 'polys': [r for _, r in L]} for (k, bx, by), L in sorted(buckets.items())]
json.dump({'note': __doc__.split('\n\n')[0], 'attribution': '© OpenStreetMap contributors (ODbL)', 'yards': out},
          open(sys.argv[2], 'w'), separators=(',', ':'))
for k in sorted(stats): print(f'  {k:24} {stats[k]}')
print(len(out), 'buckets ->', sys.argv[2])
