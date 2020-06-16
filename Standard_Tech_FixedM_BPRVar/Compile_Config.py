import os
import math
from shutil import copyfile
import subprocess
# This file creates seed geometry for configurations, sets requirements and creates the variables for the optimizer to run. 
import time
from threading import Timer
### Needs more work -- Cruise Mach, # of Wheels, Gear Height
import os.path
from os import path
import pandas
import numpy as np

def main():
    # It records all data in a new folder for each combination of payload & range. 
    
    tech_string = "Turbofan_Econ"
    payload_array = [50, 100, 150, 200 ,250 ,300, 350, 400]
    range_array   = [1000,2000,3000,4000,5000,6000,7000]
    os.system("rm -r config_compilations.txt")
    f = open("config_compilations.txt","a+")
    dataFrames_A = pandas.DataFrame()
   
    for design_range in range_array:
        for payload in payload_array:
            folder_string = tech_string + "_" + str(payload) + "_" + str(design_range)
            cwd = os.getcwd()
            config_path = cwd + "/" + folder_string + "/config_overview.txt"
            if path.exists(config_path):
                f_cur_path = config_path
            config_path = cwd + "/" + folder_string + "/config_overview.txt_1"
            if path.exists(config_path):
                f_cur_path = config_path

            f_read_config = open(f_cur_path,"r")
            config_data = f_read_config.readlines()
            #config_data.split("=")
            count = 0
            f.write("\n\n" + str(design_range) + "\n")
            f.write(str(payload) + "\n")
            colnames = ['Labels','Results']
            cur_dataFrame = pandas.read_csv(f_cur_path, sep='=', encoding='utf-8', names=colnames, header=None)
           # cur_dataFrame.drop('Labels',axis=1,inplace = True)
            dataFrames_A = pandas.DataFrame(dataFrames_A,cur_dataFrame)

            #dfs = []
            #dfs.append(cur_dataFrame)
            #import pdb; pdb.set_trace()
            #if payload == 50 and design_range == 1000:
            #    dataFrames_A = cur_dataFrame
            #else:
            #dataFrames_A = pandas.concat(dfs, axis=1)
    dataFrames_A.to_csv("config_compiled.csv") 
    return
if __name__ == '__main__':
    main()