"""pfviewer terrain bake: inner dem.bin repair + outer world-aligned heightfield, from the NRCan HRDEM 2 m mosaic DTM.

python bake_terrain.py HRDEM.tif DEM_IN_DIR WATER_PREFIX OUT_DIR
  HRDEM.tif     UTM 14N grid from fetch_hrdem.py (10 m, centred on the Forks like tools/dem_from_las.py)
  DEM_IN_DIR    holds the original LiDAR dem.bin + dem.json (inner 12 km, UTM-local, NN-filled outside the LiDAR)
  WATER_PREFIX  extract_water.py output prefix (…_polys.geojson, …_lines.geojson)
  OUT_DIR       writes dem.bin (repaired inner), dem_outer.bin/.json, previews

Inner: cells outside the City LiDAR footprint are replaced by HRDEM (+0.41 m, the datum gap), feathered over 150 m.
Outer: x/z are viewer world metres (index.html project()), ±HALF at CELL, int16 cm relative to refElev, row 0 = north.
Both: the Red River Floodway (1962–68) is filled with the surrounding ground; river polygons (and the named river
centrelines where OSM has no polygon) are cut to BED so the flat flood plane at CONFIG.water.startY shows in them."""
import sys, json, math, numpy as np, rasterio
from pyproj import Transformer
from scipy import ndimage as ndi
from scipy.ndimage import map_coordinates
from rasterio.features import rasterize
from rasterio.transform import Affine
from shapely.geometry import shape
from shapely import transform as sh_transform
from PIL import Image

HALF, CELL = 19600.0, 20.0
BED = -7.5                    # world Y the channels are cut to (plane rests at -5.8; date levels dip to ~-6.5)
DATUM = 0.41                  # HRDEM reads this much under the City LiDAR (median over land, inner 4 km)
FLOODWAY_HALF_M = 220         # channel + spoil banks
LINE_RIVERS = {'Seine River', 'Rivière Seine River', 'La Salle River', 'Sturgeon Creek', 'Assiniboine River', 'Red River'}
C_LON, C_LAT = -97.135515, 49.895396
MLON = 111320*math.cos(math.radians(C_LAT)); MLAT = 111320
UCX, UCY = 633907.9, 5528667.2
# inner mesh placement (config.js scene.terrain*): rotate about the pivot, then offset
PIV = ((-97.1283 - C_LON)*MLON, -(49.8843 - C_LAT)*MLAT); ROT = -1.5*math.pi/180; OFF = (-29.0, 14.6)

hr_path, din, wpre, out = sys.argv[1:5]
to_utm = Transformer.from_crs(4326, 32614, always_xy=True)
with rasterio.open(hr_path) as s:
    HR = s.read(1); HTF = s.transform
HRf = np.where(np.isnan(HR), np.nanmedian(HR), HR)
def hr_at(E, N):
    return map_coordinates(HRf, [(N - HTF.f)/HTF.e - 0.5, (E - HTF.c)/HTF.a - 0.5], order=1, mode='nearest')

polys = [f for f in json.load(open(wpre+'_polys.geojson'))['features']]
lines = [f for f in json.load(open(wpre+'_lines.geojson'))['features']]
river_polys = [shape(f['geometry']) for f in polys if f['properties']['water'] == 'river']
river_lines = [shape(f['geometry']) for f in lines if f['properties']['name'] in LINE_RIVERS and f['properties']['waterway'] in ('river', 'stream')]   # not 'canal': the Seine River Diversion (1950s) is tagged name=Seine River
floodway = [shape(f['geometry']) for f in lines if f['properties']['name'] == 'Red River Floodway']
def world(g):   # lon/lat geometry → viewer world (x, -z) so a north-up raster transform works
    return sh_transform(g, lambda c: np.column_stack([(c[:, 0]-C_LON)*MLON, (c[:, 1]-C_LAT)*MLAT]))

def fill_from_surroundings(h, mask, cell, sigma_m=250):
    w = (~mask).astype(np.float32); s = sigma_m/cell
    num = ndi.gaussian_filter(np.where(mask, 0, h), s); den = ndi.gaussian_filter(w, s)
    sm = num/np.maximum(den, 1e-3)
    h = h.copy(); h[mask] = sm[mask]; return h

def carve(h, tf, shape_, xy):
    """Cut river polygons (all_touched, so narrow ones stay continuous) and river centrelines to BED."""
    m = rasterize([(xy(g), 1) for g in river_polys], out_shape=shape_, transform=tf, all_touched=True) > 0
    if river_lines:
        m |= rasterize([(xy(g).buffer(6), 1) for g in river_lines], out_shape=shape_, transform=tf, all_touched=True) > 0
    return np.where(m, np.minimum(h, BED), h), m

def floodway_mask(shape_, tf, xy):
    if not floodway: return np.zeros(shape_, bool)
    return rasterize([(xy(g).buffer(FLOODWAY_HALF_M), 1) for g in floodway], out_shape=shape_, transform=tf) > 0

def hillshade(h, cell):
    gz, gx = np.gradient(h, cell); return np.clip(0.5 + (gx - gz)*1.5, 0, 1)

# ── Inner ────────────────────────────────────────────────────────────────
meta = json.load(open(f'{din}/dem.json')); S = meta['verts']; ref = meta['refElev']; icell = meta['size']/(S-1); ih = meta['size']/2
h0 = np.fromfile(f'{din}/dem.bin', np.float32).reshape(S, S)
gx = np.abs(np.diff(h0, axis=1)) > 1e-6; gz = np.abs(np.diff(h0, axis=0)) > 1e-6
both = np.zeros_like(h0, bool); both[:-1, :-1] = gx[:-1, :] & gz[:, :-1]
foot = ndi.binary_fill_holes(ndi.binary_closing(ndi.binary_opening(both, iterations=3), iterations=25))
foot = ndi.binary_erosion(foot, iterations=3)
ii = np.arange(S)*icell - ih
LX, LZ = np.meshgrid(ii, ii)
hr_in = hr_at(UCX + LX, UCY - LZ) + DATUM - ref
# geometry → inner-local (UTM-local, x east, 'y' north) for rasterising: lon/lat → UTM − centre
def inner_xy(g):
    return sh_transform(g, lambda c: np.column_stack(to_utm.transform(c[:, 0], c[:, 1])) - [UCX, UCY])
itf = Affine(icell, 0, -ih - icell/2, 0, -icell, ih + icell/2)
hr_in, _ = carve(hr_in, itf, (S, S), inner_xy)
fw = floodway_mask((S, S), itf, inner_xy)
if fw.any(): hr_in = fill_from_surroundings(hr_in, fw, icell)
dist = ndi.distance_transform_edt(~foot)*icell
w = np.clip(1 - dist/150.0, 0, 1); w = w*w*(3 - 2*w)
inner = (h0*w + hr_in*(1 - w)).astype(np.float32)
inner.tofile(f'{out}/dem.bin')
json.dump(meta, open(f'{out}/dem.json', 'w'))
print('inner: LiDAR footprint %.0f%%, max change %.1f m' % (100*foot.mean(), float(np.abs(inner - h0).max())))
img = np.stack([hillshade(inner, icell)]*3, -1); img[(inner < -5.8) & ~foot] = [0.25, 0.4, 0.85]
img[foot ^ ndi.binary_erosion(foot, iterations=2)] = [1, 0, 0]
Image.fromarray((img*255).astype(np.uint8)).resize((800, 800)).save(f'{out}/inner_preview.png')

# ── Outer ────────────────────────────────────────────────────────────────
n = int(round(2*HALF/CELL)) + 1
xs = -HALF + np.arange(n)*CELL
X, Z = np.meshgrid(xs, xs)
E, N = to_utm.transform(C_LON + X/MLON, C_LAT - Z/MLAT)
h = hr_at(E, N) + DATUM - ref
otf = Affine(CELL, 0, -HALF - CELL/2, 0, -CELL, HALF + CELL/2)
fw = floodway_mask((n, n), otf, world)
h = fill_from_surroundings(h, fw, CELL)
h, rm = carve(h, otf, (n, n), world)
q = np.clip(np.round(h*100), -32767, 32767).astype('<i2')
q.tofile(f'{out}/dem_outer.bin')
json.dump({'verts': n, 'size': 2*HALF, 'refElev': ref, 'scale': 0.01, 'format': 'int16',
           'note': 'viewer world-aligned (project()); row 0 = north (z = -size/2); NRCan HRDEM 2 m mosaic DTM; Floodway filled; rivers cut'},
          open(f'{out}/dem_outer.json', 'w'))
low = (h < -5.8)
img = np.stack([hillshade(h, CELL)]*3, -1); img[low & rm] = [0.25, 0.4, 0.85]; img[low & ~ndi.binary_dilation(rm, iterations=3)] = [0.9, 0.1, 0.1]; img[fw] *= [1, 0.85, 0.6]
Image.fromarray((img*255).astype(np.uint8)).resize((980, 980)).save(f'{out}/outer_preview.png')
print('outer: %d² range %.1f..%.1f, stray low cells %d' % (n, h.min(), h.max(), int((low & ~ndi.binary_dilation(rm, iterations=3)).sum())))
