#!/usr/bin/env python3
"""
mcphillips1910_ingest.py — Mike's digitization of the 1910 McPhillips map in areas the Goad sheets don't cover
(tools/sources/mcphillips_1910_non_goad_areas.geojson, 137 features) → the pastforward data:

  data/pastforward_2026_mcphillips1910.geojson   buildings (+ the walkway polygons: cemetery paths, the Industrial Exhibition track)
  data/early_yards.json                          company yards / complexes / stock yards: ground patches, not buildings
  data/cemeteries.json                           Elmwood Cemetery: plot polygons + the paths polygon (the viewer sets headstones)
  tools/sources/mcphillips1910_ingest_report.txt what was dropped / kept / needs review

Rules (the previous data wins):
  * features already in the data (same uid) are skipped (12);
  * exact repeats inside the file (copies stacked on one another) are collapsed;
  * a building overlapping (>25% of its area) an existing building born <= 1915 is a duplicate and dropped; overlapping a
    LATER one it is kept and ends when that one begins;
  * notes mark the non-buildings: 'Complex…' / 'area not building' → yards; 'Not building (and not sure it was ever really
    here)' (the CNR yards polygon) is dropped; cemetery polygons ('Place headstones') → cemeteries.json;
  * the digitization carries no dates: buildings get a PROCEDURAL born date spread 1895–1910 (like the Goad infill).
"""
import json, math, os, glob, hashlib, uuid
from shapely.geometry import shape
from shapely.ops import transform
from shapely.strtree import STRtree
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
M, R = 71600, 111320
prj = lambda g: transform(lambda x, y, z=None: ((x + 97.13) * M, (y - 49.89) * R), g)
def year(b):
    try: return int(str(b)[:4])
    except Exception: return 9999
def h01(s): return int(hashlib.md5(str(s).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
def iso(y):
    yi = int(y); d = int((y - yi) * 365); import datetime; return (datetime.date(yi, 1, 1) + datetime.timedelta(days=min(d, 364))).isoformat()

def main():
    src = json.load(open(os.path.join(HERE, 'sources', 'mcphillips_1910_non_goad_areas.geojson')))['features']
    existing_uids = set(); ex = []
    bb = (-97.175, 49.870, -97.100, 49.930)
    for fn in glob.glob(os.path.join(DATA, '*.geojson')):
        try: d = json.load(open(fn))
        except Exception: continue
        name = os.path.basename(fn)
        for f in d.get('features', []):
            p = f['properties']
            for k in ('uid', 'pf_uid'):
                if p.get(k): existing_uids.add(p[k])
            if name in ('pastforward_2026_assessment.geojson', 'pastforward_2026_osm.geojson', 'pastforward_2026_legislature_osm.geojson', 'pastforward_2026_stb1880.geojson') and f['geometry']['type'] in ('Polygon', 'MultiPolygon'):
                c = f['geometry']['coordinates']
                while isinstance(c[0], list): c = c[0]
                if bb[0] < c[0] < bb[2] and bb[1] < c[1] < bb[3]:
                    g = prj(shape(f['geometry']))
                    if not g.is_valid: g = g.buffer(0)
                    ex.append((g, p, name))
    tree = STRtree([e[0] for e in ex])
    rep = {k: [] for k in ('skipped_existing', 'repeats', 'dup', 'replaced', 'skipped_doubtful', 'yards', 'cemetery', 'named_existing', 'review')}
    buildings, yards, cem, seen_geo = [], [], {'plots': [], 'paths': []}, []
    for f in src:
        p = f['properties']; uid = p.get('uid') or p.get('pf_uid'); nm = p.get('name') or ''; note = (p.get('notes') or '').lower()
        if uid in existing_uids: rep['skipped_existing'].append(f"{p['id']} {nm}"); continue
        g = prj(shape(f['geometry'])); g = g if g.is_valid else g.buffer(0)
        label = f"{p['id']} {nm or '(unnamed)'} ({g.area:.0f} m²)"
        if any(g.symmetric_difference(s).area < 0.05 * g.area for s in seen_geo):
            rep['repeats'].append(label + ' — same outline as an earlier feature'); continue
        seen_geo.append(g)
        if 'not building (and not sure' in note: rep['skipped_doubtful'].append(label + ' — ' + p['notes']); continue
        if nm.startswith('Elmwood Cemetary'):
            rings = [poly for poly in (f['geometry']['coordinates'] if f['geometry']['type'] == 'MultiPolygon' else [f['geometry']['coordinates']])]
            (cem['paths'] if p.get('type') == 'walkway' else cem['plots']).extend(rings); rep['cemetery'].append(label); continue
        if 'complex' in note or 'complext' in note or 'area not building' in note:
            polys = f['geometry']['coordinates'] if f['geometry']['type'] == 'MultiPolygon' else [f['geometry']['coordinates']]
            yards.append({"name": nm or 'yard', "kind": 'stockyard' if 'stock' in nm.lower() else 'yard', "polys": polys, "born": "1895-01-01", "died": None, "note": p.get('notes'), "source": "McPhillips 1910, Mike's digitization"})
            rep['yards'].append(label + f" — {p.get('notes')}"); continue
        if p.get('type') == 'building' and g.area > 20000 and not nm:
            rep['skipped_doubtful'].append(label + ' — unnamed building outline of 27,000 m² (probably an area, not a building): not drawn; tell me if it should be'); continue
        # ---- a building (or walkway polygon): dedupe against what's there
        dup = None; later = []
        for i in tree.query(g):
            eg, ep, fn = ex[i]; ov = g.intersection(eg).area / max(g.area, 1e-6)
            if ov > 0.25:
                by = year(ep.get('born'))
                desc = f"{ep.get('name') or ep.get('address') or str(ep.get('pf_uid'))[:8]} [{fn.replace('pastforward_2026_','').replace('.geojson','')}, born {ep.get('born')}] {ov:.0%}"
                if by <= 1915: dup = dup or desc
                else: later.append((by, ep.get('born'), desc))
        if dup:
            rep['dup'].append(label + ' overlaps ' + dup)
            if 'present in pastforward data already' in note: rep['named_existing'].append((p['id'], nm, dup))
            continue
        died = None
        if later: later.sort(); died = later[0][1]; rep['replaced'].append(label + ' overlaps later ' + '; '.join(l[2] for l in later) + f' → died {died}')
        walk = p.get('type') == 'walkway'
        u = h01(uid); born_y = 1895 + 15 * u
        props = {"id": f"mcp1910-{p['id']}", "uid": uid, "pf_uid": uid, "material": p['material'], "cohort": "mcphillips_1910",
                 "born": iso(born_y), "born_low": "1895", "born_high": "1910", "born_basis": "procedural_infill (present on the 1910 McPhillips map; build date unknown)",
                 "source_file": "mcphillips_1910_non_goad_areas.geojson — Mike's digitization of the 1910 McPhillips map", "group": "import_mcphillips_1910_20261006",
                 "footprint_source": "McPhillips 1910 digitization (low detail in places)"}
        for k in ('name', 'floors', 'roof_type', 'notes', 'cause_of_death'):
            if p.get(k) not in (None, ''): props[k] = p[k]
        if walk: props['type'] = 'walkway'
        if p.get('died'): props['died'] = p['died']; props['died_basis'] = 'digitizer'
        elif died: props['died'] = died; props['died_basis'] = 'replaced by a later building on the same footprint'
        else: props['died_basis'] = 'unknown (still standing in the data)'
        if 'does not by 2026' in note: rep['review'].append(label + " — Mike's note 'Does not by 2026': it's gone today; the end date isn't known (left open)")
        buildings.append({"type": "Feature", "properties": props, "geometry": f['geometry']})
    json.dump({"type": "FeatureCollection", "name": "pastforward_2026_mcphillips1910", "features": buildings}, open(os.path.join(DATA, 'pastforward_2026_mcphillips1910.geojson'), 'w'))
    json.dump({"yards": yards}, open(os.path.join(DATA, 'early_yards.json'), 'w'), indent=1)
    json.dump({"name": "Elmwood Cemetery", "founded": 1901, "plots": cem['plots'], "paths": cem['paths'], "source": "McPhillips 1910, Mike's digitization"}, open(os.path.join(DATA, 'cemeteries.json'), 'w'))
    L = [f"1910 McPhillips digitization: {len(src)} features in → {len(buildings)} buildings/walkways added, {len(yards)} yard(s), {len(cem['plots'])} cemetery plot polygon(s)"]
    for k, t in (('skipped_existing', 'ALREADY IN THE DATA (same uid) — skipped'), ('repeats', 'REPEATS inside the file — collapsed'), ('dup', 'DUPLICATES of existing buildings born <= 1915 — dropped (previous data wins)'),
                 ('replaced', 'REPLACED by a later existing building — kept, died set'), ('skipped_doubtful', 'NOT DRAWN'), ('yards', 'YARDS / COMPLEXES (ground patches, not buildings)'),
                 ('cemetery', 'CEMETERY polygons'), ('review', 'NEEDS REVIEW')):
        L += ['', f'{t}: {len(rep[k])}'] + ['  ' + x for x in rep[k]]
    L += ['', 'NAME TO ADD TO AN EXISTING BUILDING: ' + json.dumps(rep['named_existing'])]
    open(os.path.join(HERE, 'sources', 'mcphillips1910_ingest_report.txt'), 'w').write('\n'.join(L)); print('\n'.join(L))
if __name__ == '__main__': main()
