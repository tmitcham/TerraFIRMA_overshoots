#!/usr/bin/env python3
"""
compare_netcdf.py — compare one variable between two netCDF files, year by year,
with detailed difference statistics.

Built for the case where two different workflows are supposed to produce the same
data per year. Defaults to a tolerance comparison (small floating-point noise from
different code paths is expected); pass --exact for bit-for-bit comparison.

For every common year it reports, over the absolute difference |A - B|:
  - how many / what fraction of valid points differ beyond tolerance
  - signed bias (mean of A - B), mean|Δ|, RMS, std
  - percentiles (p50, p90, p95, p99) and the max
  - the location (time / lat / lon ...) of the single worst cell, with the A and B
    values there
  - whether the NaN / fill-value pattern itself differs (a masking mismatch)
A final summary aggregates across years and gives a rough read on whether the
differences are broadly distributed or driven by a few outlier cells.

Examples
--------
    python compare_netcdf.py workflow_a.nc workflow_b.nc temperature
    python compare_netcdf.py a.nc b.nc temperature --units K
    python compare_netcdf.py a.nc b.nc temperature --rtol 1e-3
    python compare_netcdf.py a.nc b.nc temperature --exact
    python compare_netcdf.py a.nc b.nc tas --var-b temperature --csv report.csv

Exit code is 0 if every common year matches, 1 if any year differs (or a file/var
problem is found), so it can be used in scripts and CI.
"""

import argparse
import csv
import sys

import numpy as np
import xarray as xr


# --------------------------------------------------------------------------- #
# Arguments
# --------------------------------------------------------------------------- #
def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Compare one variable between two netCDF files, year by year.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("file_a", help="first netCDF file")
    p.add_argument("file_b", help="second netCDF file")
    p.add_argument("var", help="variable name to compare")
    p.add_argument("--var-b", default=None,
                   help="variable name in file_b, if it differs from VAR")
    p.add_argument("--rtol", type=float, default=1e-5, help="relative tolerance")
    p.add_argument("--atol", type=float, default=1e-8, help="absolute tolerance")
    p.add_argument("--exact", action="store_true",
                   help="require bit-for-bit equality instead of tolerance")
    p.add_argument("--time-dim", default="time",
                   help="name of the time coordinate to group years by")
    p.add_argument("--no-sort", action="store_true",
                   help="do NOT sort spatial dims before comparing (by default they "
                        "are sorted so a flipped lat/lon axis still matches)")
    p.add_argument("--units", default="",
                   help="unit label to print after numbers (e.g. K), cosmetic only")
    p.add_argument("--top", type=int, default=5,
                   help="how many worst years to highlight in the summary")
    p.add_argument("--csv", default=None,
                   help="optional path to write the full per-year stats as CSV")
    return p.parse_args(argv)


# --------------------------------------------------------------------------- #
# IO
# --------------------------------------------------------------------------- #
def load_var(path, var, time_dim, sort):
    """Open a file and return the requested DataArray, optionally spatially sorted."""
    try:
        ds = xr.open_dataset(path)
    except (FileNotFoundError, OSError) as e:
        sys.exit(f"ERROR: could not open {path!r}: {e}")
    if var not in ds.variables:
        avail = ", ".join(map(str, ds.data_vars))
        sys.exit(f"ERROR: variable {var!r} not found in {path!r}. "
                 f"Available data variables: {avail}")
    da = ds[var]
    if sort:
        spatial = [d for d in da.dims if d != time_dim]
        if spatial:
            da = da.sortby(spatial)
    return da


# --------------------------------------------------------------------------- #
# Stats
# --------------------------------------------------------------------------- #
def compute_stats(ablk, bblk, exact, rtol, atol):
    """Compare two aligned DataArrays. Returns (matched, info_dict)."""
    av = ablk.values
    bv = bblk.values

    if av.shape != bv.shape:
        return False, {"reason": "shape", "shape_a": av.shape, "shape_b": bv.shape}

    if exact:
        matched = np.array_equal(av, bv)
    else:
        matched = np.allclose(av, bv, rtol=rtol, atol=atol, equal_nan=True)

    af = av.astype("float64")
    bf = bv.astype("float64")

    valid = np.isfinite(af) & np.isfinite(bf)
    n_total = av.size
    n_valid = int(valid.sum())

    nan_a = int(np.sum(~np.isfinite(af)))
    nan_b = int(np.sum(~np.isfinite(bf)))
    nan_pattern_same = np.array_equal(~np.isfinite(af), ~np.isfinite(bf))

    info = {
        "reason": "values",
        "n_total": n_total,
        "n_valid": n_valid,
        "nan_a": nan_a,
        "nan_b": nan_b,
        "nan_pattern_same": nan_pattern_same,
        "n_diff": 0,
        "frac_diff": 0.0,
        "bias": float("nan"),
        "mean_abs": float("nan"),
        "rms": float("nan"),
        "std": float("nan"),
        "p50": float("nan"), "p90": float("nan"),
        "p95": float("nan"), "p99": float("nan"),
        "max_abs": float("nan"),
        "max_loc": None, "a_at_max": float("nan"), "b_at_max": float("nan"),
    }

    if n_valid == 0:
        return matched, info

    with np.errstate(invalid="ignore"):
        signed = af - bf
        d_full = np.abs(signed)

    d_valid = d_full[valid]
    s_valid = signed[valid]

    if exact:
        close = (af == bf)
    else:
        close = np.isclose(af, bf, rtol=rtol, atol=atol, equal_nan=True)
    n_diff = int(np.sum(~close & valid))

    info.update({
        "n_diff": n_diff,
        "frac_diff": n_diff / n_valid if n_valid else 0.0,
        "bias": float(np.mean(s_valid)),
        "mean_abs": float(np.mean(d_valid)),
        "rms": float(np.sqrt(np.mean(d_valid ** 2))),
        "std": float(np.std(d_valid)),
        "p50": float(np.percentile(d_valid, 50)),
        "p90": float(np.percentile(d_valid, 90)),
        "p95": float(np.percentile(d_valid, 95)),
        "p99": float(np.percentile(d_valid, 99)),
        "max_abs": float(np.nanmax(d_full)),
    })

    # Locate the single worst cell and label it with coordinates from A.
    flat = int(np.nanargmax(d_full))
    idx = np.unravel_index(flat, d_full.shape)
    loc = {}
    for dim, i in zip(ablk.dims, idx):
        if dim in ablk.coords and ablk[dim].ndim == 1:
            loc[dim] = _fmt_coord(ablk[dim].values[i])
        else:
            loc[dim] = f"[{i}]"
    info["max_loc"] = loc
    info["a_at_max"] = float(af[idx])
    info["b_at_max"] = float(bf[idx])

    return matched, info


def _fmt_coord(v):
    """Render a coordinate value compactly (dates as YYYY-MM-DD, numbers trimmed)."""
    if isinstance(v, np.datetime64):
        return str(np.datetime_as_string(v, unit="D"))
    if isinstance(v, (np.floating, float)):
        return f"{float(v):g}"
    return str(v)


# --------------------------------------------------------------------------- #
# Printing
# --------------------------------------------------------------------------- #
def print_year(label, matched, info, units):
    u = f" {units}" if units else ""
    if info.get("reason") == "shape":
        print(f"{label}: SHAPE mismatch {info['shape_a']} vs {info['shape_b']}")
        return
    if matched:
        mx = info["max_abs"]
        extra = f"  (max|Δ|={mx:.2e}{u})" if np.isfinite(mx) else ""
        print(f"{label}: match{extra}")
        return

    print(f"{label}: DIFFER  diff {info['frac_diff']*100:5.1f}% "
          f"({info['n_diff']:,}/{info['n_valid']:,})")
    print(f"    |Δ| mean={info['mean_abs']:.3f} rms={info['rms']:.3f} "
          f"p50={info['p50']:.3f} p90={info['p90']:.3f} p99={info['p99']:.3f} "
          f"max={info['max_abs']:.3f}{u}   bias(A-B)={info['bias']:+.3f}{u}")
    if info.get("max_loc"):
        loc = " ".join(f"{k}={v}" for k, v in info["max_loc"].items())
        print(f"    worst cell @ {loc}  (A={info['a_at_max']:.3f} "
              f"B={info['b_at_max']:.3f}{u})")
    if not info.get("nan_pattern_same", True):
        print(f"    NaN/fill pattern differs: A has {info['nan_a']:,} NaN, "
              f"B has {info['nan_b']:,} NaN — possible masking mismatch")


def print_summary(results, units, top):
    """results: list of (label, matched, info) for value-comparable blocks."""
    u = f" {units}" if units else ""
    differ = [(lab, inf) for lab, m, inf in results
              if not m and inf.get("reason") == "values"]
    matched_n = sum(1 for _, m, inf in results if m)
    print("-" * 64)
    print(f"years/blocks compared: {len(results)}   "
          f"match: {matched_n}   differ: {len(differ)}")

    if not differ:
        print("RESULT: all common years match")
        return

    overall_max = max(inf["max_abs"] for _, inf in differ)
    worst_year = max(differ, key=lambda t: t[1]["max_abs"])[0]
    mean_of_meanabs = float(np.mean([inf["mean_abs"] for _, inf in differ]))
    median_of_p50 = float(np.median([inf["p50"] for _, inf in differ]))

    print(f"overall worst |Δ| = {overall_max:.3f}{u} in {worst_year}")
    print(f"typical year: mean|Δ|≈{mean_of_meanabs:.3f}{u}, "
          f"median p50≈{median_of_p50:.3f}{u}")

    # Rough read on shape of the differences.
    ratio = median_of_p50 / overall_max if overall_max else 0.0
    if ratio >= 0.5:
        print("INTERPRETATION: differences are broadly distributed — most cells are "
              "off by an amount comparable to the max, so this looks like a "
              "systematic disagreement (averaging, packing, version, or a "
              "time/period offset), not a few bad cells.")
    elif ratio <= 0.1:
        print("INTERPRETATION: the max is an outlier — typical differences are far "
              "below it, so the large value likely comes from a few cells "
              "(edges/coastlines/poles → regridding or masking), while most of the "
              "field agrees fairly well.")
    else:
        print("INTERPRETATION: mixed — a moderate widespread offset plus some "
              "larger localized differences.")

    if top:
        print(f"\nworst {min(top, len(differ))} years by max|Δ|:")
        for lab, inf in sorted(differ, key=lambda t: t[1]["max_abs"],
                               reverse=True)[:top]:
            print(f"  {lab}: max={inf['max_abs']:.3f}{u} "
                  f"mean={inf['mean_abs']:.3f}{u} "
                  f"diff={inf['frac_diff']*100:.1f}%")


def write_csv(path, results):
    cols = ["label", "matched", "n_total", "n_valid", "n_diff", "frac_diff",
            "bias", "mean_abs", "rms", "std", "p50", "p90", "p95", "p99",
            "max_abs", "max_loc", "a_at_max", "b_at_max",
            "nan_a", "nan_b", "nan_pattern_same"]
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for label, matched, inf in results:
            if inf.get("reason") == "shape":
                w.writerow([label, matched] + [""] * (len(cols) - 2))
                continue
            loc = inf.get("max_loc") or {}
            loc_str = ";".join(f"{k}={v}" for k, v in loc.items())
            w.writerow([
                label, matched, inf["n_total"], inf["n_valid"], inf["n_diff"],
                f"{inf['frac_diff']:.6g}", f"{inf['bias']:.6g}",
                f"{inf['mean_abs']:.6g}", f"{inf['rms']:.6g}", f"{inf['std']:.6g}",
                f"{inf['p50']:.6g}", f"{inf['p90']:.6g}", f"{inf['p95']:.6g}",
                f"{inf['p99']:.6g}", f"{inf['max_abs']:.6g}", loc_str,
                f"{inf['a_at_max']:.6g}", f"{inf['b_at_max']:.6g}",
                inf["nan_a"], inf["nan_b"], inf["nan_pattern_same"],
            ])
    print(f"\nwrote per-year stats to {path}")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main(argv=None):
    args = parse_args(argv)
    var_b = args.var_b or args.var
    sort = not args.no_sort

    a = load_var(args.file_a, args.var, args.time_dim, sort)
    b = load_var(args.file_b, var_b, args.time_dim, sort)

    print(f"A: {args.file_a}  var={args.var}  dtype={a.dtype}  dims={dict(a.sizes)}")
    print(f"B: {args.file_b}  var={var_b}  dtype={b.dtype}  dims={dict(b.sizes)}")
    mode = ("exact (bit-for-bit)" if args.exact
            else f"tolerance rtol={args.rtol} atol={args.atol}")
    print(f"comparison mode: {mode}")
    if a.dtype != b.dtype and not args.exact:
        print(f"NOTE: dtypes differ ({a.dtype} vs {b.dtype}); "
              "expect differences near the lower-precision floor.")
    print("-" * 64)

    has_time = args.time_dim in a.dims and args.time_dim in b.dims
    results = []
    any_diff = False

    if not has_time:
        matched, info = compute_stats(a, b, args.exact, args.rtol, args.atol)
        results.append(("all", matched, info))
        print_year("all", matched, info, args.units)
        any_diff = not matched
    else:
        ga = dict(tuple(a.groupby(f"{args.time_dim}.year")))
        gb = dict(tuple(b.groupby(f"{args.time_dim}.year")))
        common = sorted(set(ga) & set(gb))
        if not common:
            print("ERROR: the two files share no common years.")
            any_diff = True

        for year in common:
            matched, info = compute_stats(ga[year], gb[year],
                                          args.exact, args.rtol, args.atol)
            results.append((str(year), matched, info))
            print_year(str(year), matched, info, args.units)
            if not matched:
                any_diff = True

        only_a = sorted(set(ga) - set(gb))
        only_b = sorted(set(gb) - set(ga))
        if only_a:
            print(f"years only in A: {only_a}")
            any_diff = True
        if only_b:
            print(f"years only in B: {only_b}")
            any_diff = True

    print_summary(results, args.units, args.top)

    if args.csv:
        write_csv(args.csv, results)

    return 1 if any_diff else 0


if __name__ == "__main__":
    sys.exit(main())