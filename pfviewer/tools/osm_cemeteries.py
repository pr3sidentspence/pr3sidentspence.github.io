"""osm_cemeteries.py — Winnipeg's other cemeteries from OpenStreetMap, as data/cemeteries_other.json.

    ~/.venvs/pfgis/bin/python tools/osm_cemeteries.py

Mike, 2026-10-23: add the other cemeteries. Each OSM landuse=cemetery / amenity=grave_yard (~/gisdata/osm/feat/
wpg_features.json) with a year in YEARS: its outline (lawn + headstone grid in the viewer, _buildOtherCemeteries), its
paths (OSM footways / service roads inside it, ~/gisdata/osm/feat/wpg_paths.json) buffered and left clear, the founding
year, and flushShare — memorial gardens / lawn cemeteries (founded from 1950) have mostly flush markers. Elmwood is
drawn by its own data (cemeteries.json + elmwood_rows.json) and skipped here."""
import os, json, math
from shapely.geometry import Polygon, LineString, mapping
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
FEAT = os.path.expanduser('~/gisdata/osm/feat/wpg_features.json'); PATHS = os.path.expanduser('~/gisdata/osm/feat/wpg_paths.json')
YEARS = {   # OSM id: (name, founded, source)
    'way/25275464': ('Brookside Cemetery', 1878, 'MHS (plaque: the municipal cemetery created 1878); CBC: laid out 1877–1883'),
    'way/111050601': ("St. Mary's Cemetery", 1884, 'MHS: established 12 Sep 1884 (506 Osborne St)'),
    'way/243819448': ('Transcona Cemetery', 1914, 'City of Winnipeg: opened 1914'),
    'way/100317224': ('St. Vital Cemetery', 1937, 'City of Winnipeg: opened 1937'),
    'way/39120572': ('Garry Memorial Park (Thomson in the Park)', 1953, 'Find a Grave: founded 1953'),
    'way/166393484': ('Glen Lawn Memorial Gardens', 1961, 'Find a Grave: established 1961'),
    'way/120367875': ('St. Boniface Cathedral Cemetery', 1818, 'guess: with the 1818 mission (Riel buried here 1885)'),
    'relation/19350277': ("St. John's Cathedral Cemetery", 1822, "guess: St John's churchyard from the 1820s (identification of this OSM area a guess)"),
    'way/71547043': ('Kildonan Presbyterian Cemetery', 1852, 'guess: with the Kildonan congregation (church 1854)'),
    'way/906691195': ("St. James Anglican Cemetery", 1853, 'guess: St James church 1853 (identification of this OSM area a guess)'),
    'way/71584624': ('Shaarey Zedek Cemetery', 1890, 'guess'),
    'way/47792302': ('Hebrew Sick Benefit Cemetery', 1905, 'guess'),
    'way/71905970': ('Rosh Pina Memorial Park Cemetery', 1925, 'guess'),
    'way/244177479': ('St. Boniface Cemetery', 1890, 'guess'),
    'way/277889267': ('Fort Garry Roman Catholic Cemetery', 1900, 'guess'),
    'way/99127059': ('St. Charles Roman Catholic Cemetery', 1880, 'guess'),
    'way/351786222': ("St Mary's Cemetery (Kildonan)", 1900, 'guess'),
    'way/182303524': ('Chapel Lawn Memorial Gardens', 1935, 'guess'),
    'way/243814281': ('Green Acres Memorial Gardens', 1958, 'guess'),
    'way/278851760': ('Waverley Memorial Gardens', 1970, 'guess'),
    'way/906707404': ('Sage Creek Cemetery', 2012, 'guess'),
    'way/98178024': ('All Saints Cemetery', 1900, 'guess'),
}
C_LAT = 49.9; K = math.cos(math.radians(C_LAT)) * 111320; KY = 110574
m = lambda p: ((p[0] + 97.13) * K, (p[1] - C_LAT) * KY)
ll = lambda q: [round(q[0] / K - 97.13, 7), round(q[1] / KY + C_LAT, 7)]
F = json.load(open(FEAT)); P = json.load(open(PATHS))['paths']
paths = [(LineString([m(q) for q in w['p']]), w['t'].get('highway')) for w in P if len(w['p']) > 1]
out = []
for a in F['areas']:
    if a['id'] not in YEARS: continue
    name, y, src = YEARS[a['id']]
    G = unary_union([Polygon([m(q) for q in p[0]], [[m(q) for q in h] for h in p[1:]]).buffer(0) for p in a['polys']])
    clear = [L.intersection(G).buffer(2.5 if hw in ('service', 'track') else 1.3) for L, hw in paths if L.intersects(G)]
    clear = unary_union(clear) if clear else None
    pp = []
    if clear and not clear.is_empty:
        for q in getattr(clear, 'geoms', [clear]):
            if q.geom_type == 'Polygon': pp.append([[ll(c) for c in q.exterior.coords]] + [[ll(c) for c in h.coords] for h in q.interiors])
    out.append({'name': name, 'osm': a['id'], 'founded': y, 'full': min(2026, y + 100), 'source': src, 'areaM2': round(G.area),
                'flushShare': 0.85 if y >= 1950 else 0.25, 'polys': a['polys'], 'paths': pp})
    print(name, y, round(G.area / 1e4, 1), 'ha;', len(pp), 'path pieces')
json.dump({'source': 'tools/osm_cemeteries.py from OpenStreetMap (© OpenStreetMap contributors, ODbL); founding years per cemetery (source / guess)',
           'cemeteries': out}, open(os.path.join(DATA, 'cemeteries_other.json'), 'w'), separators=(',', ':'))
print(len(out), 'cemeteries')
