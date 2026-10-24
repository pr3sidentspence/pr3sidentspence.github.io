"""stockyards.py — the Union Stockyards (St. Boniface, 1913–1988) and the packing plants beside them.

    ~/.venvs/pfgis/bin/python tools/stockyards.py

Mike, 2026-10-23: reconstruct the yards from the ruins (his satellite shot of the pen foundations, fitted to OSM's
Ibrahima Diallo Ave / Paulette Duguay St: 2.5 px/m, north up) and an old aerial photo (covered pens in long rows behind
the packing plants, open pens beyond). Writes data/pastforward_2026_stockyards.geojson:
  - the pens: blocks BLOCK_M with ALLEY_M alleys over OSM's 'Former Union Stock Yards' (way/105995544) east of PENS_W
    (the plant sites are west of it), less today's pond; open blocks are rail-fenced pens PEN_M, covered blocks
    (COVERED share) a long low shed; 1913-08-14 (opened) to PENS_DIED (a guess: closed Aug 1988, then demolished)
  - the Administration Building (1912, three storeys, off Marion St) and the powerhouse west of it
  - the Union Public Abattoir (1916, 250 × 60 ft, on the western edge)
  - Harris Abattoir / Canada Packers (1925, imploded 2001) and Swift Canadian (opened 11 May 1939, imploded 1994):
    utility building 130 × 258 ft (3 storeys), killing building 66 × 110 ft (5), garage 55 × 180 ft (1)
Footprints of the buildings are guesses (sizes from MHS where it gives them, positions from its coordinates).
Sources: MHS Historic Sites — Union Stockyards, Canada Packers, Swift Meat Packing Plant."""
import os, json, math, uuid
from shapely.geometry import Polygon, LineString, box, mapping
from shapely import affinity
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
FEAT = os.path.expanduser('~/gisdata/osm/feat/wpg_features.json')
LAT0, LON0 = 49.8790, -97.0850; K = math.cos(math.radians(LAT0)) * 111320; KY = 110574
m = lambda q: ((q[0] - LON0) * K, (q[1] - LAT0) * KY)
ll = lambda x, y: [round(LON0 + x / K, 7), round(LAT0 + y / KY, 7)]
BLOCK_M, ALLEY_M, PEN_M, COVERED, PENS_W = (56, 40), 8, (8, 10), 0.45, -400
OPENED, PENS_DIED = '1913-08-14', '1990-07-01'
SRC = {'yards': 'https://www.mhs.mb.ca/docs/sites/unionstockyards.shtml', 'cp': 'https://mhs.mb.ca/docs/sites/canadapackers.shtml',
       'swift': 'https://mhs.mb.ca/docs/sites/swifts.shtml'}
NS = uuid.UUID('6f1d2b8e-7a51-4c1b-9b8e-0a6b1d2c3e4f')
F = json.load(open(FEAT))
site = Polygon([m(q) for q in next(w for w in F['sy'] if w['id'] == 'way/105995544')['p']])
pond = Polygon([(-345, -140), (-262, -140), (-262, 28), (-345, 28)])   # today's retention pond (from the shot)
pens = site.intersection(box(PENS_W, -1e4, 1e4, 1e4)).difference(pond.buffer(6))
feats = []
def feat(geom, name, **p):
    uid = str(uuid.uuid5(NS, name + json.dumps([round(c, 1) for c in geom.bounds])))
    coords = [ll(*q) for q in (geom.exterior.coords if geom.geom_type == 'Polygon' else geom.coords)]
    props = {'uid': uid, 'pf_uid': uid, 'name': name, 'cohort': 'manual', 'source_file': 'tools/stockyards.py', **p}
    feats.append({'type': 'Feature', 'properties': props, 'geometry': {'type': 'Polygon' if geom.geom_type == 'Polygon' else 'LineString',
                                                                         'coordinates': [coords] if geom.geom_type == 'Polygon' else coords}})
x0, y0, x1, y1 = pens.bounds; bw, bh = BLOCK_M; nb = nc = 0
h = lambda i, j: (math.sin(i * 12.9898 + j * 78.233) * 43758.5453) % 1
j = 0; y = y0
while y + bh <= y1 + 1:
    i = 0; x = x0
    while x + bw <= x1 + 1:
        B = box(x, y, x + bw, y + bh)
        if pens.buffer(-1).contains(B):
            if h(i, j) < COVERED:
                feat(B.buffer(-1, join_style=2), 'Union Stockyards: covered pens', material='wood_industrial', floors=0.9, roof_type='gabled',
                     born=OPENED, died=PENS_DIED, construction_months=12, born_basis='opened 14 Aug 1913 (MHS)', died_basis='demolished after the yards closed in Aug 1988 (year a guess)',
                     footprint_source="laid out over the pen foundations in Mike's satellite shot (block grid a simplification)", notes=SRC['yards']); nc += 1
            else:
                px, py = PEN_M
                for k in range(int(bw // px) + 1):
                    feat(LineString([(x + k * px, y), (x + k * px, y + bh)]), 'Union Stockyards: pen fence', type='fence', material='wood_industrial',
                         fence_height=1.6, born=OPENED, died=PENS_DIED, born_basis='opened 14 Aug 1913 (MHS)', died_basis='demolished after Aug 1988 (a guess)')
                for k in range(int(bh // py) + 1):
                    feat(LineString([(x, y + k * py), (x + bw, y + k * py)]), 'Union Stockyards: pen fence', type='fence', material='wood_industrial',
                         fence_height=1.6, born=OPENED, died=PENS_DIED, born_basis='opened 14 Aug 1913 (MHS)', died_basis='demolished after Aug 1988 (a guess)')
            nb += 1
        x += bw + ALLEY_M; i += 1
    y += bh + ALLEY_M; j += 1
ARCH = -18.5   # Archibald Street's bearing (° from north): the plants along it
def bldg(cx, cy, w, d, rot, name, **p):
    feat(affinity.rotate(box(cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2), -rot, origin=(cx, cy)), name, **p)
FT = 0.3048
bldg(-330, 235, 36, 16, 0, 'Union Stockyards Administration Building', material='brick', floors=3, roof_type='flat', born='1912-11-01', construction_months=10,
     died='1995-07-01', born_basis='1912, John Woodman and R. M. Carey (MHS)', died_basis='gone by 2014 (MHS); year a guess', notes='offices, inspection, restaurant, Bank of Montreal; ' + SRC['yards'])
bldg(-380, 240, 22, 16, 0, 'Union Stockyards powerhouse', material='brick', floors=2, roof_type='flat', born='1913-06-01', died='1995-07-01',
     born_basis='with the yards (MHS: west of the Administration Building)', died_basis='a guess', notes=SRC['yards'])
bldg(-420, 120, 250 * FT, 60 * FT, 90, 'Union Public Abattoir', material='brick', floors=3, roof_type='flat', born='1916-12-14', construction_months=12,
     died='1990-07-01', born_basis='opened 14 Dec 1916 (MHS)', died_basis='a guess', notes='250 × 60 ft, on the western edge near the stables (position a guess); ' + SRC['yards'])
cpx, cpy = m((-97.09395, 49.88107))
bldg(cpx, cpy, 70, 32, ARCH, 'Harris Abattoir / Canada Packers plant', material='brick', floors=6, roof_type='flat', born='1925-08-01', construction_months=12,
     died='2001-07-01', born_basis='built 1925 (MHS)', died_basis='imploded 2001 (MHS; month a guess)', notes='size a guess; ' + SRC['cp'])
bldg(cpx + 30, cpy - 45, 60, 36, ARCH, 'Canada Packers plant (1926 addition)', material='brick', floors=3, roof_type='flat', born='1926-08-01',
     died='2001-07-01', born_basis='1926 addition (MHS)', died_basis='imploded 2001 (MHS)', notes='size and place a guess; ' + SRC['cp'])
sx, sy = m((-97.09334, 49.87918))
bldg(sx, sy, 130 * FT, 258 * FT, ARCH, 'Swift Canadian plant: utility building', material='brick', floors=3, roof_type='flat', born='1939-05-11', construction_months=18,
     died='1994-07-01', born_basis='opened 11 May 1939 (MHS)', died_basis='imploded 1994 (MHS; month a guess)', notes='130 × 258 ft; ' + SRC['swift'])
bldg(sx + 30, sy + 20, 66 * FT, 110 * FT, ARCH, 'Swift Canadian plant: killing building', material='brick', floors=5, roof_type='flat', born='1939-05-11', construction_months=18,
     died='1994-07-01', born_basis='opened 11 May 1939 (MHS)', died_basis='imploded 1994 (MHS)', notes='66 × 110 ft; place beside the utility building a guess; ' + SRC['swift'])
bldg(sx - 35, sy - 30, 55 * FT, 180 * FT, ARCH, 'Swift Canadian plant: garage', material='brick', floors=1, roof_type='flat', born='1939-05-11',
     died='1994-07-01', born_basis='opened 11 May 1939 (MHS)', died_basis='imploded 1994 (MHS)', notes='55 × 180 ft; place a guess; ' + SRC['swift'])
json.dump({'type': 'FeatureCollection', 'note': 'Union Stockyards and the packing plants beside them (tools/stockyards.py) — reconstructed, positions approximate',
           'features': feats}, open(os.path.join(DATA, 'pastforward_2026_stockyards.geojson'), 'w'), separators=(',', ':'))
print(len(feats), 'features;', nb, 'blocks,', nc, 'covered')
