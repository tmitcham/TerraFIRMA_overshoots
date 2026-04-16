#!/bin/bash
# retrieve_ukesm_pp_test.sh
# -------------------------
# Smoke test for retrieve_ukesm_pp.sh.
# Builds the same MOOSE query file and runs moo select for a single suite,
# but restricts the query to a short date range so only a handful of files
# are downloaded.  Confirms that paths, STASH codes, and credentials all
# work before running the full script.
#
# Run on a JASMIN server with the MOOSE client available,
# e.g. mass-cli1.jasmin.ac.uk or a sci server with moose loaded.
# Or run on Met OFfice Azure SPICE
#
# Usage:
#   bash retrieve_ukesm_pp_test.sh

set -uo pipefail

# ── Configuration ─────────────────────────────────────────────────────────────

SUITE_ID="u-cx209"    # single suite to test against

MASS_STREAM="apm"
# Base directory for test outputs/logs (must be set in the environment).
: "${DATADIR:?Please set DATADIR, e.g. export DATADIR=/path/to/datadir}"
OUTPUT_DIR="${DATADIR}/terrafirma_oggm/pp_test/${SUITE_ID}"
LOG_DIR="${DATADIR}/terrafirma_oggm/pp_test/logs"

# Precipitation mode — must match retrieve_ukesm_pp.sh.
# "single"     → retrieve m01s05i216 (total precip flux)
# "components" → retrieve m01s04i203 + m01s05i205 (large-scale + convective)
PRECIP_MODE="single"

# Date range for the test — keep this short to limit the number of files.
# Format: {YYYY/MM/DD hh:mm}  (required by MOOSE T1 field syntax).
# Five months of monthly PP = ~5 files per STASH code.
TEST_START="{1850/01/01 00:00}"
TEST_END="{1850/06/01 00:00}"

# ── End of configuration ──────────────────────────────────────────────────────

mkdir -p "${OUTPUT_DIR}" "${LOG_DIR}"

QUERY_FILE="${LOG_DIR}/moose_query_test.txt"
MASS_URI="moose:/crum/${SUITE_ID}/${MASS_STREAM}.pp"

# ── Build the query file (same STASH codes as retrieve_ukesm_pp.sh) ──────────

cat > "${QUERY_FILE}" << EOF
# tas – screen-level (1.5 m) air temperature  (m01s03i236)
begin
  stash=3236
  T1>=${TEST_START}
  T1<=${TEST_END}
end

EOF

if [[ "${PRECIP_MODE}" == "single" ]]; then
    cat >> "${QUERY_FILE}" << EOF
# pr – total precipitation flux  (m01s05i216)
begin
  stash=5216
  T1>=${TEST_START}
  T1<=${TEST_END}
end
EOF

elif [[ "${PRECIP_MODE}" == "components" ]]; then
    cat >> "${QUERY_FILE}" << EOF
# pr (large-scale component)  (m01s04i203)
begin
  stash=4203
  T1>=${TEST_START}
  T1<=${TEST_END}
end

# pr (convective component)  (m01s05i205)
begin
  stash=5205
  T1>=${TEST_START}
  T1<=${TEST_END}
end
EOF

else
    echo "ERROR: PRECIP_MODE must be 'single' or 'components', got '${PRECIP_MODE}'" >&2
    exit 1
fi

echo "Query file (${QUERY_FILE}):"
echo "────────────────────"
cat "${QUERY_FILE}"
echo "────────────────────"
echo

# ── Run moo select ────────────────────────────────────────────────────────────

echo "Suite  : ${SUITE_ID}"
echo "Source : ${MASS_URI}"
echo "Dest   : ${OUTPUT_DIR}/"
echo "Period : ${TEST_START} to ${TEST_END}"
echo

if moo select -I "${QUERY_FILE}" "${MASS_URI}" "${OUTPUT_DIR}"; then
    echo
    echo "Done. Contents of ${OUTPUT_DIR}/:"
    ls -lh "${OUTPUT_DIR}/"
else
    echo
    echo "ERROR: moo select failed (exit code $?)" >&2
    exit 1
fi
