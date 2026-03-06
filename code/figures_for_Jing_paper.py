# =====================================================================
# IMPORTS & DATA LOADING
# =====================================================================

import numpy as np
import pickle
import matplotlib.pyplot as plt
import pandas as pd

plot_fontsize = 8
id = ["cx209"]

with open("/gws/ssde/j25b/terrafirma/tm17544/TerraFIRMA_overshoots/processed_data/AIS_data_overshoots_masked_newmask_1km.pkl", 'rb') as file:
    icesheet_d = pickle.load(file)

with open("/gws/ssde/j25b/terrafirma/tm17544/TerraFIRMA_overshoots/processed_data/atmos_data_overshoots.pkl", 'rb') as file:
    atmos_d = pickle.load(file)

# =====================================================================
# PREP SMB DATA
# =====================================================================

SMB = {}
for i in id:
    SMB[i] = {}
    # FRIS
    SMB[i]["FRIS"] = icesheet_d[i][16][["time","grounded_SMB","floating_SMB"]] + icesheet_d[i][17][["time","grounded_SMB","floating_SMB"]]
    SMB[i]["FRIS"] = pd.concat([SMB[i]["FRIS"], pd.DataFrame(atmos_d[i][:,1])], axis=1)
    SMB[i]["FRIS"].drop(SMB[i]["FRIS"].tail(1).index,inplace=True)
    SMB[i]["FRIS"].columns = ["time","grounded_SMB","floating_SMB","GSAT"]

    # ROSS
    SMB[i]["Ross"] = icesheet_d[i][8][["time","grounded_SMB","floating_SMB"]] + icesheet_d[i][9][["time","grounded_SMB","floating_SMB"]]
    SMB[i]["Ross"] = pd.concat([SMB[i]["Ross"], pd.DataFrame(atmos_d[i][:,1])], axis=1)
    SMB[i]["Ross"].drop(SMB[i]["Ross"].tail(1).index,inplace=True)
    SMB[i]["Ross"].columns = ["time","grounded_SMB","floating_SMB","GSAT"]

    SMB[i]["FRIS"] = SMB[i]["FRIS"].sort_values(by="GSAT")
    SMB[i]["Ross"] = SMB[i]["Ross"].sort_values(by="GSAT")

# =====================================================================
# FUNCTIONS
# =====================================================================

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    return np.convolve(y, box, mode='valid')

def mass2sle(x):
    return x*(-1)/361.8

def sle2mass(x):
    return x*(-1)*361.8

plt.rcParams.update({
    'font.size': plot_fontsize,
    'pdf.fonttype': 42,       # Editable text in Illustrator
    'ps.fonttype': 42,
    'axes.linewidth': 0.8,
})

# =====================================================================
# FIGURE SETTINGS
# =====================================================================

fig_width = 6.85
fig_height = 9.0

fig, ax = plt.subplots(4, 2, figsize=(fig_width, fig_height), sharex='row')

line_col = "black"

# Column titles
ax[0,0].text(0.5, 1.10, "Ross", ha='center', va='center',
             transform=ax[0,0].transAxes, fontsize=11, fontweight='bold')

ax[0,1].text(0.5, 1.10, "FRIS", ha='center', va='center',
             transform=ax[0,1].transAxes, fontsize=11, fontweight='bold')

initialT = atmos_d["cx209"][0,1]
box_size = 21

# =====================================================================
# -------- PANEL (a,b): VOLUME CHANGE (Row 0)
# =====================================================================

# ROSS
initialVol_R = (icesheet_d["cx209"][8]["grounded_vol"][0] +
                icesheet_d["cx209"][8]["floating_vol"][0] +
                icesheet_d["cx209"][9]["grounded_vol"][0] +
                icesheet_d["cx209"][9]["floating_vol"][0])

plot_R = icesheet_d["cx209"][8] + icesheet_d["cx209"][9]
ax[0,0].plot(plot_R["time"]-1850,
             (plot_R["grounded_vol"] + plot_R["floating_vol"] - initialVol_R)*(0.918/1e9),
             color=line_col, linewidth=1.0)

ax[0,0].set_ylabel("Mass change (Gt)")
ax[0,0].text(0.02, 0.90, "a)", transform=ax[0,0].transAxes,
             fontsize=10, fontweight='bold')

# FRIS
initialVol_F = (icesheet_d["cx209"][16]["grounded_vol"][0] +
                icesheet_d["cx209"][16]["floating_vol"][0] +
                icesheet_d["cx209"][17]["grounded_vol"][0] +
                icesheet_d["cx209"][17]["floating_vol"][0])

plot_F = icesheet_d["cx209"][16] + icesheet_d["cx209"][17]
ax[0,1].plot(plot_F["time"]-1850,
             (plot_F["grounded_vol"] + plot_F["floating_vol"] - initialVol_F)*(0.918/1e9),
             color=line_col, linewidth=1.0)

ax[0,1].text(0.02, 0.90, "b)", transform=ax[0,1].transAxes,
             fontsize=10, fontweight='bold')

# =====================================================================
# -------- PANEL (c,d): VAF CHANGE (Row 1)
# =====================================================================

# ROSS
initialVAF_R = icesheet_d["cx209"][8]["VAF"][0] + icesheet_d["cx209"][9]["VAF"][0]

ax[1,0].plot(plot_R["time"]-1850,
             (plot_R["VAF"] - initialVAF_R)*(0.918/1e9),
             color=line_col, linewidth=1.0)

ax[1,0].set_ylabel("Mass above\nflotation (Gt)")
sec = ax[1,0].secondary_yaxis('right', functions=(mass2sle, sle2mass))
#sec.set_ylabel("Sea level (mm)")
ax[1,0].text(0.02, 0.90, "c)", transform=ax[1,0].transAxes,
             fontsize=10, fontweight='bold')

# FRIS
initialVAF_F = icesheet_d["cx209"][16]["VAF"][0] + icesheet_d["cx209"][17]["VAF"][0]

ax[1,1].plot(plot_F["time"]-1850,
             (plot_F["VAF"] - initialVAF_F)*(0.918/1e9),
             color=line_col, linewidth=1.0)

sec = ax[1,1].secondary_yaxis('right', functions=(mass2sle, sle2mass))
sec.set_ylabel("Sea level (mm)")
ax[1,1].text(0.02, 0.90, "d)", transform=ax[1,1].transAxes,
             fontsize=10, fontweight='bold')

# =====================================================================
# -------- PANEL (e,f): GROUNDED SMB vs GSAT (Row 2)
# =====================================================================

# ROSS
ax[2,0].plot(SMB["cx209"]["Ross"]["GSAT"]-initialT,
             SMB["cx209"]["Ross"]["grounded_SMB"]*(0.918/1e9),
             color=line_col, alpha=0.3)

ma_y = smooth(SMB["cx209"]["Ross"]["grounded_SMB"]*(0.918/1e9), box_size)
ma_x = (SMB["cx209"]["Ross"]["GSAT"] - initialT).values
ma_x = ma_x[int((box_size-1)/2): -int((box_size-1)/2)]
ax[2,0].plot(ma_x, ma_y, color=line_col, linewidth=1.2)

ax[2,0].set_ylabel("Grounded SMB\n(Gt yr$^{-1}$)")
ax[2,0].text(0.02, 0.90, "e)", transform=ax[2,0].transAxes,
             fontsize=10, fontweight='bold')

# FRIS
ax[2,1].plot(SMB["cx209"]["FRIS"]["GSAT"]-initialT,
             SMB["cx209"]["FRIS"]["grounded_SMB"]*(0.918/1e9),
             color=line_col, alpha=0.3)

ma_y_F = smooth(SMB["cx209"]["FRIS"]["grounded_SMB"]*(0.918/1e9), box_size)
ma_x_F = (SMB["cx209"]["FRIS"]["GSAT"] - initialT).values
ma_x_F = ma_x_F[int((box_size-1)/2): -int((box_size-1)/2)]
ax[2,1].plot(ma_x_F, ma_y_F, color=line_col, linewidth=1.2)

ax[2,1].text(0.02, 0.90, "f)", transform=ax[2,1].transAxes,
             fontsize=10, fontweight='bold')

# =====================================================================
# -------- PANEL (g,h): FLOATING SMB vs GSAT (Row 3)
# =====================================================================

# ROSS
ax[3,0].plot(SMB["cx209"]["Ross"]["GSAT"]-initialT,
             SMB["cx209"]["Ross"]["floating_SMB"]*(0.918/1e9),
             color=line_col, alpha=0.3)

ma_y = smooth(SMB["cx209"]["Ross"]["floating_SMB"]*(0.918/1e9), box_size)
ax[3,0].plot(ma_x, ma_y, color=line_col, linewidth=1.2)

ax[3,0].set_ylabel("Floating SMB\n(Gt yr$^{-1}$)")
ax[3,0].set_xlabel("ΔGSAT (K)")
ax[3,0].text(0.02, 0.90, "g)", transform=ax[3,0].transAxes,
             fontsize=10, fontweight='bold')

# FRIS
ax[3,1].plot(SMB["cx209"]["FRIS"]["GSAT"]-initialT,
             SMB["cx209"]["FRIS"]["floating_SMB"]*(0.918/1e9),
             color=line_col, alpha=0.3)

ma_y_F = smooth(SMB["cx209"]["FRIS"]["floating_SMB"]*(0.918/1e9), box_size)
ax[3,1].plot(ma_x_F, ma_y_F, color=line_col, linewidth=1.2)

ax[3,1].set_xlabel("ΔGSAT (K)")
ax[3,1].text(0.02, 0.90, "h)", transform=ax[3,1].transAxes,
             fontsize=10, fontweight='bold')

# =====================================================================
# LAYOUT + SAVE
# =====================================================================

plt.tight_layout(rect=[0, 0, 1, 0.96])

plt.savefig(
    "../figures/Jing_paper_Ross_FRIS_combined.png",
    dpi=600,
    bbox_inches="tight"
)

print("Figure saved successfully.")

# =====================================================================
# End of integrated quantities plotting
# =====================================================================

# =====================================================================
# Start of map plotting
# =====================================================================

import os
import fnmatch

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.ticker import MaxNLocator

from amrfile import io as amrio

# =====================================================================
# Options for plotting
# =====================================================================

suite_id = "cx209" # the suite ID to plot
level = 0 # the level of refinement on which to load the data (0 = coarsest mesh level)
order = 1 # type of interpolation to perform (0 = piecewise constant, 1 = linear; both are conservative)

# Which of the BISICLES plot files are needed for these maps?
years_to_load = [0, 160, 200, 240, 260, 350] # the years to load for plotting (must be in the data)

fig_w = 6.85  # inches
fig_h = 6.85

plt.rcParams.update({
    "font.size": 8,
    "axes.linewidth": 0.8,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

# =====================================================================
# Read data
# =====================================================================

print(f"Reading data from {suite_id}...")

directory = f"/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/raw_data/{suite_id}/icesheet/"
files = fnmatch.filter(sorted(os.listdir(directory)), "*plot-AIS.hdf5")
num_of_h5 = len(files)

print(f"Found {num_of_h5} files. Loading selected years: {years_to_load}...")

files_to_load = [files[i] for i in years_to_load]

count = 0

for infile in files_to_load:
    
    print(f"Loading data from {infile}...")

    ISFile = amrio.load(directory + infile)

    lo, hi = amrio.queryDomainCorners(ISFile, level)

    if count == 0:

        x, y = amrio.readBox2D(ISFile, level, lo, hi, "thickness", order)[:2]

        var_shape = (y.size, x.size, len(files_to_load))

        H = np.ndarray(shape=var_shape)
        dHdt = np.ndarray(shape=var_shape)
        B = np.ndarray(shape=var_shape)
        xVel = np.ndarray(shape=var_shape)
        yVel = np.ndarray(shape=var_shape)

    H[:,:,count] = amrio.readBox2D(ISFile, level, lo, hi, "thickness", order)[2]
    dHdt[:,:,count] = amrio.readBox2D(ISFile, level, lo, hi, "dThickness/dt", order)[2]
    B[:,:,count] = amrio.readBox2D(ISFile, level, lo, hi, "Z_base", order)[2]
    xVel[:,:,count] = amrio.readBox2D(ISFile, level, lo, hi, "xVel", order)[2]
    yVel[:,:,count] = amrio.readBox2D(ISFile, level, lo, hi, "yVel", order)[2]

    amrio.free(ISFile)

    count += 1


# =====================================================================
# Single file thickness map with grounding line contour
# =====================================================================

# Select which time slice to plot (index of 'files_to_load' list)
t_idx = 0

# Copy arrays for this time slice
H_plot   = np.array(H[:,:,t_idx], dtype=float)
B_plot   = np.array(B[:,:,t_idx], dtype=float)
x_plot   = np.array(x, dtype=float)
y_plot   = np.array(y, dtype=float)

H_plot[H_plot == 0] = np.nan

# Height-above-flotation to identify GL
rho_w = 1028.0
rho_i =  918.0
Haf   = (-1.0 * B_plot) * (rho_w / rho_i)
GL    = H_plot - Haf  # GL ≈ 0 is the grounding line

fig, ax = plt.subplots(figsize=(fig_w, fig_h))
ax.set_aspect('equal', adjustable='box')

# Define  color scale (avoid outliers)
vmin = 0.0
vmax = np.nanpercentile(H_plot, 99.5)  # cap at 99.5th percentile
norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

cmap = plt.cm.viridis

mesh = ax.pcolormesh(x_plot, y_plot, H_plot, cmap=cmap, norm=norm,
                     shading='auto', rasterized=True)

# Grounding line: GL = 0 contour
valid = np.isfinite(GL)
# For contour, need 2D X,Y meshes
# If x_plot, y_plot are 1D monotonic axes (regular grid), contour can use them directly.
# If they are 2D, convert to a meshgrid shape:
if x_plot.ndim == 1 and y_plot.ndim == 1:
    Xc, Yc = np.meshgrid(x_plot, y_plot)
else:
    Xc, Yc = x_plot, y_plot

glc = ax.contour(Xc, Yc, GL, levels=[0.0], colors='black', linewidths=0.7)

ax.tick_params(axis="both", which="both", bottom=False, left=False, labelbottom=False, labelleft=False)


cbar = fig.colorbar(mesh, ax=ax, fraction=0.035, pad=0.02)
cbar.set_label("Ice thickness (m)", rotation=90)

cbar.locator = MaxNLocator(nbins=6)
cbar.update_ticks()

ax.text(0.01, 0.98, "a)", transform=ax.transAxes, ha='left', va='top',
        fontsize=9, fontweight='bold')

out_path = f"../figures/{suite_id}_AIS_initial_thickness_publication.png"
plt.savefig(out_path, dpi=600, bbox_inches='tight')
print(f"Saved publication map to: {out_path}")

# =====================================================================
# TWO-PANEL MAP USING AXIS LIMITS (CORRECTED)
# =====================================================================

t_idx = 0

H0 = np.array(H[:,:,t_idx], dtype=float)
B0 = np.array(B[:,:,t_idx], dtype=float)
H0[H0 == 0] = np.nan

rho_w = 1028
rho_i = 918
Haf = (-B0) * (rho_w / rho_i)
GL  = H0 - Haf

# Ensure x and y are 1D axes
x1d = np.array(x).ravel()
y1d = np.array(y).ravel()

# Ensure increasing order
if x1d[0] > x1d[-1]:
    x1d = x1d[::-1]
    H0  = H0[:, ::-1]
    GL  = GL[:, ::-1]

if y1d[0] > y1d[-1]:
    y1d = y1d[::-1]
    H0  = H0[::-1, :]
    GL  = GL[::-1, :]

# FRIS + Ross bounding boxes
FRIS_xlim = (-1.7e6 + 3072000,  -0.2e6 + 3072000)
FRIS_ylim = (-0.2e6 + 3072000,  1.3e6 + 3072000)

ROSS_xlim = (-1.0e6 + 3072000,  0.7e6 + 3072000)
ROSS_ylim = (-1.5e6 + 3072000,  0.2e6 + 3072000)

# Figure setup
fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.8))

for ax in axes:
    ax.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)

# Robust thickness range
vmin, vmax = 0, np.nanpercentile(H0, 99.5)
cmap = plt.cm.viridis

##########################################
# Panel (a): FRIS
##########################################

im0 = axes[0].pcolormesh(x1d, y1d, H0, shading='auto',
                         cmap=cmap, vmin=vmin, vmax=vmax, rasterized=True)

axes[0].contour(x1d, y1d, GL, levels=[0], colors='black', linewidths=0.6)

axes[0].set_xlim(FRIS_xlim)
axes[0].set_ylim(FRIS_ylim)
axes[0].set_aspect('equal', adjustable='box')  # MUST be after limits

axes[0].text(0.02, 0.98, "a)", transform=axes[0].transAxes,
             ha='left', va='top', fontweight='bold')
axes[0].text(0.5, 1.04, "FRIS",
             transform=axes[0].transAxes,
             ha='center', va='bottom', fontsize=9, fontweight='bold')

##########################################
# Panel (b): Ross
##########################################

im1 = axes[1].pcolormesh(x1d, y1d, H0, shading='auto',
                         cmap=cmap, vmin=vmin, vmax=vmax, rasterized=True)

axes[1].contour(x1d, y1d, GL, levels=[0], colors='black', linewidths=0.6)

axes[1].set_xlim(ROSS_xlim)
axes[1].set_ylim(ROSS_ylim)
axes[1].set_aspect('equal', adjustable='box')

axes[1].text(0.02, 0.98, "b)", transform=axes[1].transAxes,
             ha='left', va='top', fontweight='bold')
axes[1].text(0.5, 1.04, "Ross",
             transform=axes[1].transAxes,
             ha='center', va='bottom', fontsize=9, fontweight='bold')

# Shared colorbar
cbar = fig.colorbar(im1, ax=axes, fraction=0.035, pad=0.04)
cbar.set_label("Ice thickness (m)")

plt.savefig("../figures/AIS_FRIS_ROSS_axesLimit_FIXED.png",
            dpi=600, bbox_inches='tight')
print("Saved FRIS+Ross two‑panel map.")

# =====================================================================
# FOUR-PANEL MAP: THICKNESS (top row) + VELOCITY (bottom row)
# =====================================================================

t_idx = 0

H0 = np.array(H[:,:,t_idx], dtype=float)
B0 = np.array(B[:,:,t_idx], dtype=float)
H0[H0 == 0] = np.nan

rho_w = 1028
rho_i = 918
Haf = (-B0) * (rho_w / rho_i)
GL  = H0 - Haf

# Velocity magnitude
u0 = np.array(xVel[:,:,t_idx], dtype=float)
v0 = np.array(yVel[:,:,t_idx], dtype=float)
speed = np.sqrt(u0**2 + v0**2)
speed[speed == 0] = np.nan
speed_log = np.log10(speed)

# Convert x,y to 1D consistent axes
x1d = np.array(x).ravel()
y1d = np.array(y).ravel()

# Ensure increasing axes
if x1d[0] > x1d[-1]:
    x1d = x1d[::-1]
    H0 = H0[:, ::-1]
    GL = GL[:, ::-1]
    speed_log = speed_log[:, ::-1]

if y1d[0] > y1d[-1]:
    y1d = y1d[::-1]
    H0 = H0[::-1, :]
    GL = GL[::-1, :]
    speed_log = speed_log[::-1, :]

# Bounding boxes
FRIS_xlim = (-1.7e6 + 3072000,  -0.2e6 + 3072000)
FRIS_ylim = (-0.2e6 + 3072000,   1.3e6 + 3072000)

ROSS_xlim = (-1.0e6 + 3072000,   0.7e6 + 3072000)
ROSS_ylim = (-1.5e6 + 3072000,   0.2e6 + 3072000)

# Figure with 2 rows × 2 columns
fig, axes = plt.subplots(2, 2, figsize=(7.1, 7.6))   # double height

# Remove ticks
for ax in axes.flat:
    ax.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)

# Thickness color scale
H_vmin, H_vmax = 0, np.nanpercentile(H0, 99.5)
cmap_thick = plt.cm.viridis

# Velocity color scale (log10)
V_vmin, V_vmax = np.nanpercentile(speed_log, 1), np.nanpercentile(speed_log, 99)
cmap_vel = plt.cm.plasma

##########################################
# (a) FRIS thickness
##########################################
im0 = axes[0,0].pcolormesh(x1d, y1d, H0, shading='auto',
                           cmap=cmap_thick, vmin=H_vmin, vmax=H_vmax,
                           rasterized=True)
axes[0,0].contour(x1d, y1d, GL, levels=[0], colors='black', linewidths=0.6)
axes[0,0].set_xlim(FRIS_xlim); axes[0,0].set_ylim(FRIS_ylim)
axes[0,0].set_aspect('equal', adjustable='box')
axes[0,0].text(0.02, 0.98, "a)", transform=axes[0,0].transAxes,
               ha='left', va='top', fontweight='bold')
axes[0,0].text(0.5, 1.04, "FRIS thickness",
               transform=axes[0,0].transAxes,
               ha='center', va='bottom', fontsize=9, fontweight='bold')

##########################################
# (b) Ross thickness
##########################################
im1 = axes[0,1].pcolormesh(x1d, y1d, H0, shading='auto',
                           cmap=cmap_thick, vmin=H_vmin, vmax=H_vmax,
                           rasterized=True)
axes[0,1].contour(x1d, y1d, GL, levels=[0], colors='black', linewidths=0.6)
axes[0,1].set_xlim(ROSS_xlim); axes[0,1].set_ylim(ROSS_ylim)
axes[0,1].set_aspect('equal', adjustable='box')
axes[0,1].text(0.02, 0.98, "b)", transform=axes[0,1].transAxes,
               ha='left', va='top', fontweight='bold')
axes[0,1].text(0.5, 1.04, "Ross thickness",
               transform=axes[0,1].transAxes,
               ha='center', va='bottom', fontsize=9, fontweight='bold')

##########################################
# (c) FRIS velocity (log10)
##########################################
im2 = axes[1,0].pcolormesh(x1d, y1d, speed_log, shading='auto',
                           cmap=cmap_vel, vmin=V_vmin, vmax=V_vmax,
                           rasterized=True)
axes[1,0].contour(x1d, y1d, GL, levels=[0], colors='black', linewidths=0.6)
axes[1,0].set_xlim(FRIS_xlim); axes[1,0].set_ylim(FRIS_ylim)
axes[1,0].set_aspect('equal', adjustable='box')
axes[1,0].text(0.02, 0.98, "c)", transform=axes[1,0].transAxes,
               ha='left', va='top', fontweight='bold')
axes[1,0].text(0.5, 1.04, "FRIS velocity",
               transform=axes[1,0].transAxes,
               ha='center', va='bottom', fontsize=9, fontweight='bold')

##########################################
# (d) Ross velocity (log10)
##########################################
im3 = axes[1,1].pcolormesh(x1d, y1d, speed_log, shading='auto',
                           cmap=cmap_vel, vmin=V_vmin, vmax=V_vmax,
                           rasterized=True)
axes[1,1].contour(x1d, y1d, GL, levels=[0], colors='black', linewidths=0.6)
axes[1,1].set_xlim(ROSS_xlim); axes[1,1].set_ylim(ROSS_ylim)
axes[1,1].set_aspect('equal', adjustable='box')
axes[1,1].text(0.02, 0.98, "d)", transform=axes[1,1].transAxes,
               ha='left', va='top', fontweight='bold')
axes[1,1].text(0.5, 1.04, "Ross velocity",
               transform=axes[1,1].transAxes,
               ha='center', va='bottom', fontsize=9, fontweight='bold')


##############################################
# Colorbar for THICKNESS (top row)
###############################################
cbar0 = fig.colorbar(im1,
                     ax=axes[0,:],
                     location='right',
                     fraction=0.046,
                     pad=0.02,
                     extend='max')
cbar0.set_label("Ice thickness (m)")

###############################################
# Colorbar for VELOCITY (bottom row)
###############################################
cbar1 = fig.colorbar(im3,
                     ax=axes[1,:],
                     location='right',
                     fraction=0.046,
                     pad=0.02,
                     extend='max')
cbar1.set_label("log$_{10}$(speed [m/yr])")


plt.savefig("../figures/AIS_FRIS_ROSS_4panel_thickness_velocity.png",
            dpi=600, bbox_inches='tight')
print("Saved FRIS+Ross 4‑panel thickness+velocity map.")


# =====================================================================
# EIGHT-PANEL DIFFERENCE MAP: 4× Ross (top), 4× FRIS (bottom)
# =====================================================================

# for reference: years_to_load = [0, 160, 200, 240, 260, 350]

# Select pairs of indices for differences
# Example: four different \Delta H intervals
pairs = [
    (0, 1),
    (1, 2),
    (2, 4),
    (4, 5)
]

assert len(pairs) == 4, "Need exactly 4 pairs for 4 columns."

# Pre-extract all H fields
H_list = [H[:,:,i].astype(float) for i in range(len(files_to_load))]

# Mask zeros as NaN
for i in range(len(H_list)):
    H_list[i][H_list[i] == 0] = np.nan

B0 = B[:,:,0].astype(float)
rho_w = 1028
rho_i = 918
Haf0 = (-B0) * (rho_w / rho_i)

# Compute GL for each time slice
GL_list = []
for i in range(len(files_to_load)):
    Haf = Haf0
    GL = H_list[i] - Haf
    GL_list.append(GL)

# Convert x and y to 1D consistent axes
x1d = np.array(x).ravel()
y1d = np.array(y).ravel()

# Correct orientation
if x1d[0] > x1d[-1]:
    x1d = x1d[::-1]
    H_list = [H[:, ::-1] for H in H_list]

if y1d[0] > y1d[-1]:
    y1d = y1d[::-1]
    H_list = [H[::-1, :] for H in H_list]

# Bounding boxes
FRIS_xlim = (-1.7e6 + 3072000,  -0.2e6 + 3072000)
FRIS_ylim = (-0.2e6 + 3072000,   1.3e6 + 3072000)

ROSS_xlim = (-1.0e6 + 3072000,   0.7e6 + 3072000)
ROSS_ylim = (-1.5e6 + 3072000,   0.2e6 + 3072000)

# Figure layout: 2 rows × 4 columns
fig, axes = plt.subplots(2, 4, figsize=(11.0, 5.5))  # wide format

for ax in axes.flat:
    ax.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)

# Difference colormap
cmap = plt.cm.RdBu

# Compute global min/max across all differences for consistent scale
all_diffs = []
for (a, b) in pairs:
    dif = H_list[b] - H_list[a]
    all_diffs.append(dif)

global_min = np.nanpercentile(all_diffs, 1)
global_max = np.nanpercentile(all_diffs, 99)
max_abs = max(abs(global_min), abs(global_max))

# Symmetric limits
vmin, vmax = -max_abs, max_abs

# Make panels
for col, (a, b) in enumerate(pairs):

    # Difference field
    dH = H_list[b] - H_list[a]
    GL0 = GL_list[a]  # Contour from first time
    GL1 = GL_list[b]  # Contour from second time

    # Top row: Ross
    ax = axes[0, col]
    im = ax.pcolormesh(x1d, y1d, dH,
                       shading='auto',
                       cmap=cmap,
                       vmin=vmin, vmax=vmax,
                       rasterized=True)
    ax.contour(x1d, y1d, GL0, levels=[0], colors='grey', linewidths=0.6)
    ax.contour(x1d, y1d, GL1, levels=[0], colors='black', linewidths=0.6)
    ax.set_xlim(ROSS_xlim)
    ax.set_ylim(ROSS_ylim)
    ax.set_aspect('equal', adjustable='box')
    ax.text(0.02, 0.97, f"{chr(97+col)})", transform=ax.transAxes,
            ha='left', va='top', fontweight='bold')
    ax.text(0.5, 1.05, f"ΔH {years_to_load[a]} → {years_to_load[b]} years",
            ha='center', va='bottom', transform=ax.transAxes,
            fontsize=8, fontweight='bold')

    # Bottom row: FRIS
    ax = axes[1, col]
    im = ax.pcolormesh(x1d, y1d, dH,
                       shading='auto',
                       cmap=cmap,
                       vmin=vmin, vmax=vmax,
                       rasterized=True)
    ax.contour(x1d, y1d, GL0, levels=[0], colors='grey', linewidths=0.6)
    ax.contour(x1d, y1d, GL1, levels=[0], colors='black', linewidths=0.6)
    ax.set_xlim(FRIS_xlim)
    ax.set_ylim(FRIS_ylim)
    ax.set_aspect('equal', adjustable='box')
    ax.text(0.02, 0.97, f"{chr(97+col+4)})", transform=ax.transAxes,
            ha='left', va='top', fontweight='bold')
    ax.text(0.5, 1.05, f"ΔH {years_to_load[a]} → {years_to_load[b]} years",
            ha='center', va='bottom', transform=ax.transAxes,
            fontsize=8, fontweight='bold')

# Shared colorbar on the right side
cbar = fig.colorbar(im, ax=axes, location='right',
                    fraction=0.03, pad=0.02, extend='both')
cbar.set_label("Δ Ice thickness (m)")

plt.savefig("../figures/AIS_FRIS_ROSS_diff_8panel.png",
            dpi=600, bbox_inches='tight')
print("Saved 8-panel ΔH figure.")


# =====================================================================
# EIGHT-PANEL ΔVELOCITY MAP: 4× Ross (top), 4× FRIS (bottom)
# =====================================================================

print("Starting 8-panel ΔVelocity figure...")

# Compute velocity magnitude for each loaded time slice
V_list = []
for i in range(len(files_to_load)):
    u = xVel[:,:,i].astype(float)
    v = yVel[:,:,i].astype(float)
    speed = np.sqrt(u*u + v*v)
    speed[speed == 0] = np.nan
    V_list.append(speed)

# Compute grounding lines
GL_list = []
for i in range(len(files_to_load)):
    GL = H_list[i] - Haf0
    GL_list.append(GL)

# Compute global min/max across ALL ΔV for symmetric colormap
all_dV = []
for (a, b) in pairs:
    dV = V_list[b] - V_list[a]
    all_dV.append(dV)

global_min = np.nanpercentile(all_dV, 1)
global_max = np.nanpercentile(all_dV, 99)
max_abs = max(abs(global_min), abs(global_max))
vmin, vmax = -max_abs, max_abs

# Figure layout: 2 rows × 4 columns
fig, axes = plt.subplots(2, 4, figsize=(11.0, 5.5))

for ax in axes.flat:
    ax.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)

# Diverging colormap for positive/negative speed change
cmap = plt.cm.RdBu_r

# Build panels
for col, (a, b) in enumerate(pairs):

    dV = V_list[b] - V_list[a]
    GL0 = GL_list[a]
    GL1 = GL_list[b]

    # ----------------------
    # Top row: Ross
    # ----------------------
    ax = axes[0, col]
    im = ax.pcolormesh(x1d, y1d, dV,
                       shading='auto',
                       cmap=cmap,
                       vmin=vmin, vmax=vmax,
                       rasterized=True)
    ax.contour(x1d, y1d, GL0, levels=[0], colors='grey', linewidths=0.6)
    ax.contour(x1d, y1d, GL1, levels=[0], colors='black', linewidths=0.6)

    ax.set_xlim(ROSS_xlim)
    ax.set_ylim(ROSS_ylim)
    ax.set_aspect('equal', adjustable='box')

    ax.text(0.02, 0.97, f"{chr(97+col)})",
            transform=ax.transAxes, ha='left', va='top', fontweight='bold')
    ax.text(0.5, 1.05, f"Δ|V| {years_to_load[a]} → {years_to_load[b]} years",
            transform=ax.transAxes, ha='center', va='bottom',
            fontsize=8, fontweight='bold')

    # ----------------------
    # Bottom row: FRIS
    # ----------------------
    ax = axes[1, col]
    im = ax.pcolormesh(x1d, y1d, dV,
                       shading='auto',
                       cmap=cmap,
                       vmin=vmin, vmax=vmax,
                       rasterized=True)
    ax.contour(x1d, y1d, GL0, levels=[0], colors='grey', linewidths=0.6)
    ax.contour(x1d, y1d, GL1, levels=[0], colors='black', linewidths=0.6)

    ax.set_xlim(FRIS_xlim)
    ax.set_ylim(FRIS_ylim)
    ax.set_aspect('equal', adjustable='box')

    ax.text(0.02, 0.97, f"{chr(97+col+4)})",
            transform=ax.transAxes, ha='left', va='top', fontweight='bold')
    ax.text(0.5, 1.05, f"Δ|V| {years_to_load[a]} → {years_to_load[b]} years",
            transform=ax.transAxes, ha='center', va='bottom',
            fontsize=8, fontweight='bold')

# Shared colorbar on right
cbar = fig.colorbar(im, ax=axes,
                    location='right',
                    fraction=0.03,
                    pad=0.02,
                    extend='both')
cbar.set_label("Δ Velocity magnitude (m/yr)")

plt.savefig("../figures/AIS_FRIS_ROSS_dV_8panel.png",
            dpi=600, bbox_inches='tight')

print("Saved ΔVelocity 8-panel figure.")
