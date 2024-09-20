# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 14:23:31 2024

Based on Matt Trevers' stats.py script

Run the BISICLES diagnostics module for all plot.*.hdf5 files within a directory and dump the output nicely in a csv file
Chosen directory is from the command line argument
Run as: "python diagnostics_GrIS.py [directory] [mask]"
@author: tom mitcham
"""

import os
import sys
import subprocess
import glob

if len(sys.argv) == 1:
    print('No directory specified. Select one by running the command "python diagnostics_GrIS.py [directory]"')
    sys.exit()

directory =  sys.argv[1]
if not directory.endswith('/'):
    directory = directory + '/'
filetoolsPath = '/home/users/tm17544/Code/BISICLES/bisicles-uob/code/filetools/'
filetoolStats = 'diagnostics2d.Linux.64.c++.gfortran.DEBUG.OPT.GNU.ex'

masked = False
maskFile = ''

if len(sys.argv) == 3 and sys.argv[2] != '0':
    masked = True
    maskFile = sys.argv[2] + ' 1'
    mask = maskFile.split('.2d.hdf5')[0]
    
outfile = '/home/users/tm17544/gws_terrafirma/overshoots/processed_data/' + directory[55:60] + '_GrIS_diagnostics.csv'

if masked:
    outfile = '/gws/nopw/j04/terrafirma/tm17544/' + directory[43:48] + '_' +  mask + '_GrIS_diagnostics.csv'

    print("Running diagnostics for directory: " + directory + "with mask: " + mask)

print("Running diagnostics for directory: " + directory)

# Write the header
header = 'file,minimumThickness,groundedArea,discharge,dhdt,smb,bmb,fluxDivRecon,fluxDivFile,errRecon,errFile'
writeCommand = 'echo ' + header + ' >> ' + outfile
os.system(writeCommand)

count = 0
for infile in sorted(os.listdir(directory)):
    if infile.endswith("AIS.hdf5"):
        count = count + 1
        
        #Run the filetools stats executable
        statsCommand = filetoolsPath + filetoolStats + ' ' + directory + infile + ' 918 1028 9.81 '+maskFile+' | grep minimumThickness'
        statsOutput = subprocess.check_output(statsCommand,shell=True)
        statsOutput = statsOutput.decode('utf-8')

        #These two lines are required when running on Porthos - otherwise remove them
        #statsOutput = str(statsOutput)
        #statsOutput = 'time' + statsOutput.split('time')[1].split('.\n')[0]
        
        #Clean up the output and write to the csv
        statsOutput = statsOutput.replace('=','').replace('  ',' ').replace(' ',',').split('.\n')[0]
        minThick = statsOutput.split('minimumThickness')[1].split('groundedArea')[0]
        groundedArea = statsOutput.split('groundedArea,')[1].split('discharge')[0]
        discharge = statsOutput.split('discharge,')[1].split('dhdt')[0]
        dhdt = statsOutput.split('dhdt,')[1].split('smb')[0]
        smb = statsOutput.split('smb,')[1].split('bmb')[0]
        bmb = statsOutput.split('bmb,')[1].split('fluxDivergenceReconstr')[0]
        fluxDivRecon = statsOutput.split('fluxDivergenceReconstr,')[1].split('fluxDivergenceFromFile')[0]
        fluxDivFile = statsOutput.split('fluxDivergenceFromFile,')[1].split('(smb+bmb-flxDivReconstr-dhdt)')[0]
        errRecon = statsOutput.split('(smb+bmb-flxDivReconstr-dhdt),')[1].split('(smb+bmb-flxDivFromFile-dhdt)')[0]
        errFile = statsOutput.split('(smb+bmb-flxDivFromFile-dhdt),')[1].split(',')[0]
        statsRow = infile + minThick + groundedArea + discharge + dhdt + smb + bmb + fluxDivRecon + fluxDivFile + errRecon + errFile
        print(statsRow)
        writeCommand = 'echo ' + statsRow + ' >> ' + outfile
        os.system(writeCommand)

if count == 0:
    print("No plot.*.hdf5 files found")
else:
    print(str(count) + " plot.*.hdf5 files found. Created diagnostics file " + outfile)
