"""
build_pastforward.py — assemble data/pastforward_2026.geojson, the temporal
"growth" master the viewer scrubs through.

The viewer already has the growth ENGINE: every building piece is tagged with a
per-vertex [bornYear, diedYear] and a fragment shader discards anything outside
[born, died) against the date-slider's year (see tagLifespan / buildingYearUniform
in ../index.html). What's been missing is DATA — born/died on every building.
This script produces it.

Inputs (all under ../data):
  mcphillips_1880.died_corrected.geojson   1880 survey (McPhillips), with the
                                           real born/died the pipeline knows.
  goad_1906.geojson                        1906 survey (Goad fire-insurance plan).
  mcphillips_goad_1906.matches.json        1880<->1906 correspondence (match_buildings.py).
  other_*.geojson (optional, any number)   supplementary features NOT from the two
                                           surveys — photos, records, the fort,
                                           later additions. Keep the survey files
                                           survey-only; put everything else here.

Output:
  pastforward_2026.geojson                 one feature per building that ever
                                           existed, every one dated.

Cohorts (each sets the date rule):
  matched   (1880 id -> 1906 id)   present in both surveys -> persisted. Rendered
                                   ONCE, using the 1906 geometry (the continuation).
                                   born = earliest real 1880 born, else present-by-1880.
                                   died = real if known, else null (still standing).
  1880_only (1880, no 1906 match)  gone by 1906. born = real/present-by-1880.
                                   died = real, else negative-evidence estimate in (1880,1906].
  1906_only (1906, no 1880 match)  built in the 1880->1906 boom. died = null.
                                   born = real (rare), else PROCEDURAL infill in (1880,1906].
  other     (other_*.geojson)      supplementary; dates used VERBATIM (never
                                   procedural). Missing born -> no lower bound;
                                   missing died -> still standing.

Identity: every building keeps its source pf_uid (minted/preserved by Planimetro,
stable across edits and renumbering). Matches key on pf_uid too (uids_1880 /
uids_1906 in matches.json), so editing the source attributes — a died date, say —
no longer desyncs the match graph; only geometry changes need a re-match.
Procedural dates are hash-seeded from the pf_uid, so a rebuild yields identical
output as long as the pf_uid is stable.

Uncertainty is made explicit, never hidden: each estimated date carries
{born,died}_low / _high year bounds and a {born,died}_basis string saying how it
was derived. Only the point estimate (born/died) drives the shader; the bounds
and basis are for later shading, auditing, and refinement.

Usage:
    python build_pastforward.py [--out PATH] [--boom-start 1881]
"""

import os
import glob
import json
import argparse
import hashlib

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')

# Survey reference dates — the point at which each map documents "present".
BORN_PRESENT_BY_1880 = '1880-08-01'   # matched / 1880-only: known present by the 1880 survey
WINDOW_LO_ISO = '1880-08-01'          # (1880, 1906] estimation window bounds
WINDOW_HI_ISO = '1906-07-01'
WINDOW_LO_YEAR, WINDOW_HI_YEAR = 1880, 1906

# City-centre gradient for procedural births: buildings nearer Portage & Main
# tend to be born earlier (the city grew outward from the centre, roughly block
# by block). This is a SOFT bias, not a cutoff — an outskirts building can still
# predate a central one, it's just less likely. Strength is --center-bias
# (0 = uniform/off). Verified: Portage & Main sits inside the data extent, which
# reaches ~1.2 km (median) to ~1.9 km (95th pct) out from it.
PORTAGE_AND_MAIN = (-97.13835, 49.89543)  # WGS84 lng,lat
CENTER_RADIUS_M = 1800.0    # distance treated as fully "outskirts" (normalized dist = 1)
CENTER_BIAS_DEFAULT = 0.6   # how strongly centre-nearness pulls a birth earlier

# Winnipeg population by year (user-supplied via Gemini; census figures + boom-
# era estimates). Drives the procedural birth curve: the cumulative building
# count is warped to follow population growth, so births cluster in the real
# 1901-1906 wheat-boom surge (pop 42k -> 90k) instead of spreading evenly.
# Anchors outside the 1880-1906 window feed edge interpolation and future
# timeline extensions. Event notes: 1874 incorporation, 1885 CPR arrival,
# 1896 federal immigration campaigns, 1906 peak Prairie wheat-boom surge.
POP_ANCHORS = [
    (1856,    200), (1871,    241), (1874,   1869), (1881,   7985),
    (1886,  20238), (1891,  25639), (1896,  31649), (1901,  42340),
    (1906,  90153), (1911, 136035),
]


def year_of(iso):
    """Leading 4-digit year from an ISO date string, or None."""
    if not iso:
        return None
    head = str(iso)[:4]
    return int(head) if head.isdigit() else None


# Dates that are NOT real observations and must not be asserted as fact:
#   - the four survey-boundary placeholders Planimetro's match-merge invents
#     (mmRealDate rejects these too — keep the two lists in sync),
#   - the 1893-01-01 midpoint nomatch_dates.py stamps as a negative-evidence
#     ESTIMATE (its died_low/high = 1880/1906 mark it as such).
# Any of these -> treat the date as unknown and fall through to present-by /
# procedural, rather than trusting it.
PLACEHOLDER_DATES = {'1879-08-01', '1881-02-01', '1905-08-01', '1907-02-01', '1893-01-01'}
# Year-only values the user flagged as "might have made them up" — kept but
# flagged provisional, never labeled as sourced data.
SUSPECT_YEARS = {'1879', '1881', '1905', '1907'}


def classify_date(iso):
    """('real' | 'provisional' | 'placeholder', year|None) — see PLACEHOLDER_DATES."""
    y = year_of(iso)
    if y is None:
        return ('placeholder', None)
    s = str(iso).strip()
    if s in PLACEHOLDER_DATES:
        return ('placeholder', None)
    # Bare year (or year with an empty/00 tail) that the user flagged as suspect.
    if len(s) == 4 and s in SUSPECT_YEARS:
        return ('provisional', y)
    return ('real', y)


def unit_hash(uid, salt):
    """Deterministic float in [0, 1) from a uid + salt — the seed for procedural dates."""
    h = hashlib.sha256(f'{uid}|{salt}'.encode()).hexdigest()
    return int(h[:12], 16) / float(1 << 48)


def iso_from_fraction(frac, lo_year=WINDOW_LO_YEAR, hi_year=WINDOW_HI_YEAR):
    """Map a [0,1) fraction to an ISO date between (lo_year, hi_year], month/day spread too."""
    span_days = (hi_year - lo_year) * 365
    # Nudge off the exact lower bound so nothing shares a birthday with the survey line.
    day = 1 + int(frac * (span_days - 2))
    y = lo_year + day // 365
    rem = day % 365
    month = 1 + rem // 31
    dom = 1 + rem % 28
    return f'{y:04d}-{month:02d}-{dom:02d}'


def population(year):
    """Piecewise-linear Winnipeg population at a (fractional) year (see POP_ANCHORS)."""
    if year <= POP_ANCHORS[0][0]:
        return POP_ANCHORS[0][1]
    if year >= POP_ANCHORS[-1][0]:
        return POP_ANCHORS[-1][1]
    for (y0, p0), (y1, p1) in zip(POP_ANCHORS, POP_ANCHORS[1:]):
        if y0 <= year <= y1:
            return p0 + (p1 - p0) * (year - y0) / (y1 - y0)
    return POP_ANCHORS[-1][1]


def pop_year_from_fraction(frac, lo_year, hi_year):
    """
    Inverse population-CDF: map a fraction [0,1) to a fractional year in
    [lo, hi] such that the cumulative building count follows population growth.
    Bisection, since population() is monotonically increasing.
    """
    p0, p1 = population(lo_year), population(hi_year)
    if p1 <= p0:
        return lo_year + frac * (hi_year - lo_year)
    target = p0 + frac * (p1 - p0)
    lo, hi = lo_year, hi_year
    for _ in range(40):
        mid = (lo + hi) / 2
        if population(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def ring_area_m2(coords):
    """Rough planar area (m^2) of a lng/lat ring via equirectangular approximation."""
    if not coords or len(coords) < 4:
        return None
    import math
    lat0 = sum(p[1] for p in coords) / len(coords)
    k = math.cos(math.radians(lat0))
    m_per_deg = 111320.0
    pts = [(p[0] * k * m_per_deg, p[1] * m_per_deg) for p in coords]
    s = 0.0
    for i in range(len(pts) - 1):
        s += pts[i][0] * pts[i + 1][1] - pts[i + 1][0] * pts[i][1]
    return abs(s) / 2.0


def feature_area_m2(geom):
    try:
        if geom['type'] == 'Polygon':
            return ring_area_m2(geom['coordinates'][0])
        if geom['type'] == 'MultiPolygon':
            return sum(ring_area_m2(poly[0]) or 0 for poly in geom['coordinates']) or None
    except Exception:
        return None
    return None


def ring_centroid(coords):
    """Area-weighted centroid (lng,lat) of a ring; falls back to vertex mean."""
    A = cx = cy = 0.0
    for i in range(len(coords) - 1):
        x0, y0 = coords[i][0], coords[i][1]
        x1, y1 = coords[i + 1][0], coords[i + 1][1]
        cross = x0 * y1 - x1 * y0
        A += cross; cx += (x0 + x1) * cross; cy += (y0 + y1) * cross
    if A == 0:
        n = max(len(coords), 1)
        return (sum(p[0] for p in coords) / n, sum(p[1] for p in coords) / n)
    A *= 0.5
    return (cx / (6 * A), cy / (6 * A))


def feature_centroid(geom):
    try:
        if geom['type'] == 'Polygon':
            return ring_centroid(geom['coordinates'][0])
        if geom['type'] == 'MultiPolygon':
            best = max(geom['coordinates'], key=lambda poly: ring_area_m2(poly[0]) or 0)
            return ring_centroid(best[0])
    except Exception:
        return None
    return None


def metres_between(a, b):
    """Rough planar distance (m) between two lng/lat points."""
    import math
    lat0 = math.radians((a[1] + b[1]) / 2)
    k = math.cos(lat0)
    m_per_deg = 111320.0
    return math.hypot((a[0] - b[0]) * k * m_per_deg, (a[1] - b[1]) * m_per_deg)


def center_shifted_born(uid, geom, bias, growth='population'):
    """
    Procedural birth ISO combining two effects, both deterministic:

      1. City-centre gradient (bias): start from the uniform hash fraction, then
         shift it earlier for buildings near Portage & Main, later for the
         outskirts (frac += bias * (dist_norm - 0.5), dist_norm 0=centre..1=edge).
         Bounded so tails still cross — an edge building CAN precede a central one.
      2. Growth curve (growth='population'): warp that fraction through the
         inverse population-CDF so the cumulative building count tracks real
         population growth — births cluster in the 1901-1906 boom instead of
         spreading evenly. growth='uniform' skips this (even spread).

    So the centre gradient decides a building's PERCENTILE in the timeline, and
    the population curve decides what date that percentile maps to.
    """
    frac = unit_hash(uid, 'born')
    c = feature_centroid(geom)
    if c is not None and bias:
        dist_norm = min(metres_between(c, PORTAGE_AND_MAIN) / CENTER_RADIUS_M, 1.0)
        frac = min(max(frac + bias * (dist_norm - 0.5), 0.0), 1.0)
    if growth == 'population':
        y = pop_year_from_fraction(frac, WINDOW_LO_YEAR, WINDOW_HI_YEAR)
        frac = (y - WINDOW_LO_YEAR) / float(WINDOW_HI_YEAR - WINDOW_LO_YEAR)
    return iso_from_fraction(frac)


# Fields the assembler computes itself (add() writes them) — excluded from the
# source passthrough so they don't shadow the computed values.
_MANAGED_PROPS = {'born', 'died', 'born_low', 'born_high', 'born_basis',
                  'died_low', 'died_high', 'died_basis', 'cohort',
                  'matched_from', 'uid', 'pf_uid'}


def carry_render_props(src_props, geom):
    """
    Pass the source feature's properties straight through, minus the fields the
    assembler computes. The viewer needs more than a fixed handful — notably
    `type` (fences, walkways, bridges, lumber all render off it), plus
    no_windows, roof_type, floors, name, material, etc. Whitelisting silently
    dropped those; passing through keeps the data whole. area_m2 is filled in
    when the source lacks it; material defaults to 'unknown'.
    """
    out = {k: v for k, v in src_props.items()
           if v is not None and k not in _MANAGED_PROPS and not str(k).startswith('_')}
    out.setdefault('material', 'unknown')
    if out.get('area_m2') is None:
        a = feature_area_m2(geom)
        if a is not None:
            out['area_m2'] = a
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--in1880', default=os.path.join(DATA_DIR, 'mcphillips_1880.died_corrected.geojson'))
    ap.add_argument('--in1906', default=os.path.join(DATA_DIR, 'goad_1906.geojson'))
    ap.add_argument('--matches', default=os.path.join(DATA_DIR, 'mcphillips_goad_1906.matches.json'))
    ap.add_argument('--out', default=os.path.join(DATA_DIR, 'pastforward_2026.geojson'))
    ap.add_argument('--center-bias', type=float, default=CENTER_BIAS_DEFAULT,
                    help='0 = uniform procedural births; higher pulls births near Portage & Main '
                         'earlier (soft gradient, tails still cross). Default %(default)s.')
    ap.add_argument('--growth', choices=['population', 'uniform'], default='population',
                    help="'population' warps procedural births to Winnipeg's population curve "
                         '(boom-weighted); \'uniform\' spreads them evenly. Default %(default)s.')
    ap.add_argument('--other', default=os.path.join(DATA_DIR, 'other_*.geojson'),
                    help='glob of supplementary source files (photos, records, the fort, later '
                         'additions) merged in as cohort "other" with their own dates. Default %(default)s.')
    args = ap.parse_args()

    with open(args.in1880, encoding='utf-8') as f:
        fc1880 = json.load(f)
    with open(args.in1906, encoding='utf-8') as f:
        fc1906 = json.load(f)
    with open(args.matches, encoding='utf-8') as f:
        matches = json.load(f)['matches']

    # Key on pf_uid (stable across Planimetro edits), not the volatile numeric
    # id. Both source layers carry pf_uid on every feature; any without one is
    # skipped (and reported) rather than silently colliding on a None key.
    def by_uid(fc, label):
        out = {}
        missing = 0
        for ft in fc['features']:
            u = ft['properties'].get('pf_uid')
            if u:
                out[u] = ft
            else:
                missing += 1
        if missing:
            print(f'  WARNING: {missing} {label} features lack pf_uid — skipped. Re-export from Planimetro to stamp them.')
        return out

    by1880 = by_uid(fc1880, '1880')
    by1906 = by_uid(fc1906, '1906')

    # ── Cohort sets from the match graph ──────────────────────────────────
    # A "real" match has buildings on BOTH sides. Every 1906 id in one is a
    # continuation; record its 1880 partners so we can inherit the earliest born.
    matched_1906 = set()
    matched_1880 = set()
    partners_1880_of_1906 = {}   # 1906 pf_uid -> set of partner 1880 pf_uids
    for m in matches:
        a = m.get('uids_1880') or []      # pf_uids, stable across source renumbering
        b = m.get('uids_1906') or []
        if m.get('classification') == 'no_match' or not a or not b:
            continue
        if m.get('status') == 'rejected':
            continue  # honour the review: a rejected match is not a continuation
        for buid in b:
            matched_1906.add(buid)
            partners_1880_of_1906.setdefault(buid, set()).update(a)
        matched_1880.update(a)

    out_features = []
    stats = {'matched': 0, '1880_only': 0, '1906_only': 0, 'other': 0,
             'born_real': 0, 'born_provisional': 0, 'born_present_by': 0, 'born_procedural': 0,
             'died_real': 0, 'died_provisional': 0, 'died_estimate': 0, 'died_null': 0}

    def add(uid, geom, render, born_iso, born_lo, born_hi, born_basis,
            died_iso, died_lo, died_hi, died_basis, cohort, extra=None):
        props = dict(render)
        props['pf_uid'] = uid
        props['uid'] = uid                      # viewer colour hash contract
        props['cohort'] = cohort
        props['born'] = born_iso
        props['born_low'] = str(born_lo) if born_lo is not None else None
        props['born_high'] = str(born_hi) if born_hi is not None else None
        props['born_basis'] = born_basis
        props['died'] = died_iso                # None => still standing (shader sentinel)
        props['died_low'] = str(died_lo) if died_lo is not None else None
        props['died_high'] = str(died_hi) if died_hi is not None else None
        props['died_basis'] = died_basis
        if extra:
            props.update(extra)
        props = {k: v for k, v in props.items() if v is not None}
        out_features.append({'type': 'Feature', 'properties': props, 'geometry': geom})

    # ── 1906 features: matched (persisted) or 1906-only (boom) ─────────────
    for uid, ft in by1906.items():   # uid = the feature's own stable pf_uid
        geom = ft['geometry']
        render = carry_render_props(ft['properties'], geom)

        if uid in matched_1906:
            # born: earliest real 1880-partner born; else earliest provisional;
            # else present-by-1880. Placeholder partner dates are ignored.
            real_borns, prov_borns = [], []
            for pid in partners_1880_of_1906.get(uid, ()):
                iso = (by1880.get(pid) or {}).get('properties', {}).get('born')
                kind, y = classify_date(iso)
                if kind == 'real':
                    real_borns.append((y, iso))
                elif kind == 'provisional':
                    prov_borns.append((y, iso))
            if real_borns:
                by, biso = min(real_borns)
                born_iso, born_lo, born_hi, born_basis = biso, by, by, 'data_1880'
                stats['born_real'] += 1
            elif prov_borns:
                by, biso = min(prov_borns)
                born_iso, born_lo, born_hi, born_basis = biso, by, by, 'provisional_1880'
                stats['born_provisional'] += 1
            else:
                born_iso, born_lo, born_hi, born_basis = BORN_PRESENT_BY_1880, None, 1880, 'present_by_1880'
                stats['born_present_by'] += 1
            add(uid, geom, render, born_iso, born_lo, born_hi, born_basis,
                None, None, None, 'still_standing', 'matched',
                extra={'matched_from': {'uids_1880': sorted(partners_1880_of_1906.get(uid, ())), 'uid_1906': uid}})
            stats['matched'] += 1
            stats['died_null'] += 1
        else:
            # 1906-only: built between 1880 and 1906. died null (still standing).
            # Birth is procedural: centre-biased earlier + population-curve warped.
            born_iso = center_shifted_born(uid, geom, args.center_bias, args.growth)
            add(uid, geom, render, born_iso, WINDOW_LO_YEAR, WINDOW_HI_YEAR, 'procedural_infill',
                None, None, None, 'still_standing', '1906_only')
            stats['1906_only'] += 1
            stats['born_procedural'] += 1
            stats['died_null'] += 1

    # ── 1880-only features: demolished by 1906 ────────────────────────────
    for uid, ft in by1880.items():   # uid = the feature's own stable pf_uid
        if uid in matched_1880:
            continue  # represented by its 1906 continuation
        geom = ft['geometry']
        p = ft['properties']
        render = carry_render_props(p, geom)

        # born (placeholder dates ignored; suspect years kept as provisional).
        bkind, by = classify_date(p.get('born'))
        if bkind == 'real':
            born_iso, born_lo, born_hi, born_basis = p['born'], by, by, 'data_1880'
            stats['born_real'] += 1
        elif bkind == 'provisional':
            born_iso, born_lo, born_hi, born_basis = p['born'], by, by, 'provisional_1880'
            stats['born_provisional'] += 1
        else:
            born_iso, born_lo, born_hi, born_basis = BORN_PRESENT_BY_1880, None, 1880, 'present_by_1880'
            stats['born_present_by'] += 1

        # died: real if known; suspect year kept provisional; placeholder /
        # estimate / unknown -> negative-evidence procedural spread in (1880, 1906].
        dkind, dy = classify_date(p.get('died'))
        if dkind == 'real':
            died_iso, died_lo, died_hi, died_basis = p['died'], dy, dy, 'data_1880'
            stats['died_real'] += 1
        elif dkind == 'provisional':
            died_iso, died_lo, died_hi, died_basis = p['died'], dy, dy, 'provisional_1880'
            stats['died_provisional'] += 1
        else:
            died_iso = iso_from_fraction(unit_hash(uid, 'died'))
            died_lo, died_hi, died_basis = WINDOW_LO_YEAR, WINDOW_HI_YEAR, 'absent_from_1906_survey'
            stats['died_estimate'] += 1

        add(uid, geom, render, born_iso, born_lo, born_hi, born_basis,
            died_iso, died_lo, died_hi, died_basis, '1880_only')
        stats['1880_only'] += 1

    # ── Other sources (other_*.geojson) ───────────────────────────────────
    # Supplementary features that are NOT part of the two frozen surveys —
    # buildings known from photos/records, the fort, later additions, etc. They
    # carry their own pf_uid and their own dates, which are used VERBATIM (never
    # procedural — these are curated, not survey-inferred). Missing born => no
    # lower bound (visible from the start); missing died => still standing.
    other_paths = sorted(glob.glob(args.other))
    seen_other = set()
    for path in other_paths:
        with open(path, encoding='utf-8') as f:
            fco = json.load(f)
        label = os.path.basename(path)
        for ft in fco.get('features', []):
            uid = ft['properties'].get('pf_uid')
            if not uid:
                print(f'  WARNING: {label} has a feature with no pf_uid — skipped (re-export from Planimetro).')
                continue
            if uid in by1880 or uid in by1906:
                print(f'  WARNING: {label} pf_uid {uid[:8]}… is also in a survey layer — skipped (belongs in one place).')
                continue
            if uid in seen_other:
                continue
            seen_other.add(uid)
            geom = ft['geometry']
            p = ft['properties']
            render = carry_render_props(p, geom)
            by = year_of(p.get('born'))   # trusted verbatim; other sources are curated
            if by is not None:
                born_iso, born_lo, born_hi, born_basis = p['born'], by, by, 'data_other'
            else:
                born_iso, born_lo, born_hi, born_basis = None, None, None, None
            dy = year_of(p.get('died'))
            if dy is not None:
                died_iso, died_lo, died_hi, died_basis = p['died'], dy, dy, 'data_other'
            else:
                died_iso, died_lo, died_hi, died_basis = None, None, None, 'still_standing'
            add(uid, geom, render, born_iso, born_lo, born_hi, born_basis,
                died_iso, died_lo, died_hi, died_basis, 'other', extra={'other_source': label})
            stats['other'] += 1

    out = {'type': 'FeatureCollection', 'features': out_features}
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(out, f)

    print(f'Wrote {len(out_features)} features -> {args.out}')
    print(f"  cohorts:  matched={stats['matched']}  1880_only={stats['1880_only']}  1906_only={stats['1906_only']}  other={stats['other']}")
    print(f"  born:     real={stats['born_real']}  provisional={stats['born_provisional']}  present_by_1880={stats['born_present_by']}  procedural={stats['born_procedural']}")
    print(f"  died:     real={stats['died_real']}  provisional={stats['died_provisional']}  estimate={stats['died_estimate']}  still_standing(null)={stats['died_null']}")


if __name__ == '__main__':
    main()
