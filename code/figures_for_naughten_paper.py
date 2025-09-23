####################################################################################
# Imports

import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt

####################################################################################

suite_ids = {
    'cs568': ['ZE-0', '#000000', 'solid'],
    'cx209': ['Up8', '#C30F0E', 'solid'],
    'cw988': ['_Up8', '#C30F0E', 'solid'],
    'cw989': ['_Up8', '#C30F0E', 'solid'],
    'cw990': ['_Up8', '#C30F0E', 'solid'],
    'cy837': ['ZE-1.5', '#0003C7', 'solid'],
    'cy838': ['ZE-2', '#168039', 'solid'],
    'cz374': ['ZE-2.5', '#ffc0cb', 'solid'],
    'cz375': ['ZE-3', '#FFE11A', 'solid'],
    'cz376': ['ZE-4', '#FA5B0F', 'solid'],
    'cz377': ['ZE-5', '#9C27B0', 'solid'],
    'cz378': ['ZE-6', '#964b00', 'solid'],
    'cz834': ['_ZE-1.5', '#0003C7', 'solid'],
    'cz855': ['_ZE-2', '#168039', 'solid'],
    'cz859': ['_ZE-2.5', '#ffc0cb', 'solid'],
    'db587': ['_ZE-3', '#FFE11A', 'solid'],
    'db723': ['_ZE-4', '#FA5B0F', 'solid'],
    'db731': ['_ZE-5', '#9C27B0', 'solid'],
    'da087': ['_ZE-1.5', '#0003C7', 'solid'],
    'da266': ['_ZE-2', '#168039', 'solid'],
    'db597': ['_ZE-3', '#FFE11A', 'solid'],
    'db733': ['_ZE-4', '#FA5B0F', 'solid'],
    'dc324': ['_ZE-5', '#9C27B0', 'solid'],
    'cz944': ['_Dn8-X_ZE-2', '#168039', 'dotted'],
    'di335': ['_Dn8-X_ZE-2', '#168039', 'dotted'],
    'da800': ['_Dn8-X_ZE-2', '#168039', 'dotted'],
    'da697': ['_Dn8-X_ZE-1.5', '#0003C7', 'dotted'],
    'da892': ['_Dn8-X_ZE-4', '#FA5B0F', 'dotted'],
    'db223': ['_Dn8-X_ZE-3', '#FFE11A', 'dotted'],
    'df453': ['_Dn8-X_ZE-3', '#FFE11A', 'dotted'],
    'de620': ['_Dn8-X_ZE-3', '#FFE11A', 'dotted'],
    'dc251': ['_Dn8-X_ZE-5', '#9C27B0', 'dotted'],
    'dc051': ['_Dn4-X_ZE-2', '#168039', 'dashed'],
    'dc052': ['_Dn4-X_ZE-1.5', '#0003C7', 'dashed'],
    'dc248': ['_Dn4-X_ZE-1.5', '#0003C7', 'dashed'],
    'dc249': ['_Dn4-X_ZE-3', '#FFE11A', 'dashed'],
    'dm757': ['_Dn8-X_ZE-4', '#FA5B0F', 'dotted'],
    'dc565': ['_Dn4-X_ZE-2', '#168039', 'dashed'],
    'dd210': ['_Dn4-X_ZE-4', '#FA5B0F', 'dashed'],
    'dc032': ['_Dn4-X_ZE-3', '#FFE11A', 'dashed'],
    'df028': ['_Dn4-X_ZE-3', '#FFE11A', 'dashed'],
    'de621': ['_Dn4-X_ZE-3', '#FFE11A', 'dashed'],
    'dc123': ['_Dn4-X_ZE-4', '#FA5B0F', 'dashed'],
    'dc130': ['_Dn4-X_ZE-5', '#9C27B0', 'dashed'],
    'df025': ['_Dn2-X_ZE-2', '#168039', 'dashdot'],
    'df027': ['_Dn2-X_ZE-2', '#168039', 'dashdot'],
    'df021': ['_Dn2-X_ZE-3', '#FFE11A', 'dashdot'],
    'df023': ['_Dn2-X_ZE-3', '#FFE11A', 'dashdot'],
    'dh541': ['_Dn2-X_ZE-4', '#FA5B0F', 'dashdot'],
    'dh859': ['_Dn2-X_ZE-4', '#FA5B0F', 'dashdot'],
    'dg093': ['_Dn8-X_ZE-5', '#9C27B0', 'dotted'],
    'dg094': ['_Dn4-X_ZE-5', '#9C27B0', 'dashed'],
    'dg095': ['_Dn2-X_ZE-5', '#9C27B0', 'dashdot'],
    'de943': ['_Dn8-X_ZE-6', '#964b00', 'dotted'],
    'de962': ['_Dn4-X_ZE-6', '#964b00', 'dashed'],
    'de963': ['_Dn2-X_ZE-6', '#964b00', 'dashdot'],
    'dk554': ['_Dn8-X_ZE-6', '#964b00', 'dotted'],
    'dk555': ['_Dn4-X_ZE-6', '#964b00', 'dashed'],
    'dk556': ['_Dn2-X_ZE-6', '#964b00', 'dashdot'],
    'dm357': ['_Dn8-X_ZE-6', '#964b00', 'dotted'],
    'dm358': ['_Dn4-X_ZE-6', '#964b00', 'dashed'],
    'dm359': ['_Dn2-X_ZE-6', '#964b00', 'dashdot'],
    'dc163': ['_1.5_Dn8-X_ZE-2', '#0003C7', (0, (1, 10))],
    'dm929': ['_0_Dn4-X_ZE-2', '#000000', (0, (5, 10))],
    'dm930': ['_0_Dn4-X_ZE-2', '#000000', (0, (5, 10))],
    'dn822': ['_2_Dn8-X_ZE-4', '#168039', (0, (1, 10))]
#    'dn966': ['_fix', '#ffc0cb', 'solid'],
#    'do135': ['_fix', '#ffc0cb', 'solid'],
#    'do136': ['_fix', '#ffc0cb', 'solid']
}

basins = [0, 8, 9, 11, 16, 17] # 8/9 = Ross, 11 = ASE, 16/17 = Filchner-Ronne

# Plot settings
plt.rcParams.update({'font.size': 6})

####################################################################################

# Load data from pickle file

with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/AIS_data_overshoots_masked_newmask_1km.pkl", 'rb') as file:
    icesheet_d = pickle.load(file)

####################################################################################

# functions for converting mass change above flotation (in Gt) to sea level contribution (in mm) for second axes

def mass2sle(x):
    return x*(-1)/361.8

def sle2mass(x):
    return x*(-1)*361.8

####################################################################################

# Loop through each basin and plot VAF vs Time

print("Starting VAF vs Time plots for each basin...")

for basin in basins:
    
    plt.figure(figsize=(4, 3))
    
    # icesheet_d["cw988"][basin] = icesheet_d["cw988"][basin].drop(index=icesheet_d["cw988"][basin].index[74], axis=0).reset_index(drop=True)

    count = 0

    for i, info in suite_ids.items():

        plot_data = icesheet_d[i]
        
        initialVAF = icesheet_d["cx209"][basin]["VAF"][0]
        initialVAFpi = icesheet_d["cs568"][basin]["VAF"][0]
        
        if i == "cs568":
            
            # *(0.918/1e9) to convert from m^3 to Gt
            plt.plot(plot_data[basin]["time"] - 1850, (plot_data[basin]["VAF"] - initialVAFpi)*(0.918/1e9), label = info[0], lw=0.8, color = info[1], linestyle = info[2])

        else:
            
            # *(0.918/1e9) to convert from m^3 to Gt
            plt.plot(plot_data[basin]["time"] - 1850, (plot_data[basin]["VAF"] - initialVAF)*(0.918/1e9), label = info[0], lw=0.8, color = info[1], linestyle = info[2])
        
        count = count + 1

    ax = plt.gca()
    
    plt.ylabel("Mass above flotation change (Gt)")
    plt.xlabel('Years')
    
    if basin == 0:
        
        plt.title("Antarctic Ice Sheet")
        
        plot_file_id = "AIS"
    
    elif basin == 8:

        plt.title("Ross Basin EAIS")
        
        plot_file_id = "Ross_eais"
        
    elif basin == 9:
        
        plt.title("Ross Basin WAIS")
        
        plot_file_id = "Ross_wais"
        
    elif basin == 16:

        plt.title("Filchner-Ronne Basin WAIS")
        
        plot_file_id = "FRIS_wais"
        
    elif basin == 17:

        plt.title("Filchner-Ronne Basin EAIS")
        
        plot_file_id = "FRIS_eais"

    elif basin == 11:

        plt.title("Amundsen Sea Basin")
        
        plot_file_id = "ASE"

    ax.legend(loc = 'best', prop={'size': 5})

    secax = ax.secondary_yaxis('right', functions=(mass2sle, sle2mass)) 
    secax.set_ylabel('Sea level contribution (mm)')

    ax.set_xlim([0, 900])

    print(f"Finished and saving VAF vs Time plot for basin {basin}...")

    plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/{plot_file_id}_basin_VAFvsTime.png", dpi = 600,  bbox_inches='tight')