####################################################################################
# Imports
import numpy as np
import pickle
import matplotlib.pyplot as plt

####################################################################################

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

####################################################################################

# Read ice sheet data
#with open('../processed_data/AIS_basins_data.pkl', 'rb') as file:

#    icesheet_d = pickle.load(file)

with open('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/AIS_basins_data.pkl', 'rb') as file:
    icesheet_d = pickle.load(file)

icesheet_d["dc051"][0] = icesheet_d["dc051"][0].reindex(icesheet_d["dc051"][0].index.tolist() + [186.5])
icesheet_d["dc051"][0] = icesheet_d["dc051"][0].sort_index().reset_index(drop=True)
icesheet_d["dc051"][0].iloc[:,[2,8,61]] = icesheet_d["dc051"][0].iloc[:,[2,8,61]].interpolate(method='linear')

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
    return x*(-1)/361.8

def sle2mass(x):
    return x*(-1)*361.8

plt.rcParams.update({'font.size': 7.5})

####################################################################################

# Plot global T vs Time graph

print("Starting Global Temp vs Time plot...")

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i][0]
    time_series = plot_data.iloc[:,2]
    temp_series = plot_data.iloc[:,8]
    
    #plt.plot(plot_data[:,0]-1851, plot_data[:,1]-initialT, label = runs[i], lw=0.8, linestyle=line_stys[count], color=line_cols[count])
    plt.plot(time_series-1850, temp_series, label = "_none", lw=0.8, linestyle="solid", color=line_cols[count], alpha=0.25)
    
    ma_y = smooth(temp_series, box_size)
    
    ma_x = time_series
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x-1850, ma_y, label = runs[i], lw=0.8, linestyle=line_stys[count], color=line_cols[count])

    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()

plt.ylabel('Global Mean T (K)')
plt.xlabel('Years')
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving Global Temp vs Time plot...")

plt.savefig('GlobalTvsTime.png', dpi = 600, bbox_inches='tight')

####################################################################################

# Plot global T vs Time anomaly graph

print("Starting Global Temp vs Time anomaly plot...")

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

ctrl_data = icesheet_d["cs568"][0]
pi_T = ctrl_data.loc[0:50,'global_T'].mean()[0]

for i in idanom:

    plot_data = icesheet_d[i][0]
    time_series = plot_data.iloc[:,2]
    temp_series = plot_data.iloc[:,8]
    
    #plt.plot(plot_data[:,0]-1851, plot_data[:,1]-initialT, label = runs[i], lw=0.8, linestyle=line_stys[count], color=line_cols[count])
    plt.plot(time_series-1850, temp_series-pi_T, label = "_none", lw=0.8, linestyle="solid", color=line_cols_anom[count], alpha=0.25)
    
    ma_y = smooth(temp_series, box_size)
    
    ma_x = time_series
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x-1850, ma_y-pi_T, label = runs_anom[i], lw=0.8, linestyle=line_stys_anom[count], color=line_cols_anom[count])

    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()

plt.ylabel('Global Mean $\Delta$T (K)')
plt.xlabel('Years')
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving Global Temp Anomaly vs Time plot...")

plt.savefig('GlobalTAnomvsTime.png', dpi = 600, bbox_inches='tight')

####################################################################################

# Plot VAF vs Time graph

print("Starting AIS VAF vs Time plot...")

initialVAF = icesheet_d["cx209"][0].iloc[0,61]
initialVAFpi = icesheet_d["cs568"][0].iloc[0,61]

count = 0

plt.figure(figsize=(4, 3))

ctrl_data = icesheet_d["cs568"][0]
pi_VAF = ctrl_data.iloc[:,61]

for i in id:

    plot_data = icesheet_d[i][0]

    VAF_data = plot_data.iloc[:,61]
    time_series = plot_data.iloc[:,2]

    if i == "cs568":
        
        plt.plot(time_series - 1850, (VAF_data - initialVAFpi)*(0.918/1e9), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    else:
        
        plt.plot(time_series - 1850, (VAF_data - initialVAF)*(0.918/1e9), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

ax = plt.gca()

plt.grid(linestyle=':')

ax.set_yticks([0, -20000, -40000, -60000, -80000, -100000]) 
ax.set_yticklabels(['0', '-20,000', '-40,000', '-60,000', '-80,000', '-100,000']) 

plt.ylabel("Mass change (Gt)")
plt.xlabel('Years')
plt.legend(loc = 'best', prop={'size': 5})

# Add a second y-axis for sea level equivalent
ax = plt.gca()
secax = ax.secondary_yaxis('right', functions=(mass2sle, sle2mass)) 
secax.set_ylabel('Sea level contribution (mm)')

print("Finished and saving AIS VAF vs Time plot...")

plt.savefig('AISVAFvsTime.png', dpi = 600,  bbox_inches='tight')

####################################################################################

# Plot VAF Anom vs Time graph

print("Starting AIS VAF Anom vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

ctrl_data = icesheet_d["cs568"][0]


for i in idanom:

    plot_data = icesheet_d[i][0]
    
    pi_VAF = ctrl_data.iloc[:,61]
    pi_time_series = ctrl_data.iloc[:,2]

    VAF_data = plot_data.iloc[:,61]
    time_series = plot_data.iloc[:,2]
    
    if max(time_series) > max(pi_time_series):

        start_year =  min(time_series)
        end_year = max(pi_time_series)

        pi_VAF = pi_VAF[(pi_time_series >= start_year) & (pi_time_series <= end_year)].reset_index(drop=True)
        VAF_data = VAF_data[(time_series >= start_year) & (time_series <= end_year)]
        time_series = time_series[(time_series >= start_year) & (time_series <= end_year)]

    elif max(time_series) < max(pi_time_series):

        start_year =  min(time_series)
        end_year = max(time_series)

        pi_VAF = pi_VAF[(pi_time_series >= start_year) & (pi_time_series <= end_year)].reset_index(drop=True)

    else:
        
        pass
        

    plt.plot(time_series - 1850, ((VAF_data - initialVAF) - (pi_VAF - initialVAFpi))*(0.918/1e9), label = runs_anom[i], lw=0.8, color = line_cols_anom[count], linestyle = line_stys_anom[count])

    count = count + 1

ax = plt.gca()

plt.grid(linestyle=':')

ax.set_yticks([0, 20000, 40000, 60000, 80000, 100000]) 
ax.set_yticklabels(['0', '20,000', '40,000', '60,000', '80,000', '100,000']) 

plt.ylabel("Mass change anomaly (Gt)")
plt.xlabel('Years')
plt.legend(loc = 'best', prop={'size': 5})

# Add a second y-axis for sea level equivalent
ax = plt.gca()
secax = ax.secondary_yaxis('right', functions=(mass2sle, sle2mass)) 
secax.set_ylabel('Sea level contribution anomaly (mm)')

print("Finished and saving AIS VAF vs Time plot...")

plt.savefig('AISVAFAnomvsTime.png', dpi = 600,  bbox_inches='tight')


####################################################################################

# Plot Grounded volume vs Time graph

print("Starting AIS Grounded Volume vs Time plot...")

initialVAF = icesheet_d["cx209"][0].iloc[0,43]
initialVAFpi = icesheet_d["cs568"][0].iloc[0,43]

count = 0

plt.figure(figsize=(4, 3))

ctrl_data = icesheet_d["cs568"][0]
pi_VAF = ctrl_data.iloc[:,43]

for i in id:

    plot_data = icesheet_d[i][0]

    VAF_data = plot_data.iloc[:,43]
    time_series = plot_data.iloc[:,2]

    if i == "cs568":
        
        plt.plot(time_series - 1850, (VAF_data - initialVAFpi)*(0.918/1e9), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    else:
        
        plt.plot(time_series - 1850, (VAF_data - initialVAF)*(0.918/1e9), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

ax = plt.gca()

plt.grid(linestyle=':')

#ax.set_yticks([0, -20000, -40000, -60000, -80000, -100000]) 
#ax.set_yticklabels(['0', '-20,000', '-40,000', '-60,000', '-80,000', '-100,000']) 

plt.ylabel("Mass change (Gt)")
plt.xlabel('Years')
plt.legend(loc = 'best', prop={'size': 5})

# Add a second y-axis for sea level equivalent
ax = plt.gca()
secax = ax.secondary_yaxis('right', functions=(mass2sle, sle2mass)) 
secax.set_ylabel('Sea level contribution (mm)')

print("Finished and saving AIS VAF vs Time plot...")

plt.savefig('AISGroundedVolvsTime.png', dpi = 600,  bbox_inches='tight')


####################################################################################

# Plot Floating volume vs Time graph

print("Starting AIS Floating Volume vs Time plot...")

initialVAF = icesheet_d["cx209"][0].iloc[0,52]
initialVAFpi = icesheet_d["cs568"][0].iloc[0,52]

count = 0

plt.figure(figsize=(4, 3))

ctrl_data = icesheet_d["cs568"][0]
pi_VAF = ctrl_data.iloc[:,52]

for i in id:

    plot_data = icesheet_d[i][0]

    VAF_data = plot_data.iloc[:,52]
    time_series = plot_data.iloc[:,2]

    if i == "cs568":
        
        plt.plot(time_series - 1850, (VAF_data - initialVAFpi)*(0.918/1e9), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    else:
        
        plt.plot(time_series - 1850, (VAF_data - initialVAF)*(0.918/1e9), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

ax = plt.gca()

plt.grid(linestyle=':')

#ax.set_yticks([0, -20000, -40000, -60000, -80000, -100000]) 
#ax.set_yticklabels(['0', '-20,000', '-40,000', '-60,000', '-80,000', '-100,000']) 

plt.ylabel("Mass change (Gt)")
plt.xlabel('Years')
plt.legend(loc = 'best', prop={'size': 5})

# Add a second y-axis for sea level equivalent
ax = plt.gca()
secax = ax.secondary_yaxis('right', functions=(mass2sle, sle2mass)) 
secax.set_ylabel('Sea level contribution (mm)')

print("Finished and saving AIS VAF vs Time plot...")

plt.savefig('AISFloatingVolvsTime.png', dpi = 600,  bbox_inches='tight')

####################################################################################

# Plot SMB (grounded and floating) vs Time graph

print("Starting AIS SMB vs Time plot...")

count = 0

box_size = 21

plt.figure(figsize=(4, 3))

fig, ax = plt.subplots(2, sharex='col', sharey='row')

for i in id:

    plot_data = icesheet_d[i][0]

    AIS_data_gr = plot_data.iloc[:,7]
    AIS_data_fl = plot_data.iloc[:,16]

    ax[0].plot(plot_data.iloc[:,2] - 1850, ((AIS_data_gr)*(0.918/1e9)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.1)
    ax[1].plot(plot_data.iloc[:,2] - 1850, ((AIS_data_fl)*(0.918/1e9)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.1)
    
    ma_y_gr = smooth((AIS_data_gr)*(0.918/1e9), box_size)
    ma_y_fl = smooth((AIS_data_fl)*(0.918/1e9), box_size)
    
    ma_x = (plot_data.iloc[:,2] - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    ax[0].plot(ma_x, ma_y_gr, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    ax[1].plot(ma_x, ma_y_fl, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    
    count = count + 1

ax[0].grid(linestyle='-', lw=0.2)
ax[1].grid(linestyle=':', lw=0.2)

ax[0].set_xlim([0, 750])
ax[1].set_xlim([0, 750])

ax[0].set_ylabel("Grounded SMB (Gt yr$^{-1}$)")
ax[1].set_ylabel("Floating SMB (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving AIS SMB vs Time plot...")

plt.savefig('TestAISSMBvsTime.png', dpi = 600,  bbox_inches='tight')  


####################################################################################

# Plot SMB (grounded and floating) Anomaly vs Time graph