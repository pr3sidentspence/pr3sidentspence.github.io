"""
dem_from_las.py  —  Build a DEM grid from Winnipeg LiDAR tiles for pfviewer.

Usage:
    python dem_from_las.py  <las_folder>  <output_folder>

    <las_folder>    folder containing  YYYY-EEEEE0_NNNNNNN0.las  files
    <output_folder> where to write  dem.bin  and  dem.json
                    (use pfviewer/data/ so the viewer can fetch them)

Requirements:
    pip install laspy numpy scipy

The script reads class-2 (ground) points from every .las tile, bins them onto
the same 301×301 vertex grid used by the Three.js terrain mesh, fills any gaps
by nearest-neighbour interpolation, and writes:

  dem.bin   — 90,601 float32 values (row-major iz,ix) in metres relative to
               the reference elevation (≈ local mean).  Y-up: add to world Y.
  dem.json  — metadata: {"verts":301,"size":12000,"refElev":<float>}
"""

import sys, os, glob, struct, json
import numpy as np
from scipy.interpolate import NearestNDInterpolator

# ── Viewer constants (must match index.html) ─────────────────────────────────
UTM_CX      = 633907.9     # UTM Zone 14N easting  of C_LON/C_LAT
UTM_CY      = 5528667.2    # UTM Zone 14N northing of C_LON/C_LAT
TERRAIN_SIZE = 12000       # metres, square
SEGMENTS     = 1200
VERTS        = SEGMENTS + 1   # 1201
CELL         = TERRAIN_SIZE / SEGMENTS   # 10 m

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    las_dir  = sys.argv[1]
    out_dir  = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    # Accept either a folder path or a direct .las file path
    if las_dir.lower().endswith('.las') and os.path.isfile(las_dir):
        tiles = [las_dir]
    else:
        tiles = sorted(glob.glob(os.path.join(las_dir, "*.las")))
    if not tiles:
        print(f"No .las files found in {las_dir}")
        sys.exit(1)
    print(f"Found {len(tiles)} tile(s)")

    acc_sum   = np.zeros((VERTS, VERTS), dtype=np.float64)
    acc_count = np.zeros((VERTS, VERTS), dtype=np.int32)

    try:
        import laspy
    except ImportError:
        print("ERROR: laspy not installed — run:  pip install laspy numpy scipy")
        sys.exit(1)

    for i, path in enumerate(tiles, 1):
        name = os.path.basename(path)
        print(f"  [{i:3d}/{len(tiles)}] {name}", end=" … ", flush=True)
        try:
            las  = laspy.read(path)
            mask = np.array(las.classification) == 2
            n_ground = mask.sum()
            if n_ground == 0:
                print("no ground pts, skipped")
                continue

            gx = np.array(las.x)[mask]
            gy = np.array(las.y)[mask]
            gz = np.array(las.z)[mask]

            # UTM → terrain grid index
            # worldX = UTM_E − UTM_CX  (east +)
            # worldZ = UTM_CY − UTM_N  (south +)
            wx = gx - UTM_CX
            wz = UTM_CY - gy
            ix = np.floor((wx + TERRAIN_SIZE / 2) / CELL).astype(np.int32)
            iz = np.floor((wz + TERRAIN_SIZE / 2) / CELL).astype(np.int32)

            valid = (ix >= 0) & (ix < VERTS) & (iz >= 0) & (iz < VERTS)
            ix, iz, gz = ix[valid], iz[valid], gz[valid]
            np.add.at(acc_sum,   (iz, ix), gz)
            np.add.at(acc_count, (iz, ix), 1)
            print(f"{valid.sum():,} pts → {(acc_count>0).sum():,} cells filled")
        except Exception as e:
            print(f"ERROR: {e}")

    # ── Compute mean elevation per cell ──────────────────────────────────────
    filled_mask = acc_count > 0
    n_filled    = filled_mask.sum()
    n_total     = VERTS * VERTS
    print(f"\nTotal cells filled: {n_filled:,} / {n_total:,} ({100*n_filled/n_total:.1f}%)")

    dem = np.full((VERTS, VERTS), np.nan, dtype=np.float64)
    dem[filled_mask] = acc_sum[filled_mask] / acc_count[filled_mask]

    # ── Fill gaps (edge tiles, water bodies, etc.) ────────────────────────────
    n_missing = (~filled_mask).sum()
    if n_missing > 0:
        print(f"Filling {n_missing:,} empty cells by nearest-neighbour …")
        rows, cols = np.where(filled_mask)
        vals = dem[rows, cols]
        all_rows, all_cols = np.where(~filled_mask)
        interp = NearestNDInterpolator(np.column_stack([rows, cols]), vals)
        dem[all_rows, all_cols] = interp(np.column_stack([all_rows, all_cols]))

    # ── Subtract reference elevation so values centre near 0 ─────────────────
    ref_elev = float(np.nanmean(dem))
    dem_rel  = (dem - ref_elev).astype(np.float32)

    print(f"Reference elevation: {ref_elev:.2f} m ASL")
    print(f"Relative DEM range:  {dem_rel.min():.2f} – {dem_rel.max():.2f} m")

    # ── Write output ──────────────────────────────────────────────────────────
    bin_path  = os.path.join(out_dir, "dem.bin")
    json_path = os.path.join(out_dir, "dem.json")

    dem_rel.flatten().tofile(bin_path)   # raw float32, row-major (iz, ix)
    with open(json_path, "w") as f:
        json.dump({"verts": VERTS, "size": TERRAIN_SIZE, "refElev": ref_elev}, f)

    bin_kb = os.path.getsize(bin_path) / 1024
    print(f"\nWrote {bin_path}  ({bin_kb:.0f} KB)")
    print(f"Wrote {json_path}")
    print("Done — copy both files to pfviewer/data/ and reload the viewer.")

if __name__ == "__main__":
    main()
