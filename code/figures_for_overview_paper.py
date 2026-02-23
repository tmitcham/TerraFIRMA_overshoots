####################################################################################
# Imports
import numpy as np
import pickle
import matplotlib.pyplot as plt
import pandas as pd

####################################################################################

# Options
icesheet = "AIS" # AIS or GrIS
plot_fontsize = 8

####################################################################################

id = ["cs568", "cx209", "cy837", "cy838", "cz375", "cz376", "cz377", "dc052", "dc051", "df028", "dc123", "dc130"]

run_type = ["ZE-0","Up8", "ZE-1.5", "ZE-2", "ZE-3", "ZE-4", "ZE-5", "_ramp-down -4 1.5C 50yr", "_ramp-down -4 2C 50yr", "_ramp-down -4 3C 50yr", "_ramp-down -4 4C 50yr", "_ramp-down -4 5C 50yr"]

runs = dict(zip(id, run_type)) 

line_cols = ['#000000','#C30F0E','#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0','#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0']
line_stys = ["dotted","solid","solid","solid","solid","solid","solid","dashed","dashed","dashed","dashed","dashed"]

####################################################################################

# Read ice sheet data

if icesheet == "AIS":
    with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/AIS_data_overview.pkl", 'rb') as file:
        icesheet_d = pickle.load(file)

elif icesheet == "GrIS":
    with open('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/GrIS_data_overview.pkl', 'rb') as file:
        icesheet_d = pickle.load(file) 

    icesheet_d["cs568"][0] = icesheet_d["cs568"][0].drop(index=icesheet_d["cs568"][0].index[0], axis=0).reset_index(drop=True)

with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/atmos_data_overview.pkl", 'rb') as file:
    atmos_d = pickle.load(file)

with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/cs495_SMB_AIS_GR_FL_masked_new_mask.pkl", 'rb') as file:
    cs495_SMB = pickle.load(file)

with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/atmos_data_cs495.pkl", 'rb') as file:
    cs495_GSAT = pickle.load(file)

## for comparison of methods load some cs568 data processed with pyglint
with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/cs568_SMB_AIS_GR_FL_masked_new_mask.pkl", 'rb') as file:
    cs568_SMB = pickle.load(file)

## for comparison of methods load some cx209 data processed with pyglint
with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/cx209_SMB_AIS_GR_FL_masked_new_mask.pkl", 'rb') as file:
    cx209_SMB = pickle.load(file)

####################################################################################

# Prepare data for SMB vs GSAT plots

SMB = {}

for i in id:
    
    SMB[i] = icesheet_d[i][0][["time","grounded_SMB","floating_SMB"]] 
    SMB[i] = pd.concat([SMB[i], pd.DataFrame(atmos_d[i][:,1])], axis=1)
    SMB[i].drop(SMB[i].tail(1).index,inplace=True)
    SMB[i].columns = ["time","grounded_SMB","floating_SMB","GSAT"]

    # Sort the rows into order of lowest to highest GSAT
    SMB[i] = SMB[i].sort_values(by="GSAT")

## Get cs495 data into the right format for plotting with other suites
cs495_GSAT = pd.DataFrame(cs495_GSAT["cs495"], columns=['time', 'GSAT'])
cs495_GSAT.time = cs495_GSAT.time - 1950
#cs495_GSAT = cs495_GSAT.iloc[:731] # only keep first 731 years to match others
cs495_GSAT = cs495_GSAT.iloc[:100]

cs495_SMB = pd.DataFrame(cs495_SMB)
cs495_SMB = cs495_SMB.iloc[:731]
cs495_SMB = pd.concat([cs495_SMB, pd.DataFrame(cs495_GSAT.GSAT)], axis=1)
cs495_SMB.columns = ["time","total_SMB","grounded_SMB","floating_SMB","GSAT"]

cs495_SMB_sorted_by_GSAT = cs495_SMB.sort_values(by="GSAT")

## for testing plot of cs568 and cx209 data processed with pyglint
cs568_SMB = pd.DataFrame(cs568_SMB, columns=['time', 'total_SMB','grounded_SMB','floating_SMB'])

cs568_SMB = cs568_SMB.iloc[1:-1]

cs568_SMB = cs568_SMB.reset_index(drop=True)

cx209_SMB = pd.DataFrame(cx209_SMB, columns=['time', 'total_SMB','grounded_SMB','floating_SMB'])

cx209_SMB.time = cx209_SMB.time + 1

cx209_SMB = cx209_SMB.iloc[:-1]

# Create full year range
full_range = range(int(cx209_SMB["time"].min()), int(cx209_SMB["time"].max()) + 1)

# Reindex
cx209_SMB = (
    cx209_SMB.set_index("time")
      .reindex(full_range)
      .rename_axis("time")
      .reset_index()
)

####################################################################################

# function for smoothing time series for plotting
def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='valid')
    return y_smooth

# functions for converting mass change above flotation (in Gt) to sea level contribution (in mm) for second axes
def mass2sle(x):
    return x*(-1)/361.8

def sle2mass(x):
    return x*(-1)*361.8

# Set font size for plots
plt.rcParams.update({'font.size': plot_fontsize})

####################################################################################

# Plot global T vs Time graph

print("Starting Global Temp vs Time plot...")

initialT = atmos_d["cx209"][0,1]

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

plt.plot(cs495_GSAT.time, cs495_GSAT.GSAT - initialT, label = "_none", lw=0.8, color='black', alpha=0.1)

ma_y = smooth(cs495_GSAT.GSAT - initialT, box_size)
ma_x = cs495_GSAT.time
ma_x = ma_x[int((box_size-1)/2):]
ma_x = ma_x[:-int((box_size-1)/2)]

plt.plot(ma_x, ma_y, label = "PI", lw=0.8, color='black')

for i in id:

    plot_data = atmos_d[i]
    time_series = plot_data[:,0]
    temp_series = plot_data[:,1] - initialT
    
    plt.plot(time_series-1850, temp_series, label = "_none", lw=0.8, linestyle="solid", color=line_cols[count], alpha=0.1)
    
    ma_y = smooth(temp_series, box_size)
    
    ma_x = time_series
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x-1850, ma_y, label = runs[i], lw=0.8, linestyle=line_stys[count], color=line_cols[count])

    count = count + 1

ax = plt.gca()

ax.set_xlim([0, 800])
ax.set_ylim([-2, 8])

plt.ylabel('Global Mean $\Delta$T (K)')
plt.xlabel('Years')
plt.legend(loc = 'best', prop={'size': 5})

handles, labels = ax.get_legend_handles_labels()

handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dotted'))
handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashed'))
handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashdot'))
labels.append('Dn8-X')
labels.append('Dn4-X')
labels.append('Dn2-X')

ax.legend(handles, labels, loc = 'best', prop={'size': 5})

print("Finished and saving Global Temp vs Time plot...")

plt.savefig('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/GlobalTvsTime.png', dpi = 600, bbox_inches='tight')

####################################################################################

# Setup the overall figure and size
fig, ax = plt.subplots(4, 1, figsize=(4.72, 6.69))

####################################################################################

# Plot VAF vs Time graph
print("Starting VAF vs Time plot...")

initialVAF = icesheet_d["cx209"][0]["VAF"][0]
initialVAFpi = icesheet_d["cs568"][0]["VAF"][0]
ctrl_data = icesheet_d["cs568"][0]
pi_VAF = ctrl_data["VAF"]

count = 0

for i in id:

    plot_data = icesheet_d[i][0]

    VAF_data = plot_data["VAF"]
    time_series = plot_data["time"]

    if i == "cs568":
        
        ax[1].plot(time_series - 1850, (VAF_data - initialVAFpi)*(0.918/1e9), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    else:
        
        ax[1].plot(time_series - 1850, (VAF_data - initialVAF)*(0.918/1e9), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

ax[1].set_ylabel("Mass above\nflotation change (Gt)")
ax[1].set_xlabel('Years')

# Add a second y-axis for sea level equivalent
secax = ax[1].secondary_yaxis('right', functions=(mass2sle, sle2mass)) 
secax.set_ylabel('Sea level contribution (mm)')

ax[1].set_xlim([0, 800])

ax[1].annotate('b)', xy=(1, 1), xycoords='axes fraction', xytext=(-1.0, -1.2), textcoords='offset fontsize', ha='center', fontsize=9)

print("Finished VAF vs Time plot...")

####################################################################################

# Plot SMB (grounded and floating) vs GSAT graph

print("Starting SMB vs GSAT plot...")

count = 0

box_size = 21

initialT = atmos_d["cx209"][0,1]

ax[2].plot(cs495_SMB_sorted_by_GSAT["GSAT"] - initialT, (cs495_SMB_sorted_by_GSAT["grounded_SMB"]), label = "_none", lw=0.8, color='black', alpha=0.1)
ax[3].plot(cs495_SMB_sorted_by_GSAT["GSAT"] - initialT, (cs495_SMB_sorted_by_GSAT["floating_SMB"]), label = "_none", lw=0.8, color='black', alpha=0.1)

ma_y_gr = smooth((cs495_SMB_sorted_by_GSAT["grounded_SMB"]), box_size)
ma_y_fl = smooth((cs495_SMB_sorted_by_GSAT["floating_SMB"]), box_size)
ma_x = (cs495_SMB_sorted_by_GSAT["GSAT"] - initialT).values
ma_x = ma_x[int((box_size-1)/2):]
ma_x = ma_x[:-int((box_size-1)/2)]

ax[2].plot(ma_x, ma_y_gr, label = "PI", lw=0.8, color='black')
ax[3].plot(ma_x, ma_y_fl, label = "PI", lw=0.8, color='black')

for i in id:
    
    plot_data = SMB[i]

    ax[2].plot(plot_data["GSAT"] - initialT, ((plot_data["grounded_SMB"])*(0.918/1e9)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.10)
    ax[3].plot(plot_data["GSAT"] - initialT, ((plot_data["floating_SMB"])*(0.918/1e9)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.10)
    
    ma_y_gr = smooth((plot_data["grounded_SMB"])*(0.918/1e9), box_size)
    ma_y_fl = smooth((plot_data["floating_SMB"])*(0.918/1e9), box_size)
    
    ma_x = (plot_data["GSAT"] - initialT).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    ax[2].plot(ma_x, ma_y_gr, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    ax[3].plot(ma_x, ma_y_fl, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    
    count = count + 1

ax[2].set_ylabel("Grounded SMB (Gt yr$^{-1}$)")
ax[3].set_ylabel("Floating SMB (Gt yr$^{-1}$)")
ax[2].set_xlabel('$\Delta$GSAT (K)')
ax[3].set_xlabel('$\Delta$GSAT (K)')


ax[2].annotate('c)', xy=(1, 1), xycoords='axes fraction', xytext=(-1.0, -1.2), textcoords='offset fontsize', ha='center', fontsize=9)
ax[3].annotate('d)', xy=(1, 1), xycoords='axes fraction', xytext=(-1.0, -1.2), textcoords='offset fontsize', ha='center', fontsize=9)

print("Finished SMB vs GSAT plot...")

####################################################################################

# Plot Volume vs Time graph

print("Starting Volume vs Time plot...")

count = 0

initialVol = icesheet_d["cx209"][0]["grounded_vol"][0] + icesheet_d["cx209"][0]["floating_vol"][0]
initialVolpi = icesheet_d["cs568"][0]["grounded_vol"][0] + icesheet_d["cs568"][0]["floating_vol"][0]

for i in id:

    plot_data = icesheet_d[i][0]

    IS_data_vol = plot_data["grounded_vol"] + plot_data["floating_vol"]
    time_series = plot_data["time"]

    if i == "cs568":
        
        ax[0].plot(time_series - 1850, (IS_data_vol - initialVolpi)*(0.918/1e9), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    else:
        
        ax[0].plot(time_series - 1850, (IS_data_vol - initialVol)*(0.918/1e9), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    
    count = count + 1

ax[0].set_ylabel("Mass change (Gt)")
ax[0].set_xlabel('Years')

ax[0].legend(handles, labels, loc = 'best', prop={'size': 8})
handles, labels = ax[0].get_legend_handles_labels()
handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashed'))
labels.append('Dn4-X')
ax[0].legend(handles, labels, loc = 'lower left', prop={'size': 5})

ax[0].annotate('a)', xy=(1, 1), xycoords='axes fraction', xytext=(-1.0, -1.2), textcoords='offset fontsize', ha='center', fontsize=9)

plt.tight_layout()

print("Finished Volume vs Time plot...")

print("Saving plot to file...")

plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/{icesheet}VafVolSmb_new_mask.png", dpi = 600,  bbox_inches='tight')  

print("Plot saved successfully.")

####################################################################################

# Add an extra total AIS SMB vs Time plot for responding to reviewers comments

print("Starting AIS total SMB vs Time plot...")

count = 0

box_size = 31

plt.figure(figsize=(4, 3))

ma_y = smooth((cs495_SMB["total_SMB"]), box_size)
ma_x = cs495_SMB["time"].values
ma_x = ma_x[int((box_size-1)/2):]
ma_x = ma_x[:-int((box_size-1)/2)]

plt.plot(ma_x, ma_y, label = "PI", lw=0.8, color='black')

for i in id:

    plot_data = icesheet_d[i][0]

    IS_data_SMB = plot_data["grounded_SMB"] + plot_data["floating_SMB"]

    time_series = plot_data["time"]

    #plt.plot(time_series - 1850, (IS_data_SMB)*(0.918/1e9), label = "_none", lw=0.8, linestyle="solid", color=line_cols[count], alpha=0.1)
    
    ma_y = smooth((IS_data_SMB)*(0.918/1e9), box_size)
    
    ma_x = time_series
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x-1850, ma_y, label = runs[i], lw=0.8, linestyle=line_stys[count], color=line_cols[count])
    
    count = count + 1

ax = plt.gca()
ax.set_ylabel("Total SMB (Gt/yr)")
ax.set_xlabel('Years')
ax.set_xlim([0, 750])

ax.legend(handles, labels, loc = 'best', prop={'size': 8})
handles, labels = ax.get_legend_handles_labels()
handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashed'))
labels.append('Dn4-X')
ax.legend(handles, labels, loc = 'best', prop={'size': 5})

ax.annotate('a)', xy=(1, 1), xycoords='axes fraction', xytext=(-1.0, -1.2), textcoords='offset fontsize', ha='center', fontsize=9)

plt.tight_layout()

print("Finished Total SMB vs Time plot...")

print("Saving plot to file...")

plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/{icesheet}TotalSMBvsTime_new_mask.png", dpi = 600,  bbox_inches='tight')  
print("Plot saved successfully.")

####

print("Starting AIS grounded SMB vs Time plot...")

count = 0

box_size = 31

plt.figure(figsize=(4, 3))

ma_y = smooth((cs495_SMB["grounded_SMB"]), box_size)
ma_x = cs495_SMB["time"].values
ma_x = ma_x[int((box_size-1)/2):]
ma_x = ma_x[:-int((box_size-1)/2)]

plt.plot(ma_x, ma_y, label = "PI", lw=0.8, color='black')

for i in id:

    plot_data = icesheet_d[i][0]

    IS_data_SMB = plot_data["grounded_SMB"]

    time_series = plot_data["time"]

    #plt.plot(time_series - 1850, (IS_data_SMB)*(0.918/1e9), label = "_none", lw=0.8, linestyle="solid", color=line_cols[count], alpha=0.1)
    
    ma_y = smooth((IS_data_SMB)*(0.918/1e9), box_size)
    
    ma_x = time_series
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x-1850, ma_y, label = runs[i], lw=0.8, linestyle=line_stys[count], color=line_cols[count])
    
    count = count + 1

ax = plt.gca()
ax.set_ylabel("Grounded SMB (Gt/yr)")
ax.set_xlabel('Years')
ax.set_xlim([0, 750])

ax.legend(handles, labels, loc = 'best', prop={'size': 8})
handles, labels = ax.get_legend_handles_labels()
handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashed'))
labels.append('Dn4-X')
ax.legend(handles, labels, loc = 'best', prop={'size': 5})

ax.annotate('a)', xy=(1, 1), xycoords='axes fraction', xytext=(-1.0, -1.2), textcoords='offset fontsize', ha='center', fontsize=9)

plt.tight_layout()

print("Finished Total SMB vs Time plot...")

print("Saving plot to file...")

plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/{icesheet}GroundedSMBvsTime_new_mask.png", dpi = 600,  bbox_inches='tight')  
print("Plot saved successfully.")

#####

print("Starting AIS floating SMB vs Time plot...")

count = 0

box_size = 31

plt.figure(figsize=(4, 3))

ma_y = smooth((cs495_SMB["floating_SMB"]), box_size)
ma_x = cs495_SMB["time"].values
ma_x = ma_x[int((box_size-1)/2):]
ma_x = ma_x[:-int((box_size-1)/2)]

plt.plot(ma_x, ma_y, label = "PI", lw=0.8, color='black')

for i in id:

    plot_data = icesheet_d[i][0]

    IS_data_SMB = plot_data["floating_SMB"]

    time_series = plot_data["time"]

    #plt.plot(time_series - 1850, (IS_data_SMB)*(0.918/1e9), label = "_none", lw=0.8, linestyle="solid", color=line_cols[count], alpha=0.1)
    
    ma_y = smooth((IS_data_SMB)*(0.918/1e9), box_size)
    
    ma_x = time_series
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x-1850, ma_y, label = runs[i], lw=0.8, linestyle=line_stys[count], color=line_cols[count])
    
    count = count + 1

ax = plt.gca()
ax.set_ylabel("Floating SMB (Gt/yr)")
ax.set_xlabel('Years')
ax.set_xlim([0, 750])

ax.legend(handles, labels, loc = 'best', prop={'size': 8})
handles, labels = ax.get_legend_handles_labels()
handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashed'))
labels.append('Dn4-X')
ax.legend(handles, labels, loc = 'best', prop={'size': 5})

ax.annotate('a)', xy=(1, 1), xycoords='axes fraction', xytext=(-1.0, -1.2), textcoords='offset fontsize', ha='center', fontsize=9)

plt.tight_layout()

print("Finished Total SMB vs Time plot...")

print("Saving plot to file...")

plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/{icesheet}FloatingSMBvsTime_new_mask.png", dpi = 600,  bbox_inches='tight')  
print("Plot saved successfully.")

####################################################################################

# Plots to explore why using pyglint and BISICLES diagnostic tools (post Glint transform) 
# are giving different results

def max_scaled_diff(x, y, eps=1e-8):
    return (x - y) / (abs(x) + abs(y) + eps)

cx209_diff = cx209_SMB.total_SMB - (icesheet_d["cx209"][0].grounded_SMB + icesheet_d["cx209"][0].floating_SMB)*(0.918/1e9)
cx209_diff_prop = cx209_diff/((icesheet_d["cx209"][0].grounded_SMB + icesheet_d["cx209"][0].floating_SMB)*(0.918/1e9))
cx209_robust_diff = max_scaled_diff(cx209_SMB.total_SMB, (icesheet_d["cx209"][0].grounded_SMB + icesheet_d["cx209"][0].floating_SMB)*(0.918/1e9))

cx209_diff_grounded = cx209_SMB.grounded_SMB - (icesheet_d["cx209"][0].grounded_SMB)*(0.918/1e9)
cx209_diff_grounded_prop = cx209_diff_grounded/((icesheet_d["cx209"][0].grounded_SMB)*(0.918/1e9))
cx209_robust_diff_grounded = max_scaled_diff(cx209_SMB.grounded_SMB, (icesheet_d["cx209"][0].grounded_SMB)*(0.918/1e9))

cx209_diff_floating = cx209_SMB.floating_SMB - (icesheet_d["cx209"][0].floating_SMB)*(0.918/1e9)
cx209_diff_floating_prop = cx209_diff_floating/((icesheet_d["cx209"][0].floating_SMB)*(0.918/1e9))
cx209_robust_diff_floating = max_scaled_diff(cx209_SMB.floating_SMB, (icesheet_d["cx209"][0].floating_SMB)*(0.918/1e9))

cs568_diff = cs568_SMB.total_SMB - (icesheet_d["cs568"][0].grounded_SMB + icesheet_d["cs568"][0].floating_SMB)*(0.918/1e9)
cs568_diff_prop = cs568_diff/((icesheet_d["cs568"][0].grounded_SMB + icesheet_d["cs568"][0].floating_SMB)*(0.918/1e9))
cs568_robust_diff = max_scaled_diff(cs568_SMB.total_SMB, (icesheet_d["cs568"][0].grounded_SMB + icesheet_d["cs568"][0].floating_SMB)*(0.918/1e9))

cs568_diff_grounded = cs568_SMB.grounded_SMB - (icesheet_d["cs568"][0].grounded_SMB)*(0.918/1e9)
cs568_diff_grounded_prop = cs568_diff_grounded/((icesheet_d["cs568"][0].grounded_SMB)*(0.918/1e9))
cs568_robust_diff_grounded = max_scaled_diff(cs568_SMB.grounded_SMB, (icesheet_d["cs568"][0].grounded_SMB)*(0.918/1e9))

cs568_diff_floating = cs568_SMB.floating_SMB - (icesheet_d["cs568"][0].floating_SMB)*(0.918/1e9)
cs568_diff_floating_prop = cs568_diff_floating/((icesheet_d["cs568"][0].floating_SMB)*(0.918/1e9))
cs568_robust_diff_floating = max_scaled_diff(cs568_SMB.floating_SMB, (icesheet_d["cs568"][0].floating_SMB)*(0.918/1e9))

# Start with a figure of just SMBs (total, grounded, floating) vs time for cx209 and cs568 raw data (no smoothing)

plt.figure(figsize=(4, 3))

plt.plot(cs568_SMB.time, cs568_SMB.total_SMB, label = "cs568 pyglint", lw=0.8, color='Orange')
plt.plot(icesheet_d["cs568"][0].time-1850, (icesheet_d["cs568"][0].grounded_SMB + icesheet_d["cs568"][0].floating_SMB)*(0.918/1e9), label = "cs568 orig", lw=0.8, color='Red')

plt.plot(cx209_SMB.time-1850, cx209_SMB.total_SMB, label = "cx209 pyglint", lw=0.8, color='Pink')
plt.plot(icesheet_d["cx209"][0].time-1850, (icesheet_d["cx209"][0].grounded_SMB + icesheet_d["cx209"][0].floating_SMB)*(0.918/1e9), label = "cx209 orig", lw=0.8, color='Purple')

ax = plt.gca()
ax.set_ylabel("Total SMB (Gt/yr)")
ax.set_xlabel('Years')
ax.set_xlim([0, 600])
ax.legend(loc = 'best', prop={'size': 5})

plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/cs568_cx209_SMB_pyglint_orig_comparison_total_SMB.png", dpi = 600,  bbox_inches='tight')

plt.figure(figsize=(4, 3))

plt.plot(cs568_SMB.time, cs568_SMB.grounded_SMB, label = "cs568 pyglint", lw=0.8, color='Orange')
plt.plot(icesheet_d["cs568"][0].time-1850, (icesheet_d["cs568"][0].grounded_SMB)*(0.918/1e9), label = "cs568 orig", lw=0.8, color='Red')

plt.plot(cx209_SMB.time-1850, cx209_SMB.grounded_SMB, label = "cx209 pyglint", lw=0.8, color='Pink')
plt.plot(icesheet_d["cx209"][0].time-1850, (icesheet_d["cx209"][0].grounded_SMB)*(0.918/1e9), label = "cx209 orig", lw=0.8, color='Purple')

ax = plt.gca()
ax.set_ylabel("Grounded SMB (Gt/yr)")
ax.set_xlabel('Years')
ax.set_xlim([0, 600])
ax.legend(loc = 'best', prop={'size': 5})

plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/cs568_cx209_SMB_pyglint_orig_comparison_grounded_SMB.png", dpi = 600,  bbox_inches='tight')

plt.figure(figsize=(4, 3))

plt.plot(cs568_SMB.time, cs568_SMB.floating_SMB, label = "cs568 pyglint", lw=0.8, color='Orange')
plt.plot(icesheet_d["cs568"][0].time-1850, (icesheet_d["cs568"][0].floating_SMB)*(0.918/1e9), label = "cs568 orig", lw=0.8, color='Red')

plt.plot(cx209_SMB.time-1850, cx209_SMB.floating_SMB, label = "cx209 pyglint", lw=0.8, color='Pink')
plt.plot(icesheet_d["cx209"][0].time-1850, (icesheet_d["cx209"][0].floating_SMB)*(0.918/1e9), label = "cx209 orig", lw=0.8, color='Purple')

ax = plt.gca()
ax.set_ylabel("Floating SMB (Gt/yr)")
ax.set_xlabel('Years')
ax.set_xlim([0, 600])
ax.legend(loc = 'best', prop={'size': 5})

plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/cs568_cx209_SMB_pyglint_orig_comparison_floating_SMB.png", dpi = 600,  bbox_inches='tight')

### now make the difference plots (first absolute, then proportional differences) again broken down by total, grounded and floating SMB

plt.figure(figsize=(4, 3))

plt.plot(cs568_SMB.time, cs568_diff, label = "cs568 diff (pyglint - orig)", lw=0.8, color='Orange')
plt.plot(cx209_SMB.time-1850, cx209_diff, label = "cx209 diff (pyglint - orig)", lw=0.8, color='Pink')

ax = plt.gca()
ax.set_ylabel("Difference in total SMB (Gt/yr)")
ax.set_xlabel('Years')
ax.set_xlim([0, 600])
ax.legend(loc = 'best', prop={'size': 5})

plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/cs568_cx209_SMB_pyglint_orig_comparison_total_SMB_diff.png", dpi = 600,  bbox_inches='tight')

plt.figure(figsize=(4, 3))
plt.plot(cs568_SMB.time, cs568_diff_prop, label = "cs568 diff prop (pyglint - orig)", lw=0.8, color='Orange')
plt.plot(cx209_SMB.time-1850, cx209_diff_prop, label = "cx209 diff prop (pyglint - orig)", lw=0.8, color='Pink')
plt.plot(cs568_SMB.time, cs568_robust_diff, label = "cs568 robust diff (pyglint - orig)", lw=0.8, color='blue')
plt.plot(cx209_SMB.time-1850, cx209_robust_diff, label = "cx209 robust diff (pyglint - orig)", lw=0.8, color='cyan')

ax = plt.gca()
ax.set_ylabel("Prop/robust difference in total SMB")
ax.set_xlabel('Years')
ax.set_xlim([0, 600])
ax.legend(loc = 'best', prop={'size': 5})

plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/cs568_cx209_SMB_pyglint_orig_comparison_total_SMB_diff_prop.png", dpi = 600,  bbox_inches='tight')

plt.figure(figsize=(4, 3))

plt.plot(cs568_SMB.time, cs568_diff_grounded, label = "cs568 diff (pyglint - orig)", lw=0.8, color='Orange')
plt.plot(cx209_SMB.time-1850, cx209_diff_grounded, label = "cx209 diff (pyglint - orig)", lw=0.8, color='Pink')

ax = plt.gca()
ax.set_ylabel("Difference in grounded SMB (Gt/yr)")
ax.set_xlabel('Years')
ax.set_xlim([0, 600])
ax.legend(loc = 'best', prop={'size': 5})

plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/cs568_cx209_SMB_pyglint_orig_comparison_grounded_SMB_diff.png", dpi = 600,  bbox_inches='tight')

plt.figure(figsize=(4, 3))

plt.plot(cs568_SMB.time, cs568_diff_grounded_prop, label = "cs568 diff prop (pyglint - orig)", lw=0.8, color='Orange')
plt.plot(cx209_SMB.time-1850, cx209_diff_grounded_prop, label = "cx209 diff prop (pyglint - orig)", lw=0.8, color='Pink')
plt.plot(cs568_SMB.time, cs568_robust_diff_grounded, label = "cs568 robust diff (pyglint - orig)", lw=0.8, color='blue')
plt.plot(cx209_SMB.time-1850, cx209_robust_diff_grounded, label = "cx209 robust diff (pyglint - orig)", lw=0.8, color='cyan')

ax = plt.gca()
ax.set_ylabel("Prop/robust difference in grounded SMB")
ax.set_xlabel('Years')
ax.set_xlim([0, 600])
ax.legend(loc = 'best', prop={'size': 5})

plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/cs568_cx209_SMB_pyglint_orig_comparison_grounded_SMB_diff_prop.png", dpi = 600,  bbox_inches='tight')

plt.figure(figsize=(4, 3))

plt.plot(cs568_SMB.time, cs568_diff_floating, label = "cs568 diff (pyglint - orig)", lw=0.8, color='Orange')
plt.plot(cx209_SMB.time-1850, cx209_diff_floating, label = "cx209 diff (pyglint - orig)", lw=0.8, color='Pink')

ax = plt.gca()
ax.set_ylabel("Difference in floating SMB (Gt/yr)")
ax.set_xlabel('Years')
ax.set_xlim([0, 600])
ax.legend(loc = 'best', prop={'size': 5})

plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/cs568_cx209_SMB_pyglint_orig_comparison_floating_SMB_diff.png", dpi = 600,  bbox_inches='tight')

plt.figure(figsize=(4, 3))
plt.plot(cs568_SMB.time, cs568_diff_floating_prop, label = "cs568 diff prop (pyglint - orig)", lw=0.8, color='Orange')
#plt.plot(cx209_SMB.time-1850, cx209_diff_floating_prop, label = "cx209 diff prop (pyglint - orig)", lw=0.8, color='Pink')
plt.plot(cs568_SMB.time, cs568_robust_diff_floating, label = "cs568 robust diff (pyglint - orig)", lw=0.8, color='blue')
#plt.plot(cx209_SMB.time-1850, cx209_robust_diff_floating, label = "cx209 robust diff (pyglint - orig)", lw=0.8, color='cyan')

ax = plt.gca()
ax.set_ylabel("Prop/robust difference in floating SMB")
ax.set_xlabel('Years')
ax.set_xlim([0, 600])
ax.legend(loc = 'best', prop={'size': 5})   

plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/cs568_cx209_SMB_pyglint_orig_comparison_floating_SMB_diff_prop.png", dpi = 600,  bbox_inches='tight')