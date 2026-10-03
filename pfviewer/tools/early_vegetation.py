#!/usr/bin/env python3
"""
early_vegetation.py — tree stands and a trail traced from the 1819 plan
"Papers Relating to the Red River Settlement", Plate 3 (House of Commons, ordered
printed 12 July 1819; "Remarks from depositions in behalf of the Half Breeds").

Scale bar on the plate: 1500 yards to an inch (7500 yd = 805 px on the scan used,
so 8.57 m/px by the bar — but see below). North is toward the lower right (the plate's compass puts N 25° below
the +x axis). Fort Gibraltar (A) is taken to be at the Forks, lon -97.1320 lat 49.8890.
The plate's own scale bar and compass don't agree with the geography (it is a sketch made from
depositions): fitting A to the Forks and B (the 1816 affray, = Seven Oaks monument,
49.93206 -97.12109, MHS) gives 9.97 m/px and north 8° below the +x axis; with that the OSM Red River's
Point Douglas hairpin, the bend at Fort Douglas and the Assiniboine all overlay the plate's river
(checked visually). Everything is traced by eye: positions good to a few hundred metres.

Output: data/early_vegetation.json  {stands:[…], trails:[…]} — read by the viewer
(CONFIG.earlyVegetation.file). Tree counts are set by the viewer from `per1000m2`.
"""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
C_LON, C_LAT = -97.135515, 49.895396
M_LON = 111320 * math.cos(C_LAT * math.pi / 180); M_LAT = 111320.0
MPP, ROT = 9.97, 1.7137
A_PX, A_LL = (260, 1198), (-97.1320, 49.8890)

def _raw(lon, lat):
    x = (lon - C_LON) * M_LON / MPP; y = -(lat - C_LAT) * M_LAT / MPP
    c, s = math.cos(ROT), math.sin(ROT); return c * x - s * y, s * x + c * y
_ax, _ay = _raw(*A_LL); TX, TY = A_PX[0] - _ax, A_PX[1] - _ay
def ll(px, py):
    x, y = px - TX, py - TY; c, s = math.cos(-ROT), math.sin(-ROT)
    ux, uy = c * x - s * y, s * x + c * y
    return [round(C_LON + ux * MPP / M_LON, 6), round(C_LAT - uy * MPP / M_LAT, 6)]

SRC = "1819 'Papers relating to the Red River Settlement' Plate 3 (traced by eye)"
STANDS = [
  # the long wooded oval west-north-west of the Forks, labelled in the plate (a willow wood)
  dict(name="Large willow wood (1819 plate)", kind="willow", per1000m2=1.5, scale=[0.9, 1.4],
       px=[(248,1018),(251,993),(273,964),(294,936),(316,900),(341,864),(359,843),(380,818),(416,804),(451,793),(473,793),(476,804),(459,821),(437,843),(416,871),(394,896),(373,929),(355,957),(334,979),(309,1000),(284,1018),(259,1021)]),
  # tree glyphs along the Assiniboine's bank (poplar / cottonwood fringe of 1819)
  dict(name="Assiniboine bank woods A", kind="poplar", per1000m2=0.7, scale=[0.9, 1.3], px=[(195,630),(245,632),(245,658),(195,658)]),
  dict(name="Assiniboine bank woods B", kind="poplar", per1000m2=0.7, scale=[0.9, 1.3], px=[(180,680),(210,682),(212,740),(182,738)]),
  dict(name="Assiniboine bank woods C", kind="poplar", per1000m2=0.7, scale=[0.9, 1.3], px=[(205,742),(262,745),(262,796),(205,796)]),
  dict(name="Assiniboine bank woods D", kind="poplar", per1000m2=0.7, scale=[0.9, 1.3], px=[(130,815),(218,820),(220,875),(130,872)]),
  dict(name="Assiniboine bank woods E", kind="poplar", per1000m2=0.7, scale=[0.9, 1.3], px=[(188,920),(222,922),(222,1030),(190,1030)]),
]
# the seven oaks of Seven Oaks (plate: "7 Oaks", beside the road from Fort Douglas to Frog Plain)
OAKS = dict(name="The seven oaks (Seven Oaks)", kind="oak", count=7, scale=[1.3, 1.7], centre_px=(770, 1365), radius_px=22)
TRAILS = [
  dict(name="Cart road to Brandon House (Portage trail)", width=5,
       px=[(287,1204),(312,1161),(326,1129),(351,1079),(366,1036),(394,986),(423,943),(437,907),(455,871),(459,830),(470,800)]),
]
def main():
    out = {"source": SRC, "stands": [], "trails": []}
    for s in STANDS:
        out["stands"].append(dict(name=s["name"], kind=s["kind"], per1000m2=s["per1000m2"], scale=s["scale"],
                                  from_="1700-01-01", to=None, ring=[ll(*p) for p in s["px"]], source=SRC))
    o = OAKS; c = ll(*o["centre_px"])
    out["stands"].append(dict(name=o["name"], kind=o["kind"], scale=o["scale"], count=o["count"], from_="1700-01-01", to="1890-01-01",
                              centre=c, radiusM=round(o["radius_px"] * MPP), source=SRC))
    for t in TRAILS:
        out["trails"].append(dict(name=t["name"], width=t["width"], born=None, died="1882-01-01", path=[ll(*p) for p in t["px"]], source=SRC))
    s = json.dumps(out, indent=1).replace('"from_"', '"from"')
    open(os.path.join(HERE, '..', 'data', 'early_vegetation.json'), 'w').write(s)
    for st in out["stands"]: print(st["name"], st.get("ring", [st.get("centre")])[0])
    print(json.dumps(out["trails"][0]["path"]))
if __name__ == '__main__': main()
