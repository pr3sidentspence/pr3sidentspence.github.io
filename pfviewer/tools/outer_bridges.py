"""outer_bridges.py — the Perimeter Highway's and Abinojii Mikanah's river bridges (Mike, 2026-10-26: "need bridges for
abinoje mikana and the perimeter highway where they cross the red and/or assiniboine").

    ~/.venvs/pfgis/bin/python tools/outer_bridges.py

Each carriageway's OSM bridge way (~/gisdata/osm/feat/wpg_more.json; picked 2026-10-26 by intersecting the
Perimeter / Abinojii Mikanah bridge=yes ways with OSM's waterway=river lines for the Red and the Assiniboine) becomes a
deck rectangle: the way's end to end, lanes × 3.7 m + 3 m of shoulders wide, concrete girder, bridge_fit (the viewer
lands the ends where the DEM bank rises). Written into data/pastforward_2026_bridges.geojson (its own features
replaced on a re-run). The years are GUESSES — the Perimeter was built through the late 1950s and the 1960s, and
Bishop Grandin's Red River crossing in the 1980s; replace them with documented ones when known."""
import os, json, math, uuid
from shapely.geometry import LineString
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
C_LAT = 49.885; K = math.cos(math.radians(C_LAT)) * 111320; KY = 110574
m = lambda q: ((q[0] + 97.132) * K, (q[1] - C_LAT) * KY)
ll = lambda q: [round(q[0] / K - 97.132, 9), round(q[1] / KY + C_LAT, 9)]
# (name, OSM ways (one per carriageway), born, basis)
BRIDGES = [
    ('North Perimeter Bridge (Red River)', ['way/5029674', 'way/32688578'], '1965-06-01', 'guess: the Perimeter was built 1958–69'),
    ('South Perimeter Bridge (Red River)', ['way/13778614', 'way/33112794'], '1962-06-01', 'guess: the Perimeter was built 1958–69'),
    ('West Perimeter Bridge (Assiniboine River)', ['way/13779365', 'way/30901467'], '1962-06-01', 'guess: the Perimeter was built 1958–69'),
    ('Abinojii Mikanah Bridge (Red River; formerly Bishop Grandin)', ['way/13787652', 'way/13787654'], '1987-06-01', 'guess: Bishop Grandin Blvd crossed the Red in the 1980s'),
]
D = {w['id']: w for w in json.load(open(os.path.expanduser('~/gisdata/osm/feat/wpg_more.json')))['roads']}
path = os.path.join(DATA, 'pastforward_2026_bridges.geojson'); B = json.load(open(path))
B['features'] = [f for f in B['features'] if 'tools/outer_bridges.py' not in f['properties'].get('source_file', '')]
NS = uuid.UUID('4f1c2b7e-93d0-4a65-8e21-6b0d9c3a7f14')
for name, ways, born, basis in BRIDGES:
    for k, wid in enumerate(ways):
        w = D[wid]; L = LineString([m(q) for q in w['p']]); (ax, az), (bx, bz) = L.coords[0], L.coords[-1]
        ln = math.hypot(bx - ax, bz - az); ux, uz = (bx - ax) / ln, (bz - az) / ln; nx, nz = -uz, ux
        lanes = int(w['t'].get('lanes') or 2); h = (lanes * 3.7 + 3.0) / 2
        ring = [(ax + nx * h, az + nz * h), (bx + nx * h, bz + nz * h), (bx - nx * h, bz - nz * h), (ax - nx * h, az - nz * h)]
        side = ['northbound', 'eastbound', 'southbound', 'westbound'][round(math.degrees(math.atan2(ux, uz)) % 360 / 90) % 4]   # OSM oneway: drawn in the direction of travel
        nm = f'{name}, {side}'; uid = str(uuid.uuid5(NS, wid))
        B['features'].append({'type': 'Feature', 'properties': {
            'id': uid, 'uid': uid, 'pf_uid': uid, 'name': nm, 'type': 'bridge', 'material': 'concrete', 'bridge_style': 'girder', 'floors': 1,
            'born': born, 'born_basis': basis, 'source_file': f'tools/outer_bridges.py: OSM {wid} (bridge=yes, {lanes} lanes)', 'cohort': 'bridges', 'bridge_fit': True},
            'geometry': {'type': 'Polygon', 'coordinates': [[ll(q) for q in ring + ring[:1]]]}})
        print(f'{nm}: {ln:.0f} m × {2*h:.1f} m, {born[:4]}')
json.dump(B, open(path, 'w'), ensure_ascii=False)
