"""Read the NRCan HRDEM 2 m mosaic DTM (overview) for a box around the Forks and write a UTM 14N GeoTIFF.
python fetch_hrdem.py OUT.tif HALF_M CELL_M [OVERVIEW_LEVEL]"""
import sys, os, numpy as np, rasterio
from rasterio.warp import reproject, Resampling, transform_bounds
from rasterio.windows import from_bounds
from rasterio.transform import from_origin
os.environ.setdefault('GDAL_DISABLE_READDIR_ON_OPEN', 'EMPTY_DIR')
os.environ.setdefault('GDAL_HTTP_MULTIRANGE', 'YES'); os.environ.setdefault('GDAL_HTTP_MERGE_CONSECUTIVE_RANGES', 'YES')
URL = '/vsicurl/https://canelevation-dem.s3.ca-central-1.amazonaws.com/hrdem-mosaic-2m/5_3-mosaic-2m-dtm.tif'
UTM_CX, UTM_CY = 633907.9, 5528667.2          # must match tools/dem_from_las.py
out, half, cell = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); ovl = int(sys.argv[4]) if len(sys.argv) > 4 else 1
n = int(round(2*half/cell)) + 1                 # vertex grid, centre on the Forks
dst_tf = from_origin(UTM_CX - half - cell/2, UTM_CY + half + cell/2, cell, cell)
utm_b = (UTM_CX-half-500, UTM_CY-half-500, UTM_CX+half+500, UTM_CY+half+500)
with rasterio.open(URL, overview_level=ovl) as s:
    b = transform_bounds('EPSG:32614', s.crs, *utm_b, densify_pts=21)
    win = from_bounds(*b, transform=s.transform).round_offsets().round_lengths()
    print('source res', s.res, 'window', win.width, 'x', win.height, flush=True)
    src = s.read(1, window=win, masked=False); src_tf = s.window_transform(win); crs = s.crs; nod = s.nodata
dst = np.full((n, n), np.nan, np.float32)
reproject(src, dst, src_transform=src_tf, src_crs=crs, src_nodata=nod, dst_transform=dst_tf, dst_crs='EPSG:32614', dst_nodata=np.nan, resampling=Resampling.average)
print('grid', n, 'x', n, 'nan', int(np.isnan(dst).sum()), 'min/max', np.nanmin(dst), np.nanmax(dst))
with rasterio.open(out, 'w', driver='GTiff', width=n, height=n, count=1, dtype='float32', crs='EPSG:32614', transform=dst_tf, nodata=np.nan, compress='deflate', predictor=3, tiled=True) as d:
    d.write(dst, 1)
