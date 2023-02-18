#!/usr/bin/env python
# coding: utf-8
# Author Prakash Perimbeti
# Date: 02/16/2023

#standard imports
import sys
import os
from os.path import exists
import ecg_plot
from pathlib import Path
import pandas as pd
import math
import scipy



#Check converted consolidated csv file is available

def getConsolidatedData(filename):
    df = pd.DataFrame()

    file_exists = exists(filename)

    if file_exists:
        df = pd.read_csv(filename)
    else:
        result = list(Path(".").rglob("*.[jJ][sS][oO][nN]"))
        print(len(result))  
        # Read json files from List
        total = pd.concat(map(pd.read_json, result))
        print(len(result), "files:", total.shape[0], total.shape[1])
        total.head(5)
        final = []
        for i in range(len(result)):
            tmp = pd.read_json(result[i])
            axM = getMagnitudeList(tmp)
            axV = getVelocityList(tmp)
            timelist =  getTimeSeconds(tmp)
            cont =  getContractility(tmp)
            tmp['magnitude'] = axM
            tmp['velocity'] = axV
            tmp['timesecs'] = timelist
            tmp['contractility'] = cont
            
            final.append(tmp)
        #print("Processed",i, result[i], tmp.shape)
        print(len(final))  
        df = pd.concat(final)
        print(df.shape)
        df.to_csv(filename) 
    return df


# ## Calculating Magnitude with accelorometer data
# 
# - The acceleration signals were re-sampled to a standard sampling rate of 500 Hz. 
# - The static gravity component of the acceleration signal was removed with a moving average filter (Tukey window of length 3 s with a cosine fraction of 0.5). 
# - To further reduce the variability of the input data, we used the magnitude of the acceleration only (amagnitude=SQRT(ax ** 2 + ay ** 2 + az ** 2)). 
# - Using the magnitude makes the approach insensitive to the orientation of the sensor axes, which is an advantage when attaching the sensor as it can be attached without concern for a specific orientation relative to the heart axes.

# In[15]:


#scipy.integrate.cumtrapz(y, x=None, dx=1.0, axis=-1, initial=None)
# average acc (xyg)
def getMagnitudeList(df):
    axeM = []
    length = df.shape[0]  
    # Loop through the array to consider
    # every window of size 3
    i=0
    #we used the magnitude of the acceleration only (amagnitude=√a2x+a2y+a2z). 
    while i < length:
        x2 = df['acc_x'][i]**2
        y2 = df['acc_y'][i]**2
        z2 = df['acc_z'][i]**2
        axeM.append(math.sqrt(x2+y2+z2))
        i = i+1
    #momentum
    #df['momentum'] = axeM
    return axeM


# ## Converting to velocity
# 
# - The sensor in itself can't provide you the velocity. 
# - The easiest way to get the velocity is to constantly monitor acceleration changes and calculate velocity instantaneaously.
# - The equation of motion (V = Vo + at)... The sensor will provide you value of acceleration at any given time. 
# - Acceleration can vary quite significantly during a huge time intervals so keep the time intervals 't' small. Lets say t = 2ms (depends on you). 
# - Calculate V after every 10ms intervale and this will give you current velocity at any given time. 
# - But what about Vo? As you know it is refered to as initial velocity so in the beginning it will be 0. Immediately after first reading when you are about to take second reading the Vo will change to the previous V calculated and hence forth.
# - This means Vo at any given interval is actually the V calculated in the previous interval.
# - I tried this method in my project when using accelerometer. hope it helps you as well.
# - velocity = scipy.integrate.simps(acc, dx=dt) v = sqrt(Vx*Vx + Vy*Vy + Vz*Vz)


def getVelocityList(df):
    start = 0
    end = 0
    vel = []
    dt = 1/500
    i=0
    length = df.shape[0] 
    for i in range(length):
        start = i
        end = start + 2;
        if(end > df.shape[0]):
            #last value repeat the same as before for entire dataset
            vel.append(math.sqrt(Vx*Vx + Vy*Vy + Vz*Vz))
        else:
            dtmp = df[start:end]
            Vx = scipy.integrate.simps(dtmp['acc_x'], dx=dt)
            Vy = scipy.integrate.simps(dtmp['acc_y'], dx=dt)
            Vz = scipy.integrate.simps(dtmp['acc_z'], dx=dt)
            vel.append(math.sqrt(Vx*Vx + Vy*Vy + Vz*Vz))
        i = i+1
    return vel



def getTimeSeconds(df):
    size = df.shape[0]
    timelist = []
    for i in range(size):
        seconds, milliseconds = divmod((i+1)*2,1000) #500hz frequency
        time = seconds + milliseconds/1000 
        timelist.append(time)
    return timelist


# ## Measure of Contractility
# - Contractility refers to the property of heart muscle that accounts for alterations in performance induced by biochemical and hormonal changes.
# - It has classically been regarded to be independent of preload and afterload. Contractility is generally used as a synonym for inotropy
# - Both terms refer to the level of activation of cross-bridge cycling during systole.
# - Contractility changes are assessed in the experimental laboratory by measuring myocardial function (extent or speed of shortening, maximum force generation) while preload and afterload are held constant. 
# - In contrast to skeletal muscle, the strength of contraction of heart muscle can be increased readily by a variety of biochemical and hormonal stimuli


def getContractility(df):
    start = 0
    end = 0
    contract = []
    dt = 1/500
    i=0
    length = df.shape[0] 
    cont = 0.0
    for i in range(length):
        start = i
        end = start + 2;
        if(end > df.shape[0]):
            #last value repeat the same as before for entire dataset
            contract.append(cont)
        else:
            dtmp = df[start:end]
            cont = scipy.integrate.simps(dtmp['lvp'], dx=dt)
            contract.append(cont)
        i = i+1
    return contract



#path = '/Users/prakashperimbeti/desktop/AAI-USD/AAI-530/finalproject/epicardially-attached-cardiac-accelerometer-data-from-canines-and-porcines-1.0.0/accelerometer_data'
#path = './prakash/iot/finalproject/.'

#%cd /Users/prakashperimbeti/desktop/AAI-USD/AAI-530/finalproject/epicardially-attached-cardiac-accelerometer-data-from-canines-and-porcines-1.0.0/accelerometer_data
#%cd /home/bear/prakash/iot/finalproject/epicardially-attached-cardiac-accelerometer-data-from-canines-and-porcines-1.0.0/accelerometer_data
#%ls



#############################
# Execution of this takes aproximately 41 minutes even in fast server
#############################
#dfFinal = getConsolidatedData("./consolidated_ep_data.csv")



############################
#   MAIN PROGROM TO CONOLIDATE JSONs
############################

# total arguments
n = len(sys.argv)
print("Total arguments passed:", n)

# Arguments passed
print("\nName of Python script:", sys.argv[0])

print("\nArguments passed:", end = " ")
for i in range(1, n):
    print(sys.argv[i], end = " ")

# Addition of numbers
print("\n\n:Arguments", n)
if (n <= 1):
        print("USAGE -> python3 consolidatedjsons.py <directory>")
        exit
else:
        print("creating consolidated data file in the following directory:", sys.argv[1])
        dir_exists = exists(sys.argv[1])
        print("Directory exists:", dir_exists)
        if (dir_exists == True):
                filename = sys.argv[1] + "/consolidated_ep_data.csv"
                print("Consolidating all JSON Files")
                df = getConsolidatedData(filename)
                print("Successfully consolidated data into one CSV")
                print(df.shape)
                print(df.head(5))
        else:
                print("Provided directory:", sys.argv[1]," DOESN'T EXISTS!")

