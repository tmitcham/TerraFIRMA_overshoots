####################################################################################
# Imports

import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt

####################################################################################

id = ["cx209", "cy837", "cy838", "cz375", "cz376", "cz377"]

run_type = ["Ramp-Up", "1.5C", "2C", "3C", "4C", "5C"]

runs = dict(zip(id, run_type)) 

line_cols = ['#C30F0E','#0003C7','#168039','#FFE11A','#FA5B0F','#9C27B0']
line_stys = ["solid","solid","solid","solid","solid","solid"]

basins = list(range(17))
#resolutions = ["500m", "1km", "2km", "4km", "8km"]
resolutions = ["4km"]

####################################################################################

# Loop through each resolution and plot VAF vs Time for each basin

for res in resolutions:
    
    print(f"Working on data using the {res} mask resolution...")

    print("Loading ice sheet data from relevant file...")

    with open(f"../processed_data/testing_AIS_basins_data.pkl", 'rb') as file:

        icesheet_d = pickle.load(file)
    
    print("Starting VAF vs Time plots for each basin...")

    for basin in basins:
        
        plt.figure(figsize=(4, 3))

        count = 0

        # Plot VAF vs Time graph for each basin

        for i in id:

            plot_data = icesheet_d[i]
            
            initialVAF = icesheet_d["cx209"][basin].iloc[0,55]
                
            plt.plot(plot_data[basin].iloc[:,2] - 1850, (plot_data[basin].iloc[:,55] - initialVAF)*(918*1000/(1028*3.625e14)), label = runs[i], lw=0.8, color = line_cols[count], linestyle = line_stys[count])
            #plt.plot(plot_data[basin].iloc[:,2] - 1850, (plot_data[basin].iloc[:,61] - initialVAF)*(918*1000/(1028*3.625e14)))    

            count = count + 1

        ax = plt.gca()

        plt.ylabel("$\Delta$VAF (-1 * mm SLE)")
        plt.xlabel('Years')
        plt.title(f"Basin {basin}")
        plt.legend(loc = 'best', prop={'size': 5})

        print(f"Finished and saving VAF vs Time plot for basin {basin}...")

        plt.savefig(f"Testing_MaskRes_4km_Basin_{basin}_VAFvsTime.png", dpi = 600,  bbox_inches='tight')