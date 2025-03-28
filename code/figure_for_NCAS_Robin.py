# Plot of AIS sea level contribution in a few select overshoot simulations
# For NCAS poster of TerraFIRMA OS simulations

# Imports
import pickle
import matplotlib.pyplot as plt

# Plotting options
basin = 0 # 0 = whole AIS, 8 = Ross, 10 = ASE, 15 = Filchner-Ronne
plot_fontsize = 8
legend_fontsize = 6
plot_linewidth = 1.2
plot_save_filepath = '/gws/nopw/j04/terrafirma/tm17544/TerraFIRMA_overshoots/figures/'
plot_save_filename = f"SLC_vs_Time_basin_{basin}.png"
ZE_0_col = '#000000'
ZE_0_sty = 'dotted'
Up8_col = '#66c2a5'
ZE_2_col = '#fc8d62'
ZE_4_col = '#8da0cb'
Up_and_ZE_sty = 'solid'
Dn_sty = 'dashed'

# IDs
id = ["cs568", "cx209", "cy838", "cz376", "dc051", "dc123"]
run_type = ["ZE-0","Up8", "ZE-2", "ZE-4", "Dn4-2", "Dn4-4"]
runs = dict(zip(id, run_type)) 
line_cols = [ZE_0_col, Up8_col, ZE_2_col, ZE_4_col, ZE_2_col, ZE_4_col]
line_stys = [ZE_0_sty, Up_and_ZE_sty, Up_and_ZE_sty, Up_and_ZE_sty, Dn_sty, Dn_sty]

# Load data
with open("/gws/nopw/j04/terrafirma/tm17544/TerraFIRMA_overshoots/processed_data/AIS_data_overshoots_masked.pkl", 'rb') as file:
    icesheet_d = pickle.load(file)

# Plot data
plt.rcParams.update({'font.size': plot_fontsize})
plt.figure(figsize=(4, 3))

initialSLE = icesheet_d["cx209"][basin]["SLE"][0]
initialSLEpi = icesheet_d["cs568"][basin]["SLE"][0]

count = 0

ctrl_data = icesheet_d["cs568"][basin]
pi_SLE = ctrl_data["SLE"]

for i in id:

    plot_data = icesheet_d[i][basin]

    SLE_data = plot_data["SLE"]
    time_series = plot_data["time"]

    if i == "cs568":
        
        plt.plot(time_series - 1850, -1*(SLE_data - initialSLEpi), label = runs[i], lw=plot_linewidth, color = line_cols[count], linestyle = line_stys[count])

    else:
        
        plt.plot(time_series - 1850, -1*(SLE_data - initialSLE), label = runs[i], lw=plot_linewidth, color = line_cols[count], linestyle = line_stys[count])

    count = count + 1

plt.legend(loc = 'best', prop={'size': legend_fontsize})

ax = plt.gca()
ax.set_ylabel("Sea level contribution (m)")
ax.set_xlabel('Years')
ax.set_xlim([0, 775])

# Save figure
plt.savefig(f"{plot_save_filepath}/{plot_save_filename}", dpi = 600, bbox_inches='tight')