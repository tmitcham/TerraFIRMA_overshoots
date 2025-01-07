#!/bin/bash

#idlist=("cz374" "cz375" "cz376" "cz377" "cz378" "cz834" "cz855" "cz859" "db587" "db723") 
idlist=("db731" "da087" "da266" "db597" "db733" "dc324" "di335" "da800" "da892" "db223") 
#idlist=("df453" "de620" "dc251" "db956" "dc051" "dc248" "dc249" "dc565" "dd210" "dc032") 
#idlist=("df028" "de621" "dc123" "dc130" "df025" "df027" "df021" "df023" "dh541" "dh859") 
#idlist=("de943" "de962" "de963" "dk554" "dk555" "dk556")

for id in "${idlist[@]}"
do
directory="/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/raw_data/${id}/icesheet/"
mask="/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/aux_data/antarctica_bedmachine_imbie2_basins_4km.hdf5"
csvfile="new_${id}_AIS_basins_diagnostics.csv"
outfile="${id}_AIS_basins_diag.out"
echo "Running new_diagnostics_AIS.py on dir: $directory \n"
echo "Using mask file: $mask \n" 
echo "Saving results in: $csvfile \n"
echo "Stdout and stderr saved in: $outfile \n"
python new_diagnostics_AIS.py $directory $csvfile $mask > $outfile 2>&1 &
done

wait

idlist=("df453" "de620" "dc251" "db956" "dc051" "dc248" "dc249" "dc565" "dd210" "dc032") 

for id in "${idlist[@]}"
do
directory="/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/raw_data/${id}/icesheet/"
mask="/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/aux_data/antarctica_bedmachine_imbie2_basins_4km.hdf5"
csvfile="new_${id}_AIS_basins_diagnostics.csv"
outfile="${id}_AIS_basins_diag.out"
echo "Running new_diagnostics_AIS.py on dir: $directory \n"
echo "Using mask file: $mask \n" 
echo "Saving results in: $csvfile \n"
echo "Stdout and stderr saved in: $outfile \n"
python new_diagnostics_AIS.py $directory $csvfile $mask > $outfile 2>&1 &
done

wait

idlist=("df028" "de621" "dc123" "dc130" "df025" "df027" "df021" "df023" "dh541" "dh859") 

for id in "${idlist[@]}"
do
directory="/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/raw_data/${id}/icesheet/"
mask="/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/aux_data/antarctica_bedmachine_imbie2_basins_4km.hdf5"
csvfile="new_${id}_AIS_basins_diagnostics.csv"
outfile="${id}_AIS_basins_diag.out"
echo "Running new_diagnostics_AIS.py on dir: $directory \n"
echo "Using mask file: $mask \n" 
echo "Saving results in: $csvfile \n"
echo "Stdout and stderr saved in: $outfile \n"
python new_diagnostics_AIS.py $directory $csvfile $mask > $outfile 2>&1 &
done

wait

idlist=("de943" "de962" "de963" "dk554" "dk555" "dk556")

for id in "${idlist[@]}"
do
directory="/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/raw_data/${id}/icesheet/"
mask="/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/aux_data/antarctica_bedmachine_imbie2_basins_4km.hdf5"
csvfile="new_${id}_AIS_basins_diagnostics.csv"
outfile="${id}_AIS_basins_diag.out"
echo "Running new_diagnostics_AIS.py on dir: $directory \n"
echo "Using mask file: $mask \n" 
echo "Saving results in: $csvfile \n"
echo "Stdout and stderr saved in: $outfile \n"
python new_diagnostics_AIS.py $directory $csvfile $mask > $outfile 2>&1 &
done