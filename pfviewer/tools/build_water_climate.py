"""
build_water_climate.py — real river levels and summer moisture for pfviewer.

Writes (under ../data):
  water_levels.json   Red River level at Winnipeg, m above sea level, by date
                      ({"datum": "asl", "records": [["1912-08-21", 224.51], ...]}),
                      read by index.html → loadWaterLevels(). Also carries the
                      seasonal climatology the viewer falls back on for years
                      without data ("normal", "seasonal").
  moisture.json       summer wetness index per year, weekly from April 1
                      ({"start": "04-01", "stepDays": 7, "years": {"1872": [...]}}),
                      -1 = severe drought (brown) … 0 = normal … +1 = very wet (green).

Sources (Environment Canada open data, api.weather.gc.ca — downloaded once
into tools/cache/, delete the cache to refresh):
  Hydrometric daily means (HYDAT), geodetic datum:
    05OJ001 Red River at Winnipeg                1912-08 → 1977 (winters patchy)
    05OJ015 Red River at James Avenue            1971-03 → present
  Climate daily precipitation, Winnipeg, chained:
    5023243 Winnipeg St John's College           1872-03 → 1938-07
    5023222 Winnipeg Richardson Int'l A          1938-08 → 2008-07
    502S001 Winnipeg A CS                        2008-07 → present
    gaps filled from 5023262 Winnipeg The Forks (1999–) and 5023226 Winnipeg
    Richardson AWOS (2008–2013); days still missing count as that date's
    average (not as dry days)
Before 1912 only the great floods have known Winnipeg levels (City of Winnipeg
historical flood table, Fleming 1879 surveys, 1-ft precision): 1826 37 ft,
1852 35 ft, 1861 33 ft James. 1826 timing from the HBC record (ice jam broke
May 3, rising from May 5, falling from May 23); 1852/1861 crest dates are
approximate (mid/late May).

Moisture: season-to-date precipitation (from April 1) as a ratio of the
1872–present median for the same date, log2-scaled (half the normal → -1,
double → +1), plus a boost in years whose spring flood crest ran well above
normal. Years without rain data (before 1872) use the flood boost alone.

Usage:  python3 tools/build_water_climate.py      (from pfviewer/)
"""
import json, math, os, statistics, urllib.request
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
CACHE = os.path.join(HERE, 'cache')
API = 'https://api.weather.gc.ca/collections'

JAMES_DATUM_M = 727.57 * 0.3048          # James Avenue gauge zero, m ASL
HISTORIC_FLOODS = {                        # year: (crest ft James, rise start, crest, back to normal) as MM-DD
    1826: (37, '05-03', '05-21', '06-25'),
    1852: (35, '04-28', '05-20', '06-25'),
    1861: (33, '04-28', '05-18', '06-20'),
}
SIMPLIFY_M = 0.04                          # drop daily points within this of the straight line between kept ones
MAX_SPAN_DAYS = 60                         # …but keep a point at least this often (viewer maxGapDays is 75)
MAX_FILL_DAYS = 200                        # bridge winter gaps (ice) up to this long


def fetch(url, cache_name):
    path = os.path.join(CACHE, cache_name)
    if os.path.exists(path):
        return json.load(open(path))
    os.makedirs(CACHE, exist_ok=True)
    rows, off = [], 0
    while True:
        d = json.load(urllib.request.urlopen(f'{url}&limit=10000&offset={off}', timeout=180))
        rows += [f['properties'] for f in d['features']]
        if len(d['features']) < 10000:
            break
        off += 10000
    json.dump(rows, open(path, 'w'))
    return rows


def hydro(stn):
    rows = fetch(f'{API}/hydrometric-daily-mean/items?STATION_NUMBER={stn}&sortby=DATE&f=json'
                 f'&properties=DATE,LEVEL', f'{stn}.json')
    return {date.fromisoformat(r['DATE']): r['LEVEL'] for r in rows if r.get('LEVEL') is not None}


def climate(cid):
    rows = fetch(f'{API}/climate-daily/items?CLIMATE_IDENTIFIER={cid}&sortby=LOCAL_DATE&f=json'
                 f'&properties=LOCAL_DATE,TOTAL_PRECIPITATION', f'clim_{cid}.json')
    out = {}
    for r in rows:
        if r.get('TOTAL_PRECIPITATION') is not None:
            out.setdefault(date.fromisoformat(r['LOCAL_DATE'][:10]), r['TOTAL_PRECIPITATION'])
    return out


def doy(d):
    return date(2001, d.month, min(d.day, 28) if d.month == 2 else d.day).timetuple().tm_yday - 1   # 365-day year, like the viewer (Feb 29 → 28)


# ── River levels ─────────────────────────────────────────────────────────
old, new = hydro('05OJ001'), hydro('05OJ015')
overlap = [d for d in new if d in old]
offset = statistics.median(new[d] - old[d] for d in overlap) if overlap else 0.0
print(f'05OJ001 {len(old)} days, 05OJ015 {len(new)} days, overlap {len(overlap)} days, '
      f'datum offset {offset:+.3f} m (applied to 05OJ001)')
level = {d: v + offset for d, v in old.items()}
level.update(new)                                   # James Avenue wins where both exist

# Continuous daily series: bridge gaps (winters under ice at the old gauge) linearly
days = sorted(level)
series = []
for a, b in zip(days, days[1:] + [None]):
    series.append((a, level[a]))
    if b and 1 < (b - a).days <= MAX_FILL_DAYS:
        for k in range(1, (b - a).days):
            t = k / (b - a).days
            series.append((a + timedelta(k), level[a] + (level[b] - level[a]) * t))

# Climatology (median by day of year) → the viewer's fallback curve and "normal"
by_doy = [[] for _ in range(365)]
for d, v in series:
    by_doy[doy(d)].append(v)
clim = [statistics.median(x) for x in by_doy]
open_water = [clim[i] for i in range(doy(date(2001, 5, 15)), doy(date(2001, 10, 15)))]
normal = statistics.median(open_water)
weekly = [(f'{(date(2001, 1, 1) + timedelta(i)).strftime("%m-%d")}', round(clim[i] - normal, 2))
          for i in range(0, 365, 7)]
print(f'normal open-water level {normal:.2f} m ASL ({(normal - JAMES_DATUM_M) / 0.3048:.1f} ft James)')

# Annual crests (for the flood boost)
peaks = {}
for d, v in series:
    if 3 <= d.month <= 6:
        peaks[d.year] = max(peaks.get(d.year, -1e9), v)
median_peak = statistics.median(peaks.values())

# Pre-gauge great floods as simple hydrographs around the crest
records = []
for yr, (ft, rise, crest, end) in sorted(HISTORIC_FLOODS.items()):
    top = JAMES_DATUM_M + ft * 0.3048
    peaks[yr] = top
    for md, v in ((rise, clim[doy(date.fromisoformat(f'2001-{rise}'))]), (crest, top),
                  (end, clim[doy(date.fromisoformat(f'2001-{end}'))])):
        records.append([f'{yr}-{md}', round(v, 2)])

# Simplify the daily series (keeps every turning point within SIMPLIFY_M)
def simplify(pts, tol):
    keep = [0]
    i = 0
    while i < len(pts) - 1:
        j = i + 2
        while j < len(pts) and (pts[j][0] - pts[i][0]).days <= MAX_SPAN_DAYS:
            (t0, v0), (t1, v1) = (pts[i][0].toordinal(), pts[i][1]), (pts[j][0].toordinal(), pts[j][1])
            if any(abs(pts[k][1] - (v0 + (v1 - v0) * (pts[k][0].toordinal() - t0) / (t1 - t0))) > tol
                   for k in range(i + 1, j)):
                break
            j += 1
        i = j - 1
        keep.append(i)
    return [pts[k] for k in keep]

kept = simplify(series, SIMPLIFY_M)
records += [[d.isoformat(), round(v, 2)] for d, v in kept]
json.dump({'datum': 'asl',
           'source': 'Environment Canada HYDAT 05OJ001 (1912–1977, datum-matched) + 05OJ015 (1971–); '
                     'pre-1912 great floods from the City of Winnipeg historical flood table (1 ft precision)',
           'normal': round(normal, 2), 'seasonal': weekly, 'records': records},
          open(os.path.join(DATA, 'water_levels.json'), 'w'), separators=(',', ':'))
print(f'water_levels.json: {len(records)} records (from {len(series)} days)')

# ── Summer moisture ──────────────────────────────────────────────────────
precip = {}
for cid in ('5023226', '5023262', '502S001', '5023222', '5023243'):   # later in the list wins; fillers first
    precip.update(climate(cid))
avg_day = [0.0] * 365
cnt_day = [0] * 365
for d, v in precip.items():
    avg_day[doy(d)] += v
    cnt_day[doy(d)] += 1
avg_day = [a / max(1, c) for a, c in zip(avg_day, cnt_day)]
years = sorted({d.year for d in precip})
START = (4, 1)
STEPS = 31                                            # weekly Apr 1 → end of Oct
cum = {}
for y in years:
    t, row, missing = 0.0, [], 0
    for k in range(STEPS * 7):
        d = date(y, *START) + timedelta(k)
        v = precip.get(d)
        if v is None:
            missing += 1
            v = avg_day[doy(d)]
        t += v
        if k % 7 == 6:
            row.append(t)
    if missing < 45 and len(row) == STEPS:
        cum[y] = row
norm = [statistics.median(cum[y][i] for y in cum) for i in range(STEPS)]

def flood_boost(y):
    p = peaks.get(y)
    return 0.0 if p is None else max(0.0, min(1.0, (p - median_peak - 1.0) / 4.0)) * 0.5

out = {}
for y in sorted(set(cum) | set(peaks)):
    fb = flood_boost(y)
    if y in cum:
        row = []
        for i in range(STEPS):
            r = (cum[y][i] + 5) / (norm[i] + 5)          # +5 mm damps the noisy first weeks
            row.append(round(max(-1.0, min(1.0, math.log2(r) + fb)), 2))
    elif fb > 0:
        row = [round(fb, 2)] * STEPS
    else:
        continue
    out[str(y)] = row
json.dump({'start': '04-01', 'stepDays': 7,
           'source': 'Winnipeg daily precipitation (St John\'s College 1872–1938, Richardson Int\'l A 1938–2008, '
                     'Winnipeg A CS 2008–), season-to-date vs median; + spring flood boost',
           'years': out}, open(os.path.join(DATA, 'moisture.json'), 'w'), separators=(',', ':'))
print(f'moisture.json: {len(out)} years ({min(out)}–{max(out)})')
for y in (1826, 1882, 1893, 1897, 1904, 1916, 1929, 1931, 1934, 1936, 1937, 1950, 1961, 1988, 1997, 2011, 2021):
    if str(y) in out:
        r = out[str(y)]
        print(f'  {y}: Jun {r[9]:+.2f}  Jul {r[13]:+.2f}  Aug {r[18]:+.2f}  crest {peaks.get(y, float("nan")):.2f}')
