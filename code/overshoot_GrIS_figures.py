####################################################################################
# Imports
import cf
import cfplot as cfp
import pandas as pd
import os
import fnmatch
import numpy as np
import pickle

import matplotlib.pyplot as plt
import matplotlib.colors as col
import matplotlib.patches as pat

"""from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation 
from IPython import display

from amrfile import io as amrio"""

####################################################################################

# Read atmosphere data

#id = ["cs568", "cx209", "cy837", "cy838", "cz374", "cz375", "cz376", "cz377", 
#      "cz378", "cz944", "da800", "da697", "da892", "db223", "dc251", "dc051", 
#      "dc052", "dc248", "dc249", "dc565", "dd210", "dc032", "dc123", "dc130"]

id = ["cs568", "cx209", "cy837", "cy838", "cz375", "cz376", "cz377", "dc052", "dc051", "df028", "dc123", "dc130"]

#run_type = ["pi-ctrl","ramp-up", "stab 1.5C", "stab 2C", "stab 2.5C", "stab 3C", "stab 4C", "stab 5C", 
#           "stab 6C", "_ramp-down -8 2C 50yr", "_ramp-down -8 2C 200yr", "_ramp-down -8 1.5C 50yr", "_ramp-down -8 4C 50yr", "_ramp-down -8 3C 50yr", "_ramp-down -8 5C 50yr", "_ramp-down -4 2C 50yr",
#           "_ramp-down -4 1.5C 50yr", "_ramp-down -4 1.5C 200yr", "_ramp-down -4 3C 200yr", "_ramp-down -4 2C 200yr", "_ramp-down -4 4C 200yr", "_ramp-down -4 3C 30yr", "_ramp-down -4 4C 50yr", "_ramp-down -4 5C 50yr"]

#run_type = ["pi-ctrl","ramp-up", "stab 1.5C", "stab 2C", "stab 2.5C", "stab 3C", "stab 4C", "stab 5C", 
#            "stab 6C", "ramp-down -8 2C 50yr", "ramp-down -8 2C 200yr", "ramp-down -8 1.5C 50yr", "ramp-down -8 4C 50yr", "ramp-down -8 3C 50yr", "ramp-down -8 5C 50yr", "ramp-down -4 2C 50yr",
#            "ramp-down -4 1.5C 50yr", "ramp-down -4 1.5C 200yr", "ramp-down -4 3C 200yr", "ramp-down -4 2C 200yr", "ramp-down -4 4C 200yr", "ramp-down -4 3C 30yr", "ramp-down -4 4C 50yr", "ramp-down -4 5C 50yr"]

run_type = ["PI-Control","Ramp-Up", "1.5C Stab", "2C Stab", "3C Stab", "4C Stab", "5C Stab", "Ramp-Down 1.5C", "Ramp-Down 2C", "Ramp-Down 3C", "Ramp-Down 4C", "Ramp-Down 5C"]

runs = dict(zip(id, run_type)) 

#             pi     ru     1.5        2    2.5   3    4       5             6      rd2  rd2      rd1.5    rd4   rd3     rd5       rd2      rd1.5       rd1.5       rd3  rd2  rd4  rd3  rd4       rd5
#line_cols = ["gray","k", "tab:purple", "b", "c", "g", "y", "tab:orange", "tab:red", "b", "b", "tab:purple", "y", "g","tab:orange", "b", "tab:purple", "tab:purple", "g", "b", "y", "g", "y", "tab:orange"]
#line_stys = ["solid","solid","solid","solid","solid","solid","solid","solid","solid","dashed","dashed","dashed","dashed","dashed","dashed","dashed","dashed","dashed","dashed","dashed","dashed","dashed","dashed","dashed"] 

line_cols = ['#000000','#C30F0E','#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0','#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0']
line_stys = ["dotted","solid","solid","solid","solid","solid","solid","dashed","dashed","dashed","dashed","dashed"]

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
        atmos_dir = f"../raw_data/{i}/atmos/"
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

if os.path.exists('../processed_data/icesheet_data_GrIS.pkl'):

    print("Loading ice sheet data from file...")

    with open('../processed_data/icesheet_data_GrIS.pkl', 'rb') as file:

        icesheet_d = pickle.load(file)

else:

    print("Getting ice sheet data...")

    icesheet_d = {}

    for i in id:

        print(f"Working on {i}: {runs[i]}")
        GrIS_stats = pd.read_csv(f"../processed_data/{i}_GrIS_stats.csv")

        if i == "cs568":    
            GrIS_stats.time = GrIS_stats.apply(lambda x: int(x.file[16:20]), axis=1)-100
        else:
            GrIS_stats.time = GrIS_stats.apply(lambda x: int(x.file[16:20]), axis=1)
        
        GrIS_stats["massSLE"] = GrIS_stats["iceVolumeAbove"]*(918/(1028*3.625e14))

        GrIS_stats["global_delta_T"] = np.nan

        count = 0

        for j in atmos_d[i][:,0]:

            year = int(j+1) # because BISICLES stores data for 01/01 of following year...
            print(f"Working on year: {year}")
            pos = np.where(GrIS_stats.time==year)

            if np.size(pos) > 0:
                pos = pos[0][0]
                GrIS_stats.at[pos,"global_delta_T"] = atmos_d[i][count,1]-initialT
            else:
                print(f"Year {year} not found in GrIS data for {i}")

            count = count + 1

        # Interpolate to fill NaN valures in global_delta_T
        GrIS_stats["global_delta_T"].interpolate(method='linear', inplace=True)

        icesheet_d[i] = GrIS_stats

####################################################################################

# Save ice sheet data

if count > 0:

    print("Saving ice sheet data to file...")

    ice_save_file = open('../processed_data/icesheet_data_GrIS.pkl', 'wb') 
    pickle.dump(icesheet_d, ice_save_file) 
    ice_save_file.close()

####################################################################################
"""
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
    
    #plt.plot(plot_data[:,0]-1851, plot_data[:,1]-initialT, label = runs[i], lw=0.8, linestyle=line_stys[count], color=line_cols[count])
    plt.plot(plot_data[:,0]-1850, plot_data[:,1]-initialT, label = "_none", lw=0.8, linestyle="solid", color=line_cols[count], alpha=0.25)
    
    ma_y = smooth(plot_data[:,1], box_size)
    
    ma_x = plot_data[int((box_size-1)/2):,0]
    ma_x = ma_x[:-int((box_size-1)/2)]
    
    plt.plot(ma_x-1850, ma_y-initialT, label = runs[i], lw=0.8, linestyle=line_stys[count], color=line_cols[count])

    count = count + 1

#plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])
ax.set_ylim([-1.5, 8.5])

plt.ylabel('Global Mean $\Delta$T (C)')
plt.xlabel('Years')
plt.legend(loc = 'center left', bbox_to_anchor=(1, 0.5))

print("Finished and saving Global Temp vs Time plot...")

plt.savefig('../figures/GlobalTvsTime.png', dpi = 600, bbox_inches='tight')
#plt.savefig('GlobalTvsTime.png', dpi = 600, bbox_inches='tight')  

####################################################################################

# Plot VAF vs Time graph

initalmassSLE = icesheet_d["cx209"]["massSLE"].iloc[0]
initalmassSLEpi = icesheet_d["cs568"]["massSLE"].iloc[1]

print("Starting GrIS VAF vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    if i == "cs568": 
        plt.plot(plot_data.time - 1850, (plot_data.massSLE-initalmassSLEpi), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    else:
        plt.plot(plot_data.time - 1850, (plot_data.massSLE-initalmassSLE), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

#plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])
ax.set_ylim([-0.9, 0.02])

ax.set_yticks([0, -0.1, -0.2, -0.3, -0.4, -0.5, -0.6, -0.7, -0.8, -0.9]) 
ax.set_yticklabels(['0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9']) 

plt.ylabel("$\Delta$VAF (m SLE)")
plt.xlabel('Years')
plt.legend(loc = 'center left', bbox_to_anchor=(1, 0.5))

print("Finished and saving GrIS VAF vs Time plot...")

plt.savefig('../figures/GrISVAFvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('GrISMassvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot GroundedArea vs Time graph

initalGA = icesheet_d["cx209"]["groundedArea"].iloc[0]
initalGApi = icesheet_d["cs568"]["groundedArea"].iloc[1]

print("Starting GrIS VAF vs Time plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    if i == "cs568": 
        plt.plot(plot_data.time - 1850, (plot_data.groundedArea-initalGApi)/1e6, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
        #plt.plot(plot_data.time - 1850, (plot_data.groundedArea-initalGA)/1e6, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
    else:
        plt.plot(plot_data.time - 1850, (plot_data.groundedArea-initalGA)/1e6, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

#plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([0, 650])
#ax.set_ylim([-0.3, 0.02])

plt.ylabel("$\Delta$ Grounded Area (km$^{2}$)")
plt.xlabel('Years')
plt.legend(loc = 'center left', bbox_to_anchor=(1, 0.5))

print("Finished and saving GrIS Grounded Area vs Time plot...")

plt.savefig('../figures/GrISGAvsTime.png', dpi = 600,  bbox_inches='tight')  
#plt.savefig('GrISGAvsTime.png', dpi = 600,  bbox_inches='tight')   

####################################################################################

# Plot VAF vs global T graph

print("Starting AIS VAF vs Temp plot...")

count = 0

plt.figure(figsize=(4, 3))

for i in id:

    plot_data = icesheet_d[i]

    if i == "cs568":
        plt.plot(plot_data.global_delta_T, (plot_data.massSLE-initalmassSLEpi), label = "_none", lw=0.8,color = line_cols[count], alpha = 0.25)
        
        ma_x = smooth(plot_data.global_delta_T, box_size)
        ma_y = ((plot_data.massSLE-initalmassSLEpi)).values
        ma_y = ma_y[int((box_size-1)/2):]
        ma_y = ma_y[:-int((box_size-1)/2)]
        
        plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
        
    else:
        plt.plot(plot_data.global_delta_T, (plot_data.massSLE-initalmassSLE), label = "_none", lw=0.8,color = line_cols[count], alpha = 0.25)
        
        ma_x = smooth(plot_data.global_delta_T, box_size)
        ma_y = ((plot_data.massSLE-initalmassSLE)).values
        ma_y = ma_y[int((box_size-1)/2):]
        ma_y = ma_y[:-int((box_size-1)/2)]
        
        plt.plot(ma_x, ma_y, label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

#plt.grid(linestyle=':')

ax = plt.gca()
ax.set_xlim([-1.5, 8.5])
ax.set_ylim([-0.9, 0.02])

ax.set_yticks([0, -0.1, -0.2, -0.3, -0.4, -0.5, -0.6, -0.7, -0.8, -0.9])
ax.set_yticklabels(['0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'])

plt.ylabel("$\Delta$VAF (m SLE)")
plt.xlabel('Global Mean $\Delta$T (C)')
plt.legend(loc = 'center left', bbox_to_anchor=(1, 0.5))

print("Finished and saving GrIS VAF vs Temp plot...")

plt.savefig('../figures/GrISVAFvsT.png', dpi = 600, bbox_inches='tight')
#plt.savefig('GrISMassvsT.png', dpi = 600, bbox_inches='tight')


####################################################################################

# Read data from the ramp-up cx209 for mapping

plot_id = "cx209"

print(f"Reading data from {plot_id}...")

# Options for loading BISICLES plot files
level = 0 # the level of refinement on which to load the data (0 = coarsest mesh level)
order = 0 # type of interpolation to perform (0 = piecewise constant, 1 = linear; both are conservative)

directory = f"/home/users/tm17544/gws_terrafirma/overshoots/raw_data/{plot_id}/icesheet/"

files = fnmatch.filter(sorted(os.listdir(directory)), "*GrIS.hdf5")
num_of_h5 = len(fnmatch.filter(os.listdir(directory), "*GrIS.hdf5"))

if num_of_h5 > 1:

    print(f"Found {num_of_h5} files")

    #infile = files[0]
    infile = f"/home/users/tm17544/gws_terrafirma/overshoots/raw_data/cx209/icesheet/bisicles_cx209c_18510101_plot-GrIS.hdf5"

    print(f"Loading data from {infile}")

    #GrISFile = amrio.load(directory + infile)
    GrISFile = amrio.load(infile)
    lo, hi = amrio.queryDomainCorners(GrISFile, level)

    x, y = amrio.readBox2D(GrISFile, level, lo, hi, "thickness", order)[:2]

    var_shape = (y.size, x.size, 2)

    H = np.ndarray(shape=var_shape)
    dHdt = np.ndarray(shape=var_shape)
    B = np.ndarray(shape=var_shape)
    xVel = np.ndarray(shape=var_shape)
    yVel = np.ndarray(shape=var_shape)

    H[:,:,0] = amrio.readBox2D(GrISFile, level, lo, hi, "thickness", order)[2]
    dHdt[:,:,0] = amrio.readBox2D(GrISFile, level, lo, hi, "dThickness/dt", order)[2]
    B[:,:,0] = amrio.readBox2D(GrISFile, level, lo, hi, "Z_base", order)[2]
    xVel[:,:,0] = amrio.readBox2D(GrISFile, level, lo, hi, "xVel", order)[2]
    yVel[:,:,0] = amrio.readBox2D(GrISFile, level, lo, hi, "yVel", order)[2]

    amrio.free(GrISFile)

    infile = files[num_of_h5-1]

    print(f"Loading data from {infile}")

    GrISFile = amrio.load(directory + infile)

    H[:,:,1] = amrio.readBox2D(GrISFile, level, lo, hi, "thickness", order)[2]
    dHdt[:,:,1] = amrio.readBox2D(GrISFile, level, lo, hi, "dThickness/dt", order)[2]
    B[:,:,1] = amrio.readBox2D(GrISFile, level, lo, hi, "Z_base", order)[2]
    xVel[:,:,1] = amrio.readBox2D(GrISFile, level, lo, hi, "xVel", order)[2]
    yVel[:,:,1] = amrio.readBox2D(GrISFile, level, lo, hi, "yVel", order)[2]

    amrio.free(GrISFile)
    

####################################################################################

# Plot total thickness change during ramp-up (map)
print("Starting total thickness change map...")

thklim = col.Normalize(-250,250) # limits for thickness change colormap

fig = plt.figure()

ax = plt.gca()
ax.set_ylim(0.85e6,5.35e6)
ax.set_xlim(0.3e6,5.85e6)
ax.set_aspect('equal', adjustable='box')

H[H==0] = np.NaN

Haf = (-1*B)*(1028/918)
GL = H-Haf
dHdt[np.isnan(H)] = np.NaN

#color and contour plot
fig = plt.pcolormesh(x,y,H[:,:,1]-H[:,:,0],norm=thklim,cmap='coolwarm_r',shading = 'auto')
plt.colorbar(extend="min",shrink=0.9,label="$\Delta H$ (m)")
fig = plt.contour(x,y,GL[:,:,1],[0.1],norm=thklim,colors='black',linewidths=0.6)
fig = plt.contour(x,y,GL[:,:,0],[0.1],norm=thklim,colors='grey',linewidths=0.6)

plt.title(f"Total $\Delta H$ (xx years) {plot_id}")
plt.tick_params(
    axis='both',
    bottom=False,
    left=False,
    labelbottom=False,
    labelleft=False)

print("Finished and saving total thickness change map...")

plt.savefig(f"../figures/GrIS-{plot_id}-totalH-change.png",dpi=600,bbox_inches='tight')

plt.clf()

####################################################################################

# Plot initial ice thickness and velocity if "cx209"

if plot_id == "cx209":

    print("Starting initial thickness and velocity maps...")

    fig = plt.figure()

    ax = plt.gca()
    ax.set_ylim(0.85e6,5.35e6)
    ax.set_xlim(0.3e6,5.85e6)
    ax.set_aspect('equal', adjustable='box')

    H[H==0] = np.NaN

    Haf = (-1*B)*(1028/918)
    GL = H-Haf

    #color and contour plot
    fig = plt.pcolormesh(x,y,H[:,:,0],cmap = 'YlGn', shading = 'auto')
    plt.colorbar(shrink=0.9,label="Ice thickness (m)")
    fig = plt.contour(x,y,GL[:,:,0],[0.1],colors='black',linewidths=0.6)

    plt.tick_params(
        axis='both',
        bottom=False,
        left=False,
        labelbottom=False,
        labelleft=False)

    plt.savefig(f"../figures/GrIS-initial-thickness.png",dpi=600,bbox_inches='tight')

    plt.clf()


    fig = plt.figure()

    spdlim = col.Normalize(0,1000)

    ax = plt.gca()
    ax.set_ylim(0.85e6,5.35e6)
    ax.set_xlim(0.3e6,5.85e6)
    ax.set_aspect('equal', adjustable='box')

    xVel[xVel==0] = np.NaN
    yVel[yVel==0] = np.NaN

    speed = np.sqrt(xVel**2 + yVel**2)

    Haf = (-1*B)*(1028/918)
    GL = H-Haf

    #color and contour plot
    fig = plt.pcolormesh(x,y,speed[:,:,0],norm=spdlim,cmap='Greys',shading = 'auto')
    fig = plt.colorbar(extend="max",shrink=0.9,label="Ice speed (m/yr)")
    fig = plt.contour(x,y,GL[:,:,0],[0.1],colors='black',linewidths=0.6)

    fig = plt.tick_params(
        axis='both',
        bottom=False,
        left=False,
        labelbottom=False,
        labelleft=False)

    plt.savefig(f"../figures/GrIS-initial-speed.png",dpi=600,bbox_inches='tight')

    plt.clf()

    print("Finished and saving initial thickness and velocity maps...")

####################################################################################

# Make animation of dh/dt during the ramp-up (map)

#print("Starting dh/dt animation...")

#thklim = col.Normalize(-2.5,2.5) # limits for thickness change colormap

#fig = plt.figure()
#ax = fig.add_subplot(111)

#ax.set_ylim(0.85e6,5.35e6)
#ax.set_xlim(0.3e6,5.85e6)
#ax.set_aspect('equal', adjustable='box')

#im = ax.pcolormesh(x,y,dHdt[:,:,0],figure=fig, norm=thklim,cmap='bwr_r',shading = 'auto')
#cb = fig.colorbar(im, extend="both",shrink=0.8,label="dH/dt (ma$^{-1}$)")

#def animation(i):
    
#    plt.pcolormesh(x,y,dHdt[:,:,i],norm=thklim,cmap='bwr_r',shading = 'auto')
#    plt.contour(x,y,GL[:,:,0],[0.1],norm=thklim,colors='grey',linewidths=0.5)
#    plt.contour(x,y,GL[:,:,i],[0.1],norm=thklim,colors='black',linewidths=0.5)
#    plt.tick_params(
#        axis='both',
#        bottom=False,
#        left=False,
#        labelbottom=False,
#        labelleft=False)
#    year = 1851 + 10*i
#    plt.title(f"{year-1851} years")
#    #return plt

#ani = FuncAnimation(fig,
#                    animation,
#                    frames = num_of_h5,
#                    interval = 500,
#                    repeat=True)

#ani.save('../figures/AIS-cx209-dHdt.gif')

#video = ani.to_html5_video() 

#html = display.HTML(video) 

# draw the animation 
#display.display(html) 
#plt.close() 

#print("Finished and saving dh/dt animation")

####################################################################################
"""
