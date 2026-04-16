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
  python ukesm_pp_to_cmor.py
  # or point INPUT_FILES at your data and run directly.
"""

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

# Glob pattern (or list) of PP files to read.
INPUT_FILES = sorted(glob.glob("/path/to/pp/files/*.pp"))

# ── STASH codes ──────────────────────────────────────────────────────────────
# Screen-level (1.5 m) air temperature.
TAS_STASH = "m01s03i236"

# Precipitation: choose "single" if a total-precipitation field exists,
# or "components" to sum large-scale and convective parts separately.
PRECIP_MODE = "single"          # "single" | "components"
PR_STASH    = "m01s05i216"      # total precip flux  (PRECIP_MODE = "single")
PR_LS_STASH = "m01s04i203"      # large-scale precip (PRECIP_MODE = "components")
PR_CV_STASH = "m01s05i205"      # convective precip  (PRECIP_MODE = "components")

# ── CMIP DRS metadata ────────────────────────────────────────────────────────
MODEL      = "UKESM1-2-LL"
EXPERIMENT = "TerraFIRMA"
VARIANT    = "r1i1p1f1"
GRID       = "gn"
MIP_TABLE  = "Amon"             # Amon = atmosphere monthly/annual

# ── Output ───────────────────────────────────────────────────────────────────
OUTPUT_DIR  = "./output"
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


def load_variable(files: list, stash_code: str) -> iris.cube.Cube:
    """Load a single STASH field from *files* and concatenate into one cube."""
    constraint = iris.AttributeConstraint(STASH=stash_code)
    cubes = iris.load(files, constraint)
    if not cubes:
        raise RuntimeError(
            f"No cubes found for STASH {stash_code!r} in the supplied files."
        )
    # Remove attributes that differ between cubes (e.g. history, date) so
    # concatenation does not fail.
    iris.util.equalise_attributes(cubes)
    return cubes.concatenate_cube()


def load_precipitation(files: list) -> iris.cube.Cube:
    """Load total precipitation, either as one field or by summing components."""
    if PRECIP_MODE == "single":
        return load_variable(files, PR_STASH)

    if PRECIP_MODE == "components":
        ls_cube = load_variable(files, PR_LS_STASH)
        cv_cube = load_variable(files, PR_CV_STASH)
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


def apply_cmip_metadata(cube: iris.cube.Cube, cmip_key: str) -> iris.cube.Cube:
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


def save_cube(cube: iris.cube.Cube, var_name: str) -> None:
    """Save *cube* as NetCDF4 in chunks of CHUNK_YEARS years (or one file if None)."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

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
        filepath = os.path.join(OUTPUT_DIR, filename)
        iris.save(
            chunk_cube, filepath,
            fill_value=FILL_VALUE,
            chunksizes=CHUNK_SIZES,
            local_keys=["comment", "original_name", "cell_measures", "missing_value"],
        )
        print(f"  Written: {filepath}")


def main() -> None:
    """Load tas and pr from INPUT_FILES, apply CMIP metadata, and write NetCDF4."""
    if not INPUT_FILES:
        raise FileNotFoundError(
            "INPUT_FILES is empty. Update the INPUT_FILES glob pattern at the "
            "top of this script to point at your PP files."
        )

    print(f"Found {len(INPUT_FILES)} PP file(s).")
    print()

    # ── Surface air temperature ──────────────────────────────────────────────
    print("Loading tas (surface air temperature) …")
    tas = load_variable(INPUT_FILES, TAS_STASH)
    tas = apply_cmip_metadata(tas, "tas")
    print(f"  Cube: {tas.summary(shorten=True)}")
    save_cube(tas, "tas")
    print()

    # ── Precipitation ────────────────────────────────────────────────────────
    print(f"Loading pr (precipitation, mode={PRECIP_MODE!r}) …")
    pr = load_precipitation(INPUT_FILES)
    pr = apply_cmip_metadata(pr, "pr")
    print(f"  Cube: {pr.summary(shorten=True)}")
    save_cube(pr, "pr")
    print()

    print("Done.")


if __name__ == "__main__":
    main()
