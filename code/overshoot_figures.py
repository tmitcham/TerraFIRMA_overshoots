# -*- coding: utf-8 -*-
"""
Created on Tue Oct 28 12:21:53 2025
This generates plots of interest from the TerraFIRMA overshoot simulations for both ice sheets and individual basins for Antarctica
@author: tm17544
"""

####################################################################################
# Imports

import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt

####################################################################################

# Select which plots to make
plot_grounded_smb_vs_time = False
plot_vaf_vs_time = False
plot_vaf_ross_fris_combined = True
plot_global_temp_vs_time = False
plot_combo_plots = False

####################################################################################

# Set options for plots
ICESHEET = "AIS" # options: "GrIS" or "AIS"

if ICESHEET == "AIS":
    basins = [0, 8, 9, 11, 16, 17] # 8/9 = Ross, 11 = ASE, 16/17 = Filchner-Ronne
    
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
        #'dc163': ['_1.5_Dn8-X_ZE-2', '#0003C7', (0, (1, 10))],
        #'dm929': ['_0_Dn4-X_ZE-2', '#000000', (0, (5, 10))],
        #'dm930': ['_0_Dn4-X_ZE-2', '#000000', (0, (5, 10))],
        #'dn822': ['_2_Dn8-X_ZE-4', '#168039', (0, (1, 10))]
    #    'dn966': ['_fix', '#ffc0cb', 'solid'],
    #    'do135': ['_fix', '#ffc0cb', 'solid'],
    #    'do136': ['_fix', '#ffc0cb', 'solid']
    }


else:
    basins = [0] # For GrIS, only whole ice sheet plot
    
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
        #'cz944': ['_Dn8-X_ZE-2', '#168039', 'dotted'],
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
        #'dm757': ['_Dn8-X_ZE-4', '#FA5B0F', 'dotted'],
        'dc565': ['_Dn4-X_ZE-2', '#168039', 'dashed'],
        'dd210': ['_Dn4-X_ZE-4', '#FA5B0F', 'dashed'],
        #'dc032': ['_Dn4-X_ZE-3', '#FFE11A', 'dashed'],
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
        #'dk554': ['_Dn8-X_ZE-6', '#964b00', 'dotted'],
        #'dk555': ['_Dn4-X_ZE-6', '#964b00', 'dashed'],
        #'dk556': ['_Dn2-X_ZE-6', '#964b00', 'dashdot'],
        'dm357': ['_Dn8-X_ZE-6', '#964b00', 'dotted'],
        'dm358': ['_Dn4-X_ZE-6', '#964b00', 'dashed'],
        'dm359': ['_Dn2-X_ZE-6', '#964b00', 'dashdot'],
        #'dc163': ['_1.5_Dn8-X_ZE-2', '#0003C7', (0, (1, 10))],
        #'dm929': ['_0_Dn4-X_ZE-2', '#000000', (0, (5, 10))],
        #'dm930': ['_0_Dn4-X_ZE-2', '#000000', (0, (5, 10))],
        #'dn822': ['_2_Dn8-X_ZE-4', '#168039', (0, (1, 10))]
    #    'dn966': ['_fix', '#ffc0cb', 'solid'],
    #    'do135': ['_fix', '#ffc0cb', 'solid'],
    #    'do136': ['_fix', '#ffc0cb', 'solid']
    }


plt.rcParams.update({'font.size': 6})

####################################################################################

# Load data from pickle file

if ICESHEET == "GrIS":
    with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/GrIS_data_overshoots_masked.pkl", 'rb') as file:
        icesheet_d = pickle.load(file)
        icesheet_d["cs568"][0] = icesheet_d["cs568"][0].drop(index=icesheet_d["cs568"][0].index[0], axis=0).reset_index(drop=True)

elif ICESHEET == "AIS":
    with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/AIS_data_overshoots_masked_newmask_1km.pkl", 'rb') as file:
        icesheet_d = pickle.load(file)

with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/atmos_data_overshoots.pkl", 'rb') as file:
    atmos_d = pickle.load(file)

####################################################################################

# function for smoothing time series for plotting
def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='valid')
    return y_smooth

# functions for converting mass change above flotation (in Gt) to sea level contribution (in mm) for second axes

def mass2sle(x):
    return x*(-1)/(361.8*1000)

def sle2mass(x):
    return x*(-1)*361.8*1000

####################################################################################

if plot_global_temp_vs_time:

    # Plot global T vs Time graph

    print("Starting Global Temp vs Time plot...")

    initialT = atmos_d["cx209"][0,1]

    count = 0

    box_size = 11

    plt.figure(figsize=(4, 3))

    for i, info in suite_ids.items():

        plot_data = atmos_d[i]
        time_series = plot_data[:,0]
        temp_series = plot_data[:,1] - initialT
        
        plt.plot(time_series-1850, temp_series, label = "_none", lw=0.8, linestyle="solid", color=info[1], alpha=0.1)
        
        ma_y = smooth(temp_series, box_size)
        
        ma_x = time_series
        ma_x = ma_x[int((box_size-1)/2):]
        ma_x = ma_x[:-int((box_size-1)/2)]
        
        plt.plot(ma_x-1850, ma_y, label = info[0], lw=0.8, linestyle=info[2], color=info[1])

        count = count + 1

    ax = plt.gca()

    ax.set_xlim([0, 900])
    ax.set_ylim([-3, 8.5])

    plt.ylabel('Global Mean $\Delta$T (K)')
    plt.xlabel('Years')
    plt.legend(loc = 'best', prop={'size': 5})

    handles, labels = ax.get_legend_handles_labels()

    handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dotted'))
    handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashed'))
    handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashdot'))
    labels.append('Dn8-X')
    labels.append('Dn4-X')
    labels.append('Dn2-X')

    ax.legend(handles, labels, bbox_to_anchor=(1.05, 1), loc = 'upper left', prop={'size': 5})

    print("Finished and saving Global Temp vs Time plot...")

    plt.savefig('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/GlobalTvsTime.png', dpi = 600, bbox_inches='tight')

####################################################################################

if plot_vaf_vs_time:

    # Plot VAF vs Time

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

        if ICESHEET == "GrIS":
            plt.title("Greenland Ice Sheet")
            
            plot_file_id = "whole"

        elif ICESHEET == "AIS":
        
            if basin == 0:
                
                plt.title("Antarctic Ice Sheet")
                
                plot_file_id = "whole"
            
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
                
        handles, labels = ax.get_legend_handles_labels()

        handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dotted'))
        handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashed'))
        handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashdot'))
        labels.append('Dn8-X')
        labels.append('Dn4-X')
        labels.append('Dn2-X')

        ax.legend(handles, labels, loc = 'best', prop={'size': 5})

        secax = ax.secondary_yaxis('right', functions=(mass2sle, sle2mass)) 
        secax.set_ylabel('Sea level contribution (m)')

        ax.set_xlim([0, 900])

        print(f"Finished and saving VAF vs Time plot for {ICESHEET}basin {basin}...")

        plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/{ICESHEET}_{plot_file_id}_basin_VAFvsTime.png", dpi = 600,  bbox_inches='tight')


    ####################################################################################

if plot_grounded_smb_vs_time:
    
    # Plot Grounded SMB vs Time

    box_size = 21

    print("Starting Grounded SMB vs Time plots for each basin...")

    for basin in basins:
        
        plt.figure(figsize=(4, 3))
        
        # icesheet_d["cw988"][basin] = icesheet_d["cw988"][basin].drop(index=icesheet_d["cw988"][basin].index[74], axis=0).reset_index(drop=True)

        count = 0

        for i, info in suite_ids.items():

            plot_data = icesheet_d[i]
            time_series = plot_data[basin]["time"]
            temp_series = plot_data[basin]["grounded_SMB"]*(0.918/1e9)

            #plt.plot(time_series-1850, temp_series, label = "_none", lw=0.8, linestyle="solid", color=info[1], alpha=0.025)
            
            ma_y = smooth(temp_series, box_size)
            
            ma_x = time_series
            ma_x = ma_x[int((box_size-1)/2):]
            ma_x = ma_x[:-int((box_size-1)/2)]
            
            plt.plot(ma_x-1850, ma_y, label = info[0], lw=0.8, linestyle=info[2], color=info[1])

            count = count + 1


        ax = plt.gca()

        plt.ylabel("Grounded SMB (Gt/yr)")
        plt.xlabel('Years')

        if ICESHEET == "GrIS":
            plt.title("Greenland Ice Sheet")
            
            plot_file_id = "whole"

        elif ICESHEET == "AIS":
        
            if basin == 0:
                
                plt.title("Antarctic Ice Sheet")
                
                plot_file_id = "whole"
            
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
                
        handles, labels = ax.get_legend_handles_labels()

        handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dotted'))
        handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashed'))
        handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashdot'))
        labels.append('Dn8-X')
        labels.append('Dn4-X')
        labels.append('Dn2-X')

        ax.legend(handles, labels, loc = 'best', prop={'size': 5})

        ax.set_xlim([0, 900])
        ax.set_ylim([-1600, 500])

        print(f"Finished and saving VAF vs Time plot for {ICESHEET}basin {basin}...")

        plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/{ICESHEET}_{plot_file_id}_basin_groundedSMBvsTime.png", dpi = 600,  bbox_inches='tight')


####################################################################################

if plot_combo_plots:

    # Create combo plots with VAF vs Time and SMB vs GSAT
    print("Starting combo plots for each basin...")
    for basin in basins:

        fig, ax = plt.subplots(4, 1, figsize=(4.72, 6.69))

        initialVAF = icesheet_d["cx209"][basin]["VAF"][0]
        initialVAFpi = icesheet_d["cs568"][basin]["VAF"][0]
        ctrl_data = icesheet_d["cs568"][basin]
        pi_VAF = ctrl_data["VAF"]

        count = 0

        for i, info in suite_ids.items():

            plot_data = icesheet_d[i][basin]

            VAF_data = plot_data["VAF"]
            time_series = plot_data["time"]

            if i == "cs568":

                ax[1].plot(time_series - 1850, (VAF_data - initialVAFpi)*(0.918/1e9), label = info[0], lw=0.8, color = info[1], linestyle = info[2])

            else:

                ax[1].plot(time_series - 1850, (VAF_data - initialVAF)*(0.918/1e9), label = info[0], lw=0.8, color = info[1], linestyle = info[2])

            count = count + 1

        ax[1].set_ylabel("Mass above\nflotation change (Gt)")
        ax[1].set_xlabel('Years')

        # Add a second y-axis for sea level equivalent
        secax = ax[1].secondary_yaxis('right', functions=(mass2sle, sle2mass)) 
        secax.set_ylabel('Sea level contribution (m)')

        ax[1].set_xlim([0, 900])

        ax[1].annotate('b)', xy=(1, 1), xycoords='axes fraction', xytext=(-1.0, -1.2), textcoords='offset fontsize', ha='center', fontsize=9)

        print("Finished VAF vs Time plot...")

        ####################################################################################

        # Plot SMB (grounded and floating) vs GSAT graph

        SMB = {}

        for i, info in suite_ids.items():
            
            SMB[i] = icesheet_d[i][0][["time","grounded_SMB","floating_SMB"]] 
            SMB[i] = pd.concat([SMB[i], pd.DataFrame(atmos_d[i][:,1])], axis=1)
            SMB[i].drop(SMB[i].tail(1).index,inplace=True)
            SMB[i].columns = ["time","grounded_SMB","floating_SMB","GSAT"]

            # Sort the rows into order of lowest to highest GSAT
            SMB[i] = SMB[i].sort_values(by="GSAT")

        print("Starting SMB vs GSAT plot...")

        count = 0

        box_size = 21

        initialT = atmos_d["cx209"][0,1]

        for i, info in suite_ids.items():
            
            plot_data = SMB[i]

            ax[2].plot(plot_data["GSAT"] - initialT, ((plot_data["grounded_SMB"])*(0.918/1e9)), label = info[0], lw=0.8, color = info[1], linestyle = info[2], alpha = 0.10)
            ax[3].plot(plot_data["GSAT"] - initialT, ((plot_data["floating_SMB"])*(0.918/1e9)), label = info[0], lw=0.8, color = info[1], linestyle = info[2], alpha = 0.10)
            
            ma_y_gr = smooth((plot_data["grounded_SMB"])*(0.918/1e9), box_size)
            ma_y_fl = smooth((plot_data["floating_SMB"])*(0.918/1e9), box_size)
            
            ma_x = (plot_data["GSAT"] - initialT).values
            ma_x = ma_x[int((box_size-1)/2):]
            ma_x = ma_x[:-int((box_size-1)/2)]

            ax[2].plot(ma_x, ma_y_gr, label = info[0], lw=0.8, color = info[1], linestyle = info[2])
            ax[3].plot(ma_x, ma_y_fl, label = info[0], lw=0.8, color = info[1], linestyle = info[2])

            count = count + 1

        ax[2].set_ylabel("Grounded SMB (Gt yr$^{-1}$)")
        ax[3].set_ylabel("Floating SMB (Gt yr$^{-1}$)")
        ax[2].set_xlabel('$\Delta$GSAT (K)')
        ax[3].set_xlabel('$\Delta$GSAT (K)')


        ax[2].annotate('c)', xy=(1, 1), xycoords='axes fraction', xytext=(-1.0, -1.2), textcoords='offset fontsize', ha='center', fontsize=9)
        ax[3].annotate('d)', xy=(1, 1), xycoords='axes fraction', xytext=(-1.0, -1.2), textcoords='offset fontsize', ha='center', fontsize=9)

        print("Finished SMB vs GSAT plot...")

        ####################################################################################

        # Plot Volume vs Time graph

        print("Starting Volume vs Time plot...")

        count = 0

        initialVol = icesheet_d["cx209"][basin]["grounded_vol"][0] + icesheet_d["cx209"][basin]["floating_vol"][0]
        initialVolpi = icesheet_d["cs568"][basin]["grounded_vol"][0] + icesheet_d["cs568"][basin]["floating_vol"][0]

        for i, info in suite_ids.items():

            plot_data = icesheet_d[i][basin]

            IS_data_vol = plot_data["grounded_vol"] + plot_data["floating_vol"]
            time_series = plot_data["time"]

            if i == "cs568":

                ax[0].plot(time_series - 1850, (IS_data_vol - initialVolpi)*(0.918/1e9), label = info[0], lw=0.8, color = info[1], linestyle = info[2])

            else:

                ax[0].plot(time_series - 1850, (IS_data_vol - initialVol)*(0.918/1e9), label = info[0], lw=0.8, color = info[1], linestyle = info[2])

            count = count + 1

        ax[0].set_ylabel("Mass change (Gt)")
        ax[0].set_xlabel('Years')
        ax[0].set_xlim([0, 900])

        #handles, labels = ax[0].get_legend_handles_labels()
        
        #ax[0].legend(handles, labels, loc = 'best', prop={'size': 8})
        #handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashed'))
        #labels.append('Dn4-X')
        #ax[0].legend(handles, labels, loc = 'lower left', prop={'size': 5})

        ax[0].annotate('a)', xy=(1, 1), xycoords='axes fraction', xytext=(-1.0, -1.2), textcoords='offset fontsize', ha='center', fontsize=9)

        plt.tight_layout()

        print("Finished Volume vs Time plot...")

        print("Saving plot to file...")

        plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/{ICESHEET}_{basin}_VafVolSmb.png", dpi = 600,  bbox_inches='tight')  

        print("Plot saved successfully.")

    ####################################################################################

if plot_vaf_ross_fris_combined:

    # Plot VAF vs Time

    print("Starting VAF vs Time plots for Ross and FRIS basin...")
        
    plt.figure(figsize=(4, 3))
    
    # icesheet_d["cw988"][basin] = icesheet_d["cw988"][basin].drop(index=icesheet_d["cw988"][basin].index[74], axis=0).reset_index(drop=True)

    count = 0

    for i, info in suite_ids.items():

        plot_data = icesheet_d[i]
        
        initialVAF = icesheet_d["cx209"][8]["VAF"][0] + icesheet_d["cx209"][9]["VAF"][0]
        initialVAFpi = icesheet_d["cs568"][8]["VAF"][0] + icesheet_d["cs568"][9]["VAF"][0]
        
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

    if ICESHEET == "GrIS":
        plt.title("Greenland Ice Sheet")
        
        plot_file_id = "whole"

    elif ICESHEET == "AIS":
    
        if basin == 0:
            
            plt.title("Antarctic Ice Sheet")
            
            plot_file_id = "whole"
        
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
            
    handles, labels = ax.get_legend_handles_labels()

    handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dotted'))
    handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashed'))
    handles.append(plt.Line2D([0], [0], color='black', lw=0.8, linestyle='dashdot'))
    labels.append('Dn8-X')
    labels.append('Dn4-X')
    labels.append('Dn2-X')

    ax.legend(handles, labels, loc = 'best', prop={'size': 5})

    secax = ax.secondary_yaxis('right', functions=(mass2sle, sle2mass)) 
    secax.set_ylabel('Sea level contribution (m)')

    ax.set_xlim([0, 900])

    print(f"Finished and saving VAF vs Time plot for {ICESHEET}basin {basin}...")

    plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/{ICESHEET}_{plot_file_id}_basin_VAFvsTime.png", dpi = 600,  bbox_inches='tight')