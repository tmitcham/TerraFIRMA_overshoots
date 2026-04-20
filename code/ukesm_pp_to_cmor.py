"""
ukesm_pp_to_cmor.py
-------------------
Read monthly PP files from the Met Office UKESM model and write
CMIP-compliant / CMORised NetCDF4 output files for:

  tas - Near-Surface Air Temperature  (standard_name: air_temperature)
  pr  - Precipitation                 (standard_name: precipitation_flux)

Output files follow the CMIP Data Reference Syntax (DRS):
  <var>_<table>_<model>_<experiment>_<variant>_<grid>_<YYYYMM-YYYYMM>.nc

Dependencies
------------
  conda install -c conda-forge iris cf-units
  (iris >= 3.x  /  cf-units >= 3.x)

Usage
-----
  python ukesm_pp_to_cmor.py /path/to/pp/files/

  Output is written to $DATADIR/cmor_outputs/.
"""

import argparse
import glob
import os
from datetime import datetime, timezone

import numpy as np
import iris
import iris.cube
import iris.util
import iris.coords
import cf_units

# ── User configuration ───────────────────────────────────────────────────────

# ── STASH codes ──────────────────────────────────────────────────────────────
# Screen-level (1.5 m) air temperature.
TAS_STASH          = "m01s03i236"
TAS_TIME_INTERVAL  = "6 hour"   # cell_method interval to select for tas

# Precipitation: choose "single" if a total-precipitation field exists,
# or "components" to sum large-scale and convective parts separately.
PRECIP_MODE       = "single"    # "single" | "components"
PR_STASH          = "m01s05i216"    # total precip flux  (PRECIP_MODE = "single")
PR_LS_STASH       = "m01s04i203"    # large-scale precip (PRECIP_MODE = "components")
PR_CV_STASH       = "m01s05i205"    # convective precip  (PRECIP_MODE = "components")
PR_TIME_INTERVAL  = "24 hour"   # cell_method interval to select for pr

# ── CMIP DRS metadata ────────────────────────────────────────────────────────
MODEL      = "UKESM1-2-LL"
EXPERIMENT = "TerraFIRMA"
VARIANT    = "r1i1p1f1"
GRID       = "gn"
MIP_TABLE  = "Amon"             # Amon = atmosphere monthly/annual

# ── Output ───────────────────────────────────────────────────────────────────
# OUTPUT_DIR is derived at runtime from $DATADIR/cmor_outputs/ (see main()).
CHUNK_YEARS = 50    # number of years per output file (set to None for one file)
FILL_VALUE  = 1e20  # missing_value and _FillValue written to every output variable
CHUNK_SIZES = None  # NetCDF4 chunk sizes, e.g. [12, 144, 192] for (time, lat, lon)
                    # None lets the netCDF4 library choose; set to control _ChunkSizes

# ── CMIP variable metadata ───────────────────────────────────────────────────
CMIP_META = {
    "tas": {
        "standard_name": "air_temperature",
        "long_name":     "Near-Surface Air Temperature",
        "var_name":      "tas",
        "units":         "K",
        "comment":       "Monthly mean near-surface (usually 2 m) air temperature.",
        "original_name": TAS_STASH,
        "cell_measures": "area: areacella",
    },
    "pr": {
        "standard_name": "precipitation_flux",
        "long_name":     "Precipitation",
        "var_name":      "pr",
        "units":         "kg m-2 s-1",
        "comment":       "Monthly mean precipitation flux.",
        "original_name": (
            PR_STASH if PRECIP_MODE == "single"
            else f"{PR_LS_STASH} + {PR_CV_STASH}"
        ),
        "cell_measures": "area: areacella",
    },
}

# ── End of configuration ─────────────────────────────────────────────────────


def filter_by_time_interval(
    cubes: iris.cube.CubeList, interval: str, stash_code: str
) -> iris.cube.CubeList:
    """Return only cubes whose time cell_method has the given interval.

    Raises RuntimeError if no cubes match, so the caller always gets a
    non-empty CubeList or an informative error.
    """
    matched = iris.cube.CubeList(
        c for c in cubes
        if any(
            "time" in cm.coord_names and interval in (cm.intervals or ())
            for cm in c.cell_methods
        )
    )
    if not matched:
        available = sorted({
            iv
            for c in cubes
            for cm in c.cell_methods
            if "time" in cm.coord_names
            for iv in (cm.intervals or ())
        })
        raise RuntimeError(
            f"No cube for STASH {stash_code!r} has time cell_method interval "
            f"{interval!r}. Available interval(s): {available}"
        )
    return matched


def load_variable(files: list, stash_code: str, time_interval: str) -> iris.cube.Cube:
    """Load a single STASH field from *files* and concatenate into one cube.

    Only cubes whose time cell_method interval matches *time_interval* are kept,
    so that when the PP files contain multiple averaging periods for the same
    STASH code the correct one is always selected.
    """
    constraint = iris.AttributeConstraint(STASH=stash_code)
    print(f"  Reading {len(files)} file(s):")
    cubes = iris.cube.CubeList()
    for f in files:
        print(f"    {os.path.basename(f)}", flush=True)
        cubes.extend(iris.load(f, constraint))
    if not cubes:
        raise RuntimeError(
            f"No cubes found for STASH {stash_code!r} in the supplied files."
        )
    cubes = filter_by_time_interval(cubes, time_interval, stash_code)
    # Remove attributes that differ between cubes (e.g. history, date) so
    # concatenation does not fail.
    iris.util.equalise_attributes(cubes)
    return cubes.concatenate_cube()


def load_precipitation(files: list) -> iris.cube.Cube:
    """Load total precipitation, either as one field or by summing components."""
    if PRECIP_MODE == "single":
        return load_variable(files, PR_STASH, PR_TIME_INTERVAL)

    if PRECIP_MODE == "components":
        ls_cube = load_variable(files, PR_LS_STASH, PR_TIME_INTERVAL)
        cv_cube = load_variable(files, PR_CV_STASH, PR_TIME_INTERVAL)
        total   = ls_cube + cv_cube          # iris broadcasts & preserves coords
        return total

    raise ValueError(
        f"PRECIP_MODE must be 'single' or 'components', got {PRECIP_MODE!r}"
    )


def promote_coords_to_double(cube: iris.cube.Cube) -> None:
    """Promote all coordinate points and bounds to float64 (CMIP requirement)."""
    for coord in cube.coords():
        if coord.points.dtype != np.float64:
            new_points = coord.points.astype(np.float64)
            new_bounds = (
                coord.bounds.astype(np.float64) if coord.has_bounds() else None
            )
            cube.replace_coord(coord.copy(points=new_points, bounds=new_bounds))


def apply_cmip_metadata(cube: iris.cube.Cube, cmip_key: str, suite_id: str) -> iris.cube.Cube:
    """Apply CMIP variable metadata and global attributes to *cube* in-place."""
    meta = CMIP_META[cmip_key]

    # ── Coordinate precision (CMIP requires double) ───────────────────────────
    promote_coords_to_double(cube)

    # ── Variable metadata ────────────────────────────────────────────────────
    cube.standard_name = meta["standard_name"]
    cube.long_name     = meta["long_name"]
    cube.var_name      = meta["var_name"]

    # ── Unit conversion ──────────────────────────────────────────────────────
    target_units = cf_units.Unit(meta["units"])
    current_units = cube.units

    if current_units != target_units:
        # Celsius → Kelvin
        if current_units == cf_units.Unit("celsius") and target_units == cf_units.Unit("K"):
            cube.convert_units("K")
        # mm/day → kg m-2 s-1  (1 mm/day = 1/86400 kg m-2 s-1, ρ_water = 1000 kg m-3)
        elif current_units == cf_units.Unit("mm day-1") and target_units == cf_units.Unit("kg m-2 s-1"):
            cube.data = cube.data / 86400.0
            cube.units = target_units
        else:
            # Attempt a generic iris unit conversion (works for dimensionally
            # compatible units such as Pa → hPa, kg/kg → g/kg, etc.).
            try:
                cube.convert_units(meta["units"])
            except ValueError:
                print(
                    f"  WARNING: cannot auto-convert {current_units} → {meta['units']}. "
                    "Units left unchanged — please check manually."
                )
    else:
        cube.units = target_units

    # ── Cell methods: CMIP standard "area: time: mean" ───────────────────────
    # Replace any pre-existing time: mean with the full area: time: mean form.
    cmip_cm     = iris.coords.CellMethod("mean", coords=["area", "time"])
    filtered_cm = tuple(
        cm for cm in cube.cell_methods
        if not (cm.method == "mean" and set(cm.coord_names) <= {"time", "area"})
    )
    cube.cell_methods = filtered_cm + (cmip_cm,)

    # ── Variable attributes ───────────────────────────────────────────────────
    cube.attributes["comment"]       = meta["comment"]
    cube.attributes["original_name"] = meta["original_name"]
    cube.attributes["cell_measures"] = meta["cell_measures"]
    cube.attributes["missing_value"] = FILL_VALUE

    # ── CMIP global attributes ────────────────────────────────────────────────
    cube.attributes.update(
        {
            "Conventions":    "CF-1.7",
            "source_model":   MODEL,
            "experiment_id":  EXPERIMENT,
            "variant_label":  VARIANT,
            "grid_label":     GRID,
            "mip_table":      MIP_TABLE,
            "mo_runid":       suite_id,
            "creation_date":  datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
    )

    return cube


def time_range_str(cube: iris.cube.Cube) -> str:
    """Return a YYYYMM-YYYYMM string for use in a CMIP DRS filename."""
    time_coord = cube.coord("time")
    if not time_coord.units.calendar:
        raise RuntimeError("Time coordinate has no calendar — cannot extract dates.")
    dates = time_coord.units.num2date(time_coord.points)
    first, last = dates[0], dates[-1]
    return f"{first.year:04d}{first.month:02d}-{last.year:04d}{last.month:02d}"


def build_drs_filename(var_name: str, time_str: str) -> str:
    """Return a CMIP DRS filename (without directory)."""
    return f"{var_name}_{MIP_TABLE}_{MODEL}_{EXPERIMENT}_{VARIANT}_{GRID}_{time_str}.nc"


def save_cube(cube: iris.cube.Cube, var_name: str, output_dir: str) -> None:
    """Save *cube* as NetCDF4 in chunks of CHUNK_YEARS years (or one file if None)."""
    os.makedirs(output_dir, exist_ok=True)

    time_coord = cube.coord("time")
    dates = time_coord.units.num2date(time_coord.points)
    years = sorted({d.year for d in dates})

    if CHUNK_YEARS is None:
        chunks = [years]
    else:
        chunks = [
            years[i : i + CHUNK_YEARS]
            for i in range(0, len(years), CHUNK_YEARS)
        ]

    for chunk in chunks:
        yr_min, yr_max = chunk[0], chunk[-1]
        chunk_constraint = iris.Constraint(
            time=lambda cell, lo=yr_min, hi=yr_max: lo <= cell.point.year <= hi
        )
        chunk_cube = cube.extract(chunk_constraint)
        if chunk_cube is None:
            print(f"  WARNING: no data found for years {yr_min}-{yr_max}, skipping.")
            continue
        time_str = time_range_str(chunk_cube)
        filename = build_drs_filename(var_name, time_str)
        filepath = os.path.join(output_dir, filename)
        iris.save(
            chunk_cube, filepath,
            fill_value=FILL_VALUE,
            chunksizes=CHUNK_SIZES,
            local_keys=["comment", "original_name", "cell_measures", "missing_value", "mo_runid"],
        )
        print(f"  Written: {filepath}")


def main() -> None:
    """Load tas and pr from a PP directory, apply CMIP metadata, and write NetCDF4."""
    parser = argparse.ArgumentParser(
        description="CMORise UKESM PP files to NetCDF4."
    )
    parser.add_argument(
        "pp_dir",
        help="Directory containing the input PP files.",
    )
    args = parser.parse_args()

    input_files = sorted(glob.glob(os.path.join(args.pp_dir, "*.pp")))
    if not input_files:
        raise FileNotFoundError(
            f"No .pp files found in {args.pp_dir!r}."
        )

    # Derive suite ID from the path: .../pp/u-cs568/ → "u-cs568"
    suite_id = os.path.basename(os.path.abspath(args.pp_dir))

    datadir = os.environ.get("DATADIR")
    if not datadir:
        raise EnvironmentError("The DATADIR environment variable is not set.")
    output_dir = os.path.join(datadir, "cmor_outputs")

    print(f"Suite  : {suite_id}")
    print(f"Input  : {args.pp_dir}  ({len(input_files)} file(s))")
    print(f"Output : {output_dir}")
    print()

    # ── Surface air temperature ──────────────────────────────────────────────
    print("Loading tas (surface air temperature) …")
    tas = load_variable(input_files, TAS_STASH, TAS_TIME_INTERVAL)
    tas = apply_cmip_metadata(tas, "tas", suite_id)
    print(f"  Cube: {tas.summary(shorten=True)}")
    save_cube(tas, "tas", output_dir)
    print()

    # ── Precipitation ────────────────────────────────────────────────────────
    print(f"Loading pr (precipitation, mode={PRECIP_MODE!r}) …")
    pr = load_precipitation(input_files)
    pr = apply_cmip_metadata(pr, "pr", suite_id)
    print(f"  Cube: {pr.summary(shorten=True)}")
    save_cube(pr, "pr", output_dir)
    print()

    print("Done.")


if __name__ == "__main__":
    main()
