####################################################################################
# Imports
import numpy as np
import pickle
import matplotlib.pyplot as plt
import pandas as pd

####################################################################################

# Read ice sheet data

ICESHEET = "AIS" # AIS or GrIS

if ICESHEET == "AIS":
    with open('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/AIS_data_overview.pkl', 'rb') as file:
        icesheet_d = pickle.load(file) 

    # only keep the first 50 years of data for cs568 to match the pyglint processed data (which only has 50 years of data)
    icesheet_d["cs568"][0] = icesheet_d["cs568"][0].iloc[:49]

    ## for comparison of methods load some cs568 data processed with pyglint
    with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/cs568_SMB_AIS_GR_FL_masked_new_mask.pkl", 'rb') as file:
        cs568_SMB = pickle.load(file)

    ## and load the data calculated with the new code
    with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/cs568_SMB_AIS_GR_FL_masked_updated_code.pkl", 'rb') as file:
        cs568_SMB_updated = pickle.load(file)

    ## and load the data calculated with the new code and new units
    with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/cs568_SMB_AIS_GR_FL_masked_updated_code_and_units.pkl", 'rb') as file:
        cs568_SMB_updated_units = pickle.load(file)

    with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/cs568_pyglint_SMB_AIS_GR_FL_masked_2502.pkl", 'rb') as file:
        cs568_SMB_Tom = pickle.load(file)

    cs568_SMB = pd.DataFrame(cs568_SMB, columns=['time', 'total_SMB', 'grounded_SMB', 'floating_SMB'])
    cs568_SMB_updated = pd.DataFrame(cs568_SMB_updated, columns=['time', 'total_SMB', 'grounded_SMB', 'floating_SMB'])
    cs568_SMB_updated_units = pd.DataFrame(cs568_SMB_updated_units, columns=['time', 'total_SMB', 'grounded_SMB', 'floating_SMB'])
    cs568_SMB_Tom = pd.DataFrame(cs568_SMB_Tom, columns=['time', 'total_SMB', 'grounded_SMB', 'floating_SMB'])

    cs568_SMB = cs568_SMB.iloc[1:50]
    cs568_SMB_updated = cs568_SMB_updated.iloc[1:]
    cs568_SMB_updated_units = cs568_SMB_updated_units.iloc[1:50]
    cs568_SMB_Tom = cs568_SMB_Tom.iloc[1:]

    cs568_SMB_updated.time = cs568_SMB_updated.time + 1 -1950
    cs568_SMB_updated_units.time = cs568_SMB_updated_units.time
    #cs568_SMB_Tom.time = cs568_SMB_Tom.time + 1

    cs568_SMB = cs568_SMB.reset_index(drop=True)
    cs568_SMB_updated = cs568_SMB_updated.reset_index(drop=True)
    cs568_SMB_updated_units = cs568_SMB_updated_units.reset_index(drop=True)
    cs568_SMB_Tom = cs568_SMB_Tom.reset_index(drop=True)

elif ICESHEET == "GrIS":

    with open('C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/GrIS_data_overview.pkl', 'rb') as file:
        icesheet_d = pickle.load(file) 

    icesheet_d["cs568"][0] = icesheet_d["cs568"][0].drop(index=icesheet_d["cs568"][0].index[0], axis=0).reset_index(drop=True)

    # only keep the first 50 years of data for cs568 to match the pyglint processed data (which only has 50 years of data)
    icesheet_d["cs568"][0] = icesheet_d["cs568"][0].iloc[:49]

    ## for comparison of methods load some cs568 data processed with pyglint
    with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/cs568_SMB_GrIS_GR_FL_masked_new_mask.pkl", 'rb') as file:
        cs568_SMB = pickle.load(file)

    ## and load the data calculated with the new code and new units
    with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/cs568_SMB_GrIS_GR_FL_masked_updated_code_and_units.pkl", 'rb') as file:
        cs568_SMB_updated_units = pickle.load(file)

    with open("C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/processed_data/cs568_SMB_GrIS_GR_FL_Tom_change.pkl", 'rb') as file:
        cs568_SMB_Tom = pickle.load(file)

    cs568_SMB = pd.DataFrame(cs568_SMB, columns=['time', 'total_SMB'])
    cs568_SMB_updated_units = pd.DataFrame(cs568_SMB_updated_units, columns=['time', 'total_SMB'])
    cs568_SMB_Tom = pd.DataFrame(cs568_SMB_Tom, columns=['time', 'total_SMB'])

    cs568_SMB = cs568_SMB.iloc[1:50]
    cs568_SMB_updated_units = cs568_SMB_updated_units.iloc[1:]
    cs568_SMB_Tom = cs568_SMB_Tom.iloc[1:]

    cs568_SMB_updated_units.time = cs568_SMB_updated_units.time

    cs568_SMB = cs568_SMB.reset_index(drop=True)
    cs568_SMB_updated_units = cs568_SMB_updated_units.reset_index(drop=True)
    cs568_SMB_Tom = cs568_SMB_Tom.reset_index(drop=True)

####################################################################################

# Plots to explore why using pyglint and BISICLES diagnostic tools (post Glint transform) 
# are giving different results

cs568_diff = cs568_SMB_updated_units.total_SMB - (icesheet_d["cs568"][0].grounded_SMB + icesheet_d["cs568"][0].floating_SMB)*(0.918/1e9)
cs568_diff_prop = cs568_diff/((icesheet_d["cs568"][0].grounded_SMB + icesheet_d["cs568"][0].floating_SMB)*(0.918/1e9))

# Start with a figure of just SMBs (total, grounded, floating) vs time for cx209 and cs568 raw data (no smoothing)

plt.figure(figsize=(4, 3))

plt.plot(cs568_SMB.time, cs568_SMB.total_SMB, label = "cs568 pyglint", lw=0.8)

if ICESHEET == "AIS":
    plt.plot(cs568_SMB_updated.time, cs568_SMB_updated.total_SMB, label = "cs568 pyglint updated", lw=0.8, color = "red")

plt.plot(cs568_SMB_Tom.time, cs568_SMB_Tom.total_SMB*(1000/918), label = "cs568 Tom change", lw=0.8, color = "cyan")
plt.plot(cs568_SMB_updated_units.time, cs568_SMB_updated_units.total_SMB, label = "cs568 pyglint updated code & units", lw=0.8)
plt.plot(icesheet_d["cs568"][0].time-1850, (icesheet_d["cs568"][0].grounded_SMB + icesheet_d["cs568"][0].floating_SMB)*(0.918/1e9), label = "cs568 orig", lw=0.8)

if ICESHEET == "GrIS":
    plt.title("Greenland Ice Sheet")

if ICESHEET == "AIS":
    plt.title("Antarctic Ice Sheet")

ax = plt.gca()
ax.set_ylabel("Total SMB (Gt/yr)")
ax.set_xlabel('Years')
ax.set_xlim([0, 50])
ax.legend(loc = 'best', prop={'size': 5})

if ICESHEET == "AIS":
    plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/cs568_SMB_pyglint_orig_comparison_total_SMB_AIS.png", dpi = 600,  bbox_inches='tight')
elif ICESHEET == "GrIS":
    plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/cs568_SMB_pyglint_orig_comparison_total_SMB_GrIS.png", dpi = 600,  bbox_inches='tight')

### now make the difference plots (first absolute, then proportional differences) again broken down by total, grounded and floating SMB

plt.figure(figsize=(4, 3))

plt.plot(cs568_SMB_updated_units.time, cs568_diff, label = "cs568 diff (final_pyglint - orig)", lw=0.8)

ax = plt.gca()
ax.set_ylabel("Difference in total SMB (Gt/yr)")
ax.set_xlabel('Years')
ax.set_xlim([0, 50])
ax.legend(loc = 'best', prop={'size': 5})

#plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/cs568_SMB_pyglint_orig_comparison_total_SMB_diff_GrIS.png", dpi = 600,  bbox_inches='tight')

plt.figure(figsize=(4, 3))
plt.plot(cs568_SMB_updated_units.time, cs568_diff_prop, label = "cs568 diff prop (final_pyglint - orig)", lw=0.8)

ax = plt.gca()
ax.set_ylabel("Prop difference in total SMB")
ax.set_xlabel('Years')
ax.set_xlim([0, 50])
ax.legend(loc = 'best', prop={'size': 5})

#plt.savefig(f"C:/Users/tm17544/OneDrive - University of Bristol/Projects/TerraFIRMA/figures/cs568_SMB_pyglint_orig_comparison_total_SMB_diff_prop_GrIS.png", dpi = 600,  bbox_inches='tight')
