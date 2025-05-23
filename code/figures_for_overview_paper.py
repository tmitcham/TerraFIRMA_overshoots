####################################################################################
# Imports
import numpy as np
import pickle
import matplotlib.pyplot as plt
import pandas as pd

####################################################################################

# Options
icesheet = "GrIS" # AIS or GrIS
run_list = "id_all" # "id" or "id_all" or "idanom"
plot_fontsize = 8

####################################################################################

id = ["cs568", "cx209", "cy837", "cy838", "cz375", "cz376", "cz377", "dc052", "dc051", "df028", "dc123", "dc130"]#, "da697", "di335", "df453", "da892", "dc251"]
idanom = ["cx209", "cy837", "cy838", "cz375", "cz376", "cz377", "dc052", "dc051", "df028", "dc123", "dc130"]#, "da697", "di335", "df453", "da892", "dc251"]
id_all=["cs568", "cx209", "cw988", "cw989", "cw990", "cy837", "cy838", "cz375", "cz376", "cz377", "cz378",
    "cz834", "cz855", "db587", "db723", "db731", "da087", "da266", "db597", "db733", "dc324",
    "di335", "da800", "da697", "da892", "db223", "df453", "de620", "dc251",
    "dc051", "dc052", "dc248", "dc249", "dc565", "dd210", "df028", "de621", "dc123", "dc130",
    "df025", "df027", "df021", "df023", "dh541", "dh859", "de943", "de962", "de963", "dg093", "dg094", "dg095", "dm357", "dm358", "dm359"]

run_type = ["ZE-0","Up8", "ZE-1.5", "ZE-2", "ZE-3", "ZE-4", "ZE-5", "_ramp-down -4 1.5C 50yr", "_ramp-down -4 2C 50yr", "_ramp-down -4 3C 50yr", "_ramp-down -4 4C 50yr", "_ramp-down -4 5C 50yr"]#, "_ramp-down -8 1.5C 50yr", "_ramp-down -8 2C 50yr", "_ramp-down -8 3C 50yr", "_ramp-down -8 4C 50yr", "_ramp-down -8 5C 50yr"]
run_type_anom = ["Up8", "ZE-1.5", "ZE-2", "ZE-3", "ZE-4", "ZE-5", "_ramp-down -4 1.5C 50yr", "_ramp-down -4 2C 50yr", "_ramp-down -4 3C 50yr", "_ramp-down -4 4C 50yr", "_ramp-down -4 5C 50yr"]#, "_ramp-down -8 1.5C 50yr", "_ramp-down -8 2C 50yr", "_ramp-down -8 3C 50yr", "_ramp-down -8 4C 50yr", "_ramp-down -8 5C 50yr"]
run_type_all = ["ZE-0","Up8", "_Up8", "_Up8", "_Up8", "ZE-1.5", "ZE-2", "ZE-3", "ZE-4", "ZE-5", "ZE-6",
            "_ZE-1.5", "_ZE-2", "_ZE-3", "_ZE-4", "_ZE-5", "_ZE-1.5", "_ZE-2", "_ZE-3", "_ZE-4", "_ZE-5",
            "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X",
            "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X",
            "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X"]
runs = dict(zip(id, run_type)) 
runs_anom = dict(zip(idanom, run_type_anom))
runs_all = dict(zip(id_all, run_type_all))

line_cols = ['#000000','#C30F0E','#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0','#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0']#, '#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0']
line_stys = ["dotted","solid","solid","solid","solid","solid","solid","dashed","dashed","dashed","dashed","dashed"]#,"dashed","dashed","dashed","dashed","dashed"]

line_cols_anom = ['#C30F0E','#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0','#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0']#,'#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0']
line_stys_anom = ["solid","solid","solid","solid","solid","solid","dashed","dashed","dashed","dashed","dashed"]#,"dashed","dashed","dashed","dashed","dashed"]

line_cols_all=['#000000','#C30F0E','#C30F0E','#C30F0E','#C30F0E','#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0','#964b00',
             '#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0', '#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0',
             '#168039','#168039','#0003C7','#FA5B0F','#FFE11A','#FFE11A','#FFE11A','#9C27B0',
             '#168039','#0003C7','#0003C7','#FFE11A','#168039','#FA5B0F','#FFE11A','#FFE11A','#FA5B0F','#9C27B0',
             '#168039','#168039','#FFE11A','#FFE11A','#FA5B0F','#FA5B0F','#964b00','#964b00','#964b00','#9C27B0','#9C27B0','#9C27B0','#964b00','#964b00','#964b00']
line_stys_all=["solid","solid","solid","solid","solid","solid","solid","solid","solid","solid","solid",
             "solid","solid","solid","solid","solid","solid","solid","solid","solid","solid",
             "dotted","dotted","dotted","dotted","dotted","dotted","dotted","dotted",
             "dashed","dashed","dashed","dashed","dashed","dashed","dashed","dashed","dashed","dashed",
             "dashdot","dashdot","dashdot","dashdot","dashdot","dashdot","dotted","dashed","dashdot","dotted","dashed","dashdot","dotted","dashed","dashdot"]

####################################################################################

# Read ice sheet data

if icesheet == "AIS":
    with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/AIS_data_overshoots_masked.pkl", 'rb') as file:
        icesheet_d = pickle.load(file)

elif icesheet == "GrIS":
    with open('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/GrIS_data_overshoots.pkl', 'rb') as file:
        icesheet_d = pickle.load(file) 

    icesheet_d["cs568"][0] = icesheet_d["cs568"][0].drop(index=icesheet_d["cs568"][0].index[0], axis=0).reset_index(drop=True)

with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/atmos_data_overshoots.pkl", 'rb') as file:
    atmos_d = pickle.load(file)

####################################################################################

# Prepare data for SMB vs GSAT plots

SMB = {}

for i in id_all:
    
    SMB[i] = icesheet_d[i][0][["time","grounded_SMB","floating_SMB"]] 
    SMB[i] = pd.concat([SMB[i], pd.DataFrame(atmos_d[i][:,1])], axis=1)
    SMB[i].drop(SMB[i].tail(1).index,inplace=True)
    SMB[i].columns = ["time","grounded_SMB","floating_SMB","GSAT"]

    # Sort the rows into order of lowest to highest GSAT
    SMB[i] = SMB[i].sort_values(by="GSAT")

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

for i in id_all:

    plot_data = atmos_d[i]
    time_series = plot_data[:,0]
    temp_series = plot_data[:,1] - initialT
    
    plt.plot(time_series-1850, temp_series, label = "_none", lw=0.8, linestyle="solid", color=line_cols_all[count], alpha=0.1)
    
    ma_y = smooth(temp_series, box_size)
    
    ma_x = time_series
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x-1850, ma_y, label = runs_all[i], lw=0.8, linestyle=line_stys_all[count], color=line_cols_all[count])

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

for i in id_all:

    plot_data = icesheet_d[i][0]

    VAF_data = plot_data["VAF"]
    time_series = plot_data["time"]

    if i == "cs568":
        
        ax[1].plot(time_series - 1850, (VAF_data - initialVAFpi)*(0.918/1e9), label = runs_all[i], lw=0.8, color = line_cols_all[count], linestyle = line_stys_all[count])

    else:
        
        ax[1].plot(time_series - 1850, (VAF_data - initialVAF)*(0.918/1e9), label = runs_all[i], lw=0.8, color = line_cols_all[count], linestyle = line_stys_all[count])

    count = count + 1

ax[1].set_ylabel("Mass above\nflotation change (Gt)")
ax[1].set_xlabel('Years')

# Add a second y-axis for sea level equivalent
secax = ax[1].secondary_yaxis('right', functions=(mass2sle, sle2mass)) 
secax.set_ylabel('Sea level contribution (mm)')

ax[1].set_xlim([0, 800])

ax[1].annotate('b)', xy=(1, 1), xycoords='axes fraction', xytext=(-1.0, -1.2), textcoords='offset fontsize', ha='center', fontsize=9)


####################################################################################

# Plot SMB (grounded and floating) vs GSAT graph

print("Starting SMB vs GSAT plot...")

count = 0

box_size = 21

initialT = atmos_d["cx209"][0,1]

for i in id_all:
    
    plot_data = SMB[i]

    ax[2].plot(plot_data["GSAT"] - initialT, ((plot_data["grounded_SMB"])*(0.918/1e9)), label = '_none', lw=0.8, color = line_cols_all[count], linestyle = line_stys_all[count], alpha = 0.10)
    ax[3].plot(plot_data["GSAT"] - initialT, ((plot_data["floating_SMB"])*(0.918/1e9)), label = '_none', lw=0.8, color = line_cols_all[count], linestyle = line_stys_all[count], alpha = 0.10)
    
    ma_y_gr = smooth((plot_data["grounded_SMB"])*(0.918/1e9), box_size)
    ma_y_fl = smooth((plot_data["floating_SMB"])*(0.918/1e9), box_size)
    
    ma_x = (plot_data["GSAT"] - initialT).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    ax[2].plot(ma_x, ma_y_gr, label = runs_all[i], lw=0.8, color = line_cols_all[count], linestyle = line_stys_all[count])
    ax[3].plot(ma_x, ma_y_fl, label = runs_all[i], lw=0.8, color = line_cols_all[count], linestyle = line_stys_all[count])
    
    count = count + 1

ax[2].set_ylabel("Grounded SMB (Gt yr$^{-1}$)")
ax[3].set_ylabel("Floating SMB (Gt yr$^{-1}$)")
ax[2].set_xlabel('$\Delta$GSAT (K)')
ax[3].set_xlabel('$\Delta$GSAT (K)')


ax[2].annotate('c)', xy=(1, 1), xycoords='axes fraction', xytext=(-1.0, -1.2), textcoords='offset fontsize', ha='center', fontsize=9)
ax[3].annotate('d)', xy=(1, 1), xycoords='axes fraction', xytext=(-1.0, -1.2), textcoords='offset fontsize', ha='center', fontsize=9)

print("Finished and saving SMB vs GSAT plot...")

####################################################################################

# Plot Volume vs Time graph

print("Starting Volume vs Time plot...")

count = 0

initialVol = icesheet_d["cx209"][0]["grounded_vol"][0] + icesheet_d["cx209"][0]["floating_vol"][0]
initialVolpi = icesheet_d["cs568"][0]["grounded_vol"][0] + icesheet_d["cs568"][0]["floating_vol"][0]

for i in id_all:

    plot_data = icesheet_d[i][0]

    IS_data_vol = plot_data["grounded_vol"] + plot_data["floating_vol"]
    time_series = plot_data["time"]

    if i == "cs568":
        
        ax[0].plot(time_series - 1850, (IS_data_vol - initialVolpi)*(0.918/1e9), label = runs_all[i], lw=0.8, color = line_cols_all[count], linestyle = line_stys_all[count])

    else:
        
        ax[0].plot(time_series - 1850, (IS_data_vol - initialVol)*(0.918/1e9), label = runs_all[i], lw=0.8, color = line_cols_all[count], linestyle = line_stys_all[count])
    
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

plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/{icesheet}VafVolSmb.pdf", dpi = 600,  bbox_inches='tight')  

####################################################################################
