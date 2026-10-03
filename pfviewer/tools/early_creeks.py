#!/usr/bin/env python3
"""
early_creeks.py — georeference creeks traced from Figure 1 of

  Robert Michael W. Graham, "The Surface Waters of Winnipeg: Rivers, Streams,
  Ponds and Wetlands, 1874-1984" (M.L.A. practicum, U. of Manitoba, 1984;
  https://mspace.lib.umanitoba.ca, handle 1993/5148). Figure 1 is compiled from
  the Fidler 1816, Taylor 1838, Hind 1857, Sinclair 1874, McPhillips 1874,
  Doupe 1880 and Ruttan 1888 surveys and the City of Winnipeg survey.

The polylines below were traced BY HAND (by eye, from the 300 dpi page render,
page 27 of the PDF) in page-pixel coordinates. Figure 1 is a generalised
1:50 000-ish map, so positions are good to ~100-300 m at best; mouths are
snapped to the OSM river banks when within 360 m.

Georeferencing: similarity transform fitted by eye so the OSM Red River outline
overlays the map's river: 13.8 m per pixel, rotation 0.08 rad, with the Red/
Assiniboine confluence (page px 1605,1185) at lon -97.1285, lat 49.8875.

Output: data/early_creeks.geojson (LineStrings, type 'fence' + name, like
Brown's Creek in the assessment layer, so the viewer's creek code picks them up).
Dates: see DIED below (sources in the comments).
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
C_LON, C_LAT = -97.135515, 49.895396
M_LON = 111320 * math.cos(C_LAT * math.pi / 180)
M_LAT = 111320.0
MPP, ROT = 13.8, 0.08
ANCHOR_PX, ANCHOR_LL = (1605, 1185), (-97.1285, 49.8875)

def _raw(lon, lat):
    x = (lon - C_LON) * M_LON / MPP; y = -(lat - C_LAT) * M_LAT / MPP
    c, s = math.cos(ROT), math.sin(ROT)
    return c * x - s * y, s * x + c * y
_ax, _ay = _raw(*ANCHOR_LL)
TX, TY = ANCHOR_PX[0] - _ax, ANCHOR_PX[1] - _ay

# Landmark check (Graham's text + today's street ends): the traced mouths of Brown's,
# Logan's and Colony creeks came out on average 155 m east and 260 m north of where
# the text puts them (Bannatyne Ave foot; Alexander Ave foot; Colony St), individually
# 30-380 m. The mean offset is removed here; what's left is the map's own inaccuracy.
SHIFT_E_M, SHIFT_N_M = -155.0, -260.0

def px_to_ll(px, py):
    x, y = px - TX, py - TY
    c, s = math.cos(-ROT), math.sin(-ROT)
    ux, uy = c * x - s * y, s * x + c * y
    return C_LON + ux * MPP / M_LON + SHIFT_E_M / M_LON, C_LAT - uy * MPP / M_LAT + SHIFT_N_M / M_LAT

# name: (lines in page px — first point of the first line is the MOUTH, died)
# Dates (Graham 1984): the 1880/1882 Colony–Omands diversion cut the source of
# Colony, Brown's, Logan's, Pritchard's, St John's and Inkster's creeks;
# "within twenty years only traces would remain" (~1900). Colony itself: diverted
# 1880. Brown's is dated 1895 elsewhere (assessment layer); Logan's matched to it.
# Inkster's, McLeod's, Omand's survive (Omand's, Inkster's still exist) → no end.
CREEKS = {
  "Colony Creek": ("1881-01-01", [[(1506,1202),(1512,1184),(1509,1175),(1512,1167),(1509,1159),(1512,1150),(1506,1140),(1501,1131),(1499,1118),(1490,1102),(1483,1099),(1475,1094)]]),
  "Logan's Creek": ("1895-02-01", [[(1603,1058),(1595,1038),(1588,1028),(1584,1024)]]),
  "Pritchard's Creek": ("1900-01-01", [[(1620,959),(1597,967),(1584,963),(1576,958),(1570,951)]]),
  "St. John's Creek": ("1900-01-01", [[(1647,897),(1640,886),(1634,878),(1626,872),(1620,863),(1617,857)]]),
  "Inkster's Creek": (None, [
      [(1775,700),(1750,697),(1737,700),(1730,703),(1728,708),(1727,713)],
      [(1727,713),(1722,717),(1708,727),(1697,747),(1698,777),(1700,792)],
      [(1730,703),(1723,700),(1713,697),(1707,688),(1695,682),(1683,675)],
      [(1722,717),(1707,709),(1693,711),(1680,706),(1667,705),(1658,703)],
      [(1700,792),(1677,793),(1670,795),(1660,792),(1650,788),(1638,783),(1630,775),(1620,773),(1613,773)],
      [(1677,793),(1667,802),(1660,817),(1652,833)]]),
  "McLeod's Creek": (None, [
      [(1818,657),(1813,667),(1812,687),(1813,708),(1807,720),(1801,733),(1802,747),(1793,755),(1792,772),(1800,783),(1808,795)],
      [(1808,795),(1820,785),(1828,792),(1843,803),(1852,817),(1863,837),(1872,853),(1880,870),(1883,886),(1877,907),(1877,925),(1886,942),(1889,960),(1902,966),(1907,984),(1916,985),(1919,995),(1924,1013)],
      [(1808,795),(1810,803),(1808,813),(1802,833)]]),
  # The creek that drained the oxbow (the swamp of the 1836 plan): from the Red's east bank at the St Boniface
  # waterfront, past a small pond, into the marsh at the north end of the bow (Parr's 1874 plan: a bridge mark
  # at its mouth, marsh stipple along Lots 8-10). Gone when the oxbow was filled (our oxbow's `until`, spring 1910).
  "Oxbow outlet creek": ("1910-04-15", [[]]),
  "Omand's Creek": (None, [[(1293,1237),(1290,1220),(1283,1209),(1277,1197),(1267,1178),(1260,1168),(1257,1160)]]),
}


# ── 1874 plan of the City of Winnipeg (J.D. Parr, compiled from surveys by Sinclair, Vaughan,
# Johnston, Brown and Parr; Copp, Clark & Co., Toronto) — a better source for the town's creeks.
# Its north points up-left (fleur-de-lis on the compass, 19.5° left of the page's up), scale taken
# as 3.4 m per pixel of the 1196×1500 scan, fitted so the OSM Red River overlays the plan's river
# with the Forks at pixel (945,885). Traced by eye; mouths snapped to the OSM river within 360 m.
# The Colony mouth lands 30 m from the Graham-based one, Logan's and Pritchard's within ~300 m.
MPP74, ROT74, ANCHOR74 = 3.4, -0.34, (945, 885)
def _raw74(lon, lat):
    x = (lon - C_LON) * M_LON / MPP74; y = -(lat - C_LAT) * M_LAT / MPP74
    c, s = math.cos(ROT74), math.sin(ROT74); return c * x - s * y, s * x + c * y
_a74 = _raw74(*ANCHOR_LL); TX74, TY74 = ANCHOR74[0] - _a74[0], ANCHOR74[1] - _a74[1]
def px74_to_ll(px, py):
    x, y = px - TX74, py - TY74; c, s = math.cos(-ROT74), math.sin(-ROT74)
    ux, uy = c * x - s * y, s * x + c * y
    return C_LON + ux * MPP74 / M_LON, C_LAT - uy * MPP74 / M_LAT

# name -> lines in 1874-plan pixels, mouth first. These REPLACE the Graham-based traces of the same name.
CREEKS_1874 = {
  "Colony Creek": [[(591,1191),(587,1187),(573,1178),(578,1161),(569,1143),(576,1126),(567,1113),(571,1098),(565,1087),(547,1083),(543,1065),(534,1048),(526,1030),(530,1013),(521,994),(504,974),(480,948),(443,930),(424,915),(419,902),(417,878)]],
  "Logan's Creek": [[(700,503),(694,489),(689,475),(683,461),(672,444),(661,433),(650,423),(645,418)]],
  "Oxbow outlet creek": [[(1028,808),(1040,803),(1052,797),(1060,788),(1063,775),(1070,768),(1085,763),(1105,753),(1125,748),(1145,745),(1160,750)],
                         [(1075,771),(1095,785),(1115,795),(1127,801)]],
  "Pritchard's Creek": [[(577,109),(574,111),(566,116),(559,122),(556,131),(553,142),(548,152),(530,159),(514,162),(497,161),(488,159),(478,153)]],
}


# ── 1836 plan: the meandering "Creek" east of the Red (the Seine's old outlet, cf. Graham fluvial landform 'a')
MPP36, ROT36, ANCHOR36 = 2.12, -0.43, (855, 1000)
def _raw36(lon, lat):
    x = (lon - C_LON) * M_LON / MPP36; y = -(lat - C_LAT) * M_LAT / MPP36
    c, s = math.cos(ROT36), math.sin(ROT36); return c * x - s * y, s * x + c * y
_a36 = _raw36(-97.1285, 49.8875); TX36, TY36 = ANCHOR36[0] - _a36[0], ANCHOR36[1] - _a36[1]
def px36_to_ll(px, py):
    x, y = px - TX36, py - TY36; c, s = math.cos(-ROT36), math.sin(-ROT36)
    ux, uy = c * x - s * y, s * x + c * y
    return C_LON + ux * MPP36 / M_LON, C_LAT - uy * MPP36 / M_LAT
CREEKS_1836 = {}   # (the plan's meandering east-bank 'Creek' is the Seine itself, already in the OSM river data)

def rings(path):
    g = json.load(open(path)); out = []
    for f in g['features']:
        if f['geometry']['type'] == 'Polygon':
            out += [[(p[0], p[1]) for p in r] for r in f['geometry']['coordinates']]
    return out

def nearest_on(rings_, lon, lat):
    best = (1e18, None)
    for r in rings_:
        for i in range(len(r) - 1):
            ax, ay = (r[i][0] - lon) * M_LON, (r[i][1] - lat) * M_LAT
            bx, by = (r[i+1][0] - lon) * M_LON, (r[i+1][1] - lat) * M_LAT
            dx, dy = bx - ax, by - ay; L2 = dx*dx + dy*dy or 1
            t = max(0, min(1, -(ax*dx + ay*dy) / L2)); qx, qy = ax + dx*t, ay + dy*t
            d = qx*qx + qy*qy
            if d < best[0]: best = (d, (lon + qx / M_LON, lat + qy / M_LAT))
    return math.sqrt(best[0]), best[1]

def main():
    rv = rings(os.path.join(HERE, '..', 'data', 'wpg_rivers.geojson'))
    feats = []
    for name, (died, lines) in {**CREEKS, **CREEKS_1836}.items():
        if name in CREEKS_1836:
            ll = [[px36_to_ll(*p) for p in line] for line in lines]
        elif name in CREEKS_1874:
            ll = [[px74_to_ll(*p) for p in line] for line in CREEKS_1874[name]]
        else:
            ll = [[px_to_ll(*p) for p in line] for line in lines]
        mouth = ll[0][0]
        d, q = nearest_on(rv, *mouth)
        shift = (0, 0)
        if q and d < 360:        # river polygons only cover part of the map; only snap small corrections
            shift = (q[0] - mouth[0], q[1] - mouth[1])
        print(f'{name}: mouth snapped {d:.0f} m' if q and d < 360 else f'{name}: no OSM river within 360 m ({d:.0f}) — left as traced')
        for line in ll:
            coords = [[round(x + shift[0], 6), round(y + shift[1], 6)] for x, y in line]
            feats.append({"type": "Feature", "properties": {
                "name": name, "type": "fence", "material": "unknown", "born": "1700-08-01", "died": died,
                "source": ("1874 plan of the City of Winnipeg (Parr)" if name in CREEKS_1874 else "1836 Plan Red River and Assiniboine" if name in CREEKS_1836 else "Graham 1984, Fig. 1")+" — traced by eye; ±100–300 m"},
                "geometry": {"type": "LineString", "coordinates": coords}})
    out = os.path.join(HERE, '..', 'data', 'early_creeks.geojson')
    json.dump({"type": "FeatureCollection", "features": feats}, open(out, 'w'))
    print('wrote', out, len(feats), 'lines')

if __name__ == '__main__':
    main()
