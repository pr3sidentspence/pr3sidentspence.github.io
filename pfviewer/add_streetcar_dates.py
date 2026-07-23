#!/usr/bin/env python3
"""
Adds `streetcar_start` (and `streetcar_type`) properties to every road feature
in data/wpg_roads.geojson, based on a segment-level table of streetcar route
extensions (by cross street, not whole-street) supplied by the project owner.

Reads:  data/wpg_roads.geojson              (untouched)
        data/wpg_rivers.geojson             (only for river-crossing endpoints)
Writes: data/wpg_roads_streetcar.geojson    (new file)

Why graph search, not address ranges: wpg_roads.geojson has no address-number
mapping to cross streets, so "Selkirk from Salter to Arlington" can only be
resolved geometrically. For each entry below, we build a small graph of the
target street's own segments (nodes = intersections, found by clustering
segment endpoints that land within NODE_TOL metres of each other), locate the
node nearest the "from" and "to" cross street's geometry, then walk the
shortest path between them along the target street's own segments. Every
original feature on that path gets tagged with the entry's year. Where a
street is tagged by more than one entry (extensions built at different
times), each segment keeps the EARLIEST year that covers it.

Known simplifications (see ROUTES below for details):
  - Two entries have no resolvable cross street at all (Johnson Ave's
    "Norse"/actual routing involves a since-removed connector + a detour via
    Grey St. that this dataset can't represent) and one multi-street chain
    (Pioneer-Westbrook-Stephenson-Provencher) — these are tagged as
    whole-street fallbacks rather than precise sub-ranges.
  - "Assiniboine River" endpoints resolve against the river polygon in
    wpg_rivers.geojson (identified by bounding box — the only two unnamed
    water features are disambiguated by position; see ASSINIBOINE_BBOX_HINT).
"""

import json
import math
from pathlib import Path
from collections import defaultdict, deque

SCRIPT_DIR = Path(__file__).resolve().parent
ROADS_PATH = SCRIPT_DIR / 'data' / 'wpg_roads.geojson'
RIVERS_PATH = SCRIPT_DIR / 'data' / 'wpg_rivers.geojson'
OUTPUT_PATH = SCRIPT_DIR / 'data' / 'wpg_roads_streetcar.geojson'

# Same equirectangular projection used in index.html — must match so distances
# here are in the same metres the 3D scene uses.
C_LON, C_LAT = -97.135515, 49.895396
COS_LAT = math.cos(C_LAT * math.pi / 180)
M_PER_LON = 111320 * COS_LAT
M_PER_LAT = 111320


def project(lon, lat):
    return ((lon - C_LON) * M_PER_LON, (lat - C_LAT) * M_PER_LAT)


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# ── Special reference markers ───────────────────────────────────────────────
class River:
    """Marks a cross-reference that should resolve against a river polygon."""
    def __init__(self, name):
        self.name = name


ASSINIBOINE_RIVER = River('Assiniboine River')
RED_RIVER = River('Red River')  # NOT the street named "Red River" (a real but unrelated
                                # street 8.6km away) — "from Red River" always means the
                                # actual river here (Osborne/Marion both start near it)

# ── Route table ─────────────────────────────────────────────────────────────
# (street, from_ref, to_ref, year) — from_ref/to_ref are cross-street names
# (matched against st_name), a River() marker, or None for "open end" (extend
# to the far side of the network from the other given end).
#
# Corrections applied per project-owner review of the original transcription:
#   Nena -> was renamed Sherbrook (extends Sherbrook south past Notre Dame)
#   Higgens -> Higgins (data spelling)
#   Norse -> unresolvable; Johnson Ave tagged whole-street instead (see note)
#   Valor -> Valour
#   Stockyards -> Archibald
#   St. Norbert / "Perimeter Hwy" -> resolved against the Perimeter road,
#     which sits at the same location per the owner ("St. Norbert begins at
#     the Perimeter highway") even though Perimeter Hwy itself postdates the
#     streetcar era — it's just being used as a location reference.
ROUTES = [
    ("Academy", ASSINIBOINE_RIVER, "Stafford", 1903),
    ("Academy", "Stafford", "Guelph", 1912),
    ("Academy", "Guelph", "Charleswood", 1913),  # via Assiniboine Park — same year either side, one hop is enough

    ("Arlington", "Portage", "Notre Dame", 1907),
    ("Arlington", "Notre Dame", "Logan", 1912),
    ("Arlington", "Dufferin", "Mountain", 1914),

    ("Bannerman", "Main", "McGregor", 1907),

    ("Broadway", "Main", "Osborne", 1892),
    ("Broadway", "Osborne", "Sherbrook", 1912),

    ("Churchill", "Jubilee", "Osborne", 1901),

    ("Corydon", "Osborne", "Stafford", 1908),
    ("Corydon", "Stafford", "Guelph", 1928),

    ("Des Meurons", "Marion", "Provencher", 1912),

    ("Donald", "Broadway", "Ellice", 1912),

    ("Dufferin", "Main", "Arlington", 1903),

    ("Ellice", "Notre Dame", "Sherbrook", 1911),  # via Kennedy — same year both hops

    ("Higgins", "Main", "Sutherland", 1896),
    ("Higgins", "Main", "Princess", 1912),
    ("Higgins", "Sutherland", "Talbot", 1907),

    ("Henderson", "Talbot", "Linden", 1903),

    ("Hespeler", "Henderson", "Glenwood", 1908),

    # Johnson Ave: owner isn't sure of the historical cross-street ("Norse"?),
    # and describes a routing (Johnson W/E once joined near where Chalmers
    # Park now is, then continuing via Grey St. to Munroe Ave) this road
    # network can't represent (the connector no longer exists; the detour
    # runs via a different named street). Tagging the whole street rather
    # than guessing a wrong precise boundary.
    ("Johnson", None, None, 1914),

    ("Jubilee", "Pembina", "Churchill", 1913),

    ("Kennedy", "Broadway", "Portage", 1884),

    ("Logan", "Main", "Sherbrook", 1893),   # was "Nena" — Nena was renamed Sherbrook
    ("Logan", "Sherbrook", "Arlington", 1905),
    ("Logan", "Arlington", "McPhillips", 1906),
    ("Logan", "McPhillips", "Keewatin", 1908),
    ("Sherbrook", "Notre Dame", "Logan", 1893),   # was "Nena from Notre Dame to Logan" — same rename

    ("Main", "Assiniboine", "William", 1882),
    ("Main", "William", "Higgins", 1883),
    ("Main", "Higgins", "Sutherland", 1884),
    ("Main", "Sutherland", "Hespeler", 1892),
    ("Main", "Hespeler", "Jefferson", 1893),   # owner: "maybe out to Stonewall, MB" — Jefferson is the resolvable extent
    ("Main", "Assiniboine", "Marion", 1904),   # crosses into St. Boniface

    ("Marion", RED_RIVER, "Tache", 1903),
    ("Marion", "Tache", "Des Meurons", 1910),
    ("Marion", "Des Meurons", "Archibald", 1915),  # was "Stockyards"

    ("McGregor", "Selkirk", "Luxton", 1907),

    ("McPhillips", "Logan", "Selkirk", 1911),

    ("Mountain", "Main", "McGregor", 1913),
    ("Mountain", "McGregor", "Arlington", 1914),

    ("Notre Dame", "Portage", "Sherbrook", 1893),
    ("Notre Dame", "Sherbrook", "Arlington", 1910),
    ("Notre Dame", "Arlington", "Midland", 1910),   # "1910 to 1923" — tag from the earlier date; see note below

    ("Osborne", RED_RIVER, "Corydon", 1891),
    ("Osborne", "Corydon", ASSINIBOINE_RIVER, 1899),
    ("Osborne", ASSINIBOINE_RIVER, "Broadway", 1893),
    ("Osborne", "Broadway", "Portage", 1926),

    ("Pembina", "Corydon", "Grant", 1906),
    ("Pembina", "Jubilee", "Perimeter", 1906),   # "to St. Norbert" — St. Norbert begins at the Perimeter Hwy per owner

    ("Pioneer", None, None, 1925),
    ("Westbrook", None, None, 1925),
    ("William Stephenson", None, None, 1925),
    # "Provencher Bridge" isn't a distinct mapped road (it's the river
    # crossing itself) — Provencher gets the 1925 tag as a whole-street
    # fallback too, but its own more specific entries below (1903/1912) will
    # still win for the segments they cover (earliest-year-wins merge).
    ("Provencher", None, None, 1925),

    ("Portage", "Main", "Donald", 1882),
    ("Portage", "Donald", "Kennedy", 1883),
    ("Portage", "Kennedy", "Sherbrook", 1893),
    ("Portage", "Sherbrook", "Perimeter", 1902),

    ("Princess", "Ellice", "Higgins", 1912),

    ("Provencher", "Tache", "Des Meurons", 1903),

    ("Redwood", "Main", "Hespeler", 1909),   # "Glenwood/Hespeler" — Hespeler is the resolvable name

    ("Sargent", "Sherbrook", "Arlington", 1909),
    ("Sargent", "Kennedy", "Sherbrook", 1911),
    ("Sargent", "Arlington", "Valour", 1918),   # was "Valor"

    ("Selkirk", "Main", "Arlington", 1892),

    ("Sherbrook", "Portage", "Cornish", 1897),
    ("Sherbrook", "Portage", "Notre Dame", 1899),

    ("Stafford", "Academy", "Corydon", 1907),
    ("Stafford", "Corydon", "Grant", 1929),

    ("St Anne's", "St Mary's", "Hindley", 1913),

    ("St Mary's", "Tache", "Berrydale", 1913),

    ("Sutherland", "Main", "Annabella", 1908),
    ("Sutherland", "Annabella", None, 1908),   # "from Annabella" (open end) — continues on past Annabella the same year

    ("Tache", "Provencher", "Marion", 1903),
    ("Tache", "Marion", "St Mary's", 1913),

    ("Talbot", "Stadacona", "Elmwood", 1907),
    ("Talbot", "Stadacona", "Henderson", 1913),

    ("William", "Main", "Arlington", 1894),
]

# ── Load data ────────────────────────────────────────────────────────────────
roads = json.load(open(ROADS_PATH, encoding='utf-8'))
rivers = json.load(open(RIVERS_PATH, encoding='utf-8'))

by_name = defaultdict(list)  # st_name -> [{'idx', 'pts', 'length'}]
for idx, f in enumerate(roads['features']):
    name = f['properties'].get('st_name')
    if not name:
        continue
    line = f['geometry']['coordinates'][0]
    pts = [project(lon, lat) for lon, lat in line]
    length = sum(dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
    by_name[name].append({'idx': idx, 'pts': pts, 'length': length})

# Identify the Assiniboine River polygon among wpg_rivers.geojson's features.
# Two of the four water features have no `name` property; disambiguated by
# bounding box — the Assiniboine's is west and south of the C_LON/C_LAT
# reference point (downtown/The Forks), the other unnamed one (Brown's Creek)
# is east and north of it. See exploration notes in the session — verified
# against known geography, not guessed blindly.
def river_points(predicate):
    pts = []
    for f in rivers['features']:
        if not predicate(f):
            continue
        ring = f['geometry']['coordinates'][0]
        pts.extend(project(lon, lat) for lon, lat in ring)
    return pts


def _is_assiniboine(f):
    if f['properties'].get('name') == 'Assiniboine River':
        return True
    if f['properties'].get('name') is not None:
        return False
    ring = f['geometry']['coordinates'][0]
    lons = [p[0] for p in ring]
    lats = [p[1] for p in ring]
    cx, cy = (min(lons) + max(lons)) / 2, (min(lats) + max(lats)) / 2
    return cx < C_LON and cy < C_LAT


ASSINIBOINE_PTS = river_points(_is_assiniboine)
RED_RIVER_PTS = river_points(lambda f: f['properties'].get('name') == 'Red River')

NODE_TOL = 6.0        # metres — endpoints within this are "the same intersection"
BRIDGE_TOL = 250.0    # metres — gaps up to this within ONE street's own segments get
                      # bridged (no ambiguity risk merging a street with itself; the
                      # existing JS route-stitcher already tolerates ~80m gaps this way)
WARN_DIST = 150.0     # metres — nearest-node match to a DIFFERENT street beyond this is suspicious
REJECT_DIST = 1000.0  # metres — beyond this it's not "imprecise", it's the wrong place; don't apply it


class Graph:
    """One target street's own segments as a small intersection graph."""
    def __init__(self, street_name):
        self.segs = by_name.get(street_name, [])
        self.node_pts = []          # node id -> representative (x,z)
        self.edges = []             # {seg, a, b, length} — seg is None for bridge edges
        self.adj = defaultdict(list)  # node id -> [(neighbor_node, edge_index)]
        for seg in self.segs:
            a = self._find_or_add(seg['pts'][0])
            b = self._find_or_add(seg['pts'][-1])
            self._add_edge(a, b, seg['length'], seg)
        self._bridge_components()

    def _add_edge(self, a, b, length, seg):
        ei = len(self.edges)
        self.edges.append({'seg': seg, 'a': a, 'b': b, 'length': length})
        self.adj[a].append((b, ei))
        self.adj[b].append((a, ei))

    def _find_or_add(self, pt):
        for i, n in enumerate(self.node_pts):
            if dist(n, pt) <= NODE_TOL:
                return i
        self.node_pts.append(pt)
        return len(self.node_pts) - 1

    def _components(self):
        seen, comps = set(), []
        for n in range(len(self.node_pts)):
            if n in seen:
                continue
            comp, q = set(), deque([n])
            while q:
                u = q.popleft()
                if u in comp:
                    continue
                comp.add(u); seen.add(u)
                for v, _ in self.adj[u]:
                    q.append(v)
            comps.append(comp)
        return comps

    def _bridge_components(self):
        """Connects nearby disconnected pieces of this SAME street with
        virtual (seg=None) edges — bridges digitizing gaps up to BRIDGE_TOL.
        No ambiguity risk since we're only ever reconnecting a street to
        itself, unlike cross-street matching (see nearest_node/WARN_DIST)."""
        while True:
            comps = sorted(self._components(), key=len, reverse=True)
            if len(comps) <= 1:
                return
            big = comps[0]
            best = None  # (dist, node_in_big, node_in_other)
            for other in comps[1:]:
                for i in other:
                    for j in big:
                        d = dist(self.node_pts[i], self.node_pts[j])
                        if best is None or d < best[0]:
                            best = (d, j, i)
            if best is None or best[0] > BRIDGE_TOL:
                return  # remaining components too far apart — leave disconnected
            d, j, i = best
            self._add_edge(j, i, d, None)

    def nearest_node(self, ref_pts):
        if not self.node_pts or not ref_pts:
            return None, math.inf
        best_i, best_d = None, math.inf
        for i, n in enumerate(self.node_pts):
            for p in ref_pts:
                d = dist(n, p)
                if d < best_d:
                    best_d, best_i = d, i
        return best_i, best_d

    def bfs(self, start):
        """Returns {node: (dist_from_start, prev_node, prev_edge)}."""
        dist_map = {start: (0.0, None, None)}
        q = deque([start])
        while q:
            u = q.popleft()
            du = dist_map[u][0]
            for v, ei in self.adj[u]:
                nd = du + self.edges[ei]['length']
                if v not in dist_map or nd < dist_map[v][0]:
                    dist_map[v] = (nd, u, ei)
                    q.append(v)
        return dist_map

    def shortest_path_edges(self, node_a, node_b):
        dist_map = self.bfs(node_a)
        if node_b not in dist_map:
            return None
        edges = []
        cur = node_b
        while cur != node_a:
            _, prev, ei = dist_map[cur]
            edges.append(ei)
            cur = prev
        return edges

    def farthest_node(self, from_node):
        dist_map = self.bfs(from_node)
        return max(dist_map.items(), key=lambda kv: kv[1][0])[0]


RIVER_PTS = {'Assiniboine River': ASSINIBOINE_PTS, 'Red River': RED_RIVER_PTS}


def ref_points(ref):
    if ref is None:
        return None
    if isinstance(ref, River):
        return RIVER_PTS[ref.name]
    segs = by_name.get(ref)
    if not segs:
        return []
    pts = []
    for s in segs:
        pts.extend(s['pts'])
    return pts


def ref_label(ref):
    if ref is None:
        return '<open end>'
    if isinstance(ref, River):
        return ref.name
    return ref


feature_year = {}   # feature idx -> year (min across all covering entries)
warnings = []

for street, from_ref, to_ref, year in ROUTES:
    g = Graph(street)
    if not g.segs:
        warnings.append(f'"{street}" has no segments in wpg_roads.geojson at all — entry skipped ({from_ref!r} -> {to_ref!r}: {year})')
        continue

    if from_ref is None and to_ref is None:
        # Whole-street fallback.
        edge_idxs = list(range(len(g.edges)))
    else:
        from_pts = ref_points(from_ref)
        to_pts = ref_points(to_ref)
        node_a = node_b = None
        if from_pts:
            node_a, d_a = g.nearest_node(from_pts)
            if d_a > REJECT_DIST:
                warnings.append(f'{street} <-> {ref_label(from_ref)}: nearest match {d_a:.0f}m apart (year {year}) — too far, treating as unresolved (falling back to far end of the street)')
                node_a = None
            elif d_a > WARN_DIST:
                warnings.append(f'{street} <-> {ref_label(from_ref)}: nearest match {d_a:.0f}m apart (year {year}) — accepted, but check this one')
        if to_pts:
            node_b, d_b = g.nearest_node(to_pts)
            if d_b > REJECT_DIST:
                warnings.append(f'{street} <-> {ref_label(to_ref)}: nearest match {d_b:.0f}m apart (year {year}) — too far, treating as unresolved (falling back to far end of the street)')
                node_b = None
            elif d_b > WARN_DIST:
                warnings.append(f'{street} <-> {ref_label(to_ref)}: nearest match {d_b:.0f}m apart (year {year}) — accepted, but check this one')

        if node_a is None and node_b is None:
            warnings.append(f'{street}: neither end ({ref_label(from_ref)!r} / {ref_label(to_ref)!r}) resolved — entry skipped (year {year})')
            continue
        if node_a is None:
            node_a = g.farthest_node(node_b)
        if node_b is None:
            node_b = g.farthest_node(node_a)

        edge_idxs = g.shortest_path_edges(node_a, node_b)
        if edge_idxs is None:
            warnings.append(f'{street}: no connected path between {ref_label(from_ref)!r} and {ref_label(to_ref)!r} (year {year}) — segments may be split by a digitizing gap; entry skipped')
            continue

    for ei in edge_idxs:
        seg = g.edges[ei]['seg']
        if seg is None:
            continue  # virtual bridge edge — connectivity aid only, not a real feature
        fidx = seg['idx']
        if fidx not in feature_year or year < feature_year[fidx]:
            feature_year[fidx] = year

# ── Write output ─────────────────────────────────────────────────────────────
matched = 0
for idx, feat in enumerate(roads['features']):
    year = feature_year.get(idx)
    feat['properties']['streetcar_start'] = year
    feat['properties']['streetcar_type'] = None if year is None else ('horsecar' if year < 1890 else 'electric')
    if year is not None:
        matched += 1

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(roads, f, ensure_ascii=False)

print(f'{matched}/{len(roads["features"])} features matched to a streetcar route.')
print(f'Wrote {OUTPUT_PATH}')
if warnings:
    print(f'\n{len(warnings)} warning(s):')
    for w in warnings:
        print(f'  - {w}')
