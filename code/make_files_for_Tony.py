####################################################################################
# Imports
import cf
import cfplot as cfp
import pandas as pd
import os
import fnmatch
import numpy as np
import pickle

####################################################################################

id = ["cx209", "cy837", "cy838", "cz375", "cz376", "cz377"]

with open('../processed_data/icesheet_data_GrIS.pkl', 'rb') as file:

        icesheet_d = pickle.load(file)

for i in id:
        
        data_to_write = icesheet_d[i].iloc[:, [0,1,3,8]]

        file_name = '../processed_data/' + i + '_GrIS_VAF.csv'

        data_to_write.to_csv(file_name, index=False, header=True)




with open('../processed_data/icesheet_data.pkl', 'rb') as file:

        icesheet_d = pickle.load(file)


for i in id:
        
        data_to_write = icesheet_d[i].iloc[:, [0,1,3,8]]

        file_name = '../processed_data/' + i + '_AIS_VAF.csv'

        data_to_write.to_csv(file_name, index=False, header=True)