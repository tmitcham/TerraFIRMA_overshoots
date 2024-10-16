####################################################################################
# Imports
import cf
import cfplot as cfp
import pandas as pd
import os
import fnmatch
import numpy as np
import pickle
import sys

import matplotlib.pyplot as plt
import matplotlib.colors as col
import matplotlib.patches as pat

# from amrfile import io as amrio

####################################################################################

id = ["cs568", "cx209", "cw988", "cw989", "cw990", "cy623", "da914", "da916", "da917"]

run_type = ["Ctrl","Ramp-Up 1", "Ramp-Up 2", "Ramp-Up 3", "Ramp-Up 4", "Hist 1", "Hist 2", "Hist 3", "Hist 4"]

runs = dict(zip(id, run_type))

line_cols = ['#000000','#C30F0E','#C30F0E','#C30F0E','#C30F0E','#0003C7','#0003C7','#0003C7','#0003C7']
line_stys = ["dotted","solid","dotted","dashed","dashdot","solid","dotted","dashed","dashdot"]

# Read ice sheet data

print("Loading ice sheet data from file...")

with open('../processed_data/historical_icesheet_data.pkl', 'rb') as file:

    icesheet_d = pickle.load(file)

####################################################################################

# function for smoothing time series for plotting

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='valid')
    return y_smooth

####################################################################################

# Plot VAF vs Time graph

initalmassSLE = icesheet_d["cx209"]["massSLE"].iloc[0]
initalmassSLEpi = icesheet_d["cs568"]["massSLE"].iloc[0]

print("Starting AIS VAF vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    if i in {"cs568","cx209", "cw988", "cw989", "cw990"}:

        plot_data = plot_data.iloc[10:50]

    else:

        plot_data = plot_data.iloc[125:]

    if i == "cs568": 
        plt.plot(plot_data.time - 1850, (plot_data.massSLE-initalmassSLEpi), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    else:
        plt.plot(plot_data.time - 1850, (plot_data.massSLE-initalmassSLE), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

#plt.grid(linestyle=':')

ax = plt.gca()

plt.ylabel("$\Delta$VAF (m SLE)")
plt.xlabel('Years')
plt.legend(loc = 'center left', bbox_to_anchor=(1, 0.5))

print("Finished and saving AIS VAF vs Time plot...")

plt.savefig('../figures/HistAISVAFvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot GroundedSMB vs Time graph

print("Starting AIS Grounded SMB vs Time plot...")

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    if i in {"cs568","cx209", "cw988", "cw989", "cw990"}:

        plot_data = plot_data.iloc[10:50]

    else:

        plot_data = plot_data.iloc[125:]

    plt.plot(plot_data.time - 1850, ((plot_data.groundedSMB)/918e6), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.01)

    ma_y = smooth((plot_data.groundedSMB)/918e6, box_size)
    
    ma_x = (plot_data.time - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    
    count = count + 1

#plt.grid(linestyle=':')

ax = plt.gca()

plt.ylabel("Grounded SMB (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.legend(loc = 'center left', bbox_to_anchor=(1, 0.5))

print("Finished and saving AIS Grounded SMB vs Time plot...")

plt.savefig('../figures/HistAISGroundedSMBvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot Discharge vs Time graph

print("Starting AIS Grounding Line Discharge vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    if i in {"cs568","cx209", "cw988", "cw989", "cw990"}:

        plot_data = plot_data.iloc[10:50]

    else:

        plot_data = plot_data.iloc[125:]

    plt.plot(plot_data.time - 1850, ((plot_data.GLDischarge)/918e6), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.01)

    ma_y = smooth(((plot_data.GLDischarge)/918e6), box_size)
    
    ma_x = (plot_data.time - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

#plt.grid(linestyle=':')

ax = plt.gca()

plt.ylabel("GL Discharge (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.legend(loc = 'center left', bbox_to_anchor=(1, 0.5))

print("Finished and saving AIS Grounding Line Discharge vs Time plot...")

plt.savefig('../figures/HistAISGLDischargevsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################