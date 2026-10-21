"""died_upper_bounds.py — older pfviewer buildings that a newer, dated building now stands on.

A building whose footprint is (mostly) covered by one the assessment roll says was built in year Y can't have
stood past Y: that is an upper bound on its died date. Lists every such pair for review.

    python tools/died_upper_bounds.py ASSESSMENT_CSV OSM_BUILDINGS_NDJSON OUT_PREFIX

  ASSESSMENT_CSV        City of Winnipeg Assessment Parcels export (Year Built: residential + condo parcels only)
  OSM_BUILDINGS_NDJSON  tools/extract_buildings.py output
  OUT_PREFIX            writes OUT_PREFIX.geojson (old footprints + the bound, for Planimetro),
                        OUT_PREFIX_by.geojson (the newer footprints) and OUT_PREFIX.json (compact list for the viewer)

Old buildings = every building file pfviewer autoloads (data/pastforward_2026_*.geojson), with building_history.json
`set.died` applied. A newer footprint counts when it covers >= OVERLAP of either footprint's area and its year is
after the old building's born year. Categories (`auto` ones are applied by tools/apply_died_bounds.py, the rest are
for review — pfviewer ?review=died):
  contradicts        its died date is later than the bound
  same_building      footprints nearly identical (IoU >= SAME_IOU), the new one at most SAME_GROW × the old with the old
                     inside it, or both standing at the 1906 survey with a roll year <= 1906: more likely the same
                     building (redrawn footprint, or the roll's 1905 default year) — no change
  misaligned         a small overlap (< AUTO_COVER of the old footprint), and the old footprint shifted by up to
                     SHIFT_M lines up (IoU >= SHIFT_IOU) with some OSM building: registration error, not a replacement
  possible_addition  the old footprint is (almost) wholly inside one SAME_GROW–ADD_GROW × its size: may still stand
                     with an addition — review
  replaced  (auto)   the new footprint covers >= AUTO_COVER of the old one: it can't still stand
  small_overlap      the rest — review
Already-consistent pairs (died <= bound) are left out, so applied ones drop off the list on the next run."""
import sys, os, csv, json, math
from collections import defaultdict, Counter
from shapely import wkt, STRtree
from shapely.geometry import shape, mapping
from shapely import transform as sh_transform
import numpy as np

csv.field_size_limit(1 << 30)
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
OLD_FILES = ['pastforward_2026_assessment.geojson', 'pastforward_2026_osm.geojson', 'pastforward_2026_mcphillips1910.geojson',
             'pastforward_2026_stb1880.geojson', 'pastforward_2026_legislature_osm.geojson', 'pastforward_2026_ogilvie_stack.geojson']
OVERLAP, SAME_IOU = 0.2, 0.7
AUTO_COVER, INSIDE = 0.4, 0.9           # replaced: new covers >= AUTO_COVER of old; 'inside': >= INSIDE
SAME_GROW, ADD_GROW = 1.5, 3.0          # new/old area ratios for same_building / possible_addition (old inside)
SHIFT_M, SHIFT_IOU = 4, 0.6             # misalignment test
GOAD_YEAR = 1906   # a building standing at the 1906 survey can't have been replaced by one the roll dates <= 1906
C_LON, C_LAT = -97.135515, 49.895396
MLON = 111320*math.cos(math.radians(C_LAT)); MLAT = 111320
to_m = lambda g: sh_transform(g, lambda c: np.column_stack([(c[:, 0]-C_LON)*MLON, (c[:, 1]-C_LAT)*MLAT]))

csv_path, osm_path, out = sys.argv[1:4]

# ── Old buildings ─────────────────────────────────────────────────────────
hist = json.load(open(os.path.join(DATA, 'building_history.json'))).get('buildings', {})
old, old_g = [], []
for fn in OLD_FILES:
    p = os.path.join(DATA, fn)
    if not os.path.exists(p): continue
    for f in json.load(open(p))['features']:
        pr = dict(f['properties']); g = f.get('geometry')
        if not g or g['type'] not in ('Polygon', 'MultiPolygon') or not pr.get('born'): continue
        h = hist.get(pr.get('pf_uid')) or {}
        if h.get('remove'): continue
        pr.update({k: v for k, v in (h.get('set') or {}).items() if k in ('died', 'born')})
        gm = to_m(shape(g)).buffer(0)
        if gm.is_empty or gm.area < 4: continue
        pr['_file'] = fn; old.append((pr, f['geometry'])); old_g.append(gm)
print(len(old), 'old buildings')

# ── Parcels with a year ───────────────────────────────────────────────────
parcels, pyear, paddr = [], [], []
seen = {}
with open(csv_path, newline='') as fh:
    for r in csv.DictReader(fh):
        yb = r['Year Built'].strip(); gw = r['Geometry']
        if not yb or not gw: continue
        y = int(yb)
        k = gw[:200]
        if k in seen:   # condo units share one parcel polygon: keep the earliest year
            i = seen[k]; pyear[i] = min(pyear[i], y); continue
        try: g = to_m(wkt.loads(gw)).buffer(0)
        except Exception: continue
        seen[k] = len(parcels); parcels.append(g); pyear.append(y); paddr.append(r['Full Address'])
ptree = STRtree(parcels)
print(len(parcels), 'dated parcels')

# ── OSM footprints → parcel year ─────────────────────────────────────────
old_osm = {pr.get('osm_id') for pr, _ in old if pr.get('osm_id')}
new, new_g, all_g = [], [], []
with open(osm_path) as fh:
    for line in fh:
        b = json.loads(line); p = b['p']
        oid = ('way/' if p['id'][0] == 'w' else 'relation/') + p['id'][1:]
        coords = b['g']
        geo = {'type': 'MultiPolygon' if isinstance(coords[0][0][0], list) else 'Polygon', 'coordinates': coords}
        try: g = to_m(shape(geo)).buffer(0)
        except Exception: continue
        if g.is_empty or g.area < 8: continue
        all_g.append(g)                        # every footprint, for the misalignment test
        if oid in old_osm: continue            # already a pfviewer building — compare only against others
        pt = g.representative_point()
        hit = [i for i in ptree.query(pt, predicate='within')]
        if not hit: continue
        i = hit[0]
        new.append({'osm_id': oid, 'year': pyear[i], 'address': paddr[i], 'osm_building': p.get('building'), 'geo': geo}); new_g.append(g)
ntree = STRtree(new_g); atree = STRtree(all_g)
print(len(new), 'OSM footprints with a parcel year')

def aligned_iou(g):
    """Best IoU of g, shifted by up to SHIFT_M in 1 m steps, with any OSM footprint."""
    best = 0.0
    for j in atree.query(g.buffer(SHIFT_M)):
        o = all_g[j]
        for dx in range(-SHIFT_M, SHIFT_M+1):
            for dy in range(-SHIFT_M, SHIFT_M+1):
                h = sh_transform(g, lambda c: c + [dx, dy]); i = h.intersection(o).area
                best = max(best, i/(h.area + o.area - i))
    return best

# ── Pairs ─────────────────────────────────────────────────────────────────
rows = []; cats = Counter()
for oi, (pr, geo) in enumerate(old):
    g = old_g[oi]; by = int(pr['born'][:4]); best = None
    for ni in ntree.query(g):
        n = new[ni]
        if n['year'] <= by: continue
        inter = g.intersection(new_g[ni]).area
        a, b = inter/g.area, inter/new_g[ni].area
        if a < OVERLAP and b < OVERLAP: continue
        iou = inter/(g.area + new_g[ni].area - inter)
        cand = (n['year'], -iou, ni, a, b, iou)
        if best is None or cand < best: best = cand
    if not best: continue
    Y, _, ni, a, b, iou = best; n = new[ni]
    died = pr.get('died'); dy = int(died[:4]) if died else None
    if dy is not None and dy <= Y: continue
    grow = new_g[ni].area/g.area
    if iou >= SAME_IOU or (a >= INSIDE and grow <= SAME_GROW) or (Y <= GOAD_YEAR and by <= GOAD_YEAR and (dy is None or dy > GOAD_YEAR)):
        cat = 'same_building'
    elif dy is not None: cat = 'contradicts'
    elif a >= INSIDE and grow <= ADD_GROW: cat = 'possible_addition'
    elif a >= AUTO_COVER: cat = 'replaced'
    elif aligned_iou(g) >= SHIFT_IOU: cat = 'misaligned'
    else: cat = 'small_overlap'
    cats[cat] += 1
    rows.append({'pf_uid': pr.get('pf_uid'), 'name': pr.get('name'), 'file': pr['_file'], 'born': pr['born'], 'died': died,
                 'died_basis': pr.get('died_basis'), 'bound_year': Y, 'category': cat, 'by_osm_id': n['osm_id'],
                 'by_address': n['address'], 'by_osm_building': n['osm_building'], 'cover_old': round(a, 2), 'cover_new': round(b, 2),
                 'iou': round(iou, 2), 'grow': round(grow, 2), 'auto': cat == 'replaced', 'cx': round(g.centroid.x, 1), 'cz': round(-g.centroid.y, 1), '_geo': geo, '_by': n['geo']})
ORDER = ['contradicts', 'possible_addition', 'small_overlap', 'replaced', 'misaligned', 'same_building']
rows.sort(key=lambda r: (ORDER.index(r['category']), r['bound_year']))
print(dict(cats))

strip = lambda r: {k: v for k, v in r.items() if not k.startswith('_')}
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': strip(r), 'geometry': r['_geo']} for r in rows]},
          open(out + '.geojson', 'w'))
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'pf_uid': r['pf_uid'], 'osm_id': r['by_osm_id'], 'year': r['bound_year'], 'address': r['by_address']}, 'geometry': r['_by']} for r in rows]},
          open(out + '_by.geojson', 'w'))
json.dump({'note': 'tools/died_upper_bounds.py — older buildings under a newer dated footprint', 'items': [{**strip(r), 'geo': r['_geo']['coordinates'], 'by': r['_by']['coordinates']} for r in rows]},
          open(out + '.json', 'w'), separators=(',', ':'))
print(len(rows), 'rows ->', out + '.{geojson,json}', out + '_by.geojson')
