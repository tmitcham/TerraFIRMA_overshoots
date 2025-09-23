# TerraFIRMA_overshoots

Repository of code to:

1) Download ice sheet and global mean temperature data from the TerraFIRMA overhsoot simulations (and the UKESM1.2 historical simulations) from MASS onto JASMIN
2) Process the BISICLES output using the diagnostics filetool (with optional masking of diagnostics into ice sheet basins) and store all necessary data for analysis and figures in pickle and netcdf files
3) Plot figures related to ice sheets evoultion in the TerraFIRMA simulations

The chain in which to run the scripts is:
1) `get_overshoot_data.sh` -> pulls icesheet/atmos files from MASS to JASMIN
2) `run_icesheet_diagnostics.sh` (which calls `icesheet_diagnostics.py`) -> runs filetool on every BISICLES plot file and returns a csv of diagnostics
3) `process_diagnostics_output.py` -> reads in csv files of diagnostics and outputs (as .pkl and .nc files) timeseries of key variables for each experiment
 
