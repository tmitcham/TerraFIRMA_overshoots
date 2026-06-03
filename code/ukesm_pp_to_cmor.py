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
import uuid
from collections import defaultdict
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
TAS_TIME_INTERVAL  = "1 hour"   # cell_method interval to select for tas

# Precipitation: choose "single" if a total-precipitation field exists,
# or "components" to sum large-scale and convective parts separately.
PRECIP_MODE       = "single"    # "single" | "components"
PR_STASH          = "m01s05i216"    # total precip flux  (PRECIP_MODE = "single")
PR_LS_STASH       = "m01s04i203"    # large-scale precip (PRECIP_MODE = "components")
PR_CV_STASH       = "m01s05i205"    # convective precip  (PRECIP_MODE = "components")
PR_TIME_INTERVAL  = "1 hour"   # cell_method interval to select for pr

# ── CMIP DRS metadata ────────────────────────────────────────────────────────
SOURCE_ID  = "UKESM1-2-LL"
EXPERIMENT = "TerraFIRMA"
VARIANT    = "r1i1p1f1"
GRID       = "gn"
MIP_TABLE  = "Amon"             # Amon = atmosphere monthly/annual

# ── Model / institution metadata ─────────────────────────────────────────────
SOURCE             = "UKESM1-2-LL (2024)"
SOURCE_TYPE        = "AOGCM AER"
INSTITUTION        = "Met Office Hadley Centre, Fitzroy Road, Exeter, Devon, EX1 3PB, UK"
INSTITUTION_ID     = "MOHC"
GRID_DESCRIPTION   = "Native N96 grid; 192 x 144 longitude/latitude"
NOMINAL_RESOLUTION = "250 km"

# ── Project / CV metadata ─────────────────────────────────────────────────────
MIP_ERA        = "GCModelDev"
CV_VERSION     = "GCModelDev v0.0.17"
ACTIVITY_ID    = "TerraFIRMA"
BRANCH_METHOD  = "no parent"
TABLE_INFO     = "Creation Date:(28 May 2020) MD5:c25ff4bde574d7d518c1f35c4da1830e"
TITLE          = f"{SOURCE_ID} output prepared for GCModelDev"
LICENSE        = (
    "GCModelDev model data is licensed under the Open Government License v3 "
    "(https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)"
)

# ── Output ───────────────────────────────────────────────────────────────────
# OUTPUT_DIR is derived at runtime from $DATADIR/cmor_outputs/ (see main()).
TIME_UNITS  = "days since 1850-01-01"   # target time axis units for output files
CHUNK_YEARS = None    # number of years per output file (set to None for one file)
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
        "comment":       "near-surface (usually, 2 meter) air temperature",
        "original_name": f"mo: (stash: {TAS_STASH}, lbproc: 128)",
        "cell_measures": "area: areacella",
    },
    "pr": {
        "standard_name": "precipitation_flux",
        "long_name":     "Precipitation",
        "var_name":      "pr",
        "units":         "kg m-2 s-1",
        "comment":       "includes both liquid and solid phases",
        "original_name": (
            f"mo: (stash: {PR_STASH}, lbproc: 128)" if PRECIP_MODE == "single"
            else f"mo: (stash: {PR_LS_STASH}, lbproc: 128) + mo: (stash: {PR_CV_STASH}, lbproc: 128)"
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


def _batch_concatenate(cubes: iris.cube.CubeList) -> iris.cube.Cube:
    """Concatenate in annual batches to avoid O(n²) cost with many cubes.

    Grouping 6000 monthly cubes by year and concatenating 12 at a time is
    orders of magnitude faster than one concatenate_cube() call on all 6000.
    """
    def first_year(cube):
        t = cube.coord("time")
        val = t.points.flat[0]
        return t.units.num2date(val).year

    by_year = defaultdict(iris.cube.CubeList)
    for cube in cubes:
        by_year[first_year(cube)].append(cube)

    annual = iris.cube.CubeList(
        by_year[y].concatenate_cube() for y in sorted(by_year)
    )
    return annual.concatenate_cube()


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
    # Remove coordinates and attributes that differ between cubes and would
    # prevent concatenation.  forecast_period and forecast_reference_time are
    # per-field PP metadata that vary across time steps and are not needed in
    # CMOR output.
    for cube in cubes:
        for coord in ["forecast_period", "forecast_reference_time"]:
            if cube.coords(coord):
                cube.remove_coord(coord)
        # Normalise time units across all cubes before merging — differing
        # reference epochs (e.g. "hours since 1970-01-01" vs "hours since
        # 1859-12-01") will otherwise block the merge.
        time_coord = cube.coord("time")
        target_time_units = cf_units.Unit(TIME_UNITS, calendar=time_coord.units.calendar)
        if time_coord.units != target_time_units:
            time_coord.convert_units(target_time_units)
        # If time is a non-scalar aux coord (not yet a dim coord), promote it
        # so that concatenate can use it as the joining axis.
        dims = cube.coord_dims(time_coord)
        if dims and not cube.coords(dimensions=dims, dim_coords=True):
            iris.util.promote_aux_coord_to_dim_coord(cube, time_coord)
    iris.util.equalise_attributes(cubes)
    # PP files can structure time either as a scalar coordinate (one timestep
    # per cube, needing merge to promote it to a dimension) or as an existing
    # dimension coordinate (needing concatenate to join along it).  Try merge
    # first; fall back to concatenate if merge fails.
    try:
        return cubes.merge_cube()
    except iris.exceptions.MergeError:
        return _batch_concatenate(cubes)


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


def apply_cmip_metadata(cube: iris.cube.Cube, cmip_key: str, suite_id: str, experiment_id: str) -> iris.cube.Cube:
    """Apply CMIP variable metadata and global attributes to *cube* in-place."""
    meta = CMIP_META[cmip_key]

    # ── Coordinate precision (CMIP requires double) ───────────────────────────
    promote_coords_to_double(cube)

    # ── Rename lat/lon coordinates to CMIP standard short names ──────────────
    for std_name, var_name in [("latitude", "lat"), ("longitude", "lon")]:
        if cube.coords(std_name):
            cube.coord(std_name).var_name = var_name

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

    # ── Time coordinate units ────────────────────────────────────────────────
    time_coord = cube.coord("time")
    target_time_units = cf_units.Unit(TIME_UNITS, calendar=time_coord.units.calendar)
    if time_coord.units != target_time_units:
        time_coord.convert_units(target_time_units)

    # ── height scalar coordinate (tas only) ──────────────────────────────────
    if cmip_key == "tas":
        if not cube.coords("height"):
            cube.add_aux_coord(iris.coords.AuxCoord(
                np.float64(1.5),
                standard_name="height",
                long_name="height",
                units=cf_units.Unit("m"),
            ))

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
    cube.attributes["missing_value"] = np.float32(FILL_VALUE)

    # ── CMIP global attributes ────────────────────────────────────────────────
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cube.attributes.update(
        {
            "Conventions":          "CF-1.7 CMIP-6.2",
            "activity_id":          ACTIVITY_ID,
            "branch_method":        BRANCH_METHOD,
            "creation_date":        now_str,
            "cv_version":           CV_VERSION,
            "data_specs_version":   CV_VERSION,
            "experiment":           "unknown",
            "experiment_id":        experiment_id,
            "external_variables":   "areacella",
            "forcing_index":        np.int32(1),
            "frequency":            "mon",
            "further_info_url":     "none",
            "grid":                 GRID_DESCRIPTION,
            "grid_label":           GRID,
            "history":              f"{now_str} ; CMOR rewrote data to be consistent with GCModelDev, CF-1.7 CMIP-6.2 and CF standards.",
            "initialization_index": np.int32(1),
            "institution":          INSTITUTION,
            "institution_id":       INSTITUTION_ID,
            "license":              LICENSE,
            "mip_era":              MIP_ERA,
            "mo_runid":             suite_id,
            "nominal_resolution":   NOMINAL_RESOLUTION,
            "physics_index":        np.int32(1),
            "product":              "model-output",
            "realization_index":    np.int32(1),
            "realm":                "atmos",
            "source":               SOURCE,
            "source_id":            SOURCE_ID,
            "source_type":          SOURCE_TYPE,
            "sub_experiment":       "none",
            "sub_experiment_id":    "none",
            "table_id":             MIP_TABLE,
            "table_info":           TABLE_INFO,
            "title":                TITLE,
            "tracking_id":          f"GCMODELDEV/{uuid.uuid4()}",
            "variable_id":          meta["var_name"],
            "variable_name":        meta["var_name"],
            "variant_label":        VARIANT,
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


def build_drs_filename(var_name: str, time_str: str, experiment_id: str) -> str:
    """Return a CMIP DRS filename (without directory)."""
    return f"{var_name}_{MIP_TABLE}_{SOURCE_ID}_{experiment_id}_{VARIANT}_{GRID}_{time_str}.nc"


def save_cube(cube: iris.cube.Cube, var_name: str, output_dir: str, experiment_id: str) -> None:
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
        # Cast to float32 here rather than up-front so only one chunk of data
        # is materialised at a time, keeping peak memory proportional to
        # CHUNK_YEARS rather than the full run length.
        chunk_cube.data = chunk_cube.data.astype(np.float32)
        time_str = time_range_str(chunk_cube)
        filename = build_drs_filename(var_name, time_str, experiment_id)
        filepath = os.path.join(output_dir, filename)
        iris.save(
            chunk_cube, filepath,
            fill_value=FILL_VALUE,
            chunksizes=CHUNK_SIZES,
            local_keys=["comment", "original_name", "cell_measures", "missing_value"],
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
    parser.add_argument(
        "experiment_id",
        help="Experiment code inserted into the output filename and metadata, e.g. 'esm-up2p0'.",
    )
    parser.add_argument(
        "--variables", "-v",
        nargs="+",
        choices=["tas", "pr"],
        default=["tas", "pr"],
        metavar="VAR",
        help="Variables to process. Choices: tas, pr. Defaults to both.",
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
    if "tas" in args.variables:
        print("Loading tas (surface air temperature) …")
        tas = load_variable(input_files, TAS_STASH, TAS_TIME_INTERVAL)
        tas = apply_cmip_metadata(tas, "tas", suite_id, args.experiment_id)
        print(f"  Cube: {tas.summary(shorten=True)}")
        save_cube(tas, "tas", output_dir, args.experiment_id)
        print()

    # ── Precipitation ────────────────────────────────────────────────────────
    if "pr" in args.variables:
        print(f"Loading pr (precipitation, mode={PRECIP_MODE!r}) …")
        pr = load_precipitation(input_files)
        pr = apply_cmip_metadata(pr, "pr", suite_id, args.experiment_id)
        print(f"  Cube: {pr.summary(shorten=True)}")
        save_cube(pr, "pr", output_dir, args.experiment_id)
        print()

    print("Done.")


if __name__ == "__main__":
    main()
