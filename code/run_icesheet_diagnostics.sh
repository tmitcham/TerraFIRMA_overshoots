#!/bin/bash

# Usage: bash run_icesheet_diagnostics.sh

###############################################################################

suite_set="overshoots" # Options: overshoots, overview, historical_rampups
icesheet="AIS" # Options: AIS, GrIS
masked="True" # Options: True, False
maskfile="/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/aux_data/antarctica_bedmachine_imbie2_basins_4km.hdf5"
mask_no_start="0"
mask_no_end="16"
jobs_per_batch=10

###############################################################################

if [[ "$suite_set" == "overshoots" ]]; then
    idlist=(
        "cs568" "cx209" "cw988" "cw989" "cw990" "cy837" "cy838" "cz374" "cz375" "cz376"
        "cz377" "cz378" "cz834" "cz855" "cz859" "db587" "db723" "db731" "da087" "da266"
        "db597" "db733" "dc324" "cz944" "di335" "da800" "da697" "da892" "db223" "df453"
        "de620" "dc251" "dc956" "dc051" "dc052" "dc248" "dc249" "dc565" "dd210" "dc032"
        "df028" "de621" "dc123" "dc130" "df025" "df027" "df021" "df023" "dh541" "dh859"
        "dg093" "dg094" "dg095" "de943" "de962" "de963" "dm357" "dm358" "dm359"

elif [[ "$suite_set" == "overview" ]]; then
    idlist=(
        "cs568" "cx209" "cy837" "cy838" "cz375" "cz376" "cz377" "dc052" "dc051" "df028"
        "dc123" "dc130" "da697" "cz944" "df453" "da892" "dc251"
    )

elif [[ "$suite_set" == "historical_rampups" ]]; then
    idlist=(
        "cs568" "cx209" "cw988" "cw989" "cw990" "cy623" "da914" "da916" "da917"
    )

else
    echo "Invalid suite_set: $suite_set"
    echo "Valid options: overshoots, overview, historical_rampups"
    exit 1
fi

# Print the selected IDs
echo "Selected suite set: $suite_set"

###############################################################################

counter=0

for id in "${idlist[@]}"; do
    
    directory="/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/raw_data/${id}/icesheet/"

    echo "Running icesheet_diagnostics.py on dir: ${directory}, for icesheet: ${icesheet} \n"
    
    if [[ "$masked" == "True"]]; then

        csvfile="${id}_${icesheet}_diagnostics_masked.csv"
        outfile="${id}_${icesheet}_diagnostics_masked.out"

        echo "Using mask file: ${mask} \n" 
        echo "Saving results in: ${csvfile} \n"
        echo "Stdout and stderr saved in: ${outfile} \n"

        python icesheet_diagnostics.py --icesheet "$icesheet" --directory "$directory" --csv_file "$csvfile" --mask "$maskfile" --mask_no_start "$mask_no_start" --mask_no_end "$mask_no_end" > "$outfile" 2>&1 &

    else

        csvfile="${id}_${icesheet}_diagnostics.csv"
        outfile="${id}_${icesheet}_diagnostics.out"

        echo "Saving results in: ${csvfile} \n"
        echo "Stdout and stderr saved in: ${outfile} \n"

        python icesheet_diagnostics.py --icesheet "$icesheet" --directory "$directory" --csv_file "$csvfile" > "$outfile" 2>&1 &

    fi

    ((counter++))

    # If the batch limit is reached, wait for all processes to complete
    if (( counter >= jobs_per_batch )); then
        wait  # Ensures the current batch completes before continuing
        counter=0  # Reset counter for the next batch
    fi
    
done