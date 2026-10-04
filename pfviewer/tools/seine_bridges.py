#!/usr/bin/env python3
"""
seine_bridges.py — timber bridges where Provencher, the railway and Marion cross the Seine, as bridge polygons
for the viewer's existing bridge system (data/pastforward_2026_seine_bridges.geojson, listed in CONFIG autoload).

The LiDAR channel of the Seine is cut by the bridge decks at these places (the viewer carves it open again:
CONFIG.terrain.riverGaps). Each polygon is centred on the gap, its long axis along the street/rail that crosses,
length = span, short side = deck width.

Dates (Mike): Provencher at the Seine "at least as far back as 1880" — the 1880s bird's-eye view draws a
substantial timber bridge there (it may be older). Marion: guess 1880. Railway: the Canadian Northern line east
(tools/date_rails.py: cnor_east, 1902 — a low-confidence identification).
"""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
M_LON = 111320 * math.cos(49.895 * math.pi / 180); M_LAT = 111320.0

# name, street (or None for the rail), centre lon/lat (the middle of the gap), span m, deck width m, born, died, notes
BRIDGES = [
  ("Provencher Bridge over the Seine", "Provencher", (-97.10979, 49.89580), 40, 12, "1880-01-01", None,
   "Timber trestle, drawn as a substantial bridge on the 1880s bird's-eye view of St Boniface (built by 1880 at the latest)."),
  ("Marion Street Bridge over the Seine", "Marion", (-97.10442, 49.88273), 28, 10, "1880-01-01", None,
   "Date a guess."),
  ("Railway bridge over the Seine", None, (-97.10414, 49.89020), 30, 6, "1902-01-01", None,
   "Canadian Northern line east (tools/date_rails.py cnor_east, 1902; low-confidence identification)."),
  # The Canadian Northern mainline over the Red River, Mill St (west) to Rue Davreau (east) — Mike. Built with the line (1901-02).
  # Centred on where the schematic link (rail_history extra 1003) crosses the Red; bearing 69.5° (the link's); bridge_fit trims the ends to the banks.
  ("Canadian Northern Railway Bridge (Red River)", 69.5, (-97.13089, 49.89570), 270, 7, "1902-01-01", None,
   "Steel through truss carrying the CNoR mainline over the Red; Mike places it from near Mill St to Rue Davreau; the date follows the line (1902); the exact crossing is schematic.",
   {"material": "iron", "bridge_style": "truss", "bridge_fit": True}),
]

def street_nearest(name, lon, lat):
    g = json.load(open(os.path.join(HERE, '..', 'data', 'wpg_roads_streetcar.geojson')))
    best = (1e9, 0.0, None)
    for f in g['features']:
        if f['properties']['st_name'] != name: continue
        for l in f['geometry']['coordinates']:
            for j in range(len(l) - 1):
                ax, ay = (l[j][0] - lon) * M_LON, (l[j][1] - lat) * M_LAT
                bx, by = (l[j + 1][0] - lon) * M_LON, (l[j + 1][1] - lat) * M_LAT
                dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1
                t = max(0, min(1, -(ax * dx + ay * dy) / L2)); d = math.hypot(ax + dx * t, ay + dy * t)
                if d < best[0]: best = (d, math.atan2(dx, dy), (lon + (ax + dx * t) / M_LON, lat + (ay + dy * t) / M_LAT))
    return best[1], best[0], best[2]

def rail_nearest(lon, lat):
    g = json.load(open(os.path.join(HERE, '..', 'data', 'wpg_rails_1906.geojson')))
    best = (1e9, 0.0, None)
    for f in g['features']:
        c = f['geometry']['coordinates']
        for l in (c if f['geometry']['type'] == 'MultiLineString' else [c]):
            for j in range(len(l) - 1):
                ax, ay = (l[j][0] - lon) * M_LON, (l[j][1] - lat) * M_LAT
                bx, by = (l[j + 1][0] - lon) * M_LON, (l[j + 1][1] - lat) * M_LAT
                dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1
                t = max(0, min(1, -(ax * dx + ay * dy) / L2)); d = math.hypot(ax + dx * t, ay + dy * t)
                if d < best[0]: best = (d, math.atan2(dx, dy), (lon + (ax + dx * t) / M_LON, lat + (ay + dy * t) / M_LAT))
    return best[1], best[0], best[2]

def main():
    feats = []
    for entry in BRIDGES:
        name, street, (lon, lat), L, W, born, died, note = entry[:8]; over = entry[8] if len(entry) > 8 else {}
        if isinstance(street, (int, float)): brg, d = math.radians(street), 0.0     # explicit bearing; centre as given
        else: brg, d, (lon, lat) = (street_nearest(street, lon, lat) if street else rail_nearest(lon, lat))   # centre the deck where the street/rail crosses the channel
        ue, un = math.sin(brg), math.cos(brg)          # along the span (east, north)
        ve, vn = -un, ue                               # across
        ring = []
        for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            e = ue * su * L / 2 + ve * sv * W / 2; n = un * su * L / 2 + vn * sv * W / 2
            ring.append([round(lon + e / M_LON, 7), round(lat + n / M_LAT, 7)])
        ring.append(ring[0])
        props = {"id": name, "uid": name, "pf_uid": name, "name": name, "type": "bridge", "material": "wood", "bridge_style": "trestle",
                 "floors": 1, "born": born, "born_basis": "estimated", "source_file": "generated: tools/seine_bridges.py", "notes": note, "cohort": "bridges"}
        props.update(over)
        if died: props["died"] = died
        feats.append({"type": "Feature", "properties": props, "geometry": {"type": "Polygon", "coordinates": [ring]}})
        print(f'{name}: axis {math.degrees(brg) % 180:.0f}° (street/rail {d:.0f} m from the gap, deck centred on it at {lon:.5f}, {lat:.5f})')
    out = os.path.join(HERE, '..', 'data', 'pastforward_2026_seine_bridges.geojson')
    json.dump({"type": "FeatureCollection", "features": feats}, open(out, 'w'))
    print('wrote', out)
if __name__ == '__main__': main()
