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

from amrfile import io as amrio

####################################################################################

# Read data from the ramp-up cx209 for mapping

plot_id = ["cx209", "dc060", "dc085"]

# Options for loading BISICLES plot files
level = 1 # the level of refinement on which to load the data (0 = coarsest mesh level)
order = 0 # type of interpolation to perform (0 = piecewise constant, 1 = linear; both are conservative)

count = 0

for i in plot_id:

    print(f"Reading data from {i}...")

    if i == "cx209":

        directory = f"/home/users/tm17544/gws_terrafirma/overshoots/raw_data/{i}/icesheet/"

        files = []
        files.append(f"{directory}bisicles_cx209c_18510101_plot-AIS.hdf5")
        files.append(f"{directory}bisicles_cx209c_19200101_plot-AIS.hdf5")

    else:

        directory = f"/gws/nopw/j04/terrafirma/rssmith/archer2/u-{i}/"

        files = []
        files.append(f"{directory}18520101T0000Z/bisicles_{i}c_18520101_plot-AIS.hdf5")
        files.append(f"{directory}19200101T0000Z/bisicles_{i}c_19200101_plot-AIS.hdf5")

    infile = files[0]

    print(f"Loading data from {infile}")

    AISFile = amrio.load(infile)

    if count == 0:

        lo, hi = amrio.queryDomainCorners(AISFile, level)

        x, y = amrio.readBox2D(AISFile, level, lo, hi, "thickness", order)[:2]

        var_shape = (y.size, x.size, 6)

        H = np.ndarray(shape=var_shape)
        dHdt = np.ndarray(shape=var_shape)
        B = np.ndarray(shape=var_shape)
        xVel = np.ndarray(shape=var_shape)
        yVel = np.ndarray(shape=var_shape)

    H[:,:,int(count*2)] = amrio.readBox2D(AISFile, level, lo, hi, "thickness", order)[2]
    dHdt[:,:,int(count*2)] = amrio.readBox2D(AISFile, level, lo, hi, "dThickness/dt", order)[2]
    B[:,:,int(count*2)] = amrio.readBox2D(AISFile, level, lo, hi, "Z_base", order)[2]
    xVel[:,:,int(count*2)] = amrio.readBox2D(AISFile, level, lo, hi, "xVel", order)[2]
    yVel[:,:,int(count*2)] = amrio.readBox2D(AISFile, level, lo, hi, "yVel", order)[2]

    amrio.free(AISFile)

    infile = files[1]

    print(f"Loading data from {infile}")

    AISFile = amrio.load(infile)

    H[:,:,int(count*2)+1] = amrio.readBox2D(AISFile, level, lo, hi, "thickness", order)[2]
    dHdt[:,:,int(count*2)+1] = amrio.readBox2D(AISFile, level, lo, hi, "dThickness/dt", order)[2]
    B[:,:,int(count*2)+1] = amrio.readBox2D(AISFile, level, lo, hi, "Z_base", order)[2]
    xVel[:,:,int(count*2)+1] = amrio.readBox2D(AISFile, level, lo, hi, "xVel", order)[2]
    yVel[:,:,int(count*2)+1] = amrio.readBox2D(AISFile, level, lo, hi, "yVel", order)[2]

    amrio.free(AISFile)

    count += 1

print(f"Shape of data array is: {H.shape}")

####################################################################################

# Plot total thickness change during ramp-up (map)
print("Starting total thickness change map...")

#plot_id = "cx209"
#plot_id = "dc060" 
#plot_id = "dc085"

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
fig = plt.pcolormesh(x,y,H[:,:,2]-H[:,:,0],norm=thklim,cmap='coolwarm_r',shading = 'auto')
plt.colorbar(extend="min",shrink=0.9,label="$\Delta H$ (m)")
fig = plt.contour(x,y,GL[:,:,2],[0.1],norm=thklim,colors='black',linewidths=0.6)
fig = plt.contour(x,y,GL[:,:,0],[0.1],norm=thklim,colors='grey',linewidths=0.6)

plt.title(f"Initial $\Delta H$ (dc060-cx209)")
plt.tick_params(
    axis='both',
    bottom=False,
    left=False,
    labelbottom=False,
    labelleft=False)

print("Finished and saving total thickness change map...")

plt.savefig(f"AIS-totalH-diff-dc060-cx209.png",dpi=600,bbox_inches='tight')

plt.clf()

####################################################################################

# Plot initial ice thickness and velocity if "cx209"

""" print("Starting initial thickness and velocity maps...")

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

plt.savefig(f"AIS-1852-thickness-{plot_id}.png",dpi=600,bbox_inches='tight')

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

plt.savefig(f"AIS-1852-speed-{plot_id}.png",dpi=600,bbox_inches='tight')

plt.clf()

print("Finished and saving initial thickness and velocity maps...") """

####################################################################################

