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

# Read data from the ramp-up cx209 for mapping

plot_id = "cz378"

print(f"Reading data from {plot_id}...")

# Options for loading BISICLES plot files
level = 0 # the level of refinement on which to load the data (0 = coarsest mesh level)
order = 0 # type of interpolation to perform (0 = piecewise constant, 1 = linear; both are conservative)

directory = f"/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/raw_data/{plot_id}/icesheet/"

files = fnmatch.filter(sorted(os.listdir(directory)), "*AIS.hdf5")
num_of_h5 = len(fnmatch.filter(os.listdir(directory), "*AIS.hdf5"))

if num_of_h5 > 1:

    print(f"Found {num_of_h5} files")

    infile = files[0]

    print(f"Loading data from {infile}")

    GrISFile = amrio.load(directory + infile)

    lo, hi = amrio.queryDomainCorners(GrISFile, level)

    x, y = amrio.readBox2D(GrISFile, level, lo, hi, "thickness", order)[:2]

    var_shape = (y.size, x.size, 2)

    H = np.ndarray(shape=var_shape)
    B = np.ndarray(shape=var_shape)

    H[:,:,0] = amrio.readBox2D(GrISFile, level, lo, hi, "thickness", order)[2]
    B[:,:,0] = amrio.readBox2D(GrISFile, level, lo, hi, "Z_base", order)[2]

    amrio.free(GrISFile)

    infile = files[num_of_h5-1]

    print(f"Loading data from {infile}")

    GrISFile = amrio.load(directory + infile)

    H[:,:,1] = amrio.readBox2D(GrISFile, level, lo, hi, "thickness", order)[2]
    B[:,:,1] = amrio.readBox2D(GrISFile, level, lo, hi, "Z_base", order)[2]

    amrio.free(GrISFile)
    

####################################################################################

# Plot total thickness change during ramp-up (map)
print("Starting total thickness change map...")

thklim = col.Normalize(-500,500) # limits for thickness change colormap

fig = plt.figure()

ax = plt.gca()
ax.set_ylim(0.85e6,5.35e6)
ax.set_xlim(0.3e6,5.85e6)
ax.set_aspect('equal', adjustable='box')

H[H==0] = np.NaN

Haf = (-1*B)*(1028/918)
GL = H-Haf

#color and contour plot
fig = plt.pcolormesh(x,y,H[:,:,1]-H[:,:,0],norm=thklim,cmap='coolwarm_r',shading = 'auto')
plt.colorbar(extend="min",shrink=0.9,label="$\Delta H$ (m)")
fig = plt.contour(x,y,GL[:,:,1],[0.1],colors='black',linewidths=0.6)
fig = plt.contour(x,y,GL[:,:,0],[0.1],colors='grey',linewidths=0.6)

plt.title(f"Total $\Delta H$ in ZE-6 (730 years)")
plt.tick_params(
    axis='both',
    bottom=False,
    left=False,
    labelbottom=False,
    labelleft=False)

print("Finished and saving total thickness change map...")

plt.savefig(f"../figures/AIS-{plot_id}-totalH-change.png",dpi=600,bbox_inches='tight')

plt.clf()

####################################################################################
"""
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

    plt.savefig(f"../figures/AIS-initial-thickness.png",dpi=600,bbox_inches='tight')

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

    plt.savefig(f"../figures/AIS-initial-speed.png",dpi=600,bbox_inches='tight')

    plt.clf()

    print("Finished and saving initial thickness and velocity maps...")


####################################################################################

# Make animation of dh/dt during the ramp-up (map)

print("Starting dh/dt animation...")

thklim = col.Normalize(-2.5,2.5) # limits for thickness change colormap

H[H==0] = np.NaN

Haf = (-1*B)*(1028/918)
GL = H-Haf
dHdt[np.isnan(H)] = np.NaN

fig, ax = plt.subplots()

ax.set_ylim(0.85e6,5.35e6)
ax.set_xlim(0.3e6,5.85e6)
ax.set_aspect('equal', adjustable='box')

im = ax.pcolormesh(x,y,dHdt[:,:,0],figure=fig, norm=thklim,cmap='bwr_r',shading = 'auto')
cb = fig.colorbar(im, extend="both",shrink=0.8,label="dH/dt (ma$^{-1}$)")

contour_lines = ax.contour(x, y, GL[:, :, 0], levels=[0.1], colors='grey', linewidths=0.5)
contour_collections = contour_lines.collections

def update_contours(new_contours):

    # Helper function to update contour lines.

    global contour_collections
    # Remove existing contours
    for collection in contour_collections:
        collection.remove()
    # Draw new contours
    contour_lines = ax.contour(x, y, new_contours, levels=[0.1], colors='black', linewidths=0.5)
    contour_collections = contour_lines.collections  # Update stored collections

def animation(i):
    
    print(f"Working on frame {i+1}")

    # Update the pcolormesh data for the current frame
    im.set_array(dHdt[:, :, i].ravel())  # Update pcolormesh instead of redrawing
    
    # Update contours for the current frame
    update_contours(GL[:, :, i])

    # Update the title for the current year
    ax.set_title(f"{i + 1} years")

    ax.tick_params(
        axis='both',
        bottom=False,
        left=False,
        labelbottom=False,
        labelleft=False
    )
    
    return im,

ani = FuncAnimation(fig,
                    animation,
                    frames = num_of_h5,
                    interval = 100,
                    repeat=True,
                    blit=True)

print("Finished and saving dh/dt animation")

ani.save(f"../figures/AIS-{plot_id}-dHdt.gif")

####################################################################################
"""