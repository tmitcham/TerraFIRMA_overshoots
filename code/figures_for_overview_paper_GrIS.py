####################################################################################
# Imports
import numpy as np
import pickle
import matplotlib.pyplot as plt
import pandas as pd

####################################################################################
'''
id = ["cs568", "cx209", "cy837", "cy838", "cz375", "cz376", "cz377", "dc052", "dc051", "df028", "dc123", "dc130", "da697", "cz944", "df453", "da892", "dc251"]
idanom = ["cx209", "cy837", "cy838", "cz375", "cz376", "cz377", "dc052", "dc051", "df028", "dc123", "dc130", "da697", "cz944", "df453", "da892", "dc251"]

run_type = ["ZE-0","Up8", "ZE-1.5", "ZE-2", "ZE-3", "ZE-4", "ZE-5", "_ramp-down -4 1.5C 50yr", "_ramp-down -4 2C 50yr", "_ramp-down -4 3C 50yr", "_ramp-down -4 4C 50yr", "_ramp-down -4 5C 50yr", "_ramp-down -8 1.5C 50yr", "_ramp-down -8 2C 50yr", "_ramp-down -8 3C 50yr", "_ramp-down -8 4C 50yr", "_ramp-down -8 5C 50yr"]
run_type_anom = ["Up8", "ZE-1.5", "ZE-2", "ZE-3", "ZE-4", "ZE-5", "_ramp-down -4 1.5C 50yr", "_ramp-down -4 2C 50yr", "_ramp-down -4 3C 50yr", "_ramp-down -4 4C 50yr", "_ramp-down -4 5C 50yr", "_ramp-down -8 1.5C 50yr", "_ramp-down -8 2C 50yr", "_ramp-down -8 3C 50yr", "_ramp-down -8 4C 50yr", "_ramp-down -8 5C 50yr"]

runs = dict(zip(id, run_type)) 
runs_anom = dict(zip(idanom, run_type_anom))

line_cols = ['#000000','#C30F0E','#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0','#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0', '#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0']
line_stys = ["dotted","solid","solid","solid","solid","solid","solid","dashed","dashed","dashed","dashed","dashed","dashdot","dashdot","dashdot","dashdot","dashdot"]

line_cols_anom = ['#C30F0E','#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0','#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0','#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0']
line_stys_anom = ["solid","solid","solid","solid","solid","solid","dashed","dashed","dashed","dashed","dashed","dashdot","dashdot","dashdot","dashdot","dashdot"]
'''
id=["cs568", "cx209", "cw988", "cw989", "cw990", "cy837", "cy838", "cz375", "cz376", "cz377", "cz378",
    "cz834", "cz855", "db587", "db723", "db731", "da087", "da266", "db597", "db733", "dc324",
    "di335", "da800", "da697", "da892", "db223", "df453", "de620", "dc251",
    "dc051", "dc052", "dc248", "dc249", "dc565", "dd210", "df028", "de621", "dc123", "dc130",
    "df025", "df027", "df021", "df023", "dh541", "dh859", "de943", "de962", "de963", "dg093", "dg094", "dg095"]

run_type = ["ZE-0","Up8", "_Up8", "_Up8", "_Up8", "ZE-1.5", "ZE-2", "ZE-3", "ZE-4", "ZE-5", "ZE-6",
            "_ZE-1.5", "_ZE-2", "_ZE-3", "_ZE-4", "_ZE-5", "_ZE-1.5", "_ZE-2", "_ZE-3", "_ZE-4", "_ZE-5",
            "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X",
            "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X",
            "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X"]
            
runs = dict(zip(id, run_type)) 


line_cols = ['#000000','#C30F0E','#C30F0E','#C30F0E','#C30F0E','#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0','#964b00',
             '#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0', '#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0',
             '#168039','#168039','#0003C7','#FA5B0F','#FFE11A','#FFE11A','#FFE11A','#9C27B0',
             '#168039','#0003C7','#0003C7','#FFE11A','#168039','#FA5B0F','#FFE11A','#FFE11A','#FA5B0F','#9C27B0',
             '#168039','#168039','#FFE11A','#FFE11A','#FA5B0F','#FA5B0F','#964b00','#964b00','#964b00','#9C27B0','#9C27B0','#9C27B0']

'''
line_cols = ['Blue','Black','Black','Black','Black','Lawngreen','Goldenrod','Red','Sienna','Pink','Indigo',
             'Lawngreen','Goldenrod','Red','Sienna','Pink', 'Lawngreen','Goldenrod','Red','Sienna','Pink',
             'Goldenrod','Goldenrod','Lawngreen','Sienna','Red','Red','Red','Pink',
             'Goldenrod','Lawngreen','Lawngreen','Red','Goldenrod','Sienna','Red','Red','Sienna','Pink',
             'Goldenrod','Goldenrod','Red','Red','Sienna','Sienna','Indigo','Indigo','Indigo']
'''
line_stys = ["solid","solid","solid","solid","solid","solid","solid","solid","solid","solid","solid",
             "solid","solid","solid","solid","solid","solid","solid","solid","solid","solid",
             "dotted","dotted","dotted","dotted","dotted","dotted","dotted","dotted",
             "dashed","dashed","dashed","dashed","dashed","dashed","dashed","dashed","dashed","dashed",
             "dashdot","dashdot","dashdot","dashdot","dashdot","dashdot","dotted","dashed","dashdot","dotted","dashed","dashdot"]


####################################################################################

# Read ice sheet data

#with open('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/AIS_data_overshoots_masked.pkl', 'rb') as file:
#    icesheet_d = pickle.load(file)
    
with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/GrIS_data_overshoots.pkl", 'rb') as file:
    icesheet_d = pickle.load(file)
    
with open('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/atmos_data_overshoots.pkl', 'rb') as file:
    atmos_d = pickle.load(file) 
    
icesheet_d["cs568"] = icesheet_d["cs568"].drop(index=icesheet_d["cs568"].index[0], axis=0).reset_index(drop=True)
icesheet_d["cw988"] = icesheet_d["cw988"].drop(index=icesheet_d["cw988"].index[74], axis=0).reset_index(drop=True)

####################################################################################

# function for smoothing time series for plotting

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='valid')
    return y_smooth

# Convert volume to sea level equivalent for second axes
def vol2sle(x):
    
    return (((x-26.27)*0.918e6)/(361.8e3)*-1)

def sle2vol(x):
    return ((((x*361.8e3)/0.918e6)+26.27)*-1)

# Convert VAF to sea level equivalent for second axes
def mass2sle(x):
    return x*(-1)/(361.8*1000)

def sle2mass(x):
    return x*(-1)*(361.8*1000)

plt.rcParams.update({'font.size': 7.5})

####################################################################################

# Plot VAF vs Time graph

print("Starting AIS VAF vs Time plot...")

initialVAF = icesheet_d["cx209"]["VAF"][0]
initialVAFpi = icesheet_d["cs568"]["VAF"][0]

count = 0

plt.figure(figsize=(4, 3))

ctrl_data = icesheet_d["cs568"]
pi_VAF = ctrl_data["VAF"]

for i in id:

    if i in ["db731", "da087", "cz944"]:
        count += 1
        continue
    
    plot_data = icesheet_d[i]

    VAF_data = plot_data["VAF"]
    time_series = plot_data["time"]

    if i == "cs568":
        
        plt.plot(time_series - 1850, (VAF_data - initialVAFpi)*(0.918/1e9), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    else:
        
        plt.plot(time_series - 1850, (VAF_data - initialVAF)*(0.918/1e9), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

ax = plt.gca()

#ax.set_yticks([0, -20000, -40000, -60000, -80000, -100000]) 
#ax.set_yticklabels(['0', '-20,000', '-40,000', '-60,000', '-80,000', '-100,000']) 

plt.ylabel("Mass change (Gt)")
plt.xlabel('Years')
plt.legend(loc = 'best', prop={'size': 5})

# Add a second y-axis for sea level equivalent
ax = plt.gca()
secax = ax.secondary_yaxis('right', functions=(mass2sle, sle2mass)) 
secax.set_ylabel('Sea level contribution (m)')

ax.set_xlim([0, 750])

handles, labels = ax.get_legend_handles_labels()

handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dotted'))
handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashed'))
handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashdot'))
labels.append('Dn8-X')
labels.append('Dn4-X')
labels.append('Dn2-X')

ax.legend(handles, labels, loc = 'best', prop={'size': 5})

print("Finished and saving AIS VAF vs Time plot...")

plt.savefig('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/GrISVAFvsTime.png', dpi = 600,  bbox_inches='tight')

####################################################################################

# Plot SMB vs Time graph

print("Starting AIS SMB vs Time plot...")

count = 0

box_size = 21

plt.figure(figsize=(4, 3))

for i in id:
    
    if i in ["db731", "da087", "cz944"]:
        count += 1
        continue

    plot_data = icesheet_d[i]

    AIS_data_gr = plot_data["grounded_SMB"] + plot_data["floating_SMB"]
    time_series = plot_data["time"]

    plt.plot(time_series - 1850, ((AIS_data_gr)*(0.918/1e9)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)
    
    ma_y_gr = smooth((AIS_data_gr)*(0.918/1e9), box_size)
    
    ma_x = (time_series - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y_gr, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    
    count = count + 1
    
ax = plt.gca()

ax.set_xlim([0, 750])

ax.set_ylabel("SMB (Gt yr$^{-1}$)")
plt.xlabel('Years')

handles, labels = ax.get_legend_handles_labels()

handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dotted'))
handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashed'))
handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashdot'))
labels.append('Dn8-X')
labels.append('Dn4-X')
labels.append('Dn2-X')

ax.legend(handles, labels, loc = 'best', prop={'size': 5})

print("Finished and saving AIS SMB vs Time plot...")

plt.savefig('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/GrISSMBvsTime.png', dpi = 600,  bbox_inches='tight')  

####################################################################################

# Plot Volume and VAF vs Time graph

print("Starting AIS Volume and VAF vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

fig, ax = plt.subplots(2, sharex='col', sharey='row')

initialVAF = icesheet_d["cx209"][0]["VAF"][0]
initialVAFpi = icesheet_d["cs568"][0]["VAF"][0]

initialVol = icesheet_d["cx209"][0]["grounded_vol"][0] + icesheet_d["cx209"][0]["floating_vol"][0]
initialVolpi = icesheet_d["cs568"][0]["grounded_vol"][0] + icesheet_d["cs568"][0]["floating_vol"][0]

for i in id:

    plot_data = icesheet_d[i][0]

    AIS_data_vol = plot_data["grounded_vol"] + plot_data["floating_vol"]
    AIS_data_vaf = plot_data["VAF"]
    time_series = plot_data["time"]

    if i == "cs568":
        
        ax[0].plot(time_series - 1850, (AIS_data_vol - initialVolpi)*(0.918/1e9), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
        ax[1].plot(time_series - 1850, (AIS_data_vaf - initialVAFpi)*(0.918/1e9), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    else:
        
        ax[0].plot(time_series - 1850, (AIS_data_vol - initialVol)*(0.918/1e9), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
        ax[1].plot(time_series - 1850, (AIS_data_vaf - initialVAF)*(0.918/1e9), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    
    count = count + 1

ax[0].set_xlim([0, 750])
ax[1].set_xlim([0, 750])

ax[0].set_ylabel("Mass change (Gt)")
ax[1].set_ylabel("Mass above flotation change (Gt)")

secax = ax[1].secondary_yaxis('right', functions=(mass2sle, sle2mass)) 
secax.set_ylabel('Sea level contribution (m)')

ax[0].set_yticks([0, -200000, -400000, -600000, -800000]) 
ax[0].set_yticklabels(['0', '-200,000', '-400,000', '-600,000', '-800,000']) 
ax[1].set_yticks([0, -20000, -40000, -60000, -80000, -100000]) 
ax[1].set_yticklabels(['0', '-20,000', '-40,000', '-60,000', '-80,000', '-100,000']) 

ax[1].set_xlabel('Years')

handles, labels = ax[0].get_legend_handles_labels()

handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dotted'))
handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashed'))
handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashdot'))
labels.append('Dn8-X')
labels.append('Dn4-X')
labels.append('Dn2-X')

ax[0].legend(handles, labels, loc = 'best', prop={'size': 4})

ax[0].annotate('a)', xy=(0, 0), xycoords='axes fraction', xytext=(+1.0, +0.5), textcoords='offset fontsize', ha='center', fontsize=9)
ax[1].annotate('b)', xy=(0, 0), xycoords='axes fraction', xytext=(+1.0, +0.5), textcoords='offset fontsize', ha='center', fontsize=9)

print("Finished and saving AIS SMB vs Time plot...")

plt.savefig('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/AISVafVolvsTime.png', dpi = 600,  bbox_inches='tight')  


####################################################################################

# Plot Volume and VAF vs Time Anomaly graph
'''
print("Starting AIS Volume and VAF Anom vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

fig, ax = plt.subplots(2, sharex='col', sharey='row')

initialVAF = icesheet_d["cx209"][0].iloc[0,61]
initialVAFpi = icesheet_d["cs568"][0].iloc[0,61]

initialVol = icesheet_d["cx209"][0].iloc[0,43] + icesheet_d["cx209"][0].iloc[0,52]
initialVolpi = icesheet_d["cs568"][0].iloc[0,43] + icesheet_d["cs568"][0].iloc[0,52]

ctrl_data = icesheet_d["cs568"][0]

for i in idanom:

    plot_data = icesheet_d[i][0]
    
    pi_VAF = ctrl_data.iloc[:,61]
    pi_Vol = ctrl_data.iloc[:,43] + ctrl_data.iloc[:,52]
    pi_time_series = ctrl_data.iloc[:,2]

    VAF_data = plot_data.iloc[:,61]
    Vol_data = plot_data.iloc[:,43] + plot_data.iloc[:,52]
    time_series = plot_data.iloc[:,2]

    if max(time_series) > max(pi_time_series):

        start_year =  min(time_series)
        end_year = max(pi_time_series)

        pi_VAF = pi_VAF[(pi_time_series >= start_year) & (pi_time_series <= end_year)].reset_index(drop=True)
        pi_Vol = pi_Vol[(pi_time_series >= start_year) & (pi_time_series <= end_year)].reset_index(drop=True)
        VAF_data = VAF_data[(time_series >= start_year) & (time_series <= end_year)]
        Vol_data = Vol_data[(time_series >= start_year) & (time_series <= end_year)]
        time_series = time_series[(time_series >= start_year) & (time_series <= end_year)]

    elif max(time_series) < max(pi_time_series):

        start_year =  min(time_series)
        end_year = max(time_series)

        pi_VAF = pi_VAF[(pi_time_series >= start_year) & (pi_time_series <= end_year)].reset_index(drop=True)
        pi_Vol = pi_Vol[(pi_time_series >= start_year) & (pi_time_series <= end_year)].reset_index(drop=True)

    else:
        
        pass

        
    ax[0].plot(time_series - 1850, ((Vol_data - initialVol) - (pi_Vol - initialVolpi))*(0.918/1e9), label = runs_anom[i], lw=0.8, color = line_cols_anom[count], linestyle = line_stys_anom[count])
    ax[1].plot(time_series - 1850, ((VAF_data - initialVAF) - (pi_VAF - initialVAFpi))*(0.918/1e9), label = runs_anom[i], lw=0.8, color = line_cols_anom[count], linestyle = line_stys_anom[count])

    count = count + 1

ax[0].grid(linestyle='-', lw=0.2)
ax[1].grid(linestyle='-', lw=0.2)

ax[0].set_xlim([0, 560])
ax[1].set_xlim([0, 560])

ax[0].set_ylabel("Mass change anomaly (Gt)")
ax[1].set_ylabel("Mass above flotation change\nanomaly (Gt)")

secax = ax[1].secondary_yaxis('right', functions=(mass2sle, sle2mass)) 
secax.set_ylabel('Sea level contribution anomaly (mm)')

ax[0].set_yticks([0, -100000, -200000, -300000, -400000]) 
ax[0].set_yticklabels(['0', '-100,000', '-200,000', '-300,000', '-400,000']) 
ax[1].set_yticks([0, 20000, 40000, 60000, 80000, 100000]) 
ax[1].set_yticklabels(['0', '20,000', '40,000', '60,000', '80,000', '100,000']) 

ax[1].set_xlabel('Years')

handles, labels = ax[0].get_legend_handles_labels()

handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashed'))
handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashdot'))
labels.append('Dn4-X')
labels.append('Dn8-X')

ax[0].legend(handles, labels, loc = 'best', prop={'size': 5})

ax[0].annotate('a)', xy=(0, 1), xycoords='axes fraction', xytext=(+1.0, -1.2), textcoords='offset fontsize', ha='center', fontsize=9)
ax[1].annotate('b)', xy=(0, 1), xycoords='axes fraction', xytext=(+1.0, -1.2), textcoords='offset fontsize', ha='center', fontsize=9)

print("Finished and saving AIS Vaf/Vol Anom vs Time plot...")

plt.savefig('TestAISVafVolAnomvsTime.png', dpi = 600,  bbox_inches='tight')  
'''
