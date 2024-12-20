####################################################################################
# Imports

import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt

####################################################################################

id = ["cs568", "cx209", "cy837", "cy838", "cz375", "cz376", "cz377", "dc052", "dc051", "df028", "dc123", "dc130"]

run_type = ["PI-Control","Ramp-Up", "1.5C Stab", "2C Stab", "3C Stab", "4C Stab", "5C Stab", "_Ramp-Down 1.5C", "_Ramp-Down 2C", "_Ramp-Down 3C", "_Ramp-Down 4C", "_Ramp-Down 5C"]

runs = dict(zip(id, run_type)) 

line_cols = ['#000000','#C30F0E','#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0','#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0']
line_stys = ["dotted","solid","solid","solid","solid","solid","solid","dashed","dashed","dashed","dashed","dashed"]

####################################################################################

# Read ice sheet data

print("Loading ice sheet data from file...")

with open('../processed_data/AIS_basins_data.pkl', 'rb') as file:

    icesheet_d = pickle.load(file)

####################################################################################

# function for smoothing time series for plotting

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='valid')
    return y_smooth

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

    AIS_data = plot_data[0].iloc[:,47] + plot_data[0].iloc[:,39]

    plt.plot(plot_data[0].iloc[:,2] - 1850, (AIS_data)/1e15, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

#plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])

plt.ylabel("AIS volume (10$^{6}$ km$^{3}$)")
plt.xlabel('Years')
plt.legend(loc = 'best', prop={'size': 5})

ax = plt.gca()
secax = ax.secondary_yaxis('right', functions=(vol2sle, sle2vol))
secax.set_ylabel('Equivalent SLR (m)')

#ax.text(0.98, 0.94, 'b)',
#        horizontalalignment='right',
#        verticalalignment='center',
#        transform=ax.transAxes,
#        size=8)

print("Finished and saving AIS Volume vs Time plot...")

plt.savefig('AISVolvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################


# Plot VAF vs Time graph

print("Starting AIS VAF vs Time plot...")

box_size = 11

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    AIS_data = plot_data[0].iloc[:,55]
    
    initialVAF = icesheet_d["cx209"][0].iloc[0,55]
    initialVAFpi = icesheet_d["cs568"][0].iloc[0,55]

    if i == "cs568":
        
        plt.plot(plot_data[0].iloc[:,2] - 1850, (AIS_data - initialVAFpi)*(918*1000/(1028*3.625e14)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)

        ma_y = smooth((AIS_data - initialVAFpi)*(918*1000/(1028*3.625e14)), box_size)
    
        ma_x = (plot_data[0].iloc[:,2] - 1850).values
        ma_x = ma_x[int((box_size-1)/2):]
        ma_x = ma_x[:-int((box_size-1)/2)]
    
        plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    else:
        
        plt.plot(plot_data[0].iloc[:,2] - 1850, (AIS_data - initialVAF)*(918*1000/(1028*3.625e14)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)

        ma_y = smooth((AIS_data - initialVAF)*(918*1000/(1028*3.625e14)), box_size)
    
        ma_x = (plot_data[0].iloc[:,2] - 1850).values
        ma_x = ma_x[int((box_size-1)/2):]
        ma_x = ma_x[:-int((box_size-1)/2)]
    
        plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

ax = plt.gca()
ax.set_xlim([0, 650])

#plt.grid(linestyle=':')

plt.ylabel("$\Delta$VAF (mm SLE)")
plt.xlabel('Years')
plt.title("Antarctica")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving AIS VAF vs Time plot...")

plt.savefig('AISVAFvsTime.png', dpi = 600,  bbox_inches='tight')

####################################################################################

# Plot VAF vs Time graph

print("Starting EAIS VAF vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    EAIS_data = plot_data[1].iloc[:,55] + plot_data[2].iloc[:,55] + plot_data[3].iloc[:,55] + plot_data[4].iloc[:,55] + plot_data[5].iloc[:,55] + plot_data[6].iloc[:,55] + plot_data[7].iloc[:,55] + plot_data[16].iloc[:,55]
    
    initialVAF = icesheet_d["cx209"][1].iloc[0,55] + icesheet_d["cx209"][2].iloc[0,55] + icesheet_d["cx209"][3].iloc[0,55] + icesheet_d["cx209"][4].iloc[0,55] + icesheet_d["cx209"][5].iloc[0,55] + icesheet_d["cx209"][6].iloc[0,55] + icesheet_d["cx209"][7].iloc[0,55] + icesheet_d["cx209"][16].iloc[0,55]
    initialVAFpi = icesheet_d["cs568"][1].iloc[0,55] + icesheet_d["cs568"][2].iloc[0,55] + icesheet_d["cs568"][3].iloc[0,55] + icesheet_d["cs568"][4].iloc[0,55] + icesheet_d["cs568"][5].iloc[0,55] + icesheet_d["cs568"][6].iloc[0,55] + icesheet_d["cs568"][7].iloc[0,55] + icesheet_d["cs568"][16].iloc[0,55]
    
    if i == "cs568":
        
        plt.plot(plot_data[0].iloc[:,2] - 1850, (EAIS_data - initialVAFpi)*(918*1000/(1028*3.625e14)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)

        ma_y = smooth((EAIS_data - initialVAFpi)*(918*1000/(1028*3.625e14)), box_size)
    
        ma_x = (plot_data[0].iloc[:,2] - 1850).values
        ma_x = ma_x[int((box_size-1)/2):]
        ma_x = ma_x[:-int((box_size-1)/2)]
    
        plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    else:
        
        plt.plot(plot_data[0].iloc[:,2] - 1850, (EAIS_data - initialVAF)*(918*1000/(1028*3.625e14)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)

        ma_y = smooth((EAIS_data - initialVAF)*(918*1000/(1028*3.625e14)), box_size)
    
        ma_x = (plot_data[0].iloc[:,2] - 1850).values
        ma_x = ma_x[int((box_size-1)/2):]
        ma_x = ma_x[:-int((box_size-1)/2)]
    
        plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

ax = plt.gca()
ax.set_xlim([0, 650])

plt.grid(linestyle=':')

plt.ylabel("$\Delta$VAF (mm SLE)")
plt.xlabel('Years')
plt.title("East Antarctica")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving EAIS VAF vs Time plot...")

plt.savefig('EAISVAFvsTime.png', dpi = 600,  bbox_inches='tight')  

####################################################################################

# Plot VAF vs Time graph

print("Starting Ross VAF vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    Ross_data = plot_data[8].iloc[:,55]

    initialVAF = icesheet_d["cx209"][8].iloc[0,55]
    initialVAFpi = icesheet_d["cs568"][8].iloc[0,55]
    
    if i == "cs568":
        
        plt.plot(plot_data[0].iloc[:,2] - 1850, (Ross_data - initialVAFpi)*(918*1000/(1028*3.625e14)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)

        ma_y = smooth((Ross_data - initialVAFpi)*(918*1000/(1028*3.625e14)), box_size)
    
        ma_x = (plot_data[0].iloc[:,2] - 1850).values
        ma_x = ma_x[int((box_size-1)/2):]
        ma_x = ma_x[:-int((box_size-1)/2)]
    
        plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    else:
        
        plt.plot(plot_data[0].iloc[:,2] - 1850, (Ross_data - initialVAF)*(918*1000/(1028*3.625e14)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)

        ma_y = smooth((Ross_data - initialVAF)*(918*1000/(1028*3.625e14)), box_size)
    
        ma_x = (plot_data[0].iloc[:,2] - 1850).values
        ma_x = ma_x[int((box_size-1)/2):]
        ma_x = ma_x[:-int((box_size-1)/2)]
    
        plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])

plt.grid(linestyle=':')

plt.ylabel("$\Delta$VAF (mm SLE)")
plt.xlabel('Years')
plt.title("Ross")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving Ross VAF vs Time plot...")

plt.savefig('RossVAFvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot VAF vs Time graph

print("Starting WAIS VAF vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    WAIS_data = plot_data[9].iloc[:,55] + plot_data[10].iloc[:,55] + plot_data[11].iloc[:,55] + plot_data[12].iloc[:,55]

    initialVAF = icesheet_d["cx209"][9].iloc[0,55] + icesheet_d["cx209"][10].iloc[0,55] + icesheet_d["cx209"][11].iloc[0,55] + icesheet_d["cx209"][12].iloc[0,55]
    initialVAFpi = icesheet_d["cs568"][9].iloc[0,55] + icesheet_d["cs568"][10].iloc[0,55] + icesheet_d["cs568"][11].iloc[0,55] + icesheet_d["cs568"][12].iloc[0,55]
    
    if i == "cs568":
        
        plt.plot(plot_data[0].iloc[:,2] - 1850, (WAIS_data - initialVAFpi)*(918*1000/(1028*3.625e14)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)

        ma_y = smooth((WAIS_data - initialVAFpi)*(918*1000/(1028*3.625e14)), box_size)
    
        ma_x = (plot_data[0].iloc[:,2] - 1850).values
        ma_x = ma_x[int((box_size-1)/2):]
        ma_x = ma_x[:-int((box_size-1)/2)]
    
        plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    else:
        
        plt.plot(plot_data[0].iloc[:,2] - 1850, (WAIS_data - initialVAF)*(918*1000/(1028*3.625e14)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)

        ma_y = smooth((WAIS_data - initialVAF)*(918*1000/(1028*3.625e14)), box_size)
    
        ma_x = (plot_data[0].iloc[:,2] - 1850).values
        ma_x = ma_x[int((box_size-1)/2):]
        ma_x = ma_x[:-int((box_size-1)/2)]
    
        plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])

plt.ylabel("$\Delta$VAF (mm SLE)")
plt.xlabel('Years')
plt.title("West Antarctica")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving WAIS VAF vs Time plot...")

plt.savefig('WAISVAFvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot VAF vs Time graph

print("Starting FRIS VAF vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    FRIS_data = plot_data[15].iloc[:,55]

    initialVAF = icesheet_d["cx209"][15].iloc[0,55]
    initialVAFpi = icesheet_d["cs568"][15].iloc[0,55]
    
    if i == "cs568":
        
        plt.plot(plot_data[0].iloc[:,2] - 1850, (FRIS_data - initialVAFpi)*(918*1000/(1028*3.625e14)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)

        ma_y = smooth((FRIS_data - initialVAFpi)*(918*1000/(1028*3.625e14)), box_size)
    
        ma_x = (plot_data[0].iloc[:,2] - 1850).values
        ma_x = ma_x[int((box_size-1)/2):]
        ma_x = ma_x[:-int((box_size-1)/2)]
    
        plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    else:
        
        plt.plot(plot_data[0].iloc[:,2] - 1850, (FRIS_data - initialVAF)*(918*1000/(1028*3.625e14)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)

        ma_y = smooth((FRIS_data - initialVAF)*(918*1000/(1028*3.625e14)), box_size)
    
        ma_x = (plot_data[0].iloc[:,2] - 1850).values
        ma_x = ma_x[int((box_size-1)/2):]
        ma_x = ma_x[:-int((box_size-1)/2)]
    
        plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])

plt.ylabel("$\Delta$VAF (mm SLE)")
plt.xlabel('Years')
plt.title("Filchner-Ronne")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving FRIS VAF vs Time plot...")

plt.savefig('FRISVAFvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot GroundedSMB vs Time graph

print("Starting AIS Grounded SMB vs Time plot...")

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    AIS_data = plot_data[0].iloc[:,7]

    plt.plot(plot_data[0].iloc[:,2] - 1850, ((AIS_data)*(0.918/1e9)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)
    
    ma_y = smooth((AIS_data)*(0.918/1e9), box_size)
    
    ma_x = (plot_data[0].iloc[:,2] - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    
    count = count + 1

#plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])

plt.ylabel("Grounded SMB (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.title("Antarctica")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving AIS Grounded SMB vs Time plot...")

plt.savefig('UpdatedAISGroundedSMBvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot GroundedSMB vs Time graph

print("Starting EAIS Grounded SMB vs Time plot...")

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    EAIS_data = plot_data[1].iloc[:,7] + plot_data[2].iloc[:,7] + plot_data[3].iloc[:,7] + plot_data[4].iloc[:,7] + plot_data[5].iloc[:,7] + plot_data[6].iloc[:,7] + plot_data[7].iloc[:,7] + plot_data[16].iloc[:,7]

    plt.plot(plot_data[0].iloc[:,2] - 1850, ((EAIS_data)/918e6), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)
    
    ma_y = smooth((EAIS_data)/918e6, box_size)
    
    ma_x = (plot_data[0].iloc[:,2] - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    
    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])

plt.ylabel("Grounded SMB (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.title("East Antarctica")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving EAIS Grounded SMB vs Time plot...")

plt.savefig('EAISGroundedSMBvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot GroundedSMB vs Time graph

print("Starting Ross Grounded SMB vs Time plot...")

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    Ross_data = plot_data[8].iloc[:,7]

    plt.plot(plot_data[0].iloc[:,2] - 1850, ((Ross_data)/918e6), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)
    
    ma_y = smooth((Ross_data)/918e6, box_size)
    
    ma_x = (plot_data[0].iloc[:,2] - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    
    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])

plt.ylabel("Grounded SMB (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.title("Ross")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving Ross Grounded SMB vs Time plot...")

plt.savefig('RossGroundedSMBvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot GroundedSMB vs Time graph

print("Starting WAIS Grounded SMB vs Time plot...")

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    WAIS_data = plot_data[9].iloc[:,7] + plot_data[10].iloc[:,7] + plot_data[11].iloc[:,7] + plot_data[12].iloc[:,7]

    plt.plot(plot_data[0].iloc[:,2] - 1850, ((WAIS_data)/918e6), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)
    
    ma_y = smooth((WAIS_data)/918e6, box_size)
    
    ma_x = (plot_data[0].iloc[:,2] - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    
    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])

plt.ylabel("Grounded SMB (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.title("West Antarctica")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving WAIS Grounded SMB vs Time plot...")

plt.savefig('WAISGroundedSMBvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot GroundedSMB vs Time graph

print("Starting FRIS Grounded SMB vs Time plot...")

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    FRIS_data = plot_data[15].iloc[:,7]

    plt.plot(plot_data[0].iloc[:,2] - 1850, (FRIS_data)*(0.918/1e9), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)
    
    ma_y = smooth((FRIS_data)/918e6, box_size)
    
    ma_x = (plot_data[0].iloc[:,2] - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    
    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])

plt.ylabel("Grounded SMB (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.title("Filchner-Ronne")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving FRIS Grounded SMB vs Time plot...")

plt.savefig('FRISGroundedSMBvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight') 

####################################################################################

# Plot Discharge vs Time graph

print("Starting AIS Grounding Line Discharge vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    AIS_data = plot_data[0].iloc[:,31]

    plt.plot(plot_data[0].iloc[:,2] - 1850, ((AIS_data)*(0.918/1e9)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)

    ma_y = smooth(((AIS_data)*(0.918/1e9)), box_size)
    
    ma_x = (plot_data[0].iloc[:,2] - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

#plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])

plt.ylabel("GL Discharge (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.title("Antarctica")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving AIS Grounding Line Discharge vs Time plot...")

plt.savefig('AISGLDischargevsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot Discharge vs Time graph

print("Starting EAIS Grounding Line Discharge vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    EAIS_data = plot_data[1].iloc[:,31] + plot_data[2].iloc[:,31] + plot_data[3].iloc[:,31] + plot_data[4].iloc[:,31] + plot_data[5].iloc[:,31] + plot_data[6].iloc[:,31] + plot_data[7].iloc[:,31] + plot_data[16].iloc[:,31]

    plt.plot(plot_data[0].iloc[:,2] - 1850, ((EAIS_data)*(0.918/1e9)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)

    ma_y = smooth(((EAIS_data)*(0.918/1e9)), box_size)
    
    ma_x = (plot_data[0].iloc[:,2] - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])

plt.ylabel("GL Discharge (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.title("East Antarctica")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving EAIS Grounding Line Discharge vs Time plot...")

plt.savefig('EAISGLDischargevsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot Discharge vs Time graph

print("Starting Ross Grounding Line Discharge vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    Ross_data = plot_data[8].iloc[:,31]

    plt.plot(plot_data[0].iloc[:,2] - 1850, ((Ross_data)*(0.918/1e9)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)

    ma_y = smooth(((Ross_data)*(0.918/1e9)), box_size)
    
    ma_x = (plot_data[0].iloc[:,2] - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])

plt.ylabel("GL Discharge (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.title("Ross")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving Ross Grounding Line Discharge vs Time plot...")

plt.savefig('RossGLDischargevsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')  

####################################################################################

# Plot Discharge vs Time graph

print("Starting WAIS Grounding Line Discharge vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    WAIS_data = plot_data[9].iloc[:,31] + plot_data[10].iloc[:,31] + plot_data[11].iloc[:,31] + plot_data[12].iloc[:,31]
    
    plt.plot(plot_data[0].iloc[:,2] - 1850, ((WAIS_data)*(0.918/1e9)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)

    ma_y = smooth(((WAIS_data)*(0.918/1e9)), box_size)
    
    ma_x = (plot_data[0].iloc[:,2] - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])

plt.ylabel("GL Discharge (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.title("West Antarctica")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving WAIS Grounding Line Discharge vs Time plot...")

plt.savefig('WAISGLDischargevsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')    

####################################################################################

# Plot Discharge vs Time graph

print("Starting FRIS Grounding Line Discharge vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    FRIS_data = plot_data[15].iloc[:,31]

    plt.plot(plot_data[0].iloc[:,2] - 1850, ((FRIS_data)*(0.918/1e9)), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)

    ma_y = smooth(((FRIS_data)*(0.918/1e9)), box_size)
    
    ma_x = (plot_data[0].iloc[:,2] - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])

plt.ylabel("GL Discharge (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.title("Filchner-Ronne")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving FRIS Grounding Line Discharge vs Time plot...")

plt.savefig('FRISGLDischargevsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')  

####################################################################################

# Plot FloatingBMB vs Time graph

print("Starting AIS Floating BMB vs Time plot...")

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    AIS_data = plot_data[0].iloc[:,23]

    #plt.plot(plot_data[0].iloc[:,2] - 1850, ((AIS_data)/918e6), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)
    
    ma_y = smooth((AIS_data)*(0.918/1e9), box_size)
    
    ma_x = (plot_data[0].iloc[:,2] - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    
    count = count + 1

#plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])

plt.ylabel("Floating BMB (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.title("Antarctica")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving AIS Floating BMB vs Time plot...")

plt.savefig('UpdatedAISFloatingBMBvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot FloatingBMB vs Time graph

print("Starting EAIS Floating BMB vs Time plot...")

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    EAIS_data = plot_data[1].iloc[:,23] + plot_data[2].iloc[:,23] + plot_data[3].iloc[:,23] + plot_data[4].iloc[:,23] + plot_data[5].iloc[:,23] + plot_data[6].iloc[:,23] + plot_data[7].iloc[:,23] + plot_data[16].iloc[:,23]

    #plt.plot(plot_data[0].iloc[:,2] - 1850, ((EAIS_data)/918e6), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)
    
    ma_y = smooth((EAIS_data)/918e6, box_size)
    
    ma_x = (plot_data[0].iloc[:,2] - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    
    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])

plt.ylabel("Floating BMB (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.title("East Antarctica")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving EAIS Floating BMB vs Time plot...")

plt.savefig('EAISFloatingBMBvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot FloatingBMB vs Time graph

print("Starting Ross Floating BMB vs Time plot...")

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    Ross_data = plot_data[8].iloc[:,23]

    #plt.plot(plot_data[0].iloc[:,2] - 1850, ((Ross_data)/918e6), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)
    
    ma_y = smooth((Ross_data)/918e6, box_size)
    
    ma_x = (plot_data[0].iloc[:,2] - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    
    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])

plt.ylabel("Floating BMB (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.title("Ross")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving Ross Floating BMB vs Time plot...")

plt.savefig('RossFloatingBMBvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot FloatingBMB vs Time graph

print("Starting WAIS Floating BMB vs Time plot...")

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    WAIS_data = plot_data[9].iloc[:,23] + plot_data[10].iloc[:,23] + plot_data[11].iloc[:,23] + plot_data[12].iloc[:,23]

    #plt.plot(plot_data[0].iloc[:,2] - 1850, ((WAIS_data)/918e6), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)
    
    ma_y = smooth((WAIS_data)/918e6, box_size)
    
    ma_x = (plot_data[0].iloc[:,2] - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    
    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])

plt.ylabel("Floating BMB (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.title("West Antarctica")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving WAIS Floating BMB vs Time plot...")

plt.savefig('WAISFloatingBMBvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot FloatingBMB vs Time graph

print("Starting FRIS Floating BMB vs Time plot...")

count = 0

box_size = 11

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    FRIS_data = plot_data[15].iloc[:,23]

    #plt.plot(plot_data[0].iloc[:,2] - 1850, ((FRIS_data)/918e6), label = '_none', lw=0.8, color = line_cols[count], linestyle = line_stys[count], alpha = 0.05)
    
    ma_y = smooth((FRIS_data)/918e6, box_size)
    
    ma_x = (plot_data[0].iloc[:,2] - 1850).values
    ma_x = ma_x[int((box_size-1)/2):]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    
    count = count + 1

plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])

plt.ylabel("Floating BMB (Gt yr$^{-1}$)")
plt.xlabel('Years')
plt.title("Filchner-Ronne")
plt.legend(loc = 'best', prop={'size': 5})

print("Finished and saving FRIS Floating BMB vs Time plot...")

plt.savefig('FRISFloatingBMBvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('AISMassvsTime.png', dpi = 600,  bbox_inches='tight') 
