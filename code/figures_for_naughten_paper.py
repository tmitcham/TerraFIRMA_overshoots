####################################################################################
# Imports

import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt

####################################################################################

id=["cs568", "cx209", "cw988", "cw989", "cw990", "cy837", "cy838", "cz375", "cz376", "cz377", "cz378",
    "cz834", "cz855", "db587", "db723", "db731", "da087", "da266", "db597", "db733", "dc324",
    "cz944", "di335", "da800", "da697", "da892", "db223", "df453", "de620", "dc251",
    "dc051", "dc052", "dc248", "dc249", "dc565", "dd210", "df028", "de621", "dc123", "dc130",
    "df025", "df027", "df021", "df023", "dh541", "dh859", "de943", "de962", "de963","dg093", "dg094", "dg095"]

run_type = ["ZE-0","Up8", "_Up8", "_Up8", "_Up8", "ZE-1.5", "ZE-2", "ZE-3", "ZE-4", "ZE-5", "ZE-6",
            "_ZE-1.5", "_ZE-2", "_ZE-3", "_ZE-4", "_ZE-5", "_ZE-1.5", "_ZE-2", "_ZE-3", "_ZE-4", "_ZE-5",
            "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X",
            "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X",
            "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X", "_X","_X", "_X", "_X"]
            
runs = dict(zip(id, run_type)) 


line_cols = ['#000000','#C30F0E','#C30F0E','#C30F0E','#C30F0E','#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0','#964b00',
             '#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0', '#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0',
             '#168039','#168039','#168039','#0003C7','#FA5B0F','#FFE11A','#FFE11A','#FFE11A','#9C27B0',
             '#168039','#0003C7','#0003C7','#FFE11A','#168039','#FA5B0F','#FFE11A','#FFE11A','#FA5B0F','#9C27B0',
             '#168039','#168039','#FFE11A','#FFE11A','#FA5B0F','#FA5B0F','#964b00','#964b00','#964b00','#9C27B0','#9C27B0','#9C27B0']

'''
line_cols = ['Blue','Black','Black','Black','Black','Lawngreen','Goldenrod','Red','Sienna','Pink','Indigo',
             'Lawngreen','Goldenrod','Red','Sienna','Pink', 'Lawngreen','Goldenrod','Red','Sienna','Pink',
             'Goldenrod','Goldenrod','Goldenrod','Lawngreen','Sienna','Red','Red','Red','Pink',
             'Goldenrod','Lawngreen','Lawngreen','Red','Goldenrod','Sienna','Red','Red','Sienna','Pink',
             'Goldenrod','Goldenrod','Red','Red','Sienna','Sienna','Indigo','Indigo','Indigo','Pink','Pink','Pink']
'''
line_stys = ["solid","solid","solid","solid","solid","solid","solid","solid","solid","solid","solid",
             "solid","solid","solid","solid","solid","solid","solid","solid","solid","solid",
             "dotted","dotted","dotted","dotted","dotted","dotted","dotted","dotted","dotted",
             "dashed","dashed","dashed","dashed","dashed","dashed","dashed","dashed","dashed","dashed",
             "dashdot","dashdot","dashdot","dashdot","dashdot","dashdot","dotted","dashed","dashdot","dotted","dashed","dashdot"]


basins = [8, 10, 15] # 8 = Ross, 15 = Filchner-Ronne

# Plot settings
plt.rcParams.update({'font.size': 7.5})

####################################################################################

# Load data from pickle file

with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/AIS_data_overshoots_masked.pkl", 'rb') as file:
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
    
    icesheet_d["cw988"][basin] = icesheet_d["cw988"][basin].drop(index=icesheet_d["cw988"][basin].index[74], axis=0).reset_index(drop=True)


    count = 0

    for i in id:

        plot_data = icesheet_d[i]
        
        initialVAF = icesheet_d["cx209"][basin]["VAF"][0]
        initialVAFpi = icesheet_d["cs568"][basin]["VAF"][0]
        
        if i == "cs568":
            
            # *(0.918/1e9) to convert from m^3 to Gt
            plt.plot(plot_data[basin]["time"] - 1850, (plot_data[basin]["VAF"] - initialVAFpi)*(0.918/1e9), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])

        else:
            
            # *(0.918/1e9) to convert from m^3 to Gt
            plt.plot(plot_data[basin]["time"] - 1850, (plot_data[basin]["VAF"] - initialVAF)*(0.918/1e9), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
        
        count = count + 1

    ax = plt.gca()
    
    plt.ylabel("Mass change (Gt)")
    plt.xlabel('Years')
    
    plt.grid(linestyle='-', lw=0.1)
    
    if basin == 8:

        plt.title("Ross Basin")
        
        plot_file_id = "Ross"
        
    elif basin == 15:

        plt.title("Filchner-Ronne Basin")
        
        plot_file_id = "FRIS"

    elif basin == 10:

        plt.title("Amundsen Sea Basin")
        
        plot_file_id = "ASE"
        

    handles, labels = ax.get_legend_handles_labels()
    handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dotted'))
    handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashed'))
    handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashdot'))
    labels.append('Dn8-X')
    labels.append('Dn4-X')
    labels.append('Dn2-X')

    ax.legend(handles, labels, loc = 'best', prop={'size': 5})
    
    secax = ax.secondary_yaxis('right', functions=(mass2sle, sle2mass)) 
    secax.set_ylabel('Sea level contribution (mm)')

    ax.set_xlim([0, 750])

    print(f"Finished and saving VAF vs Time plot for basin {basin}...")

    plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/{plot_file_id}_basin_VAFvsTime.png", dpi = 600,  bbox_inches='tight')