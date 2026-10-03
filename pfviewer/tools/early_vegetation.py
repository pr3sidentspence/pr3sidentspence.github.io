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


# ── 1836 "Plan Red River and Assiniboine in 1836" (copy dated Fort Garry, 22 Oct 1863; scale bar in chains,
# 100 chains = 870 px = 2.31 m/px nominal). Its compass puts north 25° left of up. Fitted by overlaying the OSM
# river with the Forks at pixel (855,1000): the plan's river is drawn ~9% bigger than the bar suggests,
# so 2.12 m/px fits best. Sketch map: ±300 m at best.
MPP36, ROT36, ANCHOR36 = 2.12, -0.43, (855, 1000)
def _raw36(lon, lat):
    x = (lon - C_LON) * M_LON / MPP36; y = -(lat - C_LAT) * M_LAT / MPP36
    c, s = math.cos(ROT36), math.sin(ROT36); return c * x - s * y, s * x + c * y
_a36 = _raw36(-97.1285, 49.8875); TX36, TY36 = ANCHOR36[0] - _a36[0], ANCHOR36[1] - _a36[1]
def ll36(px, py):
    x, y = px - TX36, py - TY36; c, s = math.cos(-ROT36), math.sin(-ROT36)
    ux, uy = c * x - s * y, s * x + c * y
    return [round(C_LON + ux * MPP36 / M_LON, 6), round(C_LAT - uy * MPP36 / M_LAT, 6)]
SRC36 = "1836 'Plan Red River and Assiniboine' (traced by eye)"
# kind, density per 1000 m2, "to" (a guess: when the bush was cleared/built over), polygon in plan pixels
STANDS36 = [
  ("South-bank woods (Fort Rouge side)", "poplar", 0.8, "1895-01-01",
   [(330,1420),(480,1330),(560,1210),(600,1160),(625,1250),(620,1340),(640,1450),(660,1580),(700,1690),(810,1760),(780,1800),(680,1800),(600,1790),(520,1720),(420,1620),(340,1560)]),
  ("Assiniboine south-bank woods, west", "poplar", 0.8, "1895-01-01",
   [(40,1750),(200,1740),(330,1790),(430,1850),(420,1900),(300,1940),(100,1950),(40,1900)]),
  ("St Boniface south woods", "poplar", 0.8, "1890-01-01",
   [(920,1330),(960,1250),(1100,1260),(1230,1230),(1250,1400),(1200,1480),(1080,1500),(1000,1460),(920,1420)]),
  ("St Boniface road trees", "poplar", 1.2, "1880-01-01",
   [(740,540),(830,470),(900,480),(930,640),(1000,800),(990,830),(930,800),(880,730),(820,650),(760,590)]),
  ("St Boniface convent road trees", "poplar", 1.2, "1880-01-01",
   [(990,830),(1100,820),(1240,850),(1250,890),(1100,860),(990,850)]),
]

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
    for nm,kind,dens,to,px in STANDS36:
        K = {"poplar": [0.9, 1.3], "willow": [0.9, 1.4]}[kind]
        # The plan's St Boniface side lands on the wrong bank of the Red (the old Seine outlet drawn on it comes out ~340 m
        # west of the real Seine's mouth in the OSM data), so the east-bank stands are slid 330 m east.
        dE = 330.0 if nm.startswith("St Boniface") else 0.0
        ring = [ll36(*p) for p in px]; ring = [[round(lo + dE / M_LON, 6), la] for lo, la in ring]
        out["stands"].append(dict(name=nm, kind=kind, per1000m2=dens, scale=K, from_="1700-01-01", to=to, ring=ring, source=SRC36))
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
