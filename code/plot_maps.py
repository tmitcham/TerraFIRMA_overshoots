####################################################################################

# Imports

import os
import fnmatch
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.colors as col
import matplotlib.patches as pat

from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation 
from IPython import display

from amrfile import io as amrio

####################################################################################

# Options

suite_id = "cx209"
icesheet = "AIS" # the icesheet to plot (GrIS or AIS)
level = 0 # the level of refinement on which to load the data (0 = coarsest mesh level)
order = 0 # type of interpolation to perform (0 = piecewise constant, 1 = linear; both are conservative)
animation = False # whether to load multiple files for animation (True) or just one file for a single map (False)
year_to_plot = 'initial' # the single year to plot if not an animation (initial, final, or an actual year e.g. 1905)

####################################################################################

# Read the data required for plotting

print(f"Reading data from {suite_id}...")

directory = f"/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/raw_data/{suite_id}/icesheet/"
files = fnmatch.filter(sorted(os.listdir(directory)), f"*{icesheet}*.hdf5")
num_of_h5 = len(files)

if not animation:

    if year_to_plot == 'initial':
        infile = files[0]

    elif year_to_plot == 'final':
        infile = files[num_of_h5-1]

    else:
        infile = f"bisicles_{suite_id}c_{year_to_plot}0101_plot-{icesheet}.hdf5"

    print(f"Loading data from {infile}")

    ISFile = amrio.load(directory + infile)

    lo, hi = amrio.queryDomainCorners(ISFile, level)

    x, y, H = amrio.readBox2D(ISFile, level, lo, hi, "thickness", order)[2]
    dHdt = amrio.readBox2D(ISFile, level, lo, hi, "dThickness/dt", order)[2]
    B = amrio.readBox2D(ISFile, level, lo, hi, "Z_base", order)[2]
    Speed = amrio.readBox2D(ISFile, level, lo, hi, "Vel_magnitidue", order)[2]
    xVel = amrio.readBox2D(ISFile, level, lo, hi, "xVel", order)[2]
    yVel = amrio.readBox2D(ISFile, level, lo, hi, "yVel", order)[2]

    amrio.free(ISFile)

elif animation:

    print(f"Found {num_of_h5} files")

    for i in range(num_of_h5):

        print(f"Loading data from {files[i]}")

        ISFile = amrio.load(directory + files[i])
        
        lo, hi = amrio.queryDomainCorners(ISFile, level)

        x, y = amrio.readBox2D(ISFile, level, lo, hi, "thickness", order)[:2]

        var_shape = (y.size, x.size, num_of_h5)

        H = np.ndarray(shape=var_shape)
        dHdt = np.ndarray(shape=var_shape)
        B = np.ndarray(shape=var_shape)
        Speed = np.ndarray(shape=var_shape)
        xVel = np.ndarray(shape=var_shape)
        yVel = np.ndarray(shape=var_shape)

        H[:,:,i] = amrio.readBox2D(ISFile, level, lo, hi, "thickness", order)[2]
        dHdt[:,:,i] = amrio.readBox2D(ISFile, level, lo, hi, "dThickness/dt", order)[2]
        B[:,:,i] = amrio.readBox2D(ISFile, level, lo, hi, "Z_base", order)[2]
        Speed[:,:,i] = amrio.readBox2D(ISFile, level, lo, hi, "Vel_magnitidue", order)[2]
        xVel[:,:,i] = amrio.readBox2D(ISFile, level, lo, hi, "xVel", order)[2]
        yVel[:,:,i] = amrio.readBox2D(ISFile, level, lo, hi, "yVel", order)[2]
        
        amrio.free(ISFile)
    

####################################################################################

# PLot ice thickness and ice speed maps for a single year

print("Starting initial thickness and velocity maps...")

# Plot ice thickness map

fig = plt.figure()
ax = plt.gca()

if icesheet == "GrIS":
    ax.set_ylim(0.85e6,5.35e6)
    ax.set_xlim(0.3e6,5.85e6)

ax.set_aspect('equal', adjustable='box')

H[H==0] = np.NaN

# Calculate the height above flotation to plot the grounding line
Haf = (-1*B)*(1028/918)
GL = H-Haf

# Colour and contour plot
fig = plt.pcolormesh(x,y,H,cmap = 'YlGn', shading = 'auto')
plt.colorbar(shrink=0.9,label="Ice thickness (m)")
fig = plt.contour(x,y,GL,[0.1],colors='black',linewidths=0.6)

plt.tick_params(
    axis='both',
    bottom=False,
    left=False,
    labelbottom=False,
    labelleft=False)

plt.savefig(f"../figures/{suite_id}_{icesheet}_{year_to_plot}_thickness.png",dpi=600,bbox_inches='tight')
plt.clf()

# Plot ice speed map

fig = plt.figure()
ax = plt.gca()

# May need to set limits on colourscale for clear plots
spdlim = col.Normalize(0,5000)

ax = plt.gca()

if icesheet == "GrIS":
    ax.set_ylim(0.85e6,5.35e6)
    ax.set_xlim(0.3e6,5.85e6)

ax.set_aspect('equal', adjustable='box')

Speed[Speed==0] = np.NaN

#color and contour plot
fig = plt.pcolormesh(x,y,Speed,norm=spdlim,cmap='Greys',shading = 'auto')
fig = plt.colorbar(extend="max",shrink=0.9,label="Ice flow speed (m/yr)")
fig = plt.contour(x,y,GL,[0.1],colors='black',linewidths=0.6)

fig = plt.tick_params(
    axis='both',
    bottom=False,
    left=False,
    labelbottom=False,
    labelleft=False)

plt.savefig(f"../figures/{suite_id}_{icesheet}_{year_to_plot}_speed.png",dpi=600,bbox_inches='tight')

plt.clf()

print("Finished and saved initial thickness and velocity maps...")

''' Need to work on this still...
####################################################################################

# Make animation of dh/dt during the ramp-up (map)

print("Starting dh/dt animation...")

thklim = col.Normalize(-2.5,2.5) # limits for thickness change colormap

fig = plt.figure()
ax = fig.add_subplot(111)

ax.set_ylim(0.85e6,5.35e6)
ax.set_xlim(0.3e6,5.85e6)
ax.set_aspect('equal', adjustable='box')

im = ax.pcolormesh(x,y,dHdt[:,:,0],figure=fig, norm=thklim,cmap='bwr_r',shading = 'auto')
cb = fig.colorbar(im, extend="both",shrink=0.8,label="dH/dt (ma$^{-1}$)")

def animation(i):
    
    plt.pcolormesh(x,y,dHdt[:,:,i],norm=thklim,cmap='bwr_r',shading = 'auto')
    plt.contour(x,y,GL[:,:,0],[0.1],norm=thklim,colors='grey',linewidths=0.5)
    plt.contour(x,y,GL[:,:,i],[0.1],norm=thklim,colors='black',linewidths=0.5)
    plt.tick_params(
        axis='both',
        bottom=False,
        left=False,
        labelbottom=False,
        labelleft=False)
    year = 1851 + 10*i
    plt.title(f"{year-1851} years")
    #return plt

ani = FuncAnimation(fig,
                    animation,
                    frames = num_of_h5,
                    interval = 500,
                    repeat=True)

ani.save('../figures/AIS-cx209-dHdt.gif')

video = ani.to_html5_video() 

html = display.HTML(video) 

# draw the animation 
display.display(html) 
plt.close() 

print("Finished and saving dh/dt animation")

####################################################################################'
'''