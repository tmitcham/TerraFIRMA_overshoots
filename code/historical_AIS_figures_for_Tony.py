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

# Read ice sheet data

if os.path.exists('../processed_data/historical_icesheet_data.pkl'):

    print("Loading ice sheet data from file...")

    with open('../processed_data/historical_icesheet_data.pkl', 'rb') as file:

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

# Plot Volume vs Time graph

print("Starting AIS Volume vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]
    
    plot_data["volumeAll"] = plot_data.groundedVol + plot_data.floatingVol

    plt.plot(plot_data.time, (plot_data.volumeAll)/1e15, label = id[count], lw=0.8, color = line_cols[count], linestyle = "solid")

    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()

plt.ylabel("AIS volume (10$^{6}$ km$^{3}$)")
plt.xlabel('Year')
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving AIS Volume vs Time plot...")

plt.savefig('HistAISVolvsTime.png', dpi = 600,  bbox_inches='tight')  

####################################################################################

# Plot DeltaVAF vs Time graph

print("Starting AIS VAF vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    plt.plot(plot_data.time, (plot_data.massSLE-plot_data.massSLE[0]), label = id[count], lw=0.8, color = line_cols[count], linestyle = "solid")
    #plt.plot(plot_data.time, (plot_data.massSLE), label = id[count], lw=0.8, color = line_cols[count], linestyle = "solid")
    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()

plt.ylabel("AIS $\Delta$VAF (m SLE)")
plt.xlabel('Year')
plt.legend(loc = 'best', prop={'size': 5})

ax.set_yticks([-0.12, -0.10, -0.08, -0.06, -0.04, -0.02, 0]) 
ax.set_yticklabels(['0.12', '0.10', '0.08', '0.06', '0.04', '0.02', '0']) 

print("Finished and saving AIS VAF vs Time plot...")

plt.savefig('HistAISVAFvsTime.png', dpi = 600,  bbox_inches='tight')  

####################################################################################

# Plot Grounded SMB vs Time graph

print("Starting AIS Grounded SMB vs Time plot...")

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    plt.plot(plot_data.time, ((plot_data.groundedSMB)*(0.918/1e9)), label = '_none', lw=0.8, color = line_cols[count], linestyle = "solid", alpha = 0.2)

    ma_y = smooth((plot_data.groundedSMB)*(0.918/1e9), box_size)
    
    ma_x = (plot_data.time).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = id[count], lw=0.8, color = line_cols[count], linestyle = "solid")
    
    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()

plt.ylabel("AIS Grounded SMB (Gt yr$^{-1}$)")
plt.xlabel('Year')
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving AIS Grounded SMB vs Time plot...")

plt.savefig('HistAISGroundedSMBvsTime.png', dpi = 600,  bbox_inches='tight')    

####################################################################################

# Plot Floating SMB vs Time graph

print("Starting AIS Floating SMB vs Time plot...")

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    plt.plot(plot_data.time, ((plot_data.floatingSMB)*(0.918/1e9)), label = '_none', lw=0.8, color = line_cols[count], linestyle = "solid", alpha = 0.2)

    ma_y = smooth((plot_data.floatingSMB)*(0.918/1e9), box_size)
    
    ma_x = (plot_data.time).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = id[count], lw=0.8, color = line_cols[count], linestyle = "solid")
    
    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()

plt.ylabel("AIS Floating SMB (Gt yr$^{-1}$)")
plt.xlabel('Year')
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving AIS Floating SMB vs Time plot...")

plt.savefig('HistAISFloatingSMBvsTime.png', dpi = 600,  bbox_inches='tight')  

####################################################################################

# Plot Floating BMB vs Time graph

print("Starting AIS Floating BMB vs Time plot...")

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    plt.plot(plot_data.time, ((plot_data.floatingBMB)*(0.918/1e9)), label = '_none', lw=0.8, color = line_cols[count], linestyle = "solid", alpha = 0.2)

    ma_y = smooth((plot_data.floatingBMB)*(0.918/1e9), box_size)
    
    ma_x = (plot_data.time).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = id[count], lw=0.8, color = line_cols[count], linestyle = "solid")
    
    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()

plt.ylabel("AIS Floating BMB (Gt yr$^{-1}$)")
plt.xlabel('Year')
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving AIS Floating BMB vs Time plot...")

plt.savefig('HistAISFloatingBMBvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot Discharge vs Time graph

print("Starting AIS Grounding Line Discharge vs Time plot...")

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

plt.ylabel("AIS GL Discharge (Gt yr$^{-1}$)")
plt.xlabel('Year')
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving AIS Grounding Line Discharge vs Time plot...")

plt.savefig('HistAISGLDischargevsTime.png', dpi = 600,  bbox_inches='tight')  

####################################################################################