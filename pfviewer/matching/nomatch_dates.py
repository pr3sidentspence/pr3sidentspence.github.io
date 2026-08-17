"""
nomatch_dates.py — Part 7 of the McPhillips 1880 <-> Goad's 1906 building-
match pipeline: tighten died-date estimates for 1880 buildings that have no
1906 counterpart.

Usage:
    python nomatch_dates.py [--matches PATH] [--in1880 PATH] [--out PATH]

Reads data/mcphillips_goad_1906.matches.json (produced by match_buildings.py)
and data/mcphillips_1880.geojson, and writes a full copy of the 1880
FeatureCollection to data/mcphillips_1880.died_corrected.geojson — the
source file is never modified in place.

For every 1880 feature in a 'no_match' group: absence from the 1906 survey
is direct negative evidence the building was gone by 1906, which is tighter
than whatever generic estimate (or no estimate at all) the feature currently
carries. We only touch features whose current `died` is unset — a feature
that already has a died date before 1906 already has a better (or at least
not-conflicting) estimate from some other source (a documented cause_of_death,
a known fire, etc.) and is left untouched.
"""

import os
import json
import argparse

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')

DIED_NOTE = ("Corrected via 1880/1906 building-match pipeline: absent from "
             "Goad's 1906 survey (direct negative evidence).")


def died_year(died):
    """Leading 4-digit year from a died string, or None if unset/unparseable."""
    if not died:
        return None
    digits = died[:4]
    return int(digits) if digits.isdigit() else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--matches', default=os.path.join(DATA_DIR, 'mcphillips_goad_1906.matches.json'))
    ap.add_argument('--in1880', default=os.path.join(DATA_DIR, 'mcphillips_1880.geojson'))
    ap.add_argument('--out', default=os.path.join(DATA_DIR, 'mcphillips_1880.died_corrected.geojson'))
    args = ap.parse_args()

    with open(args.matches, encoding='utf-8') as f:
        matches = json.load(f)['matches']
    with open(args.in1880, encoding='utf-8') as f:
        fc = json.load(f)

    no_match_ids = set()
    for m in matches:
        if m['classification'] == 'no_match':
            no_match_ids.update(m['ids_1880'])

    by_id = {ft['properties']['id']: ft for ft in fc['features']}
    missing = no_match_ids - by_id.keys()
    if missing:
        print(f"WARNING: {len(missing)} no_match ids from matches.json not found in {args.in1880}: "
              f"{sorted(missing)[:10]}{'...' if len(missing) > 10 else ''}")

    corrected, skipped_has_died = 0, 0
    for fid in no_match_ids:
        ft = by_id.get(fid)
        if ft is None:
            continue
        props = ft['properties']
        existing_year = died_year(props.get('died'))
        if existing_year is not None and existing_year < 1906:
            skipped_has_died += 1
            continue
        props['died'] = '1893-01-01'
        props['died_low'] = '1880'
        props['died_high'] = '1906'
        note = props.get('died_notes')
        props['died_notes'] = f"{note} {DIED_NOTE}" if note else DIED_NOTE
        corrected += 1

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(fc, f)

    print(f"no_match 1880 features: {len(no_match_ids)}")
    print(f"  corrected died estimate: {corrected}")
    print(f"  left alone (already had died < 1906): {skipped_has_died}")
    print(f"Wrote {len(fc['features'])} features -> {args.out}")


if __name__ == '__main__':
    main()
