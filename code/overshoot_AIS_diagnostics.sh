#!/bin/bash

idlist=("cs568" "cx209" "cy837" "cy838" "cz374" "cz375" "cz376" "cz377" "cz378" "cz944" "da800" "da697" "da892" "db223" "dc251" "dc051" "dc052" "dc248" "dc249" "db956" "dc565" "dd210" "dc032" "dc123" "dc130")

for id in "${idlist[@]}"
do
directory="/home/users/tm17544/gws_terrafirma/overshoots/raw_data/$id/icesheet/"
echo "Running diagnostics.py on dir: $directory" 
python diagnostics.py $directory
done
