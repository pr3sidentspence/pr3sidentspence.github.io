"""clear_forks.py — the Forks: everything not still standing is gone the year before the site opened to the public.

    ~/.venvs/pfgis/bin/python tools/clear_forks.py [--apply]

Mike, 2026-10-23: remove the non-extant buildings at the Forks as of the year before it opened as a public place (the
Forks Market and the first public spaces opened 1989; the CN East Yards tracks went in 1988, data/rail_history.json).
Area: OSM's 'The Forks National Historic Site' (way/14870831, in ~/gisdata/ufg/ufg_osm.json) plus BUFFER_M. Every
pfviewer piece there standing past CLEARED gets died = CLEARED, except the ones mostly (KEEP_SHARE) under an OSM
building in KEEP_OSM — the ones that are still there. The Inn at the Forks, the CMHR, the Agowiidiwinan Centre etc. are
new buildings on old sites, so lying under them doesn't count. Written to data/building_history.json (died_basis
site_cleared); re-running redoes its own entries."""
import sys, os, json, math, glob
from shapely.geometry import shape, Polygon
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
OLD_FILES = ['pastforward_2026_assessment.geojson', 'pastforward_2026_osm.geojson', 'pastforward_2026_mcphillips1910.geojson',
             'pastforward_2026_stb1880.geojson', 'pastforward_2026_legislature_osm.geojson', 'pastforward_2026_ogilvie_stack.geojson',
             'pastforward_2026_additions.geojson', 'pastforward_2026_ufg_walls.geojson', 'pastforward_2026_fort_douglas.geojson']   # as clear_downtown_houses.py
CLEARED, BUFFER_M, KEEP_SHARE = '1988-07-01', 15, 0.45
KEEP_OSM = {"Children's Museum": 'the B&B building (1889 CNR engine repair shop), now the Manitoba Children\'s Museum',
            'Johnston Terminal': 'the 1928 cold storage warehouse', 'The Forks Market': 'the GTP and CN stables (1909–1911)'}
TAG, NOTE = 'tools/clear_forks.py', 'Cleared with the CN East Yards before the Forks opened (tools/clear_forks.py).'
K = math.cos(math.radians(49.888)) * 111320
O = {o['id']: o for o in json.load(open(os.path.expanduser('~/gisdata/ufg/ufg_osm.json')))}
area = Polygon(O['way/14870831']['pts']).buffer(BUFFER_M / K)
keep = []
for l in open(os.path.expanduser('~/gisdata/osm/wpg40_buildings.ndjson')):
    if '"name"' not in l or '-97.1' not in l: continue
    f = json.loads(l)
    if f['p'].get('name') in KEEP_OSM: keep.append((f['p']['name'], shape({'type': 'MultiPolygon', 'coordinates': f['g']})))
hist = json.load(open(os.path.join(DATA, 'building_history.json'))); H = hist['buildings']
out, kept = {}, []
for fn in OLD_FILES:
    pth = os.path.join(DATA, fn)
    if not os.path.exists(pth): continue
    for x in json.load(open(pth))['features']:
        p = x['properties']; uid = p.get('uid') or p.get('pf_uid') or p.get('id')
        try: g = shape(x['geometry'])
        except Exception: continue
        if not uid or g.is_empty or not g.intersects(area): continue
        h = H.get(uid, {}); s = h.get('set', {})
        if h.get('remove'): continue
        mine = TAG in json.dumps(h.get('sources', []))
        died = None if mine else s.get('died', p.get('died'))
        if died and died < CLEARED: continue
        name = h.get('name') or p.get('name') or ''
        if p.get('type') == 'bridge' or 'bridge' in name.lower(): kept.append((uid, name, 'a bridge (the rail bridge is the Historic Rail Bridge now)', 1)); continue
        under = [(g.intersection(kg).area / g.area if g.area else (1 if g.intersects(kg) else 0), kn) for kn, kg in keep if kg.intersects(g)]
        share, kn = max(under or [(0, None)])
        if share >= KEEP_SHARE: kept.append((uid, name, kn, share)); continue
        out[uid] = (name, died)
print(len(out), 'cleared;', len(kept), 'kept')
for k in kept: print('  kept', k[0][:8], k[1], '→', k[2], round(k[3], 2))
if '--apply' in sys.argv:
    for uid, (name, was) in out.items():
        e = H.setdefault(uid, {})
        e['sources'] = [x for x in e.get('sources', []) if TAG not in x] + [f'{TAG} (Mike, 2026-10-23: the Forks cleared the year before it opened to the public, 1989)' + (f'; was died {was}' if was else '')]
        e['notes'] = ((e.get('notes', '').replace(NOTE, '').strip() + ' ') + NOTE).strip()
        s = e.setdefault('set', {})
        s.update(died=CLEARED, died_basis='site_cleared'); s.setdefault('date_precision', {})['died'] = 'year'
        for k in ('died_low', 'died_high', 'replaced_by'): s.pop(k, None)
    for uid, *_ in kept:   # an earlier run's entry for one that's kept now: undo it
        e = H.get(uid)
        if e and TAG in json.dumps(e.get('sources', [])):
            e['sources'] = [x for x in e['sources'] if TAG not in x]; e['notes'] = e.get('notes', '').replace(NOTE, '').strip()
            for k in ('died', 'died_basis'): e.get('set', {}).pop(k, None)
    json.dump(hist, open(os.path.join(DATA, 'building_history.json'), 'w'), indent=1, ensure_ascii=False)
    print('written', len(out))
