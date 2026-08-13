#!/usr/bin/env python3
"""
dem_qgis.py — round-trip dem.bin <-> GeoTIFF for editing in QGIS

Usage:
    python dem_qgis.py totif [--origin EASTING NORTHING --epsg 26914]
        Writes dem_edit.tif. With --origin (coords of the NW/top-left corner
        of the grid), the tif is georeferenced so basemaps line up in QGIS.
        Without it, a local 0..12000 extent is used (editable, no basemap).

    python dem_qgis.py tobin
        Reads dem_edit.tif back, verifies shape/dtype, writes dem_edited.bin.
        Original dem.bin is never modified.

Requires: numpy, rasterio  (pip install rasterio)
"""

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

META = json.loads(Path("dem.json").read_text())
N = META["verts"]
SIZE = META["size"]
CELL = SIZE / (N - 1)          # 12000 / 1200 = 10.0 units per cell
TIF = Path("dem_edit.tif")


def totif(args):
    grid = np.fromfile("dem.bin", dtype="<f4").reshape(N, N)

    epsg = 26914  # NAD83 / UTM 14N (Winnipeg)
    origin = None
    if "--origin" in args:
        i = args.index("--origin")
        origin = (float(args[i + 1]), float(args[i + 2]))
    if "--epsg" in args:
        epsg = int(args[args.index("--epsg") + 1])

    if origin:
        transform = from_origin(origin[0], origin[1], CELL, CELL)
        crs = f"EPSG:{epsg}"
    else:
        transform = from_origin(0, SIZE, CELL, CELL)  # local coords
        crs = None

    with rasterio.open(
        TIF, "w", driver="GTiff", height=N, width=N, count=1,
        dtype="float32", transform=transform, crs=crs,
        compress=None,  # keep it raw; Serval edits in place
    ) as dst:
        dst.write(grid.astype("float32"), 1)
    print(f"Wrote {TIF} ({N}x{N}, cell={CELL} m, "
          f"{'EPSG:' + str(epsg) if origin else 'local coords, no CRS'})")


def tobin():
    with rasterio.open(TIF) as src:
        assert src.count == 1, "expected single band"
        grid = src.read(1)
    assert grid.shape == (N, N), f"shape changed: {grid.shape}, expected {(N, N)}"
    if not np.isfinite(grid).all():
        bad = (~np.isfinite(grid)).sum()
        sys.exit(f"{bad} NaN/inf cells found — fix nodata in QGIS before export")
    grid.astype("<f4").tofile("dem_edited.bin")
    print(f"Wrote dem_edited.bin  min={grid.min():.2f} max={grid.max():.2f} "
          f"mean={grid.mean():.2f}")
    print("Rename over dem.bin when satisfied.")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("totif", "tobin"):
        sys.exit(__doc__)
    if sys.argv[1] == "totif":
        totif(sys.argv[2:])
    else:
        tobin()
