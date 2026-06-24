####################################################################################
# Imports
import numpy as np
import pickle
import matplotlib.pyplot as plt
import pandas as pd

####################################################################################

id_all=["cx209", "cz376", "da892", "dv234", "dn822", "dv233"]

run_type_all = ["up2p0 (cx209)", "up2p0-gwl4p0n (cz376)", "up2p0-gwl4p0-50y-dn2p0 (da892)", "up2p0-gwl4p0-50y-dn2p0-comt. (dv234)", "up2p0-gwl4p0-50y-dn2p0-gwl2p0-v1 (dn822)", "up2p0-gwl4p0-50y-dn2p0-gwl2p0-v2 (dv233)"]

runs_all = dict(zip(id_all, run_type_all))

line_cols_all=['tab:blue', 'tab:orange', 'tab:green', 'tab:green', 'tab:purple', 'tab:brown']

line_stys_all=["solid","solid","solid","solid","solid","solid"]

####################################################################################

with open('/home/tm17544/GrIS_data_individual_setup_check.pkl', 'rb') as file:
    icesheet_d = pickle.load(file) 

####################################################################################

# function for smoothing time series for plotting
def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='valid')
    return y_smooth

# functions for converting mass change above flotation (in Gt) to sea level contribution (in m) for second axes
def mass2sle(x):
    return x*(-1)/(361.8*1000)

def sle2mass(x):
    return x*(-1)*(361.8*1000)

# Set font size for plots
plt.rcParams.update({'font.size': 8})

####################################################################################

# Plot VAF vs Time graph
print("Starting VAF vs Time plot...")

initialVAF = icesheet_d["cx209"][0]["VAF"][0]

count = 0

plt.figure(figsize=(4, 3))

for i in id_all:

    plot_data = icesheet_d[i][0]

    VAF_data = plot_data["VAF"]
    time_series = plot_data["time"]

    plt.plot(time_series - 1850, (VAF_data - initialVAF)*(0.918/1e9), label = runs_all[i], lw=0.8, color = line_cols_all[count], linestyle = line_stys_all[count])

    count = count + 1

ax = plt.gca()

ax.set_ylabel("Mass above\nflotation change (Gt)")
ax.set_xlabel('Years')

# Add a second y-axis for sea level equivalent
secax = ax.secondary_yaxis('right', functions=(mass2sle, sle2mass)) 
secax.set_ylabel('Sea level contribution (m)')

ax.set_xlim([0, 800])

handles, labels = ax.get_legend_handles_labels()

ax.legend(handles, labels, loc = 'best', prop={'size': 5})

plt.savefig('/home/tm17544/GrISVAFvsTime_TIPMIP_check.png', dpi = 600, bbox_inches='tight')

####################################################################################

# Plot SMB (grounded and floating) vs GSAT graph

print("Starting SMB vs Time plot...")

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

for i in id_all:
    
    plot_data = icesheet_d[i][0]

    SMB_data = plot_data["grounded_SMB"]
    time_series = plot_data["time"]

    plt.plot(time_series - 1850, ((SMB_data)*(0.918/1e9)), label = '_None', lw=0.8, color = line_cols_all[count], linestyle = line_stys_all[count], alpha = 0.10)
    
    ma_y_gr = smooth((SMB_data)*(0.918/1e9), box_size)
    
    ma_x = (time_series - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y_gr, label = runs_all[i], lw=0.8, color = line_cols_all[count], linestyle = line_stys_all[count])
    
    count = count + 1

ax = plt.gca()

ax.set_ylabel("Grounded SMB (Gt yr$^{-1}$)")
ax.set_xlabel('Years')

handles, labels = ax.get_legend_handles_labels()

ax.legend(handles, labels, loc = 'best', prop={'size': 5})

plt.savefig('/home/tm17544/GrISSMBvsTime_TIPMIP_check.png', dpi = 600, bbox_inches='tight')

print("Finished and saving SMB vs Time plot...")


