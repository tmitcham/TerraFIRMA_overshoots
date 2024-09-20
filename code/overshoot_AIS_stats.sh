#!/bin/bash

# idlist=("cs568" "cx209" "cy837" "cy838" "cz375" "cz376" "cz377" "dc051" "dc052" "df028" "dc123" "dc130")
idlist=("cw988" "cw989")

for id in "${idlist[@]}"
do
directory="/home/users/tm17544/gws_terrafirma/overshoots/raw_data/$id/icesheet/"
echo "Running stats.py on dir: $directory" 
python stats_AIS.py $directory
done
