"""apply_died_bounds.py — write the automatic died dates from tools/died_upper_bounds.py into the building files.

    python tools/apply_died_bounds.py [REVIEW_JSON]     (default data/review_died_bounds.json)

Every item with auto = true (category `replaced`: a newer, dated footprint covers >= 40% of the old one) gets the
same treatment as matching/merge_assessment.py rule 4: died during the year before the newer building's roll year,
died_basis replaced_by_later_building, replaced_by = its address. Only buildings with no died date are touched, so
running it twice changes nothing. Rebuilding pastforward_2026_assessment.geojson (merge_assessment.py) or
pastforward_2026_stb1880.geojson (stb1880_ingest.py) drops these again: re-run died_upper_bounds.py, then this.

First applied 2026-10-21 on top of commit ff2a002 (the state before it)."""
import sys, os, json
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
sys.path.insert(0, os.path.join(HERE, '..', 'matching'))
from merge_assessment import iso_in_years
from geojson_io import dump_geojson_lines

items = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(DATA, 'review_died_bounds.json')))['items']
todo = {}
for it in items:
    if it.get('auto'): todo.setdefault(it['file'], {})[it['pf_uid']] = it
stats = Counter()
for fn, by_uid in todo.items():
    path = os.path.join(DATA, fn); text = open(path).read()
    fc = json.loads(text)
    for f in fc['features']:
        p = f['properties']; it = by_uid.get(p.get('pf_uid'))
        if not it: continue
        if p.get('died'): stats['already_dead'] += 1; continue
        y = it['bound_year'] - 1
        p.update(died=iso_in_years(p['pf_uid'], 'replaced', y, y), died_low=str(y), died_high=str(y + 1),
                 died_basis='replaced_by_later_building', replaced_by=it.get('by_address') or it.get('by_osm_id'))
        stats[fn] += 1
    with open(path, 'w') as fh:   # keep each file's own layout
        if text.lstrip().startswith('{"type":"FeatureCollection"') and '"features":[\n' in text[:2000]: dump_geojson_lines(fc, fh)
        else: json.dump(fc, fh)
print(dict(stats))
