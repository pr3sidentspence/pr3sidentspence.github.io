"""
extend_storms.py — adds storms after the curated list's last year to data/storms.json from the cached ECCC daily
climate records (tools/cache/, written by build_water_climate.py; nothing is downloaded).

The cache keeps only precipitation, rain and mean temperature (no snowfall or gusts), so:
  thunderstorm  May–Sep day with >= RAIN_MM of rain                     intensity .7 at RAIN_MM … .95 at 2x
  blizzard      Oct–Apr run of <= 3 days below freezing (mean temp <= 0 °C) holding >= SNOW_MM of precipitation,
                read as snow at 1 mm water ≈ 1 cm                       intensity .6 at SNOW_MM … 1.0 at 50 cm
Ground blizzards and wind-blown snowfalls the gauges under-catch are in DOCUMENTED below. Everything in the file from
FROM_YEAR on is rewritten each run; the curated entries before it are kept.

Usage:  python3 tools/extend_storms.py      (from pfviewer/)
"""
import json, os, statistics
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE, OUT = os.path.join(HERE, 'cache'), os.path.join(HERE, '..', 'data', 'storms.json')
FROM_YEAR, RAIN_MM, SNOW_MM = 1966, 55, 25
STATIONS = ['5023222', '502S001', '5023262', '5023226']   # Winnipeg airport, airport CS, The Forks, airport AWOS

# each day: the median over the stations that reported it (one faulty gauge — 502S001 logged 92 mm in March 2011
# while the others had none — can't make a storm on its own); temperature from whichever station has one
# storms the gauges miss or understate (automatic gauges under-catch wind-blown snow): these replace any automatic
# entry they overlap
DOCUMENTED = [
    {'type': 'blizzard', 'start': '1966-03-03', 'end': '1966-03-05', 'peak': '1966-03-04', 'intensity': 1.0, 'source': 'documented',
     'note': '35.6 cm, winds 113 km/h, drifts to the eaves; the city shut for two days (CHVN / ECCC)'},
    {'type': 'blizzard', 'start': '1997-04-04', 'end': '1997-04-06', 'peak': '1997-04-05', 'intensity': 1.0, 'source': 'documented',
     'note': '48 cm in about a day, 24-hour whiteout; the melt fed the Flood of the Century (CBC)'},
    {'type': 'blizzard', 'start': '2022-04-12', 'end': '2022-04-15', 'peak': '2022-04-13', 'intensity': 0.9, 'source': 'documented',
     'note': 'spring blizzard, north winds gusting 70–90 km/h; forecast 24–45 cm for Winnipeg (gauges caught ~13 mm; measured total not found) (CBC, Manitoba EMO)'},
]

day = {}
for stn in STATIONS:
    for r in json.load(open(os.path.join(CACHE, f'clim_{stn}.json'))):
        d = r['LOCAL_DATE'][:10]
        if d < f'{FROM_YEAR}-01-01': continue
        e = day.setdefault(d, {'p': [], 'r': [], 't': []})
        for k, key in (('p', 'TOTAL_PRECIPITATION'), ('r', 'TOTAL_RAIN'), ('t', 'MEAN_TEMPERATURE')):
            if r.get(key) is not None: e[k].append(r[key])
def val(d, k):
    e = day.get(d.isoformat())
    if not e: return None
    v = e[{'TOTAL_PRECIPITATION': 'p', 'TOTAL_RAIN': 'r', 'MEAN_TEMPERATURE': 't'}[k]]
    if k == 'TOTAL_RAIN' and not v: v = e['p']
    return statistics.median(v) if v else None

out = []
d, end = date(FROM_YEAR, 1, 1), max(date.fromisoformat(k) for k, e in day.items() if e['p'])
while d <= end:
    rain, t = val(d, 'TOTAL_RAIN') or 0, val(d, 'MEAN_TEMPERATURE')
    if 5 <= d.month <= 9 and rain >= RAIN_MM:
        out.append({'type': 'thunderstorm', 'start': d.isoformat(), 'end': d.isoformat(), 'peak': d.isoformat(),
                    'intensity': round(min(.95, .7 + .25*(rain - RAIN_MM)/RAIN_MM), 2), 'source': 'record-auto',
                    'note': f'{rain:.0f} mm' + (f', {t:.0f} °C mean' if t is not None else '')})
        d += timedelta(days=1); continue
    if (d.month >= 10 or d.month <= 4) and t is not None and t <= 0:
        run, tot, k = [], 0, d
        while len(run) < 3:
            tk, p = val(k, 'MEAN_TEMPERATURE'), val(k, 'TOTAL_PRECIPITATION') or 0
            if tk is None or tk > 0 or (run and p < 1): break
            run.append((k, p, tk)); tot += p; k += timedelta(days=1)
        if tot >= SNOW_MM:
            pk = max(run, key=lambda q: q[1])
            out.append({'type': 'blizzard', 'start': run[0][0].isoformat(), 'end': run[-1][0].isoformat(), 'peak': pk[0].isoformat(),
                        'intensity': round(min(1.0, .6 + .4*(tot - SNOW_MM)/(50 - SNOW_MM)), 2), 'source': 'record-auto',
                        'note': f'~{tot:.0f} cm snow ({tot:.0f} mm precipitation)' + (f' over {len(run)} days' if len(run) > 1 else '') + f', {min(q[2] for q in run):.0f} °C'})
            d = k; continue
    d += timedelta(days=1)

overlap = lambda a, b: a['start'] <= b['end'] and b['start'] <= a['end']
out = sorted([s for s in out if not any(overlap(s, D) for D in DOCUMENTED)] + DOCUMENTED, key=lambda s: s['start'])
J = json.load(open(OUT))
keep = [s for s in J['storms'] if s['start'] < f'{FROM_YEAR}']
J['storms'] = sorted(keep + out, key=lambda s: s['start'])
if 'record-auto' not in J['source']:
    J['source'] += f' From {FROM_YEAR}: tools/extend_storms.py ("record-auto": rain >= {RAIN_MM} mm in a day; >= {SNOW_MM} mm precipitation below freezing within 3 days, read as cm of snow).'
json.dump(J, open(OUT, 'w'), indent=1, ensure_ascii=False)
print(len(out), 'storms', FROM_YEAR, '→', end)
for s in out: print(' ', s['type'][:7], s['start'], s['intensity'], s['note'])
