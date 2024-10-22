####################################################################################
# Imports
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt

####################################################################################

# For comparison between historical and idealised ramp-up simulations
id = ["cs568", "cx209", "cw988", "cw989", "cw990", "cy623", "da914", "da916", "da917"]
run_type = ["Ctrl","Ramp-Up 1", "Ramp-Up 2", "Ramp-Up 3", "Ramp-Up 4", "Hist 1", "Hist 2", "Hist 3", "Hist 4"]
runs = dict(zip(id, run_type))

# Black, red and blue colours for plotting
line_cols = ['#000000','#C30F0E','#0003C7']

# Set plot font size for all plots
plt.rcParams.update({'font.size': 7})

# Read in the processed (using diagnostics BISICLES filetool) ice sheet data

print("Loading ice sheet data from file...")

with open('../processed_data/historical_icesheet_data.pkl', 'rb') as file:

    icesheet_d = pickle.load(file)

####################################################################################

# Define some useful functions for plotting 

# Moving window smoothing of a time series
def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='valid')
    return y_smooth

# Convert mass to sea level equivalent for second axes
def mass2sle(x):
    return x/361.8

def sle2mass(x):
    return x*361.8


####################################################################################

# Load auxillary data sets for comparison

# Load the IMBIE (2023) data
imbie = pd.read_csv('../aux_data/imbie_antarctica_2021_Gt.csv')

# Select 1992-2014 data for comparison
imbie = imbie.iloc[:265]

# Set first year to 28 rather than 1992
imbie["time"] = imbie.Year - 1975


# Load the Noel et al. (2023) data
noel = pd.read_csv('../aux_data/SMB-ANT-Sectors-1979-2021-RACMO2.3p2-ERA5-2km.csv')

noel["time"] = noel["Year"];


# Load the (preprocessed) Rignot et al. (2019) data
rignot = pd.read_csv('../aux_data/rignot_2019_AIS.csv')
rignot 

####################################################################################

# Plot VAF vs Time graph

print("Starting AIS VAF vs Time plot...")

plt.figure(figsize=(4, 3))

# Process the data for plotting

for i in id:

    plot_data = icesheet_d[i]

    if i in {"cs568","cx209", "cw988", "cw989", "cw990"}:

        # Get years 10-50 for ramp-up simulations (and piCtrl)
        plot_data = plot_data.iloc[10:50]

        # Reset the first year to 1 rather than 1861
        plot_data.time = plot_data.time - 1860

        if i == "cx209": 
            
            # Get the Year and the ice sheet VAF
            ramp_VAF = plot_data.iloc[:,1:3]
            ramp_VAF.rename(columns={'VAF': 'cx209'}, inplace=True)

        elif i == "cw988":

            ramp_VAF["cw988"] = plot_data.iloc[:,2]

        elif i == "cw989":

            ramp_VAF["cw989"] = plot_data.iloc[:,2]

        elif i == "cw990":

            ramp_VAF["cw990"] = plot_data.iloc[:,2]

        else:

            # don't want the ctrl (cs568) in the ramp-up data frame
            continue


    else:

        # Get years 1975-2014 for historical simulations
        plot_data = plot_data.iloc[124:]

        # Reset the first year to 1 rather than 1975
        plot_data.time = plot_data.time - 1974

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

# Calculate the ensemble mean and standard deviation for each time point
ramp_VAF["mean"] = ramp_VAF.iloc[:,1:].mean(axis=1, numeric_only=True)
ramp_VAF["std"] = ramp_VAF.iloc[:,1:].std(axis=1, numeric_only=True)

hist_VAF["mean"] = hist_VAF.iloc[:,1:].mean(axis=1, numeric_only=True)
hist_VAF["std"] = hist_VAF.iloc[:,1:].std(axis=1, numeric_only=True)

# Load the control run data for comparison
ctrl_data = icesheet_d["cs568"]
ctrl_data = plot_data.iloc[10:50]
ctrl_data.time = plot_data.time - 1860

# Start making the plot

# Plot the ramp-up ensemble mean VAF time series in Gt and fill between +/- 1 standard deviation
plt.plot(ramp_VAF.time, (ramp_VAF["mean"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "Overshoots", color = line_cols[1])
plt.fill_between(ramp_VAF.time, ((ramp_VAF["mean"]-ramp_VAF["mean"].iloc[0])-ramp_VAF["std"])*0.917/1e9, ((ramp_VAF["mean"]-ramp_VAF["mean"].iloc[0])+ramp_VAF["std"])*0.917/1e9, color = line_cols[1], alpha = 0.2)

# Plot (lightly in the background) the individual ensemble members
plt.plot(ramp_VAF.time, (ramp_VAF["cx209"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time, (ramp_VAF["cw988"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time, (ramp_VAF["cw989"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_VAF.time, (ramp_VAF["cw990"]-ramp_VAF["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)

# Plot the historical ensemble mean VAF time series in Gt and fill between +/- 1 standard deviation
plt.plot(hist_VAF.time, (hist_VAF["mean"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "Historical", color = line_cols[2])
plt.fill_between(hist_VAF.time, ((hist_VAF["mean"]-hist_VAF["mean"].iloc[0])-hist_VAF["std"])*0.917/1e9, ((hist_VAF["mean"]-hist_VAF["mean"].iloc[0])+hist_VAF["std"])*0.917/1e9, color = line_cols[2], alpha = 0.2)

# Plot (lightly in the background) the individual ensemble members
plt.plot(hist_VAF.time, (hist_VAF["cy623"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[2], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da914"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[2], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da916"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[2], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da917"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[2], alpha = 0.1)

# Add the control run 
plt.plot(ctrl_data.time, (ctrl_data.VAF-plot_data.VAF.iloc[0])*0.917/1e9, label = "Ctrl (cs568)", color = line_cols[0], linestyle = 'dashed')

# Add the IMBIE data
plt.plot(imbie.time, imbie["Cumulative mass balance (Gt)"], label = 'IMBIE (2023)', color = line_cols[0])

# Add labels and legend
plt.ylabel("Mass change (Gt)")
plt.xlabel('Years')
plt.legend(loc = 'best')

# Add a second y-axis for sea level equivalent
ax = plt.gca()
secax = ax.secondary_yaxis('right', functions=(mass2sle, sle2mass)) 
secax.set_ylabel('Sea level contribution (mm)')

print("Finished and saving AIS VAF vs Time plot...")

plt.savefig('../figures/HistAISVAFvsTime.png', dpi = 600,  bbox_inches='tight')  

####################################################################################

# Plot GroundedSMB vs Time graph

print("Starting AIS Grounded SMB vs Time plot...")

plt.figure(figsize=(4, 3))

# Process the data for plotting in the same way as for the VAF plot but choosing the 
# grounded SMB data from the original data frame

for i in id:

    plot_data = icesheet_d[i]

    if i in {"cs568","cx209", "cw988", "cw989", "cw990"}:

        plot_data = plot_data.iloc[10:50]
        plot_data.time = plot_data.time - 1860

        if i == "cx209": 
            
            ramp_grSMB = plot_data.iloc[:,[1,3]]
            ramp_grSMB.rename(columns={'groundedSMB': 'cx209'}, inplace=True)

        elif i == "cw988":

            ramp_grSMB["cw988"] = plot_data.iloc[:,3]

        elif i == "cw989":

            ramp_grSMB["cw989"] = plot_data.iloc[:,3]

        elif i == "cw990":

            ramp_grSMB["cw990"] = plot_data.iloc[:,3]

        else:

            continue


    else:

        plot_data = plot_data.iloc[124:]
        plot_data.time = plot_data.time - 1974

        if i == "cy623":
            
            hist_VAF = plot_data.iloc[:,[1,3]]
            hist_VAF.rename(columns={'groundedSMB': 'cy623'}, inplace=True)

        if i == "da914": 
            
            hist_VAF["da914"] = plot_data.iloc[:,3]

        elif i == "da916":

            hist_VAF["da916"] = plot_data.iloc[:,3]  

        elif i == "da917":

            hist_VAF["da917"] = plot_data.iloc[:,3]
            
ramp_grSMB.reset_index(inplace=True, drop=True)
hist_VAF.reset_index(inplace=True, drop=True)

ramp_grSMB["mean"] = ramp_grSMB.iloc[:,1:].mean(axis=1, numeric_only=True)
ramp_grSMB["std"] = ramp_grSMB.iloc[:,1:].std(axis=1, numeric_only=True)

hist_VAF["mean"] = hist_VAF.iloc[:,1:].mean(axis=1, numeric_only=True)
hist_VAF["std"] = hist_VAF.iloc[:,1:].std(axis=1, numeric_only=True)

"""
plt.plot(ramp_grSMB.time, (ramp_grSMB["mean"]-ramp_grSMB["mean"].iloc[0])*0.917/1e9, label = "Overshoots", color = line_cols[1])
plt.fill_between(ramp_grSMB.time, ((ramp_grSMB["mean"]-ramp_grSMB["mean"].iloc[0])-ramp_grSMB["std"])*0.917/1e9, ((ramp_grSMB["mean"]-ramp_grSMB["mean"].iloc[0])+ramp_grSMB["std"])*0.917/1e9, color = line_cols[1], alpha = 0.2)

plt.plot(ramp_grSMB.time, (ramp_grSMB["cx209"]-ramp_grSMB["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_grSMB.time, (ramp_grSMB["cw988"]-ramp_grSMB["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_grSMB.time, (ramp_grSMB["cw989"]-ramp_grSMB["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_grSMB.time, (ramp_grSMB["cw990"]-ramp_grSMB["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)

plt.plot(hist_VAF.time, (hist_VAF["mean"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "Historical", color = line_cols[5])
plt.fill_between(hist_VAF.time, ((hist_VAF["mean"]-hist_VAF["mean"].iloc[0])-hist_VAF["std"])*0.917/1e9, ((hist_VAF["mean"]-hist_VAF["mean"].iloc[0])+hist_VAF["std"])*0.917/1e9, color = line_cols[5], alpha = 0.2)

plt.plot(hist_VAF.time, (hist_VAF["cy623"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da914"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da916"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da917"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)

plot_data = icesheet_d["cs568"]
plot_data = plot_data.iloc[10:50]
plot_data.time = plot_data.time - 11

plt.plot(plot_data.time, (plot_data.groundedSMB-plot_data.groundedSMB.iloc[0])*0.917/1e9, label = "Ctrl (cs568)", color = line_cols[0], linestyle = line_stys[0])
"""
plt.plot(ramp_grSMB.time, (ramp_grSMB["mean"])*0.917/1e9, label = "Overshoots", color = line_cols[1])
plt.fill_between(ramp_grSMB.time, ((ramp_grSMB["mean"])-ramp_grSMB["std"])*0.917/1e9, ((ramp_grSMB["mean"])+ramp_grSMB["std"])*0.917/1e9, color = line_cols[1], alpha = 0.2)

plt.plot(ramp_grSMB.time, (ramp_grSMB["cx209"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_grSMB.time, (ramp_grSMB["cw988"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_grSMB.time, (ramp_grSMB["cw989"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_grSMB.time, (ramp_grSMB["cw990"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)

plt.plot(hist_VAF.time, (hist_VAF["mean"])*0.917/1e9, label = "Historical", color = line_cols[5])
plt.fill_between(hist_VAF.time, ((hist_VAF["mean"])-hist_VAF["std"])*0.917/1e9, ((hist_VAF["mean"])+hist_VAF["std"])*0.917/1e9, color = line_cols[5], alpha = 0.2)

plt.plot(hist_VAF.time, (hist_VAF["cy623"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da914"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da916"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da917"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)

plot_data = icesheet_d["cs568"]
plot_data = plot_data.iloc[10:50]
plot_data.time = plot_data.time - 11

plt.plot(plot_data.time, (plot_data.groundedSMB)*0.917/1e9, label = "Ctrl (cs568)", color = line_cols[0], linestyle = line_stys[0])

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
            
            ramp_GLD = plot_data.iloc[:,[1,6]]
            ramp_GLD.rename(columns={'GLDischarge': 'cx209'}, inplace=True)

        elif i == "cw988":

            ramp_GLD["cw988"] = plot_data.iloc[:,6]

        elif i == "cw989":

            ramp_GLD["cw989"] = plot_data.iloc[:,6]

        elif i == "cw990":

            ramp_GLD["cw990"] = plot_data.iloc[:,6]

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
            
ramp_GLD.reset_index(inplace=True, drop=True)
hist_VAF.reset_index(inplace=True, drop=True)

ramp_GLD["mean"] = ramp_GLD.iloc[:,1:].mean(axis=1, numeric_only=True)
ramp_GLD["std"] = ramp_GLD.iloc[:,1:].std(axis=1, numeric_only=True)

hist_VAF["mean"] = hist_VAF.iloc[:,1:].mean(axis=1, numeric_only=True)
hist_VAF["std"] = hist_VAF.iloc[:,1:].std(axis=1, numeric_only=True)
"""
plt.plot(ramp_GLD.time, (ramp_GLD["mean"]-ramp_GLD["mean"].iloc[0])*0.917/1e9, label = "Overshoots", color = line_cols[1])
plt.fill_between(ramp_GLD.time, ((ramp_GLD["mean"]-ramp_GLD["mean"].iloc[0])-ramp_GLD["std"])*0.917/1e9, ((ramp_GLD["mean"]-ramp_GLD["mean"].iloc[0])+ramp_GLD["std"])*0.917/1e9, color = line_cols[1], alpha = 0.2)

plt.plot(ramp_GLD.time, (ramp_GLD["cx209"]-ramp_GLD["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_GLD.time, (ramp_GLD["cw988"]-ramp_GLD["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_GLD.time, (ramp_GLD["cw989"]-ramp_GLD["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_GLD.time, (ramp_GLD["cw990"]-ramp_GLD["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)

plt.plot(hist_VAF.time, (hist_VAF["mean"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "Historical", color = line_cols[5])
plt.fill_between(hist_VAF.time, ((hist_VAF["mean"]-hist_VAF["mean"].iloc[0])-hist_VAF["std"])*0.917/1e9, ((hist_VAF["mean"]-hist_VAF["mean"].iloc[0])+hist_VAF["std"])*0.917/1e9, color = line_cols[5], alpha = 0.2)

plt.plot(hist_VAF.time, (hist_VAF["cy623"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da914"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da916"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da917"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)

plot_data = icesheet_d["cs568"]
plot_data = plot_data.iloc[10:50]
plot_data.time = plot_data.time - 11

plt.plot(plot_data.time, (plot_data.groundedSMB-plot_data.groundedSMB.iloc[0])*0.917/1e9, label = "Ctrl (cs568)", color = line_cols[0], linestyle = line_stys[0])
"""
plt.plot(ramp_GLD.time, (ramp_GLD["mean"])*0.917/1e9, label = "Overshoots", color = line_cols[1])
plt.fill_between(ramp_GLD.time, ((ramp_GLD["mean"])-ramp_GLD["std"])*0.917/1e9, ((ramp_GLD["mean"])+ramp_GLD["std"])*0.917/1e9, color = line_cols[1], alpha = 0.2)

plt.plot(ramp_GLD.time, (ramp_GLD["cx209"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_GLD.time, (ramp_GLD["cw988"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_GLD.time, (ramp_GLD["cw989"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_GLD.time, (ramp_GLD["cw990"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)

plt.plot(hist_VAF.time, (hist_VAF["mean"])*0.917/1e9, label = "Historical", color = line_cols[5])
plt.fill_between(hist_VAF.time, ((hist_VAF["mean"])-hist_VAF["std"])*0.917/1e9, ((hist_VAF["mean"])+hist_VAF["std"])*0.917/1e9, color = line_cols[5], alpha = 0.2)

plt.plot(hist_VAF.time, (hist_VAF["cy623"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da914"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da916"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da917"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)

plot_data = icesheet_d["cs568"]
plot_data = plot_data.iloc[10:50]
plot_data.time = plot_data.time - 11

plt.plot(plot_data.time, (plot_data.GLDischarge)*0.917/1e9, label = "Ctrl (cs568)", color = line_cols[0], linestyle = line_stys[0])

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
            
            ramp_flBMB = plot_data.iloc[:,[1,5]]
            ramp_flBMB.rename(columns={'floatingBMB': 'cx209'}, inplace=True)

        elif i == "cw988":

            ramp_flBMB["cw988"] = plot_data.iloc[:,5]

        elif i == "cw989":

            ramp_flBMB["cw989"] = plot_data.iloc[:,5]

        elif i == "cw990":

            ramp_flBMB["cw990"] = plot_data.iloc[:,5]

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

ramp_flBMB["mean"] = ramp_flBMB.iloc[:,1:].mean(axis=1, numeric_only=True)
ramp_flBMB["std"] = ramp_flBMB.iloc[:,1:].std(axis=1, numeric_only=True)

hist_VAF["mean"] = hist_VAF.iloc[:,1:].mean(axis=1, numeric_only=True)
hist_VAF["std"] = hist_VAF.iloc[:,1:].std(axis=1, numeric_only=True)
"""
plt.plot(ramp_flBMB.time, (ramp_flBMB["mean"]-ramp_flBMB["mean"].iloc[0])*0.917/1e9, label = "Overshoots", color = line_cols[1])
plt.fill_between(ramp_flBMB.time, ((ramp_flBMB["mean"]-ramp_flBMB["mean"].iloc[0])-ramp_flBMB["std"])*0.917/1e9, ((ramp_flBMB["mean"]-ramp_flBMB["mean"].iloc[0])+ramp_flBMB["std"])*0.917/1e9, color = line_cols[1], alpha = 0.2)

plt.plot(ramp_flBMB.time, (ramp_flBMB["cx209"]-ramp_flBMB["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_flBMB.time, (ramp_flBMB["cw988"]-ramp_flBMB["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_flBMB.time, (ramp_flBMB["cw989"]-ramp_flBMB["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_flBMB.time, (ramp_flBMB["cw990"]-ramp_flBMB["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)

plt.plot(hist_VAF.time, (hist_VAF["mean"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "Historical", color = line_cols[5])
plt.fill_between(hist_VAF.time, ((hist_VAF["mean"]-hist_VAF["mean"].iloc[0])-hist_VAF["std"])*0.917/1e9, ((hist_VAF["mean"]-hist_VAF["mean"].iloc[0])+hist_VAF["std"])*0.917/1e9, color = line_cols[5], alpha = 0.2)

plt.plot(hist_VAF.time, (hist_VAF["cy623"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da914"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da916"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da917"]-hist_VAF["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)

plot_data = icesheet_d["cs568"]
plot_data = plot_data.iloc[10:50]
plot_data.time = plot_data.time - 11

plt.plot(plot_data.time, (plot_data.groundedSMB-plot_data.groundedSMB.iloc[0])*0.917/1e9, label = "Ctrl (cs568)", color = line_cols[0], linestyle = line_stys[0])
"""
plt.plot(ramp_flBMB.time, (ramp_flBMB["mean"])*0.917/1e9, label = "Overshoots", color = line_cols[1])
plt.fill_between(ramp_flBMB.time, ((ramp_flBMB["mean"])-ramp_flBMB["std"])*0.917/1e9, ((ramp_flBMB["mean"])+ramp_flBMB["std"])*0.917/1e9, color = line_cols[1], alpha = 0.2)

plt.plot(ramp_flBMB.time, (ramp_flBMB["cx209"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_flBMB.time, (ramp_flBMB["cw988"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_flBMB.time, (ramp_flBMB["cw989"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_flBMB.time, (ramp_flBMB["cw990"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)

plt.plot(hist_VAF.time, (hist_VAF["mean"])*0.917/1e9, label = "Historical", color = line_cols[5])
plt.fill_between(hist_VAF.time, ((hist_VAF["mean"])-hist_VAF["std"])*0.917/1e9, ((hist_VAF["mean"])+hist_VAF["std"])*0.917/1e9, color = line_cols[5], alpha = 0.2)

plt.plot(hist_VAF.time, (hist_VAF["cy623"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da914"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da916"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_VAF.time, (hist_VAF["da917"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)

plot_data = icesheet_d["cs568"]
plot_data = plot_data.iloc[10:50]
plot_data.time = plot_data.time - 11

plt.plot(plot_data.time, (plot_data.floatingBMB)*0.917/1e9, label = "Ctrl (cs568)", color = line_cols[0], linestyle = line_stys[0])

# plt.plot(rignot.time, rignot["Discharge"], label = 'Rignot et al. (2019)', color = line_cols[0])

plt.ylabel("Ice shelf basal melt (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.legend(loc = 'center left', bbox_to_anchor=(1, 0.5))

print("Finished and saving AIS Grounding Line Discharge vs Time plot...")

plt.savefig('./Projects/figures/HistAISShelfBMBvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

#################################################################################### """