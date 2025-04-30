####################################################################################
# Imports
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt

####################################################################################

# For comparison between historical and idealised ramp-up simulations
id = ["cx209", "cw988", "cw989", "cw990", "cy623", "da914", "da916", "da917"]
run_type = ["Ramp-Up 1", "Ramp-Up 2", "Ramp-Up 3", "Ramp-Up 4", "Hist 1", "Hist 2", "Hist 3", "Hist 4"]
runs = dict(zip(id, run_type))

# Black, red and blue colours for plotting
line_cols = ['#C30F0E','#0003C7']

# Set plot font size for all plots
plt.rcParams.update({'font.size': 7})

# Read in the processed (using diagnostics BISICLES filetool) ice sheet data

print("Loading ice sheet data from file...")

with open('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/archive/processed_data/historical_icesheet_data.pkl', 'rb') as file:

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
    return x/((-1)*361.8)

def sle2mass(x):
    return x*(-1)*361.8


####################################################################################

# Load auxillary data sets for comparison

# Load the IMBIE (2023) data
imbie = pd.read_csv('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/aux_data/imbie_antarctica_2021_Gt.csv')

# Select 1992-2014 data for comparison
imbie = imbie.iloc[:267]
imbie.Year = imbie.Year

mottram = pd.read_csv('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/aux_data/Mottram_SMB_data.csv')
mottram.Year = mottram.Year

# Load the Noel et al. (2023) data
noel = pd.read_csv('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/aux_data/SMB-ANT-Sectors-1979-2021-RACMO2.3p2-ERA5-2km.csv')
noel.Year = noel.Year

# Load the (preprocessed) Rignot et al. (2019) data
rignot = pd.read_csv('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/aux_data/rignot_2019_AIS_discharge.csv')
rignot.Year = rignot.Year

davison = pd.read_csv('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/aux_data/davison_2023_basal_melt.csv')
davison.Year = davison.Year
davison = davison.iloc[:17]
davison["Basal melt"] = davison["Basal melt"]*(-1)

####################################################################################
"""
# Plot Mass Balance vs Time graph

print("Starting AIS Mass Balance vs Time plot...")

plt.figure(figsize=(4, 3))

# Process the data for plotting

ctrl_data = icesheet_d["cs568"]

ctrl_data_ramp = ctrl_data.iloc[10:49]
ctrl_data_ramp.time = ctrl_data_ramp.time - 1861

ctrl_data_hist = ctrl_data.iloc[125:]
ctrl_data_hist.time = ctrl_data_hist.time - 1976

for i in id:

    plot_data = icesheet_d[i]

    if i in {"cx209", "cw988", "cw989", "cw990"}:

        # Get years 10-50 for ramp-up simulations (and piCtrl)
        plot_data = plot_data.iloc[10:49]

        # Reset the first year to 1 rather than 1860
        plot_data.time = plot_data.time - 1861

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

        # Get years 1975-2014 for historical simulations
        plot_data = plot_data.iloc[125:]
        
        plot_data.time = plot_data.time - 1976

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

ctrl_hist_VAF = ctrl_data_hist.iloc[:,2]
ctrl_ramp_VAF = ctrl_data_ramp.iloc[:,2]

ctrl_hist_VAF.reset_index(inplace=True, drop=True)
ctrl_ramp_VAF.reset_index(inplace=True, drop=True)

# Calculate the ensemble mean and standard deviation for each time point
ramp_VAF["mean"] = ramp_VAF.iloc[:,1:].mean(axis=1, numeric_only=True)
ramp_VAF["max"] = ramp_VAF.iloc[:,1:].max(axis=1, numeric_only=True)
ramp_VAF["min"] = ramp_VAF.iloc[:,1:].min(axis=1, numeric_only=True)

hist_VAF["mean"] = hist_VAF.iloc[:,1:].mean(axis=1, numeric_only=True)
hist_VAF["max"] = hist_VAF.iloc[:,1:].max(axis=1, numeric_only=True)
hist_VAF["min"] = hist_VAF.iloc[:,1:].min(axis=1, numeric_only=True)

# convert to anomalies from control
ramp_VAF["mean"] = ramp_VAF["mean"] - ctrl_ramp_VAF
ramp_VAF["max"] = ramp_VAF["max"] - ctrl_ramp_VAF
ramp_VAF["min"] = ramp_VAF["min"] - ctrl_ramp_VAF

hist_VAF["mean"] = hist_VAF["mean"] - ctrl_hist_VAF
hist_VAF["max"] = hist_VAF["max"] - ctrl_hist_VAF
hist_VAF["min"] = hist_VAF["min"] - ctrl_hist_VAF

# Start making the plot

# Plot the ramp-up ensemble mean VAF time series in Gt and fill between max/min
plt.plot(ramp_VAF.time, (ramp_VAF["mean"]-ramp_VAF["mean"].iloc[16])*(0.918/1e9), label = "ramp-ups", color = line_cols[0])
plt.fill_between(ramp_VAF.time, (ramp_VAF["min"]-ramp_VAF["mean"].iloc[16])*(0.918/1e9), (ramp_VAF["max"]-ramp_VAF["mean"].iloc[16])*(0.918/1e9), color = line_cols[0], alpha = 0.2)

# Plot the historical ensemble mean VAF time series in Gt and fill between max/min
plt.plot(hist_VAF.time, (hist_VAF["mean"]-hist_VAF["mean"].iloc[16])*(0.918/1e9), label = "hist", color = line_cols[1])
plt.fill_between(hist_VAF.time, (hist_VAF["min"]-hist_VAF["mean"].iloc[16])*(0.918/1e9), (hist_VAF["max"]-hist_VAF["mean"].iloc[16])*(0.918/1e9), color = line_cols[1], alpha = 0.2)

# Add the IMBIE data
plt.plot(imbie.Year, imbie["Cumulative mass balance (Gt)"], label = 'obs', color = 'Black')

# Add labels and legend
plt.ylabel("Mass change anomaly (Gt)")
plt.xlabel('Years')
plt.legend(loc = 'upper left', prop={'size': 5})

# Add a second y-axis for sea level equivalent
ax = plt.gca()
secax = ax.secondary_yaxis('right', functions=(mass2sle, sle2mass)) 
secax.set_ylabel('Sea level contribution anomaly (mm)')

print("Finished and saving AIS VAF vs Time plot...")

plt.savefig('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/NewHistAISVAFvsTime.png', dpi = 600,  bbox_inches='tight')  
"""
####################################################################################

# Plot SMB vs Time graph

print("Starting AIS SMB vs Time plot...")

plt.figure(figsize=(4, 3))

# Process the data for plotting in the same way as for the VAF plot but choosing the 
# grounded SMB data from the original data frame

for i in id:

    plot_data = icesheet_d[i]

    if i in {"cs568","cx209", "cw988", "cw989", "cw990"}:

        plot_data = plot_data.iloc[10:50]
        plot_data.time = plot_data.time + 115
        
        plot_data["totalSMB"] = plot_data.groundedSMB + plot_data.floatingSMB

        if i == "cx209": 
            
            ramp_SMB = plot_data.iloc[:,[1,10]]
            ramp_SMB.rename(columns={'totalSMB': 'cx209'}, inplace=True)

        elif i == "cw988":

            ramp_SMB["cw988"] = plot_data.iloc[:,10]

        elif i == "cw989":

            ramp_SMB["cw989"] = plot_data.iloc[:,10]

        elif i == "cw990":

            ramp_SMB["cw990"] = plot_data.iloc[:,10]

        else:

            continue


    else:

        plot_data = plot_data.iloc[124:]
        plot_data.time = plot_data.time
        
        plot_data["totalSMB"] = plot_data.groundedSMB + plot_data.floatingSMB

        if i == "cy623":
            
            hist_SMB = plot_data.iloc[:,[1,10]]
            hist_SMB.rename(columns={'totalSMB': 'cy623'}, inplace=True)

        if i == "da914": 
            
            hist_SMB["da914"] = plot_data.iloc[:,10]

        elif i == "da916":

            hist_SMB["da916"] = plot_data.iloc[:,10]  

        elif i == "da917":

            hist_SMB["da917"] = plot_data.iloc[:,10]
            
ramp_SMB.reset_index(inplace=True, drop=True)
hist_SMB.reset_index(inplace=True, drop=True)

ramp_SMB["mean"] = ramp_SMB.iloc[:,1:].mean(axis=1, numeric_only=True)
ramp_SMB["min"] = ramp_SMB.iloc[:,1:].min(axis=1, numeric_only=True)
ramp_SMB["max"] = ramp_SMB.iloc[:,1:].max(axis=1, numeric_only=True)


hist_SMB["mean"] = hist_SMB.iloc[:,1:].mean(axis=1, numeric_only=True)
hist_SMB["min"] = hist_SMB.iloc[:,1:].min(axis=1, numeric_only=True)
hist_SMB["max"] = hist_SMB.iloc[:,1:].max(axis=1, numeric_only=True)

"""
plt.plot(ramp_SMB.time, (ramp_SMB["mean"]-ramp_SMB["mean"].iloc[0])*0.917/1e9, label = "Overshoots", color = line_cols[1])
plt.fill_between(ramp_SMB.time, ((ramp_SMB["mean"]-ramp_SMB["mean"].iloc[0])-ramp_SMB["std"])*0.917/1e9, ((ramp_SMB["mean"]-ramp_SMB["mean"].iloc[0])+ramp_SMB["std"])*0.917/1e9, color = line_cols[1], alpha = 0.2)

plt.plot(ramp_SMB.time, (ramp_SMB["cx209"]-ramp_SMB["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_SMB.time, (ramp_SMB["cw988"]-ramp_SMB["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_SMB.time, (ramp_SMB["cw989"]-ramp_SMB["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_SMB.time, (ramp_SMB["cw990"]-ramp_SMB["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)

plt.plot(hist_SMB.time, (hist_SMB["mean"]-hist_SMB["mean"].iloc[0])*0.917/1e9, label = "Historical", color = line_cols[5])
plt.fill_between(hist_SMB.time, ((hist_SMB["mean"]-hist_SMB["mean"].iloc[0])-hist_SMB["std"])*0.917/1e9, ((hist_SMB["mean"]-hist_SMB["mean"].iloc[0])+hist_SMB["std"])*0.917/1e9, color = line_cols[5], alpha = 0.2)

plt.plot(hist_SMB.time, (hist_SMB["cy623"]-hist_SMB["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_SMB.time, (hist_SMB["da914"]-hist_SMB["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_SMB.time, (hist_SMB["da916"]-hist_SMB["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_SMB.time, (hist_SMB["da917"]-hist_SMB["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)

plot_data = icesheet_d["cs568"]
plot_data = plot_data.iloc[10:50]
plot_data.time = plot_data.time - 11

plt.plot(plot_data.time, (plot_data.groundedSMB-plot_data.groundedSMB.iloc[0])*0.917/1e9, label = "Ctrl (cs568)", color = line_cols[0], linestyle = line_stys[0])
"""

plt.plot(ramp_SMB.time, (ramp_SMB["mean"])*0.917/1e9, label = "ramp-ups", color = 'red')
plt.fill_between(ramp_SMB.time, (ramp_SMB["min"])*0.917/1e9, (ramp_SMB["max"])*0.917/1e9, color = 'red', alpha = 0.2)

plt.plot(hist_SMB.time, (hist_SMB["mean"])*0.917/1e9, label = "hist", color = 'blue')
plt.fill_between(hist_SMB.time, (hist_SMB["min"])*0.917/1e9, (hist_SMB["max"])*0.917/1e9, color = 'blue', alpha = 0.2)

# Add the Noel data
plt.plot(noel.Year, noel["ANT"], label = 'obs', color = 'Black')

plt.plot(mottram.Year, mottram["SMB"], label = '_obs', color = 'Black')
plt.fill_between(mottram.Year, mottram["Min"], mottram["Max"],color = 'black', alpha = 0.2)

plt.ylabel("Surface mass balance (Gt yr$^{-1}$)")
plt.xlabel('Years')
#plt.legend(loc = 'best')

print("Finished and saving AIS Grounding Line Discharge vs Time plot...")

#plt.savefig('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/NewHistAISSMBvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################
"""
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
            
            hist_GLD = plot_data.iloc[:,[1,6]]
            hist_GLD.rename(columns={'GLDischarge': 'cy623'}, inplace=True)

        if i == "da914": 
            
            hist_GLD["da914"] = plot_data.iloc[:,6]

        elif i == "da916":

            hist_GLD["da916"] = plot_data.iloc[:,6]  

        elif i == "da917":

            hist_GLD["da917"] = plot_data.iloc[:,6]
            
ramp_GLD.reset_index(inplace=True, drop=True)
hist_GLD.reset_index(inplace=True, drop=True)

ramp_GLD["mean"] = ramp_GLD.iloc[:,1:].mean(axis=1, numeric_only=True)
ramp_GLD["std"] = ramp_GLD.iloc[:,1:].std(axis=1, numeric_only=True)

hist_GLD["mean"] = hist_GLD.iloc[:,1:].mean(axis=1, numeric_only=True)
hist_GLD["std"] = hist_GLD.iloc[:,1:].std(axis=1, numeric_only=True)
"""
"""
plt.plot(ramp_GLD.time, (ramp_GLD["mean"]-ramp_GLD["mean"].iloc[0])*0.917/1e9, label = "Overshoots", color = line_cols[1])
plt.fill_between(ramp_GLD.time, ((ramp_GLD["mean"]-ramp_GLD["mean"].iloc[0])-ramp_GLD["std"])*0.917/1e9, ((ramp_GLD["mean"]-ramp_GLD["mean"].iloc[0])+ramp_GLD["std"])*0.917/1e9, color = line_cols[1], alpha = 0.2)

plt.plot(ramp_GLD.time, (ramp_GLD["cx209"]-ramp_GLD["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_GLD.time, (ramp_GLD["cw988"]-ramp_GLD["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_GLD.time, (ramp_GLD["cw989"]-ramp_GLD["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_GLD.time, (ramp_GLD["cw990"]-ramp_GLD["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)

plt.plot(hist_GLD.time, (hist_GLD["mean"]-hist_GLD["mean"].iloc[0])*0.917/1e9, label = "Historical", color = line_cols[5])
plt.fill_between(hist_GLD.time, ((hist_GLD["mean"]-hist_GLD["mean"].iloc[0])-hist_GLD["std"])*0.917/1e9, ((hist_GLD["mean"]-hist_GLD["mean"].iloc[0])+hist_GLD["std"])*0.917/1e9, color = line_cols[5], alpha = 0.2)

plt.plot(hist_GLD.time, (hist_GLD["cy623"]-hist_GLD["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_GLD.time, (hist_GLD["da914"]-hist_GLD["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_GLD.time, (hist_GLD["da916"]-hist_GLD["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_GLD.time, (hist_GLD["da917"]-hist_GLD["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)

plot_data = icesheet_d["cs568"]
plot_data = plot_data.iloc[10:50]
plot_data.time = plot_data.time - 11

plt.plot(plot_data.time, (plot_data.groundedSMB-plot_data.groundedSMB.iloc[0])*0.917/1e9, label = "Ctrl (cs568)", color = line_cols[0], linestyle = line_stys[0])
"""
"""
plt.plot(ramp_GLD.time, (ramp_GLD["mean"])*0.917/1e9, label = "Overshoots", color = line_cols[1])
plt.fill_between(ramp_GLD.time, ((ramp_GLD["mean"])-ramp_GLD["std"])*0.917/1e9, ((ramp_GLD["mean"])+ramp_GLD["std"])*0.917/1e9, color = line_cols[1], alpha = 0.2)

plt.plot(ramp_GLD.time, (ramp_GLD["cx209"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_GLD.time, (ramp_GLD["cw988"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_GLD.time, (ramp_GLD["cw989"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_GLD.time, (ramp_GLD["cw990"])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)

plt.plot(hist_GLD.time, (hist_GLD["mean"])*0.917/1e9, label = "Historical", color = line_cols[5])
plt.fill_between(hist_GLD.time, ((hist_GLD["mean"])-hist_GLD["std"])*0.917/1e9, ((hist_GLD["mean"])+hist_GLD["std"])*0.917/1e9, color = line_cols[5], alpha = 0.2)

plt.plot(hist_GLD.time, (hist_GLD["cy623"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_GLD.time, (hist_GLD["da914"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_GLD.time, (hist_GLD["da916"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_GLD.time, (hist_GLD["da917"])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)

plot_data = icesheet_d["cs568"]
plot_data = plot_data.iloc[10:50]
plot_data.time = plot_data.time - 11

plt.plot(rignot.time, rignot["Discharge"], label = 'Rignot et al. (2019)', color = line_cols[0])

plt.ylabel("GL Discharge (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.legend(loc = 'center left', bbox_to_anchor=(1, 0.5))

print("Finished and saving AIS Grounding Line Discharge vs Time plot...")

#plt.savefig('./Projects/figures/NewHistAISGLDischargevsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   
"""
####################################################################################

# Plot Ice Shelf BMB vs Time graph

print("Starting AIS Ice Shelf BMB vs Time plot...")

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    if i in {"cs568","cx209", "cw988", "cw989", "cw990"}:

        plot_data = plot_data.iloc[10:50]
        plot_data.time = plot_data.time + 115

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
        plot_data.time = plot_data.time

        if i == "cy623":
            
            hist_flBMB = plot_data.iloc[:,[1,5]]
            hist_flBMB.rename(columns={'floatingBMB': 'cy623'}, inplace=True)

        if i == "da914": 
            
            hist_flBMB["da914"] = plot_data.iloc[:,5]

        elif i == "da916":

            hist_flBMB["da916"] = plot_data.iloc[:,5]  

        elif i == "da917":

            hist_flBMB["da917"] = plot_data.iloc[:,5]
            
ramp_flBMB.reset_index(inplace=True, drop=True)
hist_flBMB.reset_index(inplace=True, drop=True)

ramp_flBMB["mean"] = ramp_flBMB.iloc[:,1:].mean(axis=1, numeric_only=True)
ramp_flBMB["max"] = ramp_flBMB.iloc[:,1:].max(axis=1, numeric_only=True)
ramp_flBMB["min"] = ramp_flBMB.iloc[:,1:].min(axis=1, numeric_only=True)

hist_flBMB["mean"] = hist_flBMB.iloc[:,1:].mean(axis=1, numeric_only=True)
hist_flBMB["max"] = hist_flBMB.iloc[:,1:].max(axis=1, numeric_only=True)
hist_flBMB["min"] = hist_flBMB.iloc[:,1:].min(axis=1, numeric_only=True)

"""
plt.plot(ramp_flBMB.time, (ramp_flBMB["mean"]-ramp_flBMB["mean"].iloc[0])*0.917/1e9, label = "Overshoots", color = line_cols[1])
plt.fill_between(ramp_flBMB.time, ((ramp_flBMB["mean"]-ramp_flBMB["mean"].iloc[0])-ramp_flBMB["std"])*0.917/1e9, ((ramp_flBMB["mean"]-ramp_flBMB["mean"].iloc[0])+ramp_flBMB["std"])*0.917/1e9, color = line_cols[1], alpha = 0.2)

plt.plot(ramp_flBMB.time, (ramp_flBMB["cx209"]-ramp_flBMB["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_flBMB.time, (ramp_flBMB["cw988"]-ramp_flBMB["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_flBMB.time, (ramp_flBMB["cw989"]-ramp_flBMB["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)
plt.plot(ramp_flBMB.time, (ramp_flBMB["cw990"]-ramp_flBMB["mean"].iloc[0])*0.917/1e9, label = "_Overshoots", color = line_cols[1], alpha = 0.1)

plt.plot(hist_flBMB.time, (hist_flBMB["mean"]-hist_flBMB["mean"].iloc[0])*0.917/1e9, label = "Historical", color = line_cols[5])
plt.fill_between(hist_flBMB.time, ((hist_flBMB["mean"]-hist_flBMB["mean"].iloc[0])-hist_flBMB["std"])*0.917/1e9, ((hist_flBMB["mean"]-hist_flBMB["mean"].iloc[0])+hist_flBMB["std"])*0.917/1e9, color = line_cols[5], alpha = 0.2)

plt.plot(hist_flBMB.time, (hist_flBMB["cy623"]-hist_flBMB["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_flBMB.time, (hist_flBMB["da914"]-hist_flBMB["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_flBMB.time, (hist_flBMB["da916"]-hist_flBMB["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)
plt.plot(hist_flBMB.time, (hist_flBMB["da917"]-hist_flBMB["mean"].iloc[0])*0.917/1e9, label = "_Historical", color = line_cols[5], alpha = 0.1)

plot_data = icesheet_d["cs568"]
plot_data = plot_data.iloc[10:50]
plot_data.time = plot_data.time - 11

plt.plot(plot_data.time, (plot_data.groundedSMB-plot_data.groundedSMB.iloc[0])*0.917/1e9, label = "Ctrl (cs568)", color = line_cols[0], linestyle = line_stys[0])
"""

plt.plot(ramp_flBMB.time, (ramp_flBMB["mean"])*0.917/1e9, label = "ramp-ups", color = 'red')
plt.fill_between(ramp_flBMB.time, (ramp_flBMB["min"])*0.917/1e9, (ramp_flBMB["max"])*0.917/1e9, color = 'red', alpha = 0.2)

plt.plot(hist_flBMB.time, (hist_flBMB["mean"])*0.917/1e9, label = "hist", color = 'blue')
plt.fill_between(hist_flBMB.time, (hist_flBMB["min"])*0.917/1e9, (hist_flBMB["max"])*0.917/1e9, color = 'blue', alpha = 0.2)

# Add the Davison data
plt.plot(davison.Year, davison["Basal melt"], label = 'obs', color = 'Black')
plt.fill_between(davison.Year, davison["Basal melt"] + davison["Uncertainty"], davison["Basal melt"] - davison["Uncertainty"],color = 'black', alpha = 0.2)


plt.ylabel("Ice shelf basal melt (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.legend(loc = 'lower left')

print("Finished and saving AIS Grounding Line Discharge vs Time plot...")

#plt.savefig('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/NewHistAISShelfBMBvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot Grounded SMB and floating BMB in a 2-panel plot

print("Starting AIS SMB and BMB vs Time plot...")

count = 0

box_size = 21

plt.figure(figsize=(4, 3))

fig, ax = plt.subplots(2, sharex='col', sharey='row')

ax[0].plot(ramp_SMB.time, (ramp_SMB["mean"])*0.917/1e9, label = "esm-up2p0", color = 'red', lw=0.8)
ax[0].fill_between(ramp_SMB.time, (ramp_SMB["min"])*0.917/1e9, (ramp_SMB["max"])*0.917/1e9, color = 'red', alpha = 0.2, lw=0)

ax[0].plot(hist_SMB.time, (hist_SMB["mean"])*0.917/1e9, label = "esm-hist", color = 'blue', lw=0.8)
ax[0].fill_between(hist_SMB.time, (hist_SMB["min"])*0.917/1e9, (hist_SMB["max"])*0.917/1e9, color = 'blue', alpha = 0.2, lw=0)

# Add the Noel data
ax[0].plot(noel.Year, noel["ANT"], label = 'Noel et al. (2023)', color = 'Black', lw=0.8, linestyle = '-')

ax[0].plot(mottram.Year, mottram["SMB"], label = 'Mottram et al. (2021)', color = 'Black', lw=0.8, linestyle='--')
ax[0].fill_between(mottram.Year, mottram["Min"], mottram["Max"],color = 'black', alpha = 0.1, lw=0)

ax[1].plot(ramp_flBMB.time, (ramp_flBMB["mean"])*0.917/1e9, label = "esm-up2p0", color = 'red', lw=0.8)
ax[1].fill_between(ramp_flBMB.time, (ramp_flBMB["min"])*0.917/1e9, (ramp_flBMB["max"])*0.917/1e9, color = 'red', alpha = 0.2, lw=0)

ax[1].plot(hist_flBMB.time, (hist_flBMB["mean"])*0.917/1e9, label = "esm-hist", color = 'blue', lw=0.8)
ax[1].fill_between(hist_flBMB.time, (hist_flBMB["min"])*0.917/1e9, (hist_flBMB["max"])*0.917/1e9, color = 'blue', alpha = 0.2, lw=0)

# Add the Davison data
ax[1].plot(davison.Year, davison["Basal melt"], label = 'Davison et al. (2023)', color = 'Black', lw=0.8, linestyle='dashdot')
ax[1].fill_between(davison.Year, davison["Basal melt"] + davison["Uncertainty"], davison["Basal melt"] - davison["Uncertainty"],color = 'black', alpha = 0.1)

ax[0].grid(linestyle='-', lw=0.2)
ax[1].grid(linestyle='-', lw=0.2)

plt.xlim([1975, 2015])

ax[0].set_ylabel("Surface mass balance\n(Gt yr$^{-1}$)")
ax[1].set_ylabel("Ice shelf basal mass balance\n(Gt yr$^{-1}$)")
plt.xlabel('Years')

handles, labels = ax[0].get_legend_handles_labels()
handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashdot'))
labels.append('Davison et al. (2023)')

ax[1].legend(handles, labels, loc = 'best', prop={'size': 5})

ax[0].annotate('a)', xy=(0, 1), xycoords='axes fraction', xytext=(0.8, -1.0), textcoords='offset fontsize', ha='center', fontsize=9)
ax[1].annotate('b)', xy=(0, 1), xycoords='axes fraction', xytext=(0.8, -1.0), textcoords='offset fontsize', ha='center', fontsize=9)


print("Finished and saving AIS SMB vs Time plot...")

plt.savefig('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/NewHistAISSMBandBMBvsTime.png', dpi = 600,  bbox_inches='tight') 