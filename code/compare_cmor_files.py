#!/usr/bin/env python3
"""
compare_netcdf.py — compare one variable between two netCDF files, year by year.

Built for the case where two different workflows are supposed to produce the same
data per year. Defaults to a tolerance comparison (floating-point noise from
different code paths is expected); pass --exact for bit-for-bit comparison.

Examples
--------
    python compare_netcdf.py workflow_a.nc workflow_b.nc temperature
    python compare_netcdf.py a.nc b.nc temperature --rtol 1e-6 --atol 1e-9
    python compare_netcdf.py a.nc b.nc temperature --exact
    python compare_netcdf.py a.nc b.nc tas --var-b temperature   # different names

Exit code is 0 if every common year matches, 1 if any year differs (or a file/var
problem is found), so it can be used in scripts and CI.
"""

import argparse
import sys

import numpy as np
import xarray as xr


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Compare one variable between two netCDF files, year by year.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("file_a", help="first netCDF file")
    p.add_argument("file_b", help="second netCDF file")
    p.add_argument("var", help="variable name to compare")
    p.add_argument(
        "--var-b",
        default=None,
        help="variable name in file_b, if it differs from VAR (defaults to VAR)",
    )
    p.add_argument("--rtol", type=float, default=1e-5, help="relative tolerance")
    p.add_argument("--atol", type=float, default=1e-8, help="absolute tolerance")
    p.add_argument(
        "--exact",
        action="store_true",
        help="require bit-for-bit equality instead of tolerance",
    )
    p.add_argument(
        "--time-dim",
        default="time",
        help="name of the time coordinate to group years by",
    )
    p.add_argument(
        "--no-sort",
        action="store_true",
        help="do NOT sort spatial dims before comparing "
        "(by default they are sorted so a flipped lat/lon axis still matches)",
    )
    return p.parse_args(argv)


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


def compare_block(av, bv, exact, rtol, atol):
    """Compare two numpy arrays. Returns (matched, info_dict)."""
    if av.shape != bv.shape:
        return False, {"reason": "shape", "shape_a": av.shape, "shape_b": bv.shape}

    if exact:
        matched = np.array_equal(av, bv)
    else:
        matched = np.allclose(av, bv, rtol=rtol, atol=atol, equal_nan=True)

    if matched:
        return True, {}

    # Quantify the difference for the report.
    elementwise = np.isclose(av, bv, rtol=rtol, atol=atol, equal_nan=True)
    n_diff = int(np.sum(~elementwise))
    with np.errstate(invalid="ignore"):
        diff = np.abs(av.astype("float64") - bv.astype("float64"))
    max_abs = float(np.nanmax(diff)) if diff.size else float("nan")
    # Is the difference purely a NaN / fill-value masking mismatch?
    nan_pattern_same = np.array_equal(np.isnan(av), np.isnan(bv))
    return False, {
        "reason": "values",
        "n_diff": n_diff,
        "max_abs": max_abs,
        "nan_pattern_same": nan_pattern_same,
    }


def main(argv=None):
    args = parse_args(argv)
    var_b = args.var_b or args.var
    sort = not args.no_sort

    a = load_var(args.file_a, args.var, args.time_dim, sort)
    b = load_var(args.file_b, var_b, args.time_dim, sort)

    print(f"A: {args.file_a}  var={args.var}  dtype={a.dtype}  dims={dict(a.sizes)}")
    print(f"B: {args.file_b}  var={var_b}  dtype={b.dtype}  dims={dict(b.sizes)}")
    mode = "exact (bit-for-bit)" if args.exact else f"tolerance rtol={args.rtol} atol={args.atol}"
    print(f"Comparison mode: {mode}")
    if a.dtype != b.dtype and not args.exact:
        print(f"NOTE: dtypes differ ({a.dtype} vs {b.dtype}); "
              "expect differences near the lower-precision floor.")
    print("-" * 60)

    has_time = args.time_dim in a.dims and args.time_dim in b.dims
    any_diff = False

    if not has_time:
        # No time dimension to group on: compare the whole arrays once.
        matched, info = compare_block(a.values, b.values, args.exact, args.rtol, args.atol)
        if matched:
            print("whole array: match")
        else:
            any_diff = True
            _print_diff("whole array", info)
        return 1 if any_diff else 0

    ga = dict(tuple(a.groupby(f"{args.time_dim}.year")))
    gb = dict(tuple(b.groupby(f"{args.time_dim}.year")))
    common = sorted(set(ga) & set(gb))

    if not common:
        print("ERROR: the two files share no common years.")
        any_diff = True

    for year in common:
        matched, info = compare_block(
            ga[year].values, gb[year].values, args.exact, args.rtol, args.atol
        )
        if matched:
            print(f"{year}: match")
        else:
            any_diff = True
            _print_diff(str(year), info)

    only_a = sorted(set(ga) - set(gb))
    only_b = sorted(set(gb) - set(ga))
    if only_a:
        print(f"years only in A: {only_a}")
        any_diff = True
    if only_b:
        print(f"years only in B: {only_b}")
        any_diff = True

    print("-" * 60)
    print("RESULT: DIFFERENCES FOUND" if any_diff else "RESULT: all common years match")
    return 1 if any_diff else 0


def _print_diff(label, info):
    if info.get("reason") == "shape":
        print(f"{label}: SHAPE mismatch {info['shape_a']} vs {info['shape_b']}")
    else:
        msg = (f"{label}: DIFFER  max|Δ|={info['max_abs']:.3e}  "
               f"n_diff={info['n_diff']}")
        if not info.get("nan_pattern_same", True):
            msg += "  (NaN/fill-value pattern also differs — check masking)"
        print(msg)


if __name__ == "__main__":
    sys.exit(main())