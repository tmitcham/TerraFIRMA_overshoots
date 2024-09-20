#!/bin/bash 

#SBATCH --partition=short-serial
#SBATCH --job-name=AISdiagnosticsarray
#SBATCH -o %A_%a.out
#SBATCH -e %A_%a.err
#SBATCH --time=10:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --array=1-25

idlist=("cs568" "cx209" "cy837" "cy838" "cz374" "cz375" "cz376" "cz377" "cz378" "cz944" "da800" "da697" "da892" "db223" "dc251" "dc051" "dc052" "dc248" "dc249" "db956" "dc565" "dd210" "dc032" "dc123" "dc130")

module add jaspy

dirname=${idlist[SLURM_ARRAY_TASK_ID-1]}

directory="/home/users/tm17544/gws_terrafirma/overshoots/raw_data/${dirname}/icesheet/"

echo "This is array task ${SLURM_ARRAY_TASK_ID}, the directory name is ${directory}"

python diagnostics.py $directory 

echo "Finished analysis of ${directory}"
