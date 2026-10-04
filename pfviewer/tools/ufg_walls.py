#!/usr/bin/env python3
"""
ufg_walls.py — two pieces Upper Fort Garry was missing, as data/pastforward_2026_ufg_walls.geojson:

 1. The gap in the original NE wall (between the north bastion's surviving 36 m of wall and the east bastion, ~54 m):
    a stone wall like the SEW wall (born 1837-06 over 24 months). It stands until the northern addition is complete —
    the addition wall is finished 1853-06-01 — and goes just after, 1853-08-01 (the same date the original north wall now ends).
 2. The "angled fence" that replaced it, 1853-08-01 to the fort's demolition (1881-01-01). Two pieces of it were already
    in the data (7ec45547, 267d371b — only dated 1880-81, with no height, so they barely showed); the link between them is
    this file's LineString, and building_history.json gives all three the same dates and a fence height.
Coordinates are metres east/north of lon -97.134, lat 49.8870, as measured from the existing UFG polygons.
"""
import json, math, os, uuid
HERE = os.path.dirname(os.path.abspath(__file__))
M_LON, M_LAT = 71600.0, 111320.0
ll = lambda x, y: [round(-97.134 + x / M_LON, 7), round(49.8870 + y / M_LAT, 7)]
NS = uuid.UUID('6f1d0c1e-5b7a-4d0e-9a53-0f0718530001')

def wall(a, b, t):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy); nx, ny = -dy / L * t / 2, dx / L * t / 2
    return [ll(a[0] + nx, a[1] + ny), ll(b[0] + nx, b[1] + ny), ll(b[0] - nx, b[1] - ny), ll(a[0] - nx, a[1] - ny)]

def feat(name, props, geom):
    uid = str(uuid.uuid5(NS, name))
    p = {"id": name, "uid": uid, "pf_uid": uid, "name": name, "source_file": "generated: tools/ufg_walls.py (Mike's request, 2026-10-04)", "cohort": "ufg"}
    p.update(props)
    return {"type": "Feature", "properties": p, "geometry": geom}

def main():
    ring = wall((21.0, 29.0), (55.5, -8.5), 2.2); ring.append(ring[0])
    feats = [
      feat("Upper Fort Garry Original NE Wall", {"material": "stone", "floors": 2, "born": "1837-06-01", "construction_months": 24, "died": "1853-08-01",
           "died_basis": "removed once the northern addition was complete (addition wall finished 1853-06-01)", "born_basis": "with the original stone walls",
           "notes": "Restored where the earlier data had a gap on the north-east wall."}, {"type": "Polygon", "coordinates": [ring]}),
      feat("Upper Fort Garry angled fence", {"type": "fence", "material": "wood", "floors": 0.45, "born": "1853-08-01", "died": "1881-01-01",
           "notes": "Joins the two fence pieces already in the data (7ec45547 and 267d371b)."},
           {"type": "LineString", "coordinates": [ll(42, -9), ll(21, 15)]}),
    ]
    out = os.path.join(HERE, '..', 'data', 'pastforward_2026_ufg_walls.geojson')
    json.dump({"type": "FeatureCollection", "features": feats}, open(out, 'w'))
    print('wrote', out)
if __name__ == '__main__': main()
