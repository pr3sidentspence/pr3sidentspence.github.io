#!/usr/bin/env python3
"""
dem_paint.py — edit dem.bin elevations via painted masks or auto-thresholding

Painted-mask workflow:
    1. python dem_paint.py ref
         Writes dem_ref.png (hillshade reference, 1 px per grid vertex).
    2. Paint on a new layer in Paint.NET, flatten, save as dem_mask.png:
           RED    (255, 0, 0)   -> raise terrain      (--raise, default 2.0)
           BLUE   (0, 0, 255)   -> lower terrain      (--lower, default 2.0)
           GREEN  (0, 255, 0)   -> gaussian smooth    (--sigma, default 5)
           YELLOW (255, 255, 0) -> flatten to region median
           PURPLE (255, 0, 255) -> river scoop: U channel below rim
       Do not resize the canvas. 100% opacity brushes work best.
    3. python dem_paint.py apply [--raise 2.0] [--lower 2.0] [--sigma 5]
                                 [--depth 3.0] [--water-elev E]
                                 [--feather 2] [--fresh]

Auto-threshold workflow (no painting; selects the river by elevation):
    python dem_paint.py auto --below X [--depth 10] [--min-area 50]
                             [--feather 2] [--flat] [--fresh]
         Selects all cells with elevation < X, heals small gaps, drops
         blobs smaller than --min-area cells, then scoops a U channel
         with rim at X reaching X - depth at the centerline.
         --flat sets selected cells to a uniform X - depth instead (hard
         walls at the boundary — only sensible if water always covers it).
         Writes dem_auto_mask.png showing what got selected.

Both workflows write dem_painted.bin + dem_painted_preview.png and never
modify dem.bin. Runs chain onto dem_painted.bin unless --fresh is given.

Requires: numpy, scipy, pillow
"""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import (binary_closing, binary_fill_holes,
                           distance_transform_edt, gaussian_filter, label,
                           maximum_filter)

META = json.loads(Path("dem.json").read_text())
N = META["verts"]
SRC = Path("dem.bin")
OUT = Path("dem_painted.bin")
REF = Path("dem_ref.png")
MASK = Path("dem_mask.png")

COLORS = {  # name -> RGB
    "raise": (255, 0, 0),
    "lower": (0, 0, 255),
    "smooth": (0, 255, 0),
    "flatten": (255, 255, 0),
    "scoop": (255, 0, 255),
}


def load(fresh=False):
    src = SRC if (fresh or not OUT.exists()) else OUT
    grid = np.fromfile(src, dtype="<f4").astype(np.float64).reshape(N, N)
    print(f"Loaded {src}: min={grid.min():.2f} max={grid.max():.2f}")
    return grid


def hillshade(grid):
    gy, gx = np.gradient(grid)
    hs = (1 + (gx - gy) / max(np.hypot(gx, gy).max(), 1e-9)) / 2
    lo, hi = np.percentile(hs, [2, 98])
    hs = np.clip((hs - lo) / max(hi - lo, 1e-9), 0, 1)
    return (hs * 255).astype(np.uint8)


def make_ref():
    grid = load(fresh=True)
    Image.fromarray(hillshade(grid), mode="L").convert("RGB").save(REF)
    print(f"Wrote {REF} ({N}x{N}) — paint on it, save as {MASK}")


def color_weights(img):
    rgb = np.asarray(img.convert("RGB"), dtype=np.float64)
    if rgb.shape[:2] != (N, N):
        sys.exit(f"Mask is {rgb.shape[1]}x{rgb.shape[0]}, expected {N}x{N}. "
                 "Canvas was resized — re-save without resizing.")
    saturation = rgb.max(axis=2) - rgb.min(axis=2)
    painted = saturation > 40
    weights = {}
    for name, c in COLORS.items():
        dist = np.linalg.norm(rgb - np.array(c), axis=2)
        w = np.clip(1 - dist / 180.0, 0, 1)
        w[~painted] = 0
        weights[name] = w
    stack = np.stack(list(weights.values()))
    best = stack.argmax(axis=0)
    for i, name in enumerate(weights):
        w = weights[name]
        w[best != i] = 0
        weights[name] = w
    for name, w in weights.items():
        px = (w > 0.05).sum()
        if px:
            print(f"  {name}: {px} px painted")
    return weights


def make_soften(feather):
    def soften(m):
        """Full strength where painted; ramp to 0 over `feather` cells
        OUTSIDE the region. Never dilutes narrow features."""
        if feather <= 0:
            return m
        hard = m > 0.25
        if not hard.any():
            return m
        ramp = np.clip(1 - distance_transform_edt(~hard) / feather, 0, 1)
        return np.maximum(m, ramp)
    return soften


def scoop_channel(grid, s_hard, rim, depth, soften, weight=None):
    """Carve a U-profile channel: rim elevation at the region edge,
    rim - depth at the centerline, adapting to local channel width."""
    # smoothed distance field so pixel stair-steps in the boundary
    # don't ripple inward as perpendicular corrugations
    d = gaussian_filter(distance_transform_edt(s_hard), sigma=1.5)
    win = 2 * int(np.percentile(d[s_hard], 99) * 2) + 1
    local_half = maximum_filter(d, size=win)
    local_half = np.maximum(gaussian_filter(local_half, sigma=win / 4), 1e-9)
    frac = np.clip(d / local_half, 0, 1)
    profile = 1 - (1 - frac) ** 2      # U: fast drop off banks, flat middle
    target = rim - depth * profile
    m = soften(weight if weight is not None else s_hard.astype(np.float64))
    print(f"  scoop: rim={rim:.2f}, centerline={rim - depth:.2f} "
          f"(depth {depth} m)")
    return grid * (1 - m) + target * m


def write_out(grid):
    grid.astype("<f4").tofile(OUT)
    Image.fromarray(hillshade(grid), mode="L").save("dem_painted_preview.png")
    print(f"Wrote {OUT} and dem_painted_preview.png "
          f"(min={grid.min():.2f} max={grid.max():.2f})")
    print("Rename over dem.bin when satisfied.")


def apply_mask(args):
    feather = float(get_opt(args, "--feather", 2))
    d_raise = float(get_opt(args, "--raise", 2.0))
    d_lower = float(get_opt(args, "--lower", 2.0))
    sigma = float(get_opt(args, "--sigma", 5))

    grid = load(fresh="--fresh" in args)
    if not MASK.exists():
        sys.exit(f"{MASK} not found — save your painted image as that name.")
    w = color_weights(Image.open(MASK))
    soften = make_soften(feather)

    grid = grid + soften(w["raise"]) * d_raise
    grid = grid - soften(w["lower"]) * d_lower

    m = soften(w["smooth"])
    if m.max() > 0:
        grid = grid * (1 - m) + gaussian_filter(grid, sigma=sigma) * m

    m_hard = w["flatten"] > 0.5
    if m_hard.any():
        target = np.median(grid[m_hard])
        m = soften(w["flatten"])
        grid = grid * (1 - m) + target * m
        print(f"  flatten target: {target:.2f}")

    s_hard = w["scoop"] > 0.5
    if s_hard.any():
        depth = float(get_opt(args, "--depth", 3.0))
        we = get_opt(args, "--water-elev", None)
        rim = float(we) if we is not None else float(np.median(grid[s_hard]))
        grid = scoop_channel(grid, s_hard, rim, depth, soften, w["scoop"])

    write_out(grid)


def auto(args):
    below = get_opt(args, "--below", None)
    if below is None:
        sys.exit("auto requires --below X (elevation threshold)")
    below = float(below)
    depth = float(get_opt(args, "--depth", 10.0))
    min_area = int(get_opt(args, "--min-area", 50))
    feather = float(get_opt(args, "--feather", 2))

    grid = load(fresh="--fresh" in args)
    raw = grid < below
    frac = raw.mean()
    print(f"  below {below}: {raw.sum()} cells raw ({frac:.1%} of tile)")
    if frac > 0.25:
        sys.exit(f"Selection covers {frac:.0%} of the tile — that's not a "
                 "river. Check the sign/value of --below "
                 f"(grid min={grid.min():.2f}).")

    # heal small gaps (bridge decks, noise) then drop tiny blobs
    m = binary_closing(raw, structure=np.ones((3, 3)), iterations=2)
    lab, n = label(m)
    if n:
        sizes = np.bincount(lab.ravel())
        sizes[0] = 0
        m = sizes[lab] >= min_area
    # fill small holes (interp junk islands inside the channel)
    holes = binary_fill_holes(m) & ~m
    hlab, hn = label(holes)
    if hn:
        hsizes = np.bincount(hlab.ravel())
        keep = np.zeros(hn + 1, bool)
        keep[1:] = hsizes[1:] < min_area * 4
        m = m | keep[hlab]
    kept = int(np.max(label(m)[1]))
    print(f"  after cleanup: {m.sum()} cells in {kept} region(s)")
    if not m.any():
        sys.exit("Nothing selected — threshold too low?")

    Image.fromarray(np.where(m, 255, 0).astype(np.uint8)).save(
        "dem_auto_mask.png")
    print("Wrote dem_auto_mask.png (white = selected)")

    soften = make_soften(feather)
    if "--flat" in args:
        mm = soften(m.astype(np.float64))
        grid = grid * (1 - mm) + (below - depth) * mm
        print(f"  flat set to {below - depth:.2f}")
    else:
        grid = scoop_channel(grid, m, below, depth, soften)

    write_out(grid)


def get_opt(args, flag, default):
    return args[args.index(flag) + 1] if flag in args else default


if __name__ == "__main__":
    cmds = {"ref": lambda a: make_ref(), "apply": apply_mask, "auto": auto}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    cmds[sys.argv[1]](sys.argv[2:])
