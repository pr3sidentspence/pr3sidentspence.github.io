"""osm_golf.py — Winnipeg's golf courses from OpenStreetMap, with opening years, as data/golf_courses.json.

    ~/.venvs/pfgis/bin/python tools/osm_golf.py

Mike, 2026-10-23: add golf courses. Each OSM leisure=golf_course (in ~/gisdata/osm/feat/wpg_features.json) becomes
its rough (the whole outline) with its golf=fairway / green / tee / bunker / water_hazard / driving_range areas drawn
over it, from the course's year in YEARS (sourced, or marked guess). The viewer draws them as ground patches
(index.html _YARD_COL / _YARD_LIFT). A course with no year here is left out."""
import os, json
from shapely.geometry import Polygon
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
FEAT = os.path.expanduser('~/gisdata/osm/feat/wpg_features.json')
YEARS = {   # name: (opened, source)
    'St Charles Country Club': (1905, 'Golf Manitoba (1905); Wikipedia says founded 1904'),
    'Assiniboine Golf Club': (1917, 'Golf Manitoba'),
    'Canoe Club Golf Course': (1918, 'City of Winnipeg, "Come take a swing at Canoe Club Golf Course"'),
    'Kildonan Park Golf Course': (1921, 'opened 9 June 1921 (CBC, 2021)'),
    'Niakwa Country Club': (1923, 'first opened for play 1923 (Golf Manitoba; top100golfcourses)'),
    'Windsor Park Golf Course': (1922, 'MHS / City: opened 1922 as nine holes, bought by the city 1925 and made 18'),
    'Transcona Golf Club': (1931, 'Travel Manitoba; GolfPass'),
    'St. Boniface Golf Club': (1931, 'MHS; Wikipedia (nine holes 1931, back nine 1941)'),
    'Tuxedo Golf Club': (1935, 'GolfPass ("built in 1935")'),
    'Glendale Golf and Country Club': (1946, 'GolfLink only (year opened 1946)'),
    'Wildewood Club Golf Course': (1950, 'GolfPass ("built in 1950")'),
    'Rossmere Golf & Country Club': (1959, 'MHS: the present 18 holes opened 1959 (work began 1958)'),
    'CFB Winnipeg Golf Course': (1960, 'guess'),
    'John Blumberg Golf Course': (1969, 'guess (city course, late 1960s)'),
    'Crescent Drive Golf Course': (1950, 'guess'),
    'Harbour View Golf Course': (1979, 'guess'),
    'Shooters Golf': (1995, 'guess'),
    'Southside': (1997, 'guess'),
    'The Players Course': (1999, 'guess'),
    'The Shamrock': (2000, 'guess'),
    'The Meadows at East St. Paul Golf Course': (2004, 'guess'),
    'Southwood Golf & Country Club': (2011, "Wikipedia: the club's new course opened 2011 (the old one, 1923–2010, was beside the University of Manitoba — not drawn)"),
}
KIND = {'fairway': 'fairway', 'green': 'green', 'tee': 'tee', 'bunker': 'bunker', 'water_hazard': 'golf_water',
        'lateral_water_hazard': 'golf_water', 'driving_range': 'fairway', 'putting': 'green'}
F = json.load(open(FEAT))
courses = [a for a in F['areas'] if a['t'].get('leisure') == 'golf_course']
parts = [a for a in F['areas'] if a['t'].get('golf') in KIND]
out = []
for c in courses:
    name = c['t'].get('name')
    if name not in YEARS: print('no year:', name, c['id']); continue
    y, src = YEARS[name]
    outl = [Polygon(p[0], p[1:]).buffer(0) for p in c['polys']]
    mine = {}
    for a in parts:
        if any(o.contains(Polygon(a['polys'][0][0]).representative_point()) for o in outl):
            mine.setdefault(KIND[a['t']['golf']], []).extend(a['polys'])
    P = [{'kind': 'golf_rough', 'polys': c['polys']}] + [{'kind': k, 'polys': v} for k, v in sorted(mine.items(), key=lambda kv: ['fairway', 'tee', 'green', 'bunker', 'golf_water'].index(kv[0]))]
    out.append({'name': name, 'osm': c['id'], 'born': f'{y}-05-01', 'died': None, 'source': src, 'parts': P})
    print(name, y, {k: len(v) for k, v in mine.items()})
json.dump({'source': 'tools/osm_golf.py from OpenStreetMap (© OpenStreetMap contributors, ODbL); years per course (source / guess)',
           'courses': out}, open(os.path.join(DATA, 'golf_courses.json'), 'w'), separators=(',', ':'))
print(len(out), 'courses')
