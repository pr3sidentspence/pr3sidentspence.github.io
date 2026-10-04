#!/usr/bin/env python3
"""
stb1880_ingest.py — add the buildings Mike traced from the 1880 bird's-eye view of St Boniface
(tools/sources/stb1880_buildings.geojson, 135 footprints, 'Stoner 1880 bird's-eye view') to the pastforward data
as data/pastforward_2026_stb1880.geojson (autoloaded; the master files are left untouched).

Dedupe — the previous data wins (Mike):
  1. DUPLICATE: the footprint overlaps (>25% of its area) an existing building (assessment / OSM / legislature) with
     born <= 1890 → dropped.
  2. PROBABLE DUPLICATE: no overlap but its centre is within 12 m of an existing building born <= 1890 → dropped.
     (The drawing's footprints are approximate squares; an offset of ~10 m for the same building is normal.)
  3. REPLACED: overlaps an existing building born AFTER 1890 → kept (an 1880 building the later one replaced),
     with died = the earliest such born date.
  4. Within 50 m of an existing early (<=1890) building but neither of the above → kept and listed for review.
Everything kept is born 1880-01-01 ("present by 1880"; true build dates unknown).
Writes the report to tools/sources/stb1880_ingest_report.txt.
"""
import json, math, os, uuid
from shapely.geometry import shape
from shapely.ops import transform
from shapely.strtree import STRtree
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
M, R = 71600, 111320
prj = lambda g: transform(lambda x, y, z=None: ((x + 97.12) * M, (y - 49.89) * R), g)
NS = uuid.UUID('6f1d0c1e-5b7a-4d0e-9a53-1880ab5b0001')
EARLY = 1890
ROOF = {'gable': 'gabled', 'cross-gable': 'gabled', 'hip': 'hip', 'mansard': 'mansard'}
MAT = {'wood': 'wood', 'wood (log)': 'log', 'stone': 'stone', 'brick': 'brick'}

def year(b):
    try: return int(str(b)[:4])
    except Exception: return 9999

def main():
    new = json.load(open(os.path.join(HERE, 'sources', 'stb1880_buildings.geojson')))['features']
    bb = (-97.1360, 49.8800, -97.1040, 49.9020)
    ex = []
    for fn in ('pastforward_2026_assessment', 'pastforward_2026_osm', 'pastforward_2026_legislature_osm'):
        for f in json.load(open(os.path.join(DATA, fn + '.geojson')))['features']:
            if f['geometry']['type'] not in ('Polygon', 'MultiPolygon'): continue
            c = f['geometry']['coordinates']
            while isinstance(c[0], list): c = c[0]
            if not (bb[0] < c[0] < bb[2] and bb[1] < c[1] < bb[3]): continue
            g = prj(shape(f['geometry']))
            if not g.is_valid: g = g.buffer(0)
            p = f['properties']
            ex.append((g, fn.replace('pastforward_2026_', ''), p, year(p.get('born'))))
    tree = STRtree([e[0] for e in ex])
    out, rep = [], {'dup': [], 'probable': [], 'replaced': [], 'review': [], 'kept': 0}
    for f in new:
        p = f['properties']; g = prj(shape(f['geometry'])); a = g.area; cen = g.centroid
        label = f"{p['id']} ({p['type']}, {a:.0f} m², {p['note'] or p['detail'] or '-'})"
        dup = None; later = []; probable = None; near = None
        for i in tree.query(g.buffer(50)):
            eg, src, ep, by = ex[i]; ov = g.intersection(eg).area / a; d = cen.distance(eg.centroid)
            desc = f"{ep.get('name') or ep.get('address') or ep.get('pf_uid','?')[:8]} [{src}, born {ep.get('born')}, {ep.get('born_basis')}]"
            if ov > 0.25:
                if by <= EARLY: dup = dup or (desc, ov)
                else: later.append((by, ep.get('born'), desc, ov))
            elif by <= EARLY:
                if d <= 12: probable = probable or (desc, d)
                elif d <= 50: near = near or (desc, d)
        if dup: rep['dup'].append(f"{label} overlaps {dup[0]} ({dup[1]:.0%} of it)"); continue
        if probable: rep['probable'].append(f"{label} is {probable[1]:.0f} m from {probable[0]}"); continue
        died = None
        if later:
            later.sort(); died = later[0][1]
            rep['replaced'].append(f"{label} overlaps later building(s): " + "; ".join(f"{l[2]} ({l[3]:.0%})" for l in later) + f" → died {died}")
        if near: rep['review'].append(f"{label} is {near[1]:.0f} m from early {near[0]}")
        name = None
        if p['legend_no'] and p['note']:
            name = p['note'].split(' ', 1)[1] if p['note'][:1].isdigit() and ' ' in p['note'] else p['note']
            name = name.split(' (')[0]
        uid = str(uuid.uuid5(NS, p['id']))
        props = {"id": 'stb1880-' + p['id'], "uid": uid, "pf_uid": uid, "material": MAT.get(p['material'], 'wood'),
                 "floors": p['floors'], "roof_type": ROOF.get(p['roof'], 'gabled'), "born": "1880-01-01", "born_low": "1700", "born_high": "1880",
                 "born_basis": "bird's-eye view 1880 (present by then; build date unknown)", "cohort": "stb1880",
                 "source_file": "stb1880_buildings.geojson — Stoner 1880 bird's-eye view of St Boniface, traced by Mike", "group": "import_stb1880_20261004",
                 "footprint_source": "bird's-eye view, approximate", "building_type": p['type'],
                 "notes": "; ".join(x for x in (f"confidence {p['confidence']}", p['note'], p['detail'], (p['material_basis'] or '')) if x)}
        if name: props["name"] = name
        if died: props["died"] = died; props["died_basis"] = "replaced by a later building on the same footprint"
        else: props["died_basis"] = "unknown (not in later sources)"
        out.append({"type": "Feature", "properties": props, "geometry": f['geometry']})
        rep['kept'] += 1
    json.dump({"type": "FeatureCollection", "name": "pastforward_2026_stb1880", "features": out}, open(os.path.join(DATA, 'pastforward_2026_stb1880.geojson'), 'w'))
    lines = [f"Stoner 1880 St Boniface buildings: {len(new)} in, {rep['kept']} added, {len(rep['dup'])} duplicates dropped, {len(rep['probable'])} probable duplicates dropped"]
    for k, t in (('dup', 'DUPLICATES (overlap an existing building born <= 1890) — dropped'), ('probable', 'PROBABLE DUPLICATES (centre within 12 m of an existing early building) — dropped'),
                 ('replaced', 'REPLACED (an existing LATER building stands on the footprint) — kept, died set'), ('review', 'NEAR (within 50 m of an early building) — kept, for review')):
        lines += ['', f'{t}: {len(rep[k])}'] + ['  ' + x for x in rep[k]]
    open(os.path.join(HERE, 'sources', 'stb1880_ingest_report.txt'), 'w').write('\n'.join(lines))
    print('\n'.join(lines))
if __name__ == '__main__': main()
