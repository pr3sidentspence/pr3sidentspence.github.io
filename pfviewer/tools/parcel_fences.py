#!/usr/bin/env python3
"""parcel_fences.py — back- and side-yard fences along the real property lines of newer houses, for the viewer's
city fence layer (initCityFences): data/tiles/f/.

    ~/.venvs/pfgis/bin/python tools/parcel_fences.py ~/sandbox/Assessment_Parcels_20260923.geojson [OUT_DIR]

Mike, 2026-10-25: newer neighbourhoods should get fences at property lines, but not in front yards, and a fence between
neighbouring houses. From the City's assessment parcels (lot polygons + year built + property use):

  - lots: detached houses, side-by-sides and duplexes (USES) built MIN_BUILT or later, under MAX_LOT_M2;
  - every lot edge with another lot on its far side is a side or rear fence; an edge with no lot beyond it (street,
    lane, park) is fenced only behind the house (a lane, or the flanking street of a corner lot);
  - the front: the open edge nearest the lot's own street (its address, matched by name to wpg_roads_streetcar); the
    fences start GATE_BACK m behind the front of the house (the outer-city OSM house on the lot, else DEFAULT_SETBACK);
  - returns: at that line, short fences from each side lot line to the house wall close the back yard;
  - an edge two fenced lots share is drawn once, from the earlier house's year;
  - born = the house's year + LAG years (a hash); type wood privacy almost always, a little chain link (more of it
    on pre-1970 lots).

Output: index.json {tileM, tiles: {"tx,tz": count}, types, fields} and one file per 1 km tile (same frame as tiles/b):
{o: [x, z], f: [[born, type, x0, z0, x1, z1], ...]} in dm from the tile corner (x east, z south).
Parcels: City of Winnipeg Assessment Parcels (Open Government Licence – Winnipeg); houses © OpenStreetMap contributors."""
import sys, os, json, math, glob
from collections import defaultdict, Counter
import numpy as np
from shapely import STRtree
from shapely.geometry import shape, Polygon, LineString, Point
from shapely import transform as sh_transform

HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
C_LON, C_LAT = -97.135515, 49.895396
MLON = 111320*math.cos(math.radians(C_LAT)); MLAT = 111320
to_xz = lambda g: sh_transform(g, lambda c: np.column_stack([(c[:, 0]-C_LON)*MLON, -(c[:, 1]-C_LAT)*MLAT]))
USES = {'RESSD', 'RESSS', 'RESDU'}
MIN_BUILT, MAX_LOT_M2 = 1946, 4000
GATE_BACK, DEFAULT_SETBACK, MAX_RETURN_M, MIN_PIECE_M = 2.0, 7.5, 12.0, 0.8
LAG = (1, 4)
TILE_M = 1000
TYPES = ['chainlink', 'wood']
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(DATA, 'tiles', 'f')
h01 = lambda n, k=0: ((int(n)*2654435761 + k*40503) % 100000)/100000

# ── parcels: every one (for "is there a lot beyond this edge"), plus the details of the fenced ones
geoms, info = [], {}
for line in open(sys.argv[1]):
    line = line.strip().rstrip(',')
    if not line.startswith('{"type":"Feature"'): continue
    f = json.loads(line); p = f['properties']; g = f.get('geometry')
    if not g: continue
    try: s = to_xz(shape(g))
    except Exception: continue
    if s.geom_type == 'MultiPolygon': s = max(s.geoms, key=lambda q: q.area)
    if s.is_empty or s.geom_type != 'Polygon': continue
    i = len(geoms); geoms.append(s)
    use = (p.get('property_use_code') or '').split(' - ')[0]
    y = p.get('year_built')
    if use in USES and y and int(y) >= MIN_BUILT and s.area <= MAX_LOT_M2:
        info[i] = (int(y), (p.get('street_name') or '').upper(), int(p.get('roll_number') or i) if (p.get('roll_number') or '').isdigit() else i)
tree = STRtree(geoms)
print(len(geoms), 'parcels,', len(info), 'fenced lots')

# ── streets by name, houses from the outer-city tiles
R = json.load(open(os.path.join(DATA, 'wpg_roads_streetcar.geojson')))['features']
rg, rn = [], []
for f in R:
    g = f.get('geometry'); nm = (f['properties'].get('st_name') or '').upper()
    if not g or not nm: continue
    for part in ([g['coordinates']] if g['type'] == 'LineString' else g['coordinates'] if g['type'] == 'MultiLineString' else []):
        if len(part) > 1: rg.append(to_xz(LineString(part))); rn.append(nm)
rtree = STRtree(rg)
T = os.path.join(DATA, 'tiles', 'b'); kinds = json.load(open(os.path.join(T, 'index.json')))['kinds']
houses = []
for fn in glob.glob(os.path.join(T, '*_*.json')):
    J = json.load(open(fn)); ox, oz = J['o']
    for b in J['b']:
        if kinds[b[3]] != 'house' or (len(b)-8)//2 < 3: continue
        q = Polygon([(ox + b[8+2*k]/10, oz + b[9+2*k]/10) for k in range((len(b)-8)//2)])
        if q.is_valid and q.area > 20: houses.append(q)
htree = STRtree(houses)
print(len(rg), 'street pieces,', len(houses), 'houses')

def edges_of(poly):
    """lot outline → straight edges, near-collinear runs merged"""
    pts = list(poly.simplify(0.25).exterior.coords)[:-1]
    if len(pts) < 3: return []
    E = []
    for k in range(len(pts)):
        a, b = pts[k], pts[(k+1) % len(pts)]
        if math.dist(a, b) < 0.3: continue
        if E:
            pa, pb = E[-1]; d1 = math.atan2(pb[1]-pa[1], pb[0]-pa[0]); d2 = math.atan2(b[1]-a[1], b[0]-a[0])
            if abs((d2-d1+math.pi) % (2*math.pi)-math.pi) < math.radians(8): E[-1] = (pa, b); continue
        E.append((a, b))
    if len(E) > 1:   # the last edge may continue the first
        (pa, pb), (a, b) = E[-1], E[0]; d1 = math.atan2(pb[1]-pa[1], pb[0]-pa[0]); d2 = math.atan2(b[1]-a[1], b[0]-a[0])
        if abs((d2-d1+math.pi) % (2*math.pi)-math.pi) < math.radians(8) and pb == a: E[0] = (pa, b); E.pop()
    return E

def beyond(i, poly, a, b):
    """(outward normal, index of the lot past this edge or None)"""
    mx, mz = (a[0]+b[0])/2, (a[1]+b[1])/2; L = math.dist(a, b); nx, nz = (b[1]-a[1])/L, -(b[0]-a[0])/L
    if poly.contains(Point(mx + nx*0.5, mz + nz*0.5)): nx, nz = -nx, -nz
    pt = Point(mx + nx*1.5, mz + nz*1.5)
    for j in tree.query(pt, predicate='intersects'):
        if j != i: return (nx, nz), int(j)
    return (nx, nz), None

tiles = defaultdict(list); stats = Counter()
def emit(born, typ, a, b):
    if math.dist(a, b) < MIN_PIECE_M: return
    mx, mz = (a[0]+b[0])/2, (a[1]+b[1])/2; tx, tz = math.floor(mx/TILE_M), math.floor(mz/TILE_M)
    ox, oz = tx*TILE_M, tz*TILE_M
    tiles[(tx, tz)].append([born, typ, round((a[0]-ox)*10), round((a[1]-oz)*10), round((b[0]-ox)*10), round((b[1]-oz)*10)])
    stats['pieces'] += 1; stats['m'] += math.dist(a, b)

for n, (i, (year, street, roll)) in enumerate(info.items()):
    if n % 20000 == 0: print(f'  {n}/{len(info)}', flush=True)
    poly = geoms[i]; E = edges_of(poly)
    if len(E) < 3: stats['skip_shape'] += 1; continue
    side = [beyond(i, poly, a, b) for a, b in E]
    # the front: the open edge nearest the lot's own street
    best = (1e9, None)
    for k, ((a, b), (nrm, j)) in enumerate(zip(E, side)):
        if j is not None: continue
        m = Point((a[0]+b[0])/2, (a[1]+b[1])/2)
        for r in rtree.query(m.buffer(60)):
            if rn[r] == street:
                d = rg[r].distance(m)
                if d < best[0]: best = (d, k)
    if best[1] is None:   # no street of that name nearby: the open edge nearest any street
        for k, ((a, b), (nrm, j)) in enumerate(zip(E, side)):
            if j is not None: continue
            m = Point((a[0]+b[0])/2, (a[1]+b[1])/2); r = rtree.nearest(m)
            d = rg[r].distance(m)
            if d < best[0] and d < 40: best = (d, k)
    if best[1] is None: stats['skip_no_front'] += 1; continue
    fa, fb = E[best[1]]; (fnx, fnz), _ = side[best[1]]
    dist = lambda p: (p[0]-fa[0])*(-fnx) + (p[1]-fa[1])*(-fnz)   # into the lot from the front line
    depth = max(dist(p) for p in poly.exterior.coords)
    house = None
    for h in htree.query(poly, predicate='intersects'):
        q = houses[h]
        if poly.contains(q.representative_point()) and (house is None or q.area > house.area): house = q
    dh = min(dist(p) for p in house.exterior.coords) if house is not None else DEFAULT_SETBACK
    d0 = min(max(dh, 1.0) + GATE_BACK, depth*0.6)
    lag = LAG[0] + int(h01(roll, 1)*(LAG[1]-LAG[0]+1))
    p_wood = 0.85 if year < 1970 else 0.92 if year < 1990 else 0.97   # Mike, 2026-10-26: almost nobody fences a back yard in chain link (no privacy)
    typ = 1 if h01(roll, 2) < p_wood else 0
    for k, ((a, b), (nrm, j)) in enumerate(zip(E, side)):
        if k == best[1]: continue
        if j is not None and j in info:
            if j < i: continue   # the neighbour draws the shared edge
            born = min(year, info[j][0]) + lag
        else: born = year + lag
        da, db = dist(a), dist(b)
        if da < d0 and db < d0: continue
        if da < d0: t = (d0-da)/(db-da); a = (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t)
        elif db < d0: t = (d0-db)/(da-db); b = (b[0]+(a[0]-b[0])*t, b[1]+(a[1]-b[1])*t)
        emit(born, typ, a, b); stats['side_rear' if j is not None else 'open_back'] += 1
    if house is not None:   # returns: lot line to house wall, along the gate line
        ux, uz = fb[0]-fa[0], fb[1]-fa[1]; ul = math.hypot(ux, uz); ux, uz = ux/ul, uz/ul
        cx, cz = fa[0] - fnx*d0, fa[1] - fnz*d0
        try: cut = LineString([(cx - ux*500, cz - uz*500), (cx + ux*500, cz + uz*500)]).intersection(poly.buffer(0)).difference(house.buffer(0.05))
        except Exception: cut = LineString()   # a lot or house outline GEOS can't cut
        for g in (getattr(cut, 'geoms', None) or [cut]):
            if g.geom_type != 'LineString' or g.is_empty or g.length > MAX_RETURN_M: continue
            c = list(g.coords); emit(year + lag, typ, c[0], c[-1]); stats['return'] += 1
    stats['lots'] += 1

os.makedirs(OUT, exist_ok=True)
for fn in glob.glob(os.path.join(OUT, '*_*.json')): os.remove(fn)
for (tx, tz), L in tiles.items():
    json.dump({'o': [tx*TILE_M, tz*TILE_M], 'f': L}, open(os.path.join(OUT, f'{tx}_{tz}.json'), 'w'), separators=(',', ':'))
json.dump({'tileM': TILE_M, 'tiles': {f'{tx},{tz}': len(L) for (tx, tz), L in sorted(tiles.items())}, 'types': TYPES,
           'fields': 'born, type (index into types), x0, z0, x1, z1 in dm from the tile corner (x east, z south)',
           'source': 'tools/parcel_fences.py', 'attribution': 'City of Winnipeg Assessment Parcels (Open Government Licence – Winnipeg); houses © OpenStreetMap contributors'},
          open(os.path.join(OUT, 'index.json'), 'w'), separators=(',', ':'))
for k in sorted(stats): print(f'  {k:14} {round(stats[k])}')
print(len(tiles), 'tiles ->', OUT)
