#!/bin/bash

idlist=("cx209" "cy837" "cy838 "cz375" "cz376" "cz377") 

for id in "${idlist[@]}"
do
directory="/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/raw_data/${id}/icesheet/"
mask="/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/aux_data/antarctica_bedmachine_imbie2_basins_4km.hdf5"
csvfile="testing_new_${id}_AIS_basins_diagnostics.csv"
outfile="testing_${id}_AIS_basins_diag.out"
echo "Running new_diagnostics_AIS.py on dir: $directory \n"
echo "Using mask file: $mask \n" 
echo "Saving results in: $csvfile \n"
echo "Stdout and stderr saved in: $outfile \n"
python new_diagnostics_AIS.py $directory $csvfile $mask > $outfile 2>&1 &
done