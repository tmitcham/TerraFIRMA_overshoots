####################################################################################

import os
import argparse
import subprocess

####################################################################################

# Check that all the data in the raw_data directory has been processed

RUN_IDS=[
  "cs568", "cx209", "cw988", "cw989", "cw990", "cy837", "cy838", "cz374", "cz375", "cz376",
  "cz377", "cz378", "cz834", "cz855", "cz859", "db587", "db723", "db731", "da087", "da266",
  "db597", "db733", "dc324", "cz944", "di335", "da800", "da697", "da892", "db223", "df453",
  "de620", "dc251", "dc051", "dc052", "dc248", "dc249", "dm757", "dc565", "dd210", "dc032",
  "df028", "de621", "dc123", "dc130", "df025", "df027", "df021", "df023", "dh541", "dh859",
  "dg093", "dg094", "dg095", "de943", "de962", "de963", "dk554", "dk555", "dk556", "dm357",
  "dm358", "dm359", "dc163", "dm929", "dm930", "dn822", "dn966", "do135", "do136"
]

RUN_IDS=[
    "cs568", "cx209", "cy837", "cy838", "cz375", "cz376", "cz377", "dc052", "dc051", "df028",
    "dc123", "dc130"
]

suites_to_fix = []

for suite in RUN_IDS:

    print(f"Checking suite: {suite}")

    last_raw_file = subprocess.run([f"ls ../raw_data/{suite}/icesheet/*GrIS.hdf5 | tail -n 1"], shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')

    last_raw_year = last_raw_file[43:47]

    last_processed_file = subprocess.run([f"tail -n 1 ../processed_data/{suite}_GrIS_diagnostics.csv"], shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')

    last_processed_year = last_processed_file[105:109]

    correct_data_string = "0,nonice,area"

    if correct_data_string not in last_processed_file:
        print(f"Partially processed file for suite {suite}")
        suites_to_fix.append(suite)

    if last_raw_year != last_processed_year:
        print(f"Year mismatch for {suite}\nLast raw year: {last_raw_year}\nLast processed year: {last_processed_year}")
        suites_to_fix.append(suite)
    else:
        print(f"{suite} is up to date.")

print(f"\nSuites that need processing: {suites_to_fix}")
