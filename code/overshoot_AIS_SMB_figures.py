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

# Options for loading BISICLES plot files
level = 1 # the level of refinement on which to load the data (0 = coarsest mesh level)
order = 0 # type of interpolation to perform (0 = piecewise constant, 1 = linear; both are conservative)

AISFile = amrio.load("plot.3lev.004521.2d.hdf5")

lo, hi = amrio.queryDomainCorners(AISFile, level)

x, y = amrio.readBox2D(AISFile, level, lo, hi, "thickness", order)[:2]

var_shape = (y.size, x.size,1)

H = np.ndarray(shape=var_shape)
B = np.ndarray(shape=var_shape)
SMB = np.ndarray(shape=var_shape)

H[:,:,0] = amrio.readBox2D(AISFile, level, lo, hi, "thickness", order)[2]
B[:,:,0] = amrio.readBox2D(AISFile, level, lo, hi, "Z_base", order)[2]
SMB[:,:,0] = amrio.readBox2D(AISFile, level, lo, hi, "SMB", order)[2]

amrio.free(AISFile)

####################################################################################

thklim = col.Normalize(-1,1) # limits for thickness change colormap

fig = plt.figure()

ax = plt.gca()
ax.set_ylim(0.85e6,5.35e6)
ax.set_xlim(0.3e6,5.85e6)
ax.set_aspect('equal', adjustable='box')

H[H==0] = np.NaN
SMB[SMB==0] = np.NaN

Haf = (-1*B)*(1028/918)
GL = H-Haf

#color and contour plot
fig = plt.pcolormesh(x,y,SMB[:,:,0],norm=thklim,cmap='coolwarm_r',shading = 'auto')
plt.colorbar(extend="both",shrink=0.9,label="SMB (m w.e./yr)")
fig = plt.contour(x,y,GL[:,:,0],[0.1],norm=thklim,colors='grey',linewidths=0.6)

plt.title(f"SMB in MAR")
plt.tick_params(
    axis='both',
    bottom=False,
    left=False,
    labelbottom=False,
    labelleft=False)

plt.savefig(f"AIS-SMB-MAR.png",dpi=600,bbox_inches='tight')

plt.clf()
