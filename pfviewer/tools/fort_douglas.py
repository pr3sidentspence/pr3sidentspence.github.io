#!/usr/bin/env python3
"""
fort_douglas.py — PLACEHOLDER footprints for Fort Douglas (Selkirk settlers' fort, 1813-15), as
data/pastforward_2026_fort_douglas.geojson. No footprints were found anywhere in the data or in Planimetro's files,
so the plan below is invented from the history:

  built 1813-15 by the Selkirk settlers; Hudson's Bay Company-associated post and the Governor's residence; captured
  1816 (Seven Oaks / Pemmican War) and retaken; mostly destroyed by the 1826 flood; final remnants washed away 1852.
  Site (Mike): the NW corner of the junction of the Red River and the creek at the southern base of Point Douglas
  (Logan's Creek) — the Fort Douglas cairn stands by the foot of Alexander Ave.

Layout (all guesses): a ~45 x 35 m log palisade turned 15 deg to follow the river bank, the Governor's house, a barracks
and a store inside. Everything dies in the 1826 flood except the barracks (a remnant) until 1852.
Replace with real footprints when there are some.
"""
import json, math, os, uuid
HERE = os.path.dirname(os.path.abspath(__file__))
M_LON, M_LAT = 71600.0, 111320.0
CEN = (-97.13150, 49.90015)       # lon, lat — downstream (north) of Logan's Creek, on the west bank (the creek mouth is at -97.13103, 49.89930)
ROT = math.radians(15)
NS = uuid.UUID('6f1d0c1e-5b7a-4d0e-9a53-0f0718130001')
def pt(x, y):                      # local metres (east, north) → lon/lat, turned by ROT
    xr, yr = x * math.cos(ROT) + y * math.sin(ROT), -x * math.sin(ROT) + y * math.cos(ROT)
    return [round(CEN[0] + xr / M_LON, 7), round(CEN[1] + yr / M_LAT, 7)]
def rect(cx, cy, w, d):
    return [pt(cx - w / 2, cy - d / 2), pt(cx + w / 2, cy - d / 2), pt(cx + w / 2, cy + d / 2), pt(cx - w / 2, cy + d / 2)]
def feat(name, props, geom):
    uid = str(uuid.uuid5(NS, name))
    p = {"id": name, "uid": uid, "pf_uid": uid, "name": name, "cohort": "fort_douglas", "source_file": "generated: tools/fort_douglas.py — PLACEHOLDER footprints (no source plan found)",
         "notes": "Placeholder: the layout is invented; location per Mike (NW corner of the Red River / Logan's Creek junction)."}
    p.update(props); return {"type": "Feature", "properties": p, "geometry": geom}
def main():
    FLOOD, GONE = "1826-05-20", "1852-01-01"
    pal = rect(0, 0, 45, 35); pal.append(pal[0])
    feats = [
      feat("Fort Douglas stockade", {"type": "fence", "material": "wood", "fence_height": 3.0, "fence_gap": 0.03, "fence_width": 0.22, "fence_thickness": 0.12, "fence_color": "#6B5A44",
           "born": "1813-09-01", "died": FLOOD, "died_basis": "1826 flood"}, {"type": "LineString", "coordinates": pal}),
      feat("Fort Douglas — Governor's house", {"material": "log", "floors": 1.5, "roof_type": "gabled", "born": "1815-06-01", "construction_months": 24, "died": FLOOD, "died_basis": "1826 flood"},
           {"type": "Polygon", "coordinates": [rect(-5, 9, 18, 9) + [rect(-5, 9, 18, 9)[0]]]}),
      feat("Fort Douglas — barracks", {"material": "log", "floors": 1, "roof_type": "gabled", "born": "1814-06-01", "construction_months": 12, "died": GONE, "died_basis": "remnant washed away 1852"},
           {"type": "Polygon", "coordinates": [rect(-3, -9, 22, 7) + [rect(-3, -9, 22, 7)[0]]]}),
      feat("Fort Douglas — store", {"material": "log", "floors": 1, "roof_type": "gabled", "born": "1814-09-01", "construction_months": 8, "died": FLOOD, "died_basis": "1826 flood"},
           {"type": "Polygon", "coordinates": [rect(14, 1, 9, 12) + [rect(14, 1, 9, 12)[0]]]}),
    ]
    out = os.path.join(HERE, '..', 'data', 'pastforward_2026_fort_douglas.geojson')
    json.dump({"type": "FeatureCollection", "features": feats}, open(out, 'w'))
    print('wrote', out)
if __name__ == '__main__': main()
