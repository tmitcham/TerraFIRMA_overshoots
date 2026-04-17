#!/bin/bash
# retrieve_ukesm_pp.sh
# --------------------
# Download monthly PP files from MASS onto JASMIN using moo select,
# filtering to only the STASH codes needed by ukesm_pp_to_cmor.py.
# Multiple suites are retrieved in parallel.
#
# Run this on a JASMIN server that has the MOOSE client available,
# e.g. mass-cli1.jasmin.ac.uk or a sci server with moose loaded.
# Or run on Met OFfice Azure SPICE
#
# Usage:
#   bash retrieve_ukesm_pp.sh

set -uo pipefail

# ── Configuration ─────────────────────────────────────────────────────────────

SUITE_IDS=(
    # PI and ramp ups (cs495 cz826 excluded — static ice sheets)
    "u-cs568" "u-cx209" "u-cw988" "u-cw989" "u-cw990"

    # Stabilisations
    "u-cy837" "u-cy838" "u-cz374" "u-cz375" "u-cz376" "u-cz377" "u-cz378"
    "u-cz834" "u-cz855" "u-cz859" "u-db587" "u-db723" "u-db731"
    "u-da087" "u-da266" "u-db597" "u-db733" "u-dc324"

    # Ramp downs (cz944 dc032 excluded — replaced; db956 excluded — not available)
    "u-di335" "u-da800" "u-da697" "u-da892" "u-db223" "u-df453" "u-de620" "u-dc251"
    "u-dc051" "u-dc052" "u-dc248" "u-dc249" "u-dm757" "u-dc565" "u-dd210" "u-df028" "u-de621" "u-dc123" "u-dc130"
    "u-df025" "u-df027" "u-df021" "u-df023" "u-dh541" "u-dh859"
    "u-dg093" "u-dg094" "u-dg095" "u-de943" "u-de962" "u-de963" "u-dm357" "u-dm358" "u-dm359"  # dk554 dk555 dk556 excluded — replaced

    # Zero-emission (off ramp downs)
    "u-dc163" "u-dm929" "u-dm930" "u-dn822" "u-dn973" "u-dn966" "u-do135" "u-do136"

    # Historical UKESM
    "u-cy623" "u-da914" "u-da916" "u-da917"
)

MASS_STREAM="apm"                       # PP stream (apm = atmosphere monthly)
# Base directory for outputs/logs (must be set in the environment).
: "${DATADIR:?Please set DATADIR, e.g. export DATADIR=/path/to/data}"
OUTPUT_BASE="${DATADIR}/terrafirma_oggm/pp"  # one sub-directory per suite created here
LOG_DIR="${DATADIR}/terrafirma_oggm/logs"    # one log file per suite written here

# Precipitation mode — must match the setting in ukesm_pp_to_cmor.py.
# "single"     → retrieve m01s05i216 (total precip flux)
# "components" → retrieve m01s04i203 + m01s05i205 (large-scale + convective)
PRECIP_MODE="single"

# ── End of configuration ──────────────────────────────────────────────────────

# ── Build the query file (shared across all suites) ───────────────────────────

mkdir -p "${LOG_DIR}"

QUERY_FILE="${LOG_DIR}/moose_query.txt"

cat > "${QUERY_FILE}" << 'EOF'
# tas – screen-level (1.5 m) air temperature  (m01s03i236)
begin
  stash=3236
end

EOF

if [[ "${PRECIP_MODE}" == "single" ]]; then
    cat >> "${QUERY_FILE}" << 'EOF'
# pr – total precipitation flux  (m01s05i216)
begin
  stash=5216
end
EOF

elif [[ "${PRECIP_MODE}" == "components" ]]; then
    cat >> "${QUERY_FILE}" << 'EOF'
# pr (large-scale component)  (m01s04i203)
begin
  stash=4203
end

# pr (convective component)  (m01s05i205)
begin
  stash=5205
end
EOF

else
    echo "ERROR: PRECIP_MODE must be 'single' or 'components', got '${PRECIP_MODE}'" >&2
    exit 1
fi

echo "Query file contents:"
echo "────────────────────"
cat "${QUERY_FILE}"
echo "────────────────────"
echo

# ── Per-suite retrieval function ──────────────────────────────────────────────
# Runs moo select for one suite, writes output to a dedicated log file, and
# writes the exit code to a .rc file so the main loop can detect completion
# without needing to know which PID finished.

retrieve_suite() {
    local suite_id="$1"
    local mass_uri="moose:/crum/${suite_id}/${MASS_STREAM}.pp"
    local output_dir="${OUTPUT_BASE}/${suite_id}"
    local log_file="${LOG_DIR}/${suite_id}.log"
    local rc=0

    mkdir -p "${output_dir}"

    {
        echo "$(date '+%Y-%m-%dT%H:%M:%S')  [${suite_id}]  Starting"
        echo "  Source : ${mass_uri}"
        echo "  Dest   : ${output_dir}"
        echo

        # Flags:
        #   -I : incremental — fills gaps and overwrites smaller (incomplete) files
        if moo select -I "${QUERY_FILE}" "${mass_uri}" "${output_dir}"; then
            echo
            echo "$(date '+%Y-%m-%dT%H:%M:%S')  [${suite_id}]  Done"
        else
            rc=$?
            echo
            echo "$(date '+%Y-%m-%dT%H:%M:%S')  [${suite_id}]  FAILED (exit code ${rc})"
        fi
    } > "${log_file}" 2>&1

    # Write exit code for the main loop to read, then report to stdout.
    echo "${rc}" > "${LOG_DIR}/${suite_id}.rc"
    if (( rc == 0 )); then
        echo "[${suite_id}]  Done  →  ${log_file}"
    else
        echo "[${suite_id}]  FAILED  →  ${log_file}"
    fi
    return "${rc}"
}

# ── Reap any jobs that have written a .rc file ────────────────────────────────
# Called after wait -n signals that at least one job has finished.
# Updates running_pids / running_suites in-place and appends to failed.

reap_finished() {
    local new_pids=() new_suites=()
    local i rc
    for i in "${!running_pids[@]}"; do
        local sid="${running_suites[$i]}"
        local rc_file="${LOG_DIR}/${sid}.rc"
        if [[ -f "${rc_file}" ]]; then
            rc=$(< "${rc_file}")
            wait "${running_pids[$i]}" 2>/dev/null || true   # reap zombie
            if (( rc != 0 )); then
                failed+=("${sid}")
            fi
        else
            new_pids+=("${running_pids[$i]}")
            new_suites+=("${sid}")
        fi
    done
    running_pids=("${new_pids[@]+"${new_pids[@]}"}")
    running_suites=("${new_suites[@]+"${new_suites[@]}"}")
}

# ── Launch suites in parallel, up to MAX_PARALLEL at a time ──────────────────

MAX_PARALLEL=20

echo "Processing ${#SUITE_IDS[@]} suite(s) with up to ${MAX_PARALLEL} running in parallel..."
echo

# Parallel arrays: running_pids[i] and running_suites[i] are always in sync.
running_pids=()
running_suites=()
failed=()

for suite_id in "${SUITE_IDS[@]}"; do

    # Remove any stale .rc file from a previous run of this suite.
    rm -f "${LOG_DIR}/${suite_id}.rc"

    # While the pool is full, wait for any job to finish then reap it.
    # wait -n (bash 4.3+) returns as soon as the first available child exits,
    # so a new suite is launched the moment a slot opens rather than waiting
    # for a specific (possibly slow) job.
    while (( ${#running_pids[@]} >= MAX_PARALLEL )); do
        wait -n || true
        reap_finished
    done

    retrieve_suite "${suite_id}" &
    running_pids+=($!)
    running_suites+=("${suite_id}")
    echo "[${suite_id}]  Launched (${#running_pids[@]}/${MAX_PARALLEL} slots used)"

done

# ── Drain the remaining jobs ──────────────────────────────────────────────────

echo
echo "All suites launched — waiting for the last ${#running_pids[@]} to finish..."

while (( ${#running_pids[@]} > 0 )); do
    wait -n || true
    reap_finished
done

# ── Summary ───────────────────────────────────────────────────────────────────

echo
if [[ ${#failed[@]} -eq 0 ]]; then
    echo "All ${#SUITE_IDS[@]} suite(s) retrieved successfully."
else
    echo "ERROR: ${#failed[@]} suite(s) failed: ${failed[*]}"
    echo "Check the per-suite log files in ${LOG_DIR}/"
    exit 1
fi
