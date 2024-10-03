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

from amrfile import io as amrio

####################################################################################

id = ["cs568", "cx209", "cw988", "cw989", "cw990", "cy623", "da914", "da916", "da917"]
id_anom = ["cx209", "cw988", "cw989", "cw990", "cy623", "da914", "da916", "da917"]

#run_type = ["pi-ctrl","ramp-up", "stab 1.5C", "stab 2C", "stab 2.5C", "stab 3C", "stab 4C", "stab 5C", 
#           "stab 6C", "_ramp-down -8 2C 50yr", "_ramp-down -8 2C 200yr", "_ramp-down -8 1.5C 50yr", "_ramp-down -8 4C 50yr", "_ramp-down -8 3C 50yr", "_ramp-down -8 5C 50yr", "_ramp-down -4 2C 50yr",
#           "_ramp-down -4 1.5C 50yr", "_ramp-down -4 1.5C 200yr", "_ramp-down -4 3C 200yr", "_ramp-down -4 2C 200yr", "_ramp-down -4 4C 200yr", "_ramp-down -4 3C 30yr", "_ramp-down -4 4C 50yr", "_ramp-down -4 5C 50yr"]

#run_type = ["pi-ctrl","ramp-up", "stab 1.5C", "stab 2C", "stab 2.5C", "stab 3C", "stab 4C", "stab 5C", less 
#            "stab 6C", "ramp-down -8 2C 50yr", "ramp-down -8 2C 200yr", "ramp-down -8 1.5C 50yr", "ramp-down -8 4C 50yr", "ramp-down -8 3C 50yr", "ramp-down -8 5C 50yr", "ramp-down -4 2C 50yr",
#            "ramp-down -4 1.5C 50yr", "ramp-down -4 1.5C 200yr", "ramp-down -4 3C 200yr", "ramp-down -4 2C 200yr", "ramp-down -4 4C 200yr", "ramp-down -4 3C 30yr", "ramp-down -4 4C 50yr", "ramp-down -4 5C 50yr"]

run_type = ["Ctrl","Ramp-Up 1", "Ramp-Up 2", "Ramp-Up 3", "Ramp-Up 4", "Hist 1", "Hist 2", "Hist 3", "Hist 4"]
run_type_anom = ["Ramp-Up 1", "Ramp-Up 2", "Ramp-Up 3", "Ramp-Up 4", "Hist 1", "Hist 2", "Hist 3", "Hist 4"]

runs = dict(zip(id, run_type))
runs_anom = dict(zip(id_anom, run_type_anom))

line_cols = ['#000000','#C30F0E','#C30F0E','#C30F0E','#C30F0E','#0003C7','#0003C7','#0003C7','#0003C7']
line_stys = ["dotted","solid","dotted","dashed","dashdot","solid","dotted","dashed","dashdot"]

line_cols_anom = ['#C30F0E','#C30F0E','#C30F0E','#C30F0E','#0003C7','#0003C7','#0003C7','#0003C7']
line_stys_anom = ["solid","dotted","dashed","dashdot","solid","dotted","dashed","dashdot"]

count = 0

# Get atmosphere data

if os.path.exists('../processed_data/atmos_data.pkl'):

    print("Loading atmosphere data from file...")

    with open('../processed_data/atmos_data.pkl', 'rb') as file:
    
        atmos_d = pickle.load(file)

else:

    atmos_d = {}

    print("Getting atmosphere data...")

    for i in id:

        print(f"Working on {i}: {runs[i]}")
        atmos_dir = f"/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/raw_data/{i}/atmos/"
        atmos_files = sorted(os.listdir(atmos_dir))
        atmos_files_matched = fnmatch.filter(atmos_files, f"{i}*.pp")

        count = 0
        atmos_df = np.ndarray(shape = (len(atmos_files_matched),2))

        for j in atmos_files_matched:
        
            filename = f"{atmos_dir}/{j}"
            f = cf.read(filename)
            temp = f[0]
            temp_global_avg = temp.collapse('area: mean', weights=True)

            if i == "cs568":
                atmos_df[count, 0] = int(j[9:13])-100
            else:
                atmos_df[count, 0] = int(j[9:13])
            
            atmos_df[count, 1] = temp_global_avg.data

            count = count + 1
        
        atmos_d[i] = atmos_df

####################################################################################

# Save atmosphere data

if count > 0:
    print("Saving atmosphere data to file...")

    atmos_save_file = open('../processed_data/atmos_data.pkl', 'wb') 
    pickle.dump(atmos_d, atmos_save_file) 
    atmos_save_file.close() 

####################################################################################

# Read ice sheet data

initialT = atmos_d["cx209"][0,1]

if os.path.exists('../processed_data/icesheet_data.pkl'):

    print("Loading ice sheet data from file...")

    with open('../processed_data/icesheet_data.pkl', 'rb') as file:

        icesheet_d = pickle.load(file)

    icesheet_d["dc051"] = icesheet_d["dc051"].reindex(icesheet_d["dc051"].index.tolist() + [186.5])
    icesheet_d["dc051"] = icesheet_d["dc051"].sort_index().reset_index(drop=True)
    icesheet_d["dc051"].iloc[:,1:] = icesheet_d["dc051"].iloc[:,1:].interpolate(method='linear')

else:

    print("Getting ice sheet data...")

    icesheet_d = {}

    for i in id:

        print(f"Working on {i}: {runs[i]}")
        AIS_stats = pd.read_csv(f"/gws/nopw/j04/terrafirma/tm17544/TerraFIRMA_overshoots/processed_data/{i}_diagnostics.csv")

        # AIS_stats = AIS_stats.dropna(how='any')
        # AIS_stats["file"] = AIS_stats["file"].astype(str)

        if i == "cs568":    
            AIS_stats.time = AIS_stats.apply(lambda x: int(x.file[16:20]), axis=1)-100
        else:
            AIS_stats.time = AIS_stats.apply(lambda x: int(x.file[16:20]), axis=1)
        
        AIS_stats["massSLE"] = AIS_stats["volumeAbove"]*(918/(1028*3.625e14))

        AIS_stats["global_delta_T"] = np.nan

        count = 0

        for j in atmos_d[i][:,0]:

            year = int(j+1) # because BISICLES stores data for 01/01 of following year...
            print(f"Working on year: {year}")
            pos = np.where(AIS_stats.time==year)

            if np.size(pos) > 0:
                pos = pos[0][0]
                AIS_stats.at[pos,"global_delta_T"] = atmos_d[i][count,1]-initialT
            else:
                print(f"Year {year} not found in AIS data for {i}")

            count = count + 1

        # Interpolate to fill NaN valures in global_delta_T
        AIS_stats["global_delta_T"].interpolate(method='linear', inplace=True)

        icesheet_d[i] = AIS_stats

####################################################################################

# Save ice sheet data

if count > 0:

    print("Saving ice sheet data to file...")

    ice_save_file = open('../processed_data/icesheet_data.pkl', 'wb') 
    pickle.dump(icesheet_d, ice_save_file) 
    ice_save_file.close()

####################################################################################

# function for smoothing time series for plotting

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='valid')
    return y_smooth

####################################################################################

# Plot global T vs Time graph

print("Starting Global Temp vs Time plot...")

initialT = atmos_d["cx209"][0,1]

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = atmos_d[i]

    if i in {"cs568","cx209", "cw988", "cw989", "cw990"}:

        plot_data = plot_data[10:50,:]

    else:

        plot_data = plot_data[125:165,:]


    
    plt.plot(plot_data[:,0]-1850, plot_data[:,1]-initialT, label = "_none", lw=0.8, linestyle="solid", color=line_cols[count], alpha=0.01)
    
    ma_y = smooth(plot_data[:,1], box_size)
    
    ma_x = plot_data[int((box_size-1)/2):,0]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x-1850, ma_y-initialT, label = runs[i], lw=0.8, linestyle=line_stys[count], color=line_cols[count])

    count = count + 1

#plt.grid(linestyle=':')

ax = plt.gca()

plt.ylabel('Global Mean $\Delta$T (C)')
plt.xlabel('Years')
plt.legend(loc = 'center left', bbox_to_anchor=(1, 0.5))

print("Finished and saving Global Temp vs Time plot...")

plt.savefig('../figures/HistGlobalTvsTime.png', dpi = 600, bbox_inches='tight')
#plt.savefig('GlobalTvsTime.png', dpi = 600, bbox_inches='tight')

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

        plot_data = plot_data[10:50,:]

    else:

        plot_data = plot_data[125:165,:]

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

# Plot VAF Anomaly vs Time graph

initialmassSLE = icesheet_d["cx209"]["massSLE"].iloc[0]
initialmassSLEpi = icesheet_d["cs568"]["massSLE"].iloc[0]

print("Starting AIS VAF Anomaly vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id_anom:

    print(f"Plotting {i}: {runs_anom[i]}")

    plot_data = icesheet_d[i]

    if i in {"cs568","cx209", "cw988", "cw989", "cw990"}:

        plot_data = plot_data[10:50,:]

    else:

        plot_data = plot_data[125:165,:]


    plot_data_max_time = plot_data.time.max()
    plot_data_min_time = plot_data.time.min()

    ctrl_data = icesheet_d["cs568"]
    ctrl_data_max_time = ctrl_data.time.max()
    ctrl_data_min_time = ctrl_data.time.min()

    min_time = max(plot_data_min_time, ctrl_data_min_time)
    max_time = min(plot_data_max_time, ctrl_data_max_time)

    plot_data = plot_data[(plot_data.time <= max_time) & (plot_data.time >= min_time)]
    ctrl_data = ctrl_data[(ctrl_data.time <= max_time) & (ctrl_data.time >= min_time)]

    plot_data = plot_data.reset_index(drop=True)
    ctrl_data = ctrl_data.reset_index(drop=True)

    plt.plot(plot_data.time - 1850, ((plot_data.massSLE-initialmassSLE)-(ctrl_data.massSLE-initialmassSLEpi)), label = runs_anom[i], lw=0.8, color = line_cols_anom[count], linestyle = line_stys_anom[count])

    count = count + 1

#plt.grid(linestyle=':')

ax = plt.gca()

plt.ylabel("$\Delta$VAF Anomaly (m SLE)")
plt.xlabel('Years')
plt.legend(loc = 'center left', bbox_to_anchor=(1, 0.5))

print("Finished and saving AIS VAF Anomaly vs Time plot...")

plt.savefig('../figures/HistAISVAFAnomalyvsTime.png', dpi = 600,  bbox_inches='tight')  
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

        plot_data = plot_data[10:50,:]

    else:

        plot_data = plot_data[125:165,:]

    plt.plot(plot_data.time - 1850, ((plot_data.smbGrounded)/918e6), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.01)

    ma_y = smooth((plot_data.smbGrounded)/918e6, box_size)
    
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

# Plot SMB Anomaly vs Time graph

print("Starting AIS Grounded SMB Anomaly vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id_anom:

    plot_data = icesheet_d[i]

    if i in {"cs568","cx209", "cw988", "cw989", "cw990"}:

        plot_data = plot_data[10:50,:]

    else:

        plot_data = plot_data[125:165,:]
        
    plot_data_max_time = plot_data.time.max()
    plot_data_min_time = plot_data.time.min()

    ctrl_data = icesheet_d["cs568"]
    ctrl_data_max_time = ctrl_data.time.max()
    ctrl_data_min_time = ctrl_data.time.min()

    min_time = max(plot_data_min_time, ctrl_data_min_time)
    max_time = min(plot_data_max_time, ctrl_data_max_time)

    plot_data = plot_data[(plot_data.time <= max_time) & (plot_data.time >= min_time)]
    ctrl_data = ctrl_data[(ctrl_data.time <= max_time) & (ctrl_data.time >= min_time)]

    plot_data = plot_data.reset_index(drop=True)
    ctrl_data = ctrl_data.reset_index(drop=True)

    plt.plot(plot_data.time - 1850, (((plot_data.smbGrounded)-(ctrl_data.smbGrounded))/918e6), label = '_none', lw=0.8, color = line_cols_anom[count], linestyle = line_stys_anom[count], alpha = 0.01)

    ma_y = smooth((((plot_data.smbGrounded)-(ctrl_data.smbGrounded))/918e6), box_size)
    
    ma_x = (plot_data.time - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = runs_anom[i], lw=0.8, color = line_cols_anom[count], linestyle = line_stys_anom[count])

    count = count + 1

#plt.grid(linestyle=':')

ax = plt.gca()

plt.ylabel("Grounded SMB Anomaly (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.legend(loc = 'center left', bbox_to_anchor=(1, 0.5))

print("Finished and saving AIS Grounded SMB Anomaly vs Time plot...")

plt.savefig('../figures/HistAISGroundedSMBAnomalyvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot Discharge vs Time graph

print("Starting AIS Grounding Line Discharge vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    plt.plot(plot_data.time - 1850, ((plot_data.fluxDivFileGrounded)/918e6), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.01)

    ma_y = smooth(((plot_data.fluxDivFileGrounded)/918e6), box_size)
    
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

# Plot Discharge Anomaly vs Time graph

print("Starting AIS Grounding Line Discharge Anomaly vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id_anom:

    plot_data = icesheet_d[i]
    plot_data_max_time = plot_data.time.max()
    plot_data_min_time = plot_data.time.min()

    ctrl_data = icesheet_d["cs568"]
    ctrl_data_max_time = ctrl_data.time.max()
    ctrl_data_min_time = ctrl_data.time.min()

    min_time = max(plot_data_min_time, ctrl_data_min_time)
    max_time = min(plot_data_max_time, ctrl_data_max_time)

    plot_data = plot_data[(plot_data.time <= max_time) & (plot_data.time >= min_time)]
    ctrl_data = ctrl_data[(ctrl_data.time <= max_time) & (ctrl_data.time >= min_time)]

    plot_data = plot_data.reset_index(drop=True)
    ctrl_data = ctrl_data.reset_index(drop=True)

    plt.plot(plot_data.time - 1850, (((plot_data.fluxDivFileGrounded)-(ctrl_data.fluxDivFileGrounded))/918e6), label = '_none', lw=0.8, color = line_cols_anom[count], linestyle = line_stys_anom[count], alpha = 0.01)

    ma_y = smooth((((plot_data.fluxDivFileGrounded)-(ctrl_data.fluxDivFileGrounded))/918e6), box_size)

    ma_x = (plot_data.time - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = runs_anom[i], lw=0.8, color = line_cols_anom[count], linestyle = line_stys_anom[count])

    count = count + 1

#plt.grid(linestyle=':')

ax = plt.gca()

plt.ylabel("GL Discharge Anomaly (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.legend(loc = 'center left', bbox_to_anchor=(1, 0.5))

print("Finished and saving AIS Grounding Line Discharge Anomaly vs Time plot...")

plt.savefig('../figures/HistAISGlDischargeAnomalyvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################