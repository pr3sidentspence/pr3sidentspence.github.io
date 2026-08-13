#!/usr/bin/env python3
"""
dem_edit.py — inspect and selectively smooth a raw heightfield (dem.bin + dem.json)

Usage:
    python dem_edit.py preview                 # writes dem_preview.png (hillshade + heatmap)
    python dem_edit.py smooth r0 r1 c0 c1 SIGMA [--feather N]
                                               # smooths rows r0:r1, cols c0:c1, writes dem_smoothed.bin
    python dem_edit.py flatten r0 r1 c0 c1 [--feather N]
                                               # flattens region to its median elevation

Row/col indices refer to the preview image axes, so you can read them
straight off the PNG. Repeat smooth/flatten calls chain onto dem_smoothed.bin
if it exists, so you can iterate region by region.
"""

import json
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter, distance_transform_edt

META = Path("dem.json")
SRC = Path("dem.bin")
OUT = Path("dem_smoothed.bin")


def load():
    meta = json.loads(META.read_text())
    n = meta["verts"]
    src = OUT if OUT.exists() else SRC   # chain edits if output already exists
    raw = src.read_bytes()
    n_vals = n * n
    per_val = len(raw) / n_vals
    if per_val == 4:
        dtype = np.dtype("<f4")
    elif per_val == 2:
        dtype = np.dtype("<i2")
    elif per_val == 8:
        dtype = np.dtype("<f8")
    else:
        sys.exit(f"Can't infer dtype: {len(raw)} bytes / {n_vals} values = {per_val}")
    grid = np.frombuffer(raw, dtype=dtype).reshape(n, n).astype(np.float64)
    print(f"Loaded {src} as {dtype} {n}x{n}; "
          f"min={grid.min():.2f} max={grid.max():.2f} mean={grid.mean():.2f}")
    return grid, dtype, meta


def save(grid, dtype):
    if dtype.kind == "i":
        grid = np.rint(grid)
    grid.astype(dtype).tofile(OUT)
    print(f"Wrote {OUT}")


def preview(grid):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(18, 9))
    im = axes[0].imshow(grid, cmap="terrain")
    axes[0].set_title("Elevation")
    fig.colorbar(im, ax=axes[0], shrink=0.7)

    # cheap hillshade to make berms/cuts pop
    gy, gx = np.gradient(grid)
    hs = 255 * (1 + (gx - gy) / np.hypot(gx, gy).max()) / 2
    axes[1].imshow(hs, cmap="gray")
    axes[1].set_title("Hillshade (spot the earthworks here)")

    for ax in axes:
        ax.set_xlabel("col")
        ax.set_ylabel("row")
    fig.tight_layout()
    fig.savefig("dem_preview.png", dpi=150)
    print("Wrote dem_preview.png — read row/col ranges off the axes")


def feathered_mask(shape, r0, r1, c0, c1, feather):
    """1.0 inside the box, ramping to 0.0 over `feather` cells outside it."""
    hard = np.zeros(shape, dtype=bool)
    hard[r0:r1, c0:c1] = True
    if feather <= 0:
        return hard.astype(np.float64)
    dist = distance_transform_edt(~hard)
    return np.clip(1.0 - dist / feather, 0.0, 1.0)


def smooth(grid, r0, r1, c0, c1, sigma, feather):
    blurred = gaussian_filter(grid, sigma=sigma)
    m = feathered_mask(grid.shape, r0, r1, c0, c1, feather)
    return grid * (1 - m) + blurred * m


def flatten(grid, r0, r1, c0, c1, feather):
    target = np.median(grid[r0:r1, c0:c1])
    m = feathered_mask(grid.shape, r0, r1, c0, c1, feather)
    return grid * (1 - m) + target * m


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    cmd, args = args[0], args[1:]

    feather = 15
    if "--feather" in args:
        i = args.index("--feather")
        feather = int(args[i + 1])
        del args[i:i + 2]

    grid, dtype, meta = load()

    if cmd == "preview":
        preview(grid)
    elif cmd == "smooth":
        r0, r1, c0, c1, sigma = map(float, args)
        grid = smooth(grid, int(r0), int(r1), int(c0), int(c1), sigma, feather)
        save(grid, dtype)
    elif cmd == "flatten":
        r0, r1, c0, c1 = map(int, args)
        grid = flatten(grid, r0, r1, c0, c1, feather)
        save(grid, dtype)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
