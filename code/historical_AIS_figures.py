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

def mass2sle(x):
    return x/361.8

def sle2mass(x):
    return x*361.8

####################################################################################

plt.rcParams.update({'font.size': 7})

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
        plot_data.time = plot_data.time - 11

        if i == "cx209": 
            
            ramp_VAF = plot_data.iloc[:,1:3]
            ramp_VAF.rename(columns={'VAF': 'cx209'}, inplace=True)

        elif i == "cw988":

            ramp_VAF["cw988"] = plot_data.iloc[:,2]

        elif i == "cw989":

            ramp_VAF["cw989"] = plot_data.iloc[:,2]

        elif i == "cw990":

            ramp_VAF["cw990"] = plot_data.iloc[:,2]

        else:

            continue


    else:

        plot_data = plot_data.iloc[124:]
        plot_data.time = plot_data.time - 125

        if i == "cy623":
            
            hist_VAF = plot_data.iloc[:,1:3]
            hist_VAF.rename(columns={'VAF': 'cy623'}, inplace=True)

        if i == "da914": 
            
            hist_VAF["da914"] = plot_data.iloc[:,2]

        elif i == "da916":

            hist_VAF["da916"] = plot_data.iloc[:,2]  

        elif i == "da917":

            hist_VAF["da917"] = plot_data.iloc[:,2]
            
ramp_VAF.reset_index(inplace=True, drop=True)
hist_VAF.reset_index(inplace=True, drop=True)

ramp_VAF["mean"] = ramp_VAF.iloc[:,1:].mean(axis=1, numeric_only=True)
ramp_VAF["std"] = ramp_VAF.iloc[:,1:].std(axis=1, numeric_only=True)

hist_VAF["mean"] = hist_VAF.iloc[:,1:].mean(axis=1, numeric_only=True)
hist_VAF["std"] = hist_VAF.iloc[:,1:].std(axis=1, numeric_only=True)

# get imbie data
imbie = pd.read_csv('/Users/tm17544/Downloads/imbie_antarctica_2021_Gt.csv')

imbie = imbie.iloc[:265]

imbie["time"] = imbie.Year - 125 - 1850

plt.plot(ramp_VAF.time - 1850, (ramp_VAF["mean"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "Overshoots", color = line_cols[1])
plt.fill_between(ramp_VAF.time - 1850, ((ramp_VAF["mean"]-ramp_VAF["mean"].iloc[0])-ramp_VAF["std"])*0.917/1e9, ((ramp_VAF["mean"]-ramp_VAF["mean"].iloc[0])+ramp_VAF["std"])*0.917/1e9, color = line_cols[1], alpha = 0.2)

plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cx209"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw988"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw989"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw990"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)

plt.plot(hist_VAF.time - 1850, (hist_VAF["mean"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "Historical", color = line_cols[5])
plt.fill_between(hist_VAF.time - 1850, ((hist_VAF["mean"]-hist_VAF["mean"].iloc[0])-hist_VAF["std"])*0.917/1e9, ((hist_VAF["mean"]-hist_VAF["mean"].iloc[0])+hist_VAF["std"])*0.917/1e9, color = line_cols[5], alpha = 0.2)

plt.plot(hist_VAF.time - 1850, (hist_VAF["cy623"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da914"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da916"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da917"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)

plot_data = icesheet_d["cs568"]
plot_data = plot_data.iloc[10:50]
plot_data.time = plot_data.time - 11

plt.plot(plot_data.time - 1850, (plot_data.VAF-plot_data.VAF.iloc[0])*0.917/1e9, label = "Ctrl (cs568)", color = line_cols[0], linestyle = line_stys[0])

plt.plot(imbie.time, imbie["Cumulative mass balance (Gt)"], label = 'IMBIE (2023)', color = line_cols[0])

plt.ylabel("Mass change (Gt)")
plt.xlabel('Years')
plt.legend(loc = 'best')

ax = plt.gca()

secax = ax.secondary_yaxis('right', functions=(mass2sle, sle2mass)) 
secax.set_ylabel('Sea level contribution (mm)')

print("Finished and saving AIS VAF vs Time plot...")

plt.savefig('./Projects/figures/HistAISVAFvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot GroundedSMB vs Time graph

print("Starting AIS Grounded SMB vs Time plot...")

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    if i in {"cs568","cx209", "cw988", "cw989", "cw990"}:

        plot_data = plot_data.iloc[10:50]
        plot_data.time = plot_data.time - 11

        if i == "cx209": 
            
            ramp_VAF = plot_data.iloc[:,[1,3]]
            ramp_VAF.rename(columns={'groundedSMB': 'cx209'}, inplace=True)

        elif i == "cw988":

            ramp_VAF["cw988"] = plot_data.iloc[:,3]

        elif i == "cw989":

            ramp_VAF["cw989"] = plot_data.iloc[:,3]

        elif i == "cw990":

            ramp_VAF["cw990"] = plot_data.iloc[:,3]

        else:

            continue


    else:

        plot_data = plot_data.iloc[124:]
        plot_data.time = plot_data.time - 125

        if i == "cy623":
            
            hist_VAF = plot_data.iloc[:,[1,3]]
            hist_VAF.rename(columns={'groundedSMB': 'cy623'}, inplace=True)

        if i == "da914": 
            
            hist_VAF["da914"] = plot_data.iloc[:,3]

        elif i == "da916":

            hist_VAF["da916"] = plot_data.iloc[:,3]  

        elif i == "da917":

            hist_VAF["da917"] = plot_data.iloc[:,3]
            
ramp_VAF.reset_index(inplace=True, drop=True)
hist_VAF.reset_index(inplace=True, drop=True)

ramp_VAF["mean"] = ramp_VAF.iloc[:,1:].mean(axis=1, numeric_only=True)
ramp_VAF["std"] = ramp_VAF.iloc[:,1:].std(axis=1, numeric_only=True)

hist_VAF["mean"] = hist_VAF.iloc[:,1:].mean(axis=1, numeric_only=True)
hist_VAF["std"] = hist_VAF.iloc[:,1:].std(axis=1, numeric_only=True)

rignot = pd.read_csv('/Users/tm17544/Downloads/SMB-ANT-Sectors-1979-2021-RACMO2.3p2-ERA5-2km.csv')

rignot["time"] = rignot["Year"] - 124 - 1850

"""
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["mean"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "Overshoots", color = line_cols[1])
plt.fill_between(ramp_VAF.time - 1850, ((ramp_VAF["mean"]-ramp_VAF["mean"].iloc[0])-ramp_VAF["std"])*0.917/1e9, ((ramp_VAF["mean"]-ramp_VAF["mean"].iloc[0])+ramp_VAF["std"])*0.917/1e9, color = line_cols[1], alpha = 0.2)

plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cx209"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw988"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw989"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw990"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)

plt.plot(hist_VAF.time - 1850, (hist_VAF["mean"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "Historical", color = line_cols[5])
plt.fill_between(hist_VAF.time - 1850, ((hist_VAF["mean"]-hist_VAF["mean"].iloc[0])-hist_VAF["std"])*0.917/1e9, ((hist_VAF["mean"]-hist_VAF["mean"].iloc[0])+hist_VAF["std"])*0.917/1e9, color = line_cols[5], alpha = 0.2)

plt.plot(hist_VAF.time - 1850, (hist_VAF["cy623"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da914"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da916"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da917"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)

plot_data = icesheet_d["cs568"]
plot_data = plot_data.iloc[10:50]
plot_data.time = plot_data.time - 11

plt.plot(plot_data.time - 1850, (plot_data.groundedSMB-plot_data.groundedSMB.iloc[0])*0.917/1e9, label = "Ctrl (cs568)", color = line_cols[0], linestyle = line_stys[0])
"""
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["mean"])*0.917/1e9, label = "Overshoots", color = line_cols[1])
plt.fill_between(ramp_VAF.time - 1850, ((ramp_VAF["mean"])-ramp_VAF["std"])*0.917/1e9, ((ramp_VAF["mean"])+ramp_VAF["std"])*0.917/1e9, color = line_cols[1], alpha = 0.2)

plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cx209"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw988"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw989"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw990"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)

plt.plot(hist_VAF.time - 1850, (hist_VAF["mean"])*0.917/1e9, label = "Historical", color = line_cols[5])
plt.fill_between(hist_VAF.time - 1850, ((hist_VAF["mean"])-hist_VAF["std"])*0.917/1e9, ((hist_VAF["mean"])+hist_VAF["std"])*0.917/1e9, color = line_cols[5], alpha = 0.2)

plt.plot(hist_VAF.time - 1850, (hist_VAF["cy623"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da914"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da916"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da917"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)

plot_data = icesheet_d["cs568"]
plot_data = plot_data.iloc[10:50]
plot_data.time = plot_data.time - 11

plt.plot(plot_data.time - 1850, (plot_data.groundedSMB)*0.917/1e9, label = "Ctrl (cs568)", color = line_cols[0], linestyle = line_stys[0])

plt.plot(rignot.time, rignot["AIS"], label = 'Noel et al. (2023)', color = line_cols[0])

plt.ylabel("Grounded SMB (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.legend(loc = 'center left', bbox_to_anchor=(1, 0.5))

print("Finished and saving AIS Grounded SMB vs Time plot...")

plt.savefig('./Projects/figures/HistAISGroundedSMBvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot Discharge vs Time graph

print("Starting AIS Grounding Line Discharge vs Time plot...")

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    if i in {"cs568","cx209", "cw988", "cw989", "cw990"}:

        plot_data = plot_data.iloc[10:50]
        plot_data.time = plot_data.time - 11

        if i == "cx209": 
            
            ramp_VAF = plot_data.iloc[:,[1,6]]
            ramp_VAF.rename(columns={'GLDischarge': 'cx209'}, inplace=True)

        elif i == "cw988":

            ramp_VAF["cw988"] = plot_data.iloc[:,6]

        elif i == "cw989":

            ramp_VAF["cw989"] = plot_data.iloc[:,6]

        elif i == "cw990":

            ramp_VAF["cw990"] = plot_data.iloc[:,6]

        else:

            continue


    else:

        plot_data = plot_data.iloc[124:]
        plot_data.time = plot_data.time - 125

        if i == "cy623":
            
            hist_VAF = plot_data.iloc[:,[1,6]]
            hist_VAF.rename(columns={'GLDischarge': 'cy623'}, inplace=True)

        if i == "da914": 
            
            hist_VAF["da914"] = plot_data.iloc[:,6]

        elif i == "da916":

            hist_VAF["da916"] = plot_data.iloc[:,6]  

        elif i == "da917":

            hist_VAF["da917"] = plot_data.iloc[:,6]
            
ramp_VAF.reset_index(inplace=True, drop=True)
hist_VAF.reset_index(inplace=True, drop=True)

ramp_VAF["mean"] = ramp_VAF.iloc[:,1:].mean(axis=1, numeric_only=True)
ramp_VAF["std"] = ramp_VAF.iloc[:,1:].std(axis=1, numeric_only=True)

hist_VAF["mean"] = hist_VAF.iloc[:,1:].mean(axis=1, numeric_only=True)
hist_VAF["std"] = hist_VAF.iloc[:,1:].std(axis=1, numeric_only=True)
"""
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["mean"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "Overshoots", color = line_cols[1])
plt.fill_between(ramp_VAF.time - 1850, ((ramp_VAF["mean"]-ramp_VAF["mean"].iloc[0])-ramp_VAF["std"])*0.917/1e9, ((ramp_VAF["mean"]-ramp_VAF["mean"].iloc[0])+ramp_VAF["std"])*0.917/1e9, color = line_cols[1], alpha = 0.2)

plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cx209"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw988"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw989"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw990"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)

plt.plot(hist_VAF.time - 1850, (hist_VAF["mean"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "Historical", color = line_cols[5])
plt.fill_between(hist_VAF.time - 1850, ((hist_VAF["mean"]-hist_VAF["mean"].iloc[0])-hist_VAF["std"])*0.917/1e9, ((hist_VAF["mean"]-hist_VAF["mean"].iloc[0])+hist_VAF["std"])*0.917/1e9, color = line_cols[5], alpha = 0.2)

plt.plot(hist_VAF.time - 1850, (hist_VAF["cy623"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da914"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da916"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da917"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)

plot_data = icesheet_d["cs568"]
plot_data = plot_data.iloc[10:50]
plot_data.time = plot_data.time - 11

plt.plot(plot_data.time - 1850, (plot_data.groundedSMB-plot_data.groundedSMB.iloc[0])*0.917/1e9, label = "Ctrl (cs568)", color = line_cols[0], linestyle = line_stys[0])
"""
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["mean"])*0.917/1e9, label = "Overshoots", color = line_cols[1])
plt.fill_between(ramp_VAF.time - 1850, ((ramp_VAF["mean"])-ramp_VAF["std"])*0.917/1e9, ((ramp_VAF["mean"])+ramp_VAF["std"])*0.917/1e9, color = line_cols[1], alpha = 0.2)

plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cx209"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw988"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw989"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw990"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)

plt.plot(hist_VAF.time - 1850, (hist_VAF["mean"])*0.917/1e9, label = "Historical", color = line_cols[5])
plt.fill_between(hist_VAF.time - 1850, ((hist_VAF["mean"])-hist_VAF["std"])*0.917/1e9, ((hist_VAF["mean"])+hist_VAF["std"])*0.917/1e9, color = line_cols[5], alpha = 0.2)

plt.plot(hist_VAF.time - 1850, (hist_VAF["cy623"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da914"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da916"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da917"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)

plot_data = icesheet_d["cs568"]
plot_data = plot_data.iloc[10:50]
plot_data.time = plot_data.time - 11

plt.plot(plot_data.time - 1850, (plot_data.GLDischarge)*0.917/1e9, label = "Ctrl (cs568)", color = line_cols[0], linestyle = line_stys[0])

plt.plot(rignot.time, rignot["Discharge"], label = 'Rignot et al. (2019)', color = line_cols[0])

plt.ylabel("GL Discharge (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.legend(loc = 'center left', bbox_to_anchor=(1, 0.5))

print("Finished and saving AIS Grounding Line Discharge vs Time plot...")

plt.savefig('./Projects/figures/HistAISGLDischargevsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot Ice Shelf BMB vs Time graph

print("Starting AIS Ice Shelf BMB vs Time plot...")

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    if i in {"cs568","cx209", "cw988", "cw989", "cw990"}:

        plot_data = plot_data.iloc[10:50]
        plot_data.time = plot_data.time - 11

        if i == "cx209": 
            
            ramp_VAF = plot_data.iloc[:,[1,5]]
            ramp_VAF.rename(columns={'floatingBMB': 'cx209'}, inplace=True)

        elif i == "cw988":

            ramp_VAF["cw988"] = plot_data.iloc[:,5]

        elif i == "cw989":

            ramp_VAF["cw989"] = plot_data.iloc[:,5]

        elif i == "cw990":

            ramp_VAF["cw990"] = plot_data.iloc[:,5]

        else:

            continue


    else:

        plot_data = plot_data.iloc[124:]
        plot_data.time = plot_data.time - 125

        if i == "cy623":
            
            hist_VAF = plot_data.iloc[:,[1,5]]
            hist_VAF.rename(columns={'floatingBMB': 'cy623'}, inplace=True)

        if i == "da914": 
            
            hist_VAF["da914"] = plot_data.iloc[:,5]

        elif i == "da916":

            hist_VAF["da916"] = plot_data.iloc[:,5]  

        elif i == "da917":

            hist_VAF["da917"] = plot_data.iloc[:,5]
            
ramp_VAF.reset_index(inplace=True, drop=True)
hist_VAF.reset_index(inplace=True, drop=True)

ramp_VAF["mean"] = ramp_VAF.iloc[:,1:].mean(axis=1, numeric_only=True)
ramp_VAF["std"] = ramp_VAF.iloc[:,1:].std(axis=1, numeric_only=True)

hist_VAF["mean"] = hist_VAF.iloc[:,1:].mean(axis=1, numeric_only=True)
hist_VAF["std"] = hist_VAF.iloc[:,1:].std(axis=1, numeric_only=True)
"""
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["mean"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "Overshoots", color = line_cols[1])
plt.fill_between(ramp_VAF.time - 1850, ((ramp_VAF["mean"]-ramp_VAF["mean"].iloc[0])-ramp_VAF["std"])*0.917/1e9, ((ramp_VAF["mean"]-ramp_VAF["mean"].iloc[0])+ramp_VAF["std"])*0.917/1e9, color = line_cols[1], alpha = 0.2)

plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cx209"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw988"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw989"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw990"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)

plt.plot(hist_VAF.time - 1850, (hist_VAF["mean"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "Historical", color = line_cols[5])
plt.fill_between(hist_VAF.time - 1850, ((hist_VAF["mean"]-hist_VAF["mean"].iloc[0])-hist_VAF["std"])*0.917/1e9, ((hist_VAF["mean"]-hist_VAF["mean"].iloc[0])+hist_VAF["std"])*0.917/1e9, color = line_cols[5], alpha = 0.2)

plt.plot(hist_VAF.time - 1850, (hist_VAF["cy623"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da914"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da916"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da917"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)

plot_data = icesheet_d["cs568"]
plot_data = plot_data.iloc[10:50]
plot_data.time = plot_data.time - 11

plt.plot(plot_data.time - 1850, (plot_data.groundedSMB-plot_data.groundedSMB.iloc[0])*0.917/1e9, label = "Ctrl (cs568)", color = line_cols[0], linestyle = line_stys[0])
"""
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["mean"])*0.917/1e9, label = "Overshoots", color = line_cols[1])
plt.fill_between(ramp_VAF.time - 1850, ((ramp_VAF["mean"])-ramp_VAF["std"])*0.917/1e9, ((ramp_VAF["mean"])+ramp_VAF["std"])*0.917/1e9, color = line_cols[1], alpha = 0.2)

plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cx209"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw988"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw989"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time - 1850, (ramp_VAF["cw990"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)

plt.plot(hist_VAF.time - 1850, (hist_VAF["mean"])*0.917/1e9, label = "Historical", color = line_cols[5])
plt.fill_between(hist_VAF.time - 1850, ((hist_VAF["mean"])-hist_VAF["std"])*0.917/1e9, ((hist_VAF["mean"])+hist_VAF["std"])*0.917/1e9, color = line_cols[5], alpha = 0.2)

plt.plot(hist_VAF.time - 1850, (hist_VAF["cy623"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da914"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da916"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time - 1850, (hist_VAF["da917"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)

plot_data = icesheet_d["cs568"]
plot_data = plot_data.iloc[10:50]
plot_data.time = plot_data.time - 11

plt.plot(plot_data.time - 1850, (plot_data.floatingBMB)*0.917/1e9, label = "Ctrl (cs568)", color = line_cols[0], linestyle = line_stys[0])

# plt.plot(rignot.time, rignot["Discharge"], label = 'Rignot et al. (2019)', color = line_cols[0])

plt.ylabel("Ice shelf basal melt (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.legend(loc = 'center left', bbox_to_anchor=(1, 0.5))

print("Finished and saving AIS Grounding Line Discharge vs Time plot...")

plt.savefig('./Projects/figures/HistAISShelfBMBvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

#################################################################################### """