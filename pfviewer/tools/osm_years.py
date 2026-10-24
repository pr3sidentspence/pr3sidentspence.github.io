"""osm_years.py — built years for OSM footprints that don't come from the assessment roll (shared by
build_building_tiles.py and died_upper_bounds.py).

known_year(oid, props) -> (year, basis) or (None, None), in order:
  building_years.json   hand-kept, keyed by OSM id                         basis 'manual'
  wikidata_years.json   the footprint's wikidata tag (opening / inception)  basis 'wikidata'
  OSM start_date, construction_date, building:start_date (first 4-digit year; '1976..1977' → 1976)  basis 'osm_start_date'"""
import os, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
MANUAL = {k: v if isinstance(v, int) else v['year'] for k, v in json.load(open(os.path.join(HERE, 'building_years.json')))['years'].items()}
WIKIDATA = {k: v['year'] for k, v in json.load(open(os.path.join(HERE, 'wikidata_years.json')))['years'].items()}

def year_of(s):
    m = re.match(r'\s*~?(\d{4})', s or ''); return int(m.group(1)) if m else None

def known_year(oid, props):
    if oid in MANUAL: return MANUAL[oid], 'manual'
    if props.get('wikidata') in WIKIDATA: return WIKIDATA[props['wikidata']], 'wikidata'
    for k in ('start_date', 'construction_date', 'building:start_date'):
        y = year_of(props.get(k))
        if y: return y, 'osm_start_date'
    return None, None
