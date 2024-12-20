####################################################################################
# Imports
import pandas as pd
import os
import fnmatch
import numpy as np
import pickle
import sys

import matplotlib.pyplot as plt
import matplotlib.colors as col
import matplotlib.patches as pat

####################################################################################

# For historical simulations
id = ["cy623", "da914", "da916", "da917"]
run_type = ["Hist 1", "Hist 2", "Hist 3", "Hist 4"]
runs = dict(zip(id, run_type))

line_cols = ['#000000','#C30F0E','#0003C7','#168039']

# Set plot font size for all plots
plt.rcParams.update({'font.size': 7})

####################################################################################

# Get atmosphere data

if os.path.exists('../processed_data/historical_atmos_data.pkl'):

    print("Loading atmosphere data from file...")

    with open('../processed_data/historical_atmos_data.pkl', 'rb') as file:
    
        atmos_d = pickle.load(file)

####################################################################################

# Read ice sheet data

if os.path.exists('../processed_data/historical_icesheet_data_GrIS.pkl'):

    print("Loading ice sheet data from file...")

    with open('../processed_data/historical_icesheet_data_GrIS.pkl', 'rb') as file:

        icesheet_d = pickle.load(file)

####################################################################################

# function for smoothing time series for plotting

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='valid')
    return y_smooth

# functions for plotting SLE axes for volume plots
def vol2sle(x):
    
    return (((x-26.27)*0.918e6)/(361.8e3)*-1)

def sle2vol(x):
    return ((((x*361.8e3)/0.918e6)+26.27)*-1)

####################################################################################

# Plot global T vs Time graph

print("Starting Global Temp vs Time plot...")

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = atmos_d[i]
    
    plt.plot(plot_data[:,0], plot_data[:,1]-273, label = "_none", lw=0.8, linestyle="solid", color=line_cols[count], alpha=0.2)
    
    ma_y = smooth(plot_data[:,1], box_size)
    
    ma_x = plot_data[:,0]
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y-273, label = id[count], lw=0.8, linestyle="solid", color=line_cols[count])

    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()

plt.ylabel('Global Mean T (C)')
plt.xlabel('Year')
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving Global Temp vs Time plot...")

plt.savefig('HistGlobalTvsTime.png', dpi = 600, bbox_inches='tight')
#plt.savefig('GlobalTvsTime.png', dpi = 600, bbox_inches='tight')

####################################################################################

# Plot Volume vs Time graph

print("Starting GrIS Volume vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]
    
    plot_data["volumeAll"] = plot_data.groundedVol + plot_data.floatingVol

    plt.plot(plot_data.time, (plot_data.volumeAll)/1e15, label = id[count], lw=0.8, color = line_cols[count], linestyle = "solid")

    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()

plt.ylabel("GrIS volume (10$^{6}$ km$^{3}$)")
plt.xlabel('Year')
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving GrIS Volume vs Time plot...")

plt.savefig('HistGrISVolvsTime.png', dpi = 600,  bbox_inches='tight')  

####################################################################################

# Plot DeltaVAF vs Time graph

print("Starting GrIS VAF vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    plt.plot(plot_data.time, (plot_data.massSLE-plot_data.massSLE[0]), label = id[count], lw=0.8, color = line_cols[count], linestyle = "solid")
    #plt.plot(plot_data.time, (plot_data.massSLE), label = id[count], lw=0.8, color = line_cols[count], linestyle = "solid")
    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()

plt.ylabel("GrIS $\Delta$VAF (m SLE)")
plt.xlabel('Year')
plt.legend(loc = 'best', prop={'size': 5})

ax.set_yticks([-0.003, -0.002, -0.001, 0, 0.001, 0.002, 0.003]) 
ax.set_yticklabels(['0.003', '0.002', '0.001', '0', '-0.001', '-0.002', '-0.003']) 

print("Finished and saving GrIS VAF vs Time plot...")

plt.savefig('HistGrISVAFvsTime.png', dpi = 600,  bbox_inches='tight')  

####################################################################################

# Plot SMB vs Time graph

print("Starting GrIS SMB vs Time plot...")

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    plot_data["totalSMB"] = plot_data.groundedSMB + plot_data.floatingSMB

    plt.plot(plot_data.time, ((plot_data.totalSMB)*(0.918/1e9)), label = '_none', lw=0.8, color = line_cols[count], linestyle = "solid", alpha = 0.2)

    ma_y = smooth((plot_data.totalSMB)*(0.918/1e9), box_size)
    
    ma_x = (plot_data.time).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = id[count], lw=0.8, color = line_cols[count], linestyle = "solid")
    
    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()

plt.ylabel("GrIS SMB (Gt yr$^{-1}$)")
plt.xlabel('Year')
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving GrIS SMB vs Time plot...")

plt.savefig('HistGrISSMBvsTime.png', dpi = 600,  bbox_inches='tight')  

####################################################################################

# Plot Discharge vs Time graph

print("Starting GrIS Grounding Line Discharge vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    plt.plot(plot_data.time, ((plot_data.GLDischarge)*(0.918/1e9)), label = '_none', lw=0.8, color = line_cols[count], linestyle = "solid", alpha = 0.2)

    ma_y = smooth(((plot_data.GLDischarge)*(0.918/1e9)), box_size)
    
    ma_x = (plot_data.time).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = id[count], lw=0.8, color = line_cols[count], linestyle = "solid")

    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()

plt.ylabel("GrIS GL Discharge (Gt yr$^{-1}$)")
plt.xlabel('Year')
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving GrIS Grounding Line Discharge vs Time plot...")

plt.savefig('HistGrISGLDischargevsTime.png', dpi = 600,  bbox_inches='tight')  

####################################################################################