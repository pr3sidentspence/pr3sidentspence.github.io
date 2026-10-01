#!/usr/bin/env python3
"""
date_rails.py — born/died dates for the digitized rail lines (wpg_rails_1906.geojson).

The Goad sheets only show what existed in 1906, so dates come from railway
history, one entry per corridor in LINES below (edit freely, then re-run:
`python3 tools/date_rails.py` from pfviewer/ → data/rail_history.json).

  - Through lines: dated by corridor (THROUGH maps feature index → line).
  - Yard tracks (short through lines inside a yard): spread between the yard's
    date and `spread_to`, so a yard fills in instead of appearing at once.
  - Sidings: born with the first building within 70 m (a siding serves an
    industry), never before the line they branch from, never after 1905;
    sidings with no building beside them are spread like yard tracks.
  - Long lines that cross the Red River are split at vertex indices (SPLITS)
    so each piece gets its own date (e.g. the CPR line before/after its 1902
    bridge).

Feature keys in the output are the geojson `id` property (and `id/piece`
for split features). Loaded by the viewer (CONFIG.dataFiles.railHistory).
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
C_LON, C_LAT = -97.135515, 49.895396
M = 111320 * math.cos(math.radians(C_LAT))
W = lambda q: ((q[0] - C_LON) * M, -(q[1] - C_LAT) * 111320)

# name: (born, died, confidence, basis)
LINES = {
  'cpr_louise':  ('1881-07-26', None, 'high',
      'CPR yards at Point Douglas and the line over the Louise Bridge: first CPR train into Winnipeg 26 Jul 1881 (CBC / MHS)'),
  'cpr_west':    ('1881-12-01', None, 'medium',
      'CPR main line west, Winnipeg–Portage la Prairie, built direct in late 1881 (MHS, "Rails Across the Red")'),
  'cpr_yardtrk': ('1881-07-26', None, 'medium',
      'CPR Point Douglas yard tracks — yard dates from 1881, tracks added as traffic grew (spread to 1900)'),
  'cpr_bridge':  ('1902-07-01', None, 'high',
      'CPR Red River bridge at Point Douglas and its approaches: built 1901–02, first train early July 1902 (MHS)'),
  'cpr_sw':      ('1882-01-01', None, 'low',
      'Pembina Mountain / Southwestern branch (Manitoba & South Western) — grading 1881, rails 1881–82 (MHS); identification of this line is a guess'),
  'cpr_weston':  ('1903-01-01', None, 'low',
      'CPR Weston yards and approaches — Weston shops/yards 1900s; no firm date found (spread 1903–1906)'),
  'npm_forks':   ('1889-09-01', None, 'medium',
      'Northern Pacific & Manitoba line to the Forks / Water Ave station and shops, 1889 (MHS); later Canadian Northern East Yards'),
  'transfer':    ('1894-01-01', None, 'medium',
      'Winnipeg Transfer Railway: company 1889, "about five years" to complete, joining the CPR at Point Douglas Ave to the NP&M at Water Ave'),
  'cnor_east':   ('1902-01-01', None, 'low',
      'Canadian Northern line east over its Red River bridge (built 1901–02, MHS); identification is a guess'),
  'gwwd':        ('1914-01-01', None, 'low',
      'Greater Winnipeg Water District Railway from St. Boniface (c.1913–1915); identification is a guess'),
}
# feature index (position in wpg_rails_1906.geojson) → line, for every `through` feature
THROUGH = {}
def put(line, *idx): [THROUGH.__setitem__(i, line) for i in idx]
put('cpr_louise', 35,36,37,38,54,55,56,57,58,59,70,103,167,172,274,275,276)       # yards + lines toward the Louise Bridge
put('cpr_west', 249)
put('cpr_sw', 251)
put('cpr_bridge', 277,278,280)
put('npm_forks', 13,150)
put('transfer', 78)
put('cpr_weston', 180,181,182,183,184,186,187,188,189,190,191,192,194,195,200,205,207,218,219,223,234,235,247,248,252,
                  255,256,257,258,259,260,261,262,264,265)
# unclassified long lines (class None)
OTHER = {282:'cnor_east', 283:'gwwd'}
# split long features at vertex indices → pieces (first piece = from vertex 0)
#   246 = "CPR Mainline" (10 km): vertices 0–3 east of the Red (the 1902 bridge is between 2 and 3),
#   3–14 through the yards, 14–19 main line west
SPLITS = {246: [(0, 3, 'cpr_bridge'), (3, 14, 'cpr_louise'), (14, 19, 'cpr_west')]}
# short through lines in these yards are yard tracks (spread), the rest are main tracks (at the line date)
YARD_TRACK_MAX_M = 1000
SPREAD_TO = {'cpr_louise': '1900-01-01', 'cpr_weston': '1906-01-01', 'npm_forks': '1904-01-01',
             'cpr_bridge': '1906-01-01', 'cpr_west': '1896-01-01', 'cpr_sw': '1892-01-01', 'transfer': '1900-01-01',
             'cnor_east': '1906-01-01', 'gwwd': '1915-01-01'}
SIDING_CAP = '1905-12-31'
NEAR_BLDG_M = 70

def yf(s):
    if not s: return None
    y, m, d = (int(s[0:4]), int(s[5:7] or 1), int(s[8:10] or 1))
    return y + (m - 1) / 12 + (d - 1) / 365
def iso_from_yf(v):
    y = int(v); doy = int((v - y) * 365)
    import datetime
    return (datetime.date(y, 1, 1) + datetime.timedelta(days=min(doy, 364))).isoformat()
def h01(n): return ((int(n) * 2654435761) % 1000) / 1000.0

def load_buildings():
    pts = []
    for fn in ('pastforward_2026_assessment.geojson', 'pastforward_2026_osm.geojson'):
        for f in json.load(open(os.path.join(DATA, fn)))['features']:
            b = (f['properties'].get('born') or '')[:10]
            if len(b) < 4 or b < '1850': continue
            c = f['geometry']['coordinates']
            try:
                while isinstance(c[0][0], list): c = c[0]
                x = sum(q[0] for q in c) / len(c); y = sum(q[1] for q in c) / len(c)
            except Exception: continue
            wx, wz = W((x, y)); pts.append((wx, wz, yf(b if len(b) == 10 else b[:4] + '-07-01')))
    grid = {}
    for p in pts: grid.setdefault((int(p[0] // 100), int(p[1] // 100)), []).append(p)
    return grid
def earliest_near(grid, P, radius):
    best = None
    for (x, z) in P[::2] + [P[-1]]:
        gx, gz = int(x // 100), int(z // 100)
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                for (bx, bz, by) in grid.get((gx + i, gz + j), []):
                    if (bx - x) ** 2 + (bz - z) ** 2 < radius * radius and (best is None or by < best): best = by
    return best

def main():
    R = json.load(open(os.path.join(DATA, 'wpg_rails_1906.geojson')))['features']
    P = [[W(q) for q in f['geometry']['coordinates']] for f in R]
    grid = load_buildings()
    # nearest through feature for each non-through feature
    thr = [i for i in THROUGH]
    def line_of(i):
        if i in THROUGH: return THROUGH[i]
        if i in OTHER: return OTHER[i]
        best = (1e18, None)
        for t in thr:
            d = min(math.hypot(a[0] - b[0], a[1] - b[1]) for a in P[i][::2] for b in P[t][::3])
            if d < best[0]: best = (d, THROUGH[t])
        return best[1]
    out, stats = {}, {}
    def put_feat(key, line, born, basis, conf, kind):
        out[key] = {'line': line, 'born': born, 'died': LINES[line][1], 'kind': kind, 'basis': basis, 'confidence': conf}
        stats.setdefault((line, conf), []).append(born)
    for i, f in enumerate(R):
        p = f['properties']; fid = p['id']
        length = p.get('length_m') or sum(math.dist(a, b) for a, b in zip(P[i], P[i][1:]))
        if i in SPLITS:
            for k, (a, b, line) in enumerate(SPLITS[i]):
                born, _, conf, basis = LINES[line]
                put_feat(f'{fid}/{k}', line, born, basis, conf, 'through'); out[f'{fid}/{k}']['from'] = a; out[f'{fid}/{k}']['to'] = b
            continue
        line = line_of(i); born0, died, conf, basis = LINES[line]
        b0 = yf(born0)
        if i in THROUGH or i in OTHER:
            if i in THROUGH and length < YARD_TRACK_MAX_M and line in SPREAD_TO and i not in (70, 167):
                b1 = yf(SPREAD_TO[line]); born = iso_from_yf(b0 + h01(fid) * (b1 - b0)); kind = 'yard track'
            else: born, kind = born0, 'through'
            put_feat(str(fid), line, born, basis, conf, kind)
        else:   # siding / unclassified short
            nb = earliest_near(grid, P[i], NEAR_BLDG_M)
            cap = yf(SIDING_CAP)
            if nb is not None and nb > b0 + 0.25: v = min(nb, cap); how = 'with the first building within %d m' % NEAR_BLDG_M   # a building built after the line
            else:   # no building, or only ones that predate the line (e.g. 1880 placeholders): spread
                end = yf(SPREAD_TO.get(line, SIDING_CAP)); end = max(end, b0 + 0.5); v = b0 + h01(fid) * (min(end, cap) - b0); how = 'spread (no later building beside it)'
            put_feat(str(fid), line, iso_from_yf(max(v, b0)), f'siding on the {line} yard, {how}', conf, 'siding')
    hist = {'_format': 'tools/date_rails.py output. features: { "<geojson id>" | "<id>/<piece>": {line, born, died, kind, basis, confidence, [from,to]} }. '
                       'Split features are cut at vertex indices from..to. Edit tools/date_rails.py (LINES / THROUGH / SPLITS) and re-run, or edit this file directly.',
            'lines': {k: {'born': v[0], 'died': v[1], 'confidence': v[2], 'basis': v[3]} for k, v in LINES.items()},
            'features': out}
    json.dump(hist, open(os.path.join(DATA, 'rail_history.json'), 'w'), ensure_ascii=False, indent=1)
    print('wrote rail_history.json:', len(out), 'entries')
    for (line, conf), v in sorted(stats.items()):
        v.sort(); print(f'  {line:12} {conf:6} n={len(v):3}  {v[0]} … {v[-1]}')
    yrs = {}
    for e in out.values(): yrs[e['born'][:4]] = yrs.get(e['born'][:4], 0) + 1
    print('by year:', ' '.join(f'{y}:{n}' for y, n in sorted(yrs.items())))

if __name__ == '__main__':
    main()
