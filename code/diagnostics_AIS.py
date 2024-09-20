# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 14:23:31 2024

Based on Matt Trevers' stats.py script

Run the BISICLES diagnostics module for all plot.*.hdf5 files within a directory and dump the output nicely in a csv file
Chosen directory is from the command line argument
Run as: "python diagnostics_AIS.py [directory] [mask]"
@author: tom mitcham
"""

import os
import sys
import subprocess
import glob

if len(sys.argv) == 1:
    print('No directory specified. Select one by running the command "python diagnostics_AIS.py [directory]"')
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
    
outfile = '/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/processed_data/' + directory[55:60] + '_diagnostics.csv'

if masked:
    outfile = '/gws/nopw/j04/terrafirma/tm17544/' + directory[43:48] + '_' +  mask + '_diagnostics.csv'

    print("Running diagnostics for directory: " + directory + "with mask: " + mask)

print("Running diagnostics for directory: " + directory)

# Write the header
header = 'file,time,volumeAll,volumeAbove,groundedArea,floatingArea,minimumThickness,dischargeGrounded,dhdtGrounded,smbGrounded,bmbGrounded,fluxDivReconGrounded,fluxDivFileGrounded,errReconGrounded,errFileGrounded,dischargeFloating,calvingFloating,dhdtFloating,smbFloating,bmbFloating,fluxDivReconFloating,fluxDivFileFloating,errReconFloating,errFileFloating,dischargeSheet,dhdtSheet,smbSheet,bmbSheet,calvingSheet,fluxDivReconSheet,fluxDivFileSheet,errReconSheet,errFileSheet'
writeCommand = 'echo ' + header + ' >> ' + outfile
os.system(writeCommand)

count = 0
for infile in sorted(os.listdir(directory)):
    if infile.endswith("AIS.hdf5"):
        count = count + 1
        
        print("Running diagnostics for file: " + infile)
        #Run the filetools stats executable
        statsCommand = filetoolsPath + filetoolStats + ' ' + directory + infile + ' 918 1028 9.81 ' + maskFile
        statsOutput = subprocess.check_output(statsCommand,shell=True)
        statsOutput = statsOutput.decode('utf-8')

        statsOutput = statsOutput.split('\n')
        
        statsTotal = statsOutput[7].replace('=','').replace('  ',' ').replace(' ',',')
        statsGrounded = statsOutput[11].replace('=','').replace('  ',' ').replace(' ',',')
        statsFloating = statsOutput[14].replace('=','').replace('  ',' ').replace(' ',',')
        statsSheet = statsOutput[17].replace('=','').replace('  ',' ').replace(' ',',')

        #Clean up the output and write to the csv

        time = statsTotal.split('time')[1].split('iceVolumeAll')[0]
        volumeAll = statsTotal.split('iceVolumeAll,')[1].split('iceVolumeAbove')[0]
        volumeAbove = statsTotal.split('iceVolumeAbove,')[1].split('melangeVolume')[0]
        groundedArea = statsTotal.split('groundedArea,')[1].split('floatingArea')[0]
        floatingArea = statsTotal.split('floatingArea,')[1].split(',totalArea')[0]

        minThick = statsGrounded.split('minimumThickness')[1].split('groundedArea')[0]
        dischargeG = statsGrounded.split('discharge,')[1].split('dhdt')[0]
        dhdtG = statsGrounded.split('dhdt,')[1].split('smb')[0]
        smbG = statsGrounded.split('smb,')[1].split('bmb')[0]
        bmbG = statsGrounded.split('bmb,')[1].split('fluxDivergenceReconstr')[0]
        fluxDivReconG = statsGrounded.split('fluxDivergenceReconstr,')[1].split('fluxDivergenceFromFile')[0]
        fluxDivFileG = statsGrounded.split('fluxDivergenceFromFile,')[1].split('(smb+bmb-flxDivReconstr-dhdt)')[0]
        errReconG = statsGrounded.split('(smb+bmb-flxDivReconstr-dhdt),')[1].split('(smb+bmb-flxDivFromFile-dhdt)')[0]
        errFileG = statsGrounded.split('(smb+bmb-flxDivFromFile-dhdt),')[1].split(',')[0]

        dischargeF = statsFloating.split('dischargeFloating')[1].split('calving')[0]
        calvingF = statsFloating.split('calving,')[1].split('dhdt')[0]
        dhdtF = statsFloating.split('dhdt,')[1].split('smb')[0]
        smbF = statsFloating.split('smb,')[1].split('bmb')[0]
        bmbF = statsFloating.split('bmb,')[1].split('fluxDivergenceReconstr')[0]
        fluxDivReconF = statsFloating.split('fluxDivergenceReconstr,')[1].split('fluxDivergenceFromFile')[0]
        fluxDivFileF = statsFloating.split('fluxDivergenceFromFile,')[1].split('(smb+bmb-flxDivReconstr-dhdt)')[0]
        errReconF = statsFloating.split('(smb+bmb-flxDivReconstr-dhdt),')[1].split('(smb+bmb-flxDivFromFile-dhdt)')[0]
        errFileF = statsFloating.split('(smb+bmb-flxDivFromFile-dhdt),')[1].split(',')[0]

        dischargeS = statsSheet.split('discharge')[1].split('dhdt')[0]
        dhdtS = statsSheet.split('dhdt,')[1].split('smb')[0]
        smbS = statsSheet.split('smb,')[1].split('bmb')[0]
        bmbS = statsSheet.split('bmb,')[1].split('calving')[0]
        calvingS = statsSheet.split('calving,')[1].split('fluxDivergenceReconstr')[0]
        fluxDivReconS = statsSheet.split('fluxDivergenceReconstr,')[1].split('fluxDivergenceFromFile')[0]
        fluxDivFileS = statsSheet.split('fluxDivergenceFromFile,')[1].split('(smb+bmb-flxDivReconstr-dhdt)')[0]
        errReconS = statsSheet.split('(smb+bmb-flxDivReconstr-dhdt),')[1].split('(smb+bmb-flxDivFromFile-dhdt)')[0]
        errFileS = statsSheet.split('(smb+bmb-flxDivFromFile-dhdt),')[1].split(',')[0]

        statsRow = infile + time + volumeAll + volumeAbove + groundedArea + floatingArea + minThick + dischargeG + dhdtG + smbG + bmbG + fluxDivReconG + fluxDivFileG + errReconG + errFileG + dischargeF + calvingF + dhdtF + smbF + bmbF + fluxDivReconF + fluxDivFileF + errReconF + errFileF + dischargeS + dhdtS + smbS + bmbS + calvingS + fluxDivReconS + fluxDivFileS + errReconS + errFileS       
        print(statsRow)
        writeCommand = 'echo ' + statsRow + ' >> ' + outfile
        os.system(writeCommand)

if count == 0:
    print("No plot.*.hdf5 files found")
else:
    print(str(count) + " plot.*.hdf5 files found. Created diagnostics file " + outfile)
