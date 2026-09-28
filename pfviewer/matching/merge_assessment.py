"""
merge_assessment.py — add City of Winnipeg assessment + heritage buildings to
the pastforward growth master, writing a NEW file and leaving
data/pastforward_2026.geojson untouched.

Run after build_pastforward.py:
    python build_pastforward.py
    python merge_assessment.py --assess-dir ~/sandbox/assessment_import

Inputs:
  data/pastforward_2026.geojson            growth master (Goad 1906 / McPhillips 1880).
  data/wpg_roads.geojson                   used to find which lot edge faces the street.
  <assess-dir>/assessment_to_1906.geojson  assessment parcels, year_built <= 1906
                                           (residential only — the roll has no year for
                                           commercial/institutional parcels).
  <assess-dir>/osm_buildings.geojson       OpenStreetMap footprints (fetch_osm.py). ODbL.
  <assess-dir>/historical_resources.json   City of Winnipeg Historical Resources (ptpx-kgiu).

Outputs:
  data/pastforward_2026_assessment.geojson          master + assessment/heritage dates (no OSM data).
  data/pastforward_2026_osm.geojson                 new buildings with OSM footprints (ODbL, separate DB).
  <assess-dir>/assessment_review.geojson            held back for review in Planimetro.

Rules:
  1. A parcel containing Goad structure(s): keep the Goad geometry. The main building
     (largest non-wood_industrial) takes the assessment year, but ONLY if its born is
     procedural_infill — survey-backed dates are never overwritten. Outbuildings with
     procedural dates are pushed no earlier than their house.
  2. A parcel outside Goad coverage: new structure. Footprint = the OSM building on the
     parcel if there is one, else a synthetic footprint of 25-35% of the lot, placed
     toward the street (sized from living area / floors where known).
  3. New structures get a material: OSM building:material if tagged, else inferred from
     Goad 1906 brick rates for comparable houses (noted as unknown in `notes`).
  Parcels inside Goad coverage with no Goad structure are held back for review.
  Heritage (Historical Resources, built <= 1906) dates/names take precedence over
  assessment and procedural dates; they add non-residential buildings where an OSM
  footprint exists outside Goad coverage.
  Assessment year 1905 is treated as a likely assessor default: born spread over 1900-1905.
"""

import os
import re
import json
from geojson_io import dump_geojson_lines   # one feature per line (editor/diff friendly)
import uuid
import argparse
from collections import defaultdict

from shapely.geometry import shape, mapping, Point, Polygon
from shapely.ops import transform, unary_union
from shapely import STRtree
from shapely.affinity import scale as shp_scale
from pyproj import Transformer

from build_pastforward import unit_hash, iso_from_fraction

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
UID_NS = uuid.UUID('6f1c1e8a-5b1e-4c2a-9d3e-0a55e55a0001')  # same namespace as extract_pre1907.py
GOAD_SURVEY_ISO = '1906-06-30'
NON_BUILDING = re.compile(r'\b(gates?|monument|cairn|pillars?|bridge|fence|statue|plaque|sign)\b', re.I)
NEW_ID_BASE = 100001            # pastforward ids top out ~19k; keep new ones clear of them
COVERAGE_BUFFER_M = 60          # Goad coverage ≈ Goad 1906 buildings buffered by this
SECONDARY_OSM = {'garage', 'garages', 'shed', 'carport', 'roof', 'construction', 'hut', 'kiosk'}
OSM_MATERIAL = {'brick': 'brick', 'wood': 'wood', 'timber_framing': 'wood', 'stone': 'stone',
                'concrete': 'concrete', 'sandstone': 'stone', 'limestone': 'stone'}

# Output is split in two so the ODbL (share-alike) applies only to the OSM-derived
# file: the two are independent databases loaded side by side (an ODbL "Collective
# Database"); the rendered view is a "Produced Work" that just needs the OSM credit.
ATTRIBUTION = ("Buildings: Goad's 1906 & McPhillips 1880 digitization (PastForward); "
               "Contains information licensed under the Open Government Licence – Winnipeg")
ATTRIBUTION_OSM = "Footprints © OpenStreetMap contributors (ODbL)"
LICENSE_OSM = ('This database is made available under the Open Database License (ODbL) 1.0: '
               'https://opendatacommons.org/licenses/odbl/1-0/ . It contains data © OpenStreetMap '
               'contributors (https://www.openstreetmap.org/copyright) and information licensed under '
               'the Open Government Licence – Winnipeg (https://data.winnipeg.ca/stories/s/rwzh-4ijx).')

to_m = Transformer.from_crs(4326, 26914, always_xy=True).transform
to_ll = Transformer.from_crs(26914, 4326, always_xy=True).transform


def geom_m(g):
    g = transform(to_m, shape(g))
    return g.buffer(0) if g.geom_type in ('Polygon', 'MultiPolygon') else g  # buffer(0) empties lines


def geom_ll(g):
    g = transform(to_ll, g)
    return json.loads(json.dumps(mapping(g)))  # tuples -> lists


def clean(props):
    return {k: v for k, v in props.items() if v is not None}


def iso_in_years(uid, salt, lo, hi):
    """Deterministic ISO date within years lo..hi inclusive, never after the Goad survey
    (pfviewer's 1906 view is 1906-07-01, so later 1906 dates wouldn't appear on it)."""
    return min(iso_from_fraction(unit_hash(uid, salt), lo, hi + 1), GOAD_SURVEY_ISO)


def born_from_year(uid, year, circa=False, basis='assessment_year_built'):
    """(born_iso, lo, hi, basis). 1905 assessment years and circa heritage dates get a window."""
    if basis == 'assessment_year_built' and year == 1905:
        lo, hi, basis = 1900, 1905, 'assessment_year_built_1905_default'
    elif circa:
        lo, hi = year - 3, min(year + 3, 1906)
    else:
        lo = hi = year
    iso = iso_in_years(uid, 'assess_born', lo, hi)
    return iso, lo, hi, basis


def floors_from_text(t):
    words = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8,
             'nine': 9, 'ten': 10, 'storey-and-a-half': 1.5}
    m = re.search(r'\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)(?:\s*and\s*one-half|\s*and\s*a\s*half|-and-one-half|½)?[- ]stor(?:e)?y', t)
    if not m:
        return None
    n = words.get(m.group(1)) or float(m.group(1))
    return n + (0.5 if re.search(r'half|½', m.group(0)) else 0)


def material_from_text(t):
    if re.search(r'\blimestone\b|\bstone\b(?! (?:sill|trim|belt|base|foundation|accent|detail|lintel|coping|band))', t):
        return 'stone' if 'brick' not in t else 'brick'
    if 'brick' in t:
        return 'brick'
    if re.search(r'\bframe\b|\bwood\b|clapboard|\blog\b|siding', t):
        return 'log' if re.search(r'\blog\b', t) else 'wood'
    return None


def lot_frame(lot, road_tree, roads):
    """Return (origin, u, v, width, depth) for the lot's min rotated rectangle, with the
    origin at the midpoint of the street-facing short edge, u along it, v into the lot."""
    rect = lot.minimum_rotated_rectangle
    if not isinstance(rect, Polygon):
        return None
    c = list(rect.exterior.coords)[:4]
    edges = [(c[i], c[(i + 1) % 4]) for i in range(4)]
    lens = [((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5 for a, b in edges]
    short = [0, 2] if lens[0] <= lens[1] else [1, 3]
    best = None
    for i in short:
        a, b = edges[i]
        mid = Point((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        d = roads[road_tree.nearest(mid)].distance(mid)
        if best is None or d < best[0]:
            best = (d, i, mid)
    _, i, mid = best
    a, b = edges[i]
    w = lens[i]
    u = ((b[0] - a[0]) / w, (b[1] - a[1]) / w)
    v = (-u[1], u[0])
    ctr = rect.centroid
    if (ctr.x - mid.x) * v[0] + (ctr.y - mid.y) * v[1] < 0:
        v = (-v[0], -v[1])
    depth = lens[(i + 1) % 4]
    return (mid.x, mid.y), u, v, w, depth


def synthetic_footprint(lot, uid, living_sqft, floors, road_tree, roads):
    """Rule 2: 25-35% of the lot, toward the street. Returns (geom, basis)."""
    lot_area = lot.area
    frac = 0.25 + 0.10 * unit_hash(uid, 'footprint_frac')
    target = frac * lot_area
    if living_sqft and floors:
        ground = living_sqft * 0.092903 / max(floors, 1)
        target = min(max(ground, 0.25 * lot_area), 0.35 * lot_area)
        if 0.25 * lot_area > 2 * ground:   # big lot — a 25% house would be a mansion; use the house size
            target = ground
    else:
        target = min(target, 300.0)
    fr = lot_frame(lot, road_tree, roads)
    if fr:
        (ox, oy), u, v, lw, ld = fr
        w = max(min(lw - 2.4, 0.85 * lw), min(4.0, 0.85 * lw))
        s = min(5.0, 0.15 * ld)
        d = target / w
        if s + d > 0.9 * ld:
            d = max(0.9 * ld - s, 1.0)
            w = min(target / d, 0.9 * lw)
        pts = []
        for du, dv in ((-w / 2, s), (w / 2, s), (w / 2, s + d), (-w / 2, s + d)):
            pts.append((ox + u[0] * du + v[0] * dv, oy + u[1] * du + v[1] * dv))
        rect = Polygon(pts)
        g = rect.intersection(lot)
        if not g.is_empty and g.area >= 0.8 * rect.area and g.geom_type == 'Polygon':
            return g, 'synthetic_street_front'
    k = (target / lot_area) ** 0.5
    return shp_scale(lot, k, k, origin='centroid'), 'synthetic_scaled_lot'


def area_bucket(sqft):
    if not sqft:
        return 'na'
    for lim in (1000, 1500, 2000, 3000):
        if sqft < lim:
            return f'<{lim}'
    return '3000+'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--assess-dir', default=os.path.expanduser('~/sandbox/assessment_import'))
    ap.add_argument('--master', default=os.path.join(DATA_DIR, 'pastforward_2026.geojson'))
    ap.add_argument('--roads', default=os.path.join(DATA_DIR, 'wpg_roads.geojson'))
    ap.add_argument('--out', default=os.path.join(DATA_DIR, 'pastforward_2026_assessment.geojson'))
    ap.add_argument('--out-osm', default=os.path.join(DATA_DIR, 'pastforward_2026_osm.geojson'))
    a = ap.parse_args()
    A = lambda n: os.path.join(a.assess_dir, n)

    master = json.load(open(a.master))
    pf = master['features']
    parcels = json.load(open(A('assessment_to_1906.geojson')))['features']
    osm = json.load(open(A('osm_buildings.geojson')))
    heritage = json.load(open(A('historical_resources.json')))
    roads = [geom_m(f['geometry']) for f in json.load(open(a.roads))['features'] if f.get('geometry')]
    road_tree = STRtree(roads)

    pg = [geom_m(f['geometry']) for f in pf]
    goad = [i for i, f in enumerate(pf) if f['properties'].get('cohort') in ('1906_only', 'matched')]
    goad_tree = STRtree([pg[i] for i in goad])
    coverage = unary_union([pg[i].buffer(COVERAGE_BUFFER_M) for i in goad])

    og = [geom_m(f['geometry']) for f in osm['features']]
    osm_tree = STRtree(og)

    stats = defaultdict(int)
    review = []

    # ── Rule 1: parcels with Goad structures ────────────────────────────────
    main_year = {}          # pf index -> (year, parcel props)
    out_floor = {}          # pf index -> earliest year its house was built
    no_goad = []
    for p in parcels:
        lot = geom_m(p['geometry'])
        pp = p['properties']
        members = []
        for k in goad_tree.query(lot):
            i = goad[k]
            inter = pg[i].intersection(lot).area
            if pg[i].area and (inter / pg[i].area >= 0.5 or inter / lot.area >= 0.3):
                members.append(i)
        if not members:
            no_goad.append((p, lot))
            continue
        houses = [i for i in members if pf[i]['properties'].get('material') != 'wood_industrial'] or members
        main = max(houses, key=lambda i: pg[i].area)
        y = int(pp['born_low'])
        if main not in main_year or y < main_year[main][0]:
            main_year[main] = (y, pp)
        for i in members:
            if i != main:
                out_floor[i] = min(out_floor.get(i, 9999), y)

    # training data for material inference: parcel attributes -> Goad main-building material
    train = defaultdict(lambda: [0, 0])      # key -> [brick, total]
    for i, (y, pp) in main_year.items():
        mat = pf[i]['properties'].get('material')
        if mat not in ('wood', 'brick', 'stone'):
            continue
        brick = mat in ('brick', 'stone')
        for key in (('all',), ('strata', pp.get('floors'), area_bucket(pp.get('living_area_sqft'))),
                    ('nb', pp.get('neighbourhood'))):
            train[key][0] += brick
            train[key][1] += 1
    g_b, g_n = train[('all',)]
    p_global = (g_b + 1) / (g_n + 2)

    def p_brick(pp):
        sb, sn = train[('strata', pp.get('floors'), area_bucket(pp.get('living_area_sqft')))]
        p_s = (sb + 10 * p_global) / (sn + 10)
        nb, nn = train[('nb', pp.get('neighbourhood'))]
        p_nb = (nb + 20 * p_global) / (nn + 20)
        return min(p_s * p_nb / p_global, 0.95)

    for i, (y, pp) in main_year.items():
        props = pf[i]['properties']
        props.setdefault('address', pp.get('address'))
        props['assess_roll'] = pp.get('roll_number')
        props['assess_year_built'] = y
        if props.get('born_basis') == 'procedural_infill':
            uid = props.get('pf_uid') or str(i)
            iso, lo, hi, basis = born_from_year(uid, y)
            props.update(born=iso, born_low=str(lo), born_high=str(hi), born_basis=basis)
            stats['goad_redated'] += 1
        else:
            stats['goad_kept_survey_date'] += 1
    for i, y in out_floor.items():
        props = pf[i]['properties']
        if i in main_year or props.get('born_basis') != 'procedural_infill':
            continue
        if int(props['born'][:4]) < y:
            uid = props.get('pf_uid') or str(i)
            props['born'] = iso_in_years(uid, 'outbuilding', y, min(y + 3, 1906))
            props['born_low'] = str(y)
            props['born_basis'] = 'procedural_infill_after_house'
            stats['outbuilding_pushed_later'] += 1

    # ── Rule 2/3: new structures outside Goad coverage ──────────────────────
    new = {}                # key (osm id or roll) -> dict(geom, props)
    osm_used = {}
    for p, lot in no_goad:
        pp = p['properties']
        if coverage.contains(lot.centroid):
            review.append({'type': 'Feature', 'geometry': p['geometry'],
                           'properties': {**pp, 'review_reason': 'inside Goad coverage but no Goad structure on parcel'}})
            stats['held_for_review'] += 1
            continue
        cands = []
        for k in osm_tree.query(lot):
            t = osm['features'][k]['properties']
            if t.get('building') in SECONDARY_OSM or og[k].area < 25:
                continue
            inter = og[k].intersection(lot).area
            if inter / og[k].area >= 0.5 or inter / lot.area >= 0.3:
                cands.append(k)
        year = int(pp['born_low'])
        if cands:
            k = max(cands, key=lambda k: og[k].area)
            t = osm['features'][k]['properties']
            key = t['osm_id']
            if key in new:        # one OSM building across several parcels (duplex/terrace)
                n = new[key]
                n['props']['address'] += '; ' + pp['address']
                n['props']['roll_number'] += ',' + pp['roll_number']
                n['years'].append(year)
                continue
            geom, fp_src = og[k], 'osm'
            stats['new_osm_footprint'] += 1
        else:
            key = pp['roll_number']
            t = {}
            geom, fp_src = synthetic_footprint(lot, pp['pf_uid'], pp.get('living_area_sqft'),
                                               pp.get('floors'), road_tree, roads)
            stats['new_' + fp_src] += 1
        uid = str(uuid.uuid5(UID_NS, key))
        notes = []
        osm_mat = OSM_MATERIAL.get(t.get('building:material'))
        if osm_mat:
            mat = osm_mat
            notes.append('material from OSM building:material')
        else:
            pb = p_brick(pp)
            mat = 'brick' if unit_hash(uid, 'material') < pb else 'wood'
            notes.append(f'material inferred from Goad 1906 brick rates for similar houses (p_brick={pb:.2f}); actual material unknown')
            stats['material_inferred_' + mat] += 1
        if fp_src != 'osm':
            notes.append(f'footprint synthetic ({fp_src}) from assessment parcel; real footprint unknown')
        new[key] = {'geom': geom, 'years': [year], 'props': {
            'pf_uid': uid, 'name': pp.get('name'), 'address': pp.get('address'),
            'material': mat, 'floors': pp.get('floors'), 'roof_type': 'gabled',
            'died_basis': 'still_standing', 'cohort': 'assessment',
            'source': pp.get('source'), 'footprint_source': fp_src,
            'osm_id': t.get('osm_id'), 'roll_number': pp.get('roll_number'),
            'assess_building_type': pp.get('assess_building_type'), 'assess_use': pp.get('assess_use'),
            'neighbourhood': pp.get('neighbourhood'), 'notes': notes,
            'snapped': False, 'group': 'assessment_2026',
        }}

    for key, n in new.items():
        y = min(n['years'])
        iso, lo, hi, basis = born_from_year(n['props']['pf_uid'], y)
        n['props'].update(born=iso, born_low=str(lo), born_high=str(hi), born_basis=basis)

    # ── Heritage (Historical Resources) ─────────────────────────────────────
    new_tree_keys = list(new)
    new_tree = STRtree([new[k]['geom'] for k in new_tree_keys]) if new else None
    for r in heritage:
        m = re.search(r'(1[6-9]\d\d)', r.get('construction_date') or '')
        if not m or int(m.group(1)) > 1906 or not r.get('point') or NON_BUILDING.search(r.get('historical_name') or ''):
            continue
        year = int(m.group(1))
        circa = bool(re.match(r'\s*\d{4}\s*c', r.get('construction_date') or ''))
        pt = transform(to_m, shape(r['point']))
        text = ' '.join(str(r.get(k) or '') for k in ('condition_1', 'summary', 'report_summary')).lower()
        hname = r.get('historical_name')
        addr = f"{r.get('street_number') or ''} {r.get('street_name') or ''}".strip()
        heritage_props = {'heritage_name': hname, 'heritage_date': r.get('construction_date'),
                          'heritage_url': (r.get('short_report_url') or {}).get('url') if isinstance(r.get('short_report_url'), dict) else r.get('short_report_url')}

        def apply_date(props, uid):
            if props.get('born_basis') not in ('procedural_infill', 'procedural_infill_after_house',
                                               'assessment_year_built', 'assessment_year_built_1905_default'):
                return False
            iso, lo, hi, basis = born_from_year(uid, year, circa, basis='heritage_construction_date')
            props.update(born=iso, born_low=str(lo), born_high=str(hi), born_basis=basis)
            return True

        # (a) a Goad building at the point
        hit = [goad[k] for k in goad_tree.query(pt.buffer(5)) if pg[goad[k]].distance(pt) <= 5]
        if hit:
            i = min(hit, key=lambda i: pg[i].distance(pt))
            props = pf[i]['properties']
            props.update(clean(heritage_props))
            props.setdefault('name', hname)
            stats['heritage_goad_redated' if apply_date(props, props.get('pf_uid') or str(i)) else 'heritage_goad_named_only'] += 1
            continue
        # (b) a new assessment structure at the point
        if new_tree is not None:
            hit = [new_tree_keys[k] for k in new_tree.query(pt.buffer(5)) if new[new_tree_keys[k]]['geom'].distance(pt) <= 5]
            if hit:
                n = new[hit[0]]
                n['props'].update(clean(heritage_props))
                n['props']['name'] = hname or n['props']['name']
                apply_date(n['props'], n['props']['pf_uid'])
                tm = material_from_text(text)
                if tm:
                    n['props']['material'] = tm
                    n['props']['notes'] = [x for x in n['props']['notes'] if not x.startswith('material inferred')] + ['material from Historical Resources description']
                stats['heritage_assessment_updated'] += 1
                continue
        # (c) inside Goad coverage but nothing there — review
        if coverage.contains(pt):
            review.append({'type': 'Feature', 'geometry': r['point'], 'properties': {
                **clean(heritage_props), 'address': addr, 'review_reason': 'heritage point inside Goad coverage with no Goad structure'}})
            stats['heritage_review'] += 1
            continue
        # (d) an OSM building at the point — new non-residential (or unassessed) structure
        hit = [k for k in osm_tree.query(pt.buffer(5)) if og[k].distance(pt) <= 5
               and osm['features'][k]['properties'].get('building') not in SECONDARY_OSM]
        if not hit:
            review.append({'type': 'Feature', 'geometry': r['point'], 'properties': {
                **clean(heritage_props), 'address': addr, 'review_reason': 'heritage point with no footprint (possibly demolished)'}})
            stats['heritage_no_footprint'] += 1
            continue
        k = min(hit, key=lambda k: og[k].distance(pt))
        t = osm['features'][k]['properties']
        if t['osm_id'] in new:
            continue
        uid = str(uuid.uuid5(UID_NS, t['osm_id']))
        notes = []
        mat = material_from_text(text) or OSM_MATERIAL.get(t.get('building:material'))
        if mat:
            notes.append('material from Historical Resources description / OSM')
        else:
            mat = 'brick'
            notes.append('material assumed brick (heritage building, no description); actual material unknown')
        floors = floors_from_text(text)
        if floors is None:
            try:
                floors = float(t.get('building:levels'))
            except (TypeError, ValueError):
                floors = 2
                notes.append('floors assumed 2')
        props = {'pf_uid': uid, 'name': hname or addr, 'address': addr, 'material': mat, 'floors': floors,
                 'died_basis': 'still_standing', 'cohort': 'heritage', 'source': 'winnipeg_historical_resources',
                 'footprint_source': 'osm', 'osm_id': t['osm_id'], 'notes': notes, 'snapped': False,
                 'group': 'heritage_2026', **clean(heritage_props)}
        if re.search(r'church|cathedral|synagogue', (hname or '').lower()) and not re.search(r'house|rectory|residence|hall|school', (hname or '').lower()):
            props['type'] = 'church'
        iso, lo, hi, basis = born_from_year(uid, year, circa, basis='heritage_construction_date')
        props.update(born=iso, born_low=str(lo), born_high=str(hi), born_basis=basis)
        new[t['osm_id']] = {'geom': og[k], 'years': [year], 'props': props}
        stats['heritage_new_osm'] += 1

    # ── Write ───────────────────────────────────────────────────────────────
    # Anything with OSM geometry (or OSM tags) goes ONLY to the ODbL file.
    out, out_osm = list(pf), []
    for n, (key, v) in enumerate(new.items()):
        props = clean(v['props'])
        props['id'] = NEW_ID_BASE + n
        props['notes'] = '; '.join(props.get('notes', [])) or None
        feat = {'type': 'Feature', 'properties': clean(props), 'geometry': geom_ll(v['geom'])}
        (out_osm if props.get('footprint_source') == 'osm' else out).append(feat)
    assert not any('osm_id' in f['properties'] for f in out)

    with open(a.out, 'w') as f:
        dump_geojson_lines({'type': 'FeatureCollection', 'attribution': ATTRIBUTION, 'features': out}, f)
    with open(a.out_osm, 'w') as f:
        dump_geojson_lines({'type': 'FeatureCollection', 'attribution': ATTRIBUTION_OSM, 'license': LICENSE_OSM,
                            'osm_retrieved': osm.get('retrieved'), 'features': out_osm}, f)
    with open(A('assessment_review.geojson'), 'w') as f:
        dump_geojson_lines({'type': 'FeatureCollection', 'features': review}, f)
    print(f'{len(out)} features -> {a.out}')
    print(f'{len(out_osm)} OSM-footprint features (ODbL) -> {a.out_osm}')
    print(f'{len(review)} held for review -> {A("assessment_review.geojson")}')
    for k in sorted(stats):
        print(f'  {k:40} {stats[k]}')

if __name__ == '__main__':
    main()
