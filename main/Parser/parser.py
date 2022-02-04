import numpy as np
import pandas as pd
import sys
import os

def checkIfAllTablesExist(arr):
    # Check if the excel file contains all the necessary tables
    if "BUS DATA FOLLOWS" or "BRANCH DATA FOLLOWS" in arr:
        return True
    else:
        return False

def extractData(npArr, txt):

    lenOfArray = npArr.shape[0]
    widthOfArray = npArr.shape[1]
    forLoopStartValue = int(np.where(npArr==txt)[0])+1
    for i in range(forLoopStartValue, lenOfArray):
        if npArr[i][0] == -999:
            newArray = npArr[forLoopStartValue:i]
            break

    if txt == "BUS DATA FOLLOWS":
        # Add code here for extracting SBase
        arrayToReturn = np.zeros((newArray.shape[0],4))
        arrayToReturn[:,0] = newArray[:,0]
        arrayToReturn[:,1] = newArray[:,7]
        arrayToReturn[:,2] = newArray[:,8]
        arrayToReturn[:,3] = newArray[:,11]
    elif txt == "BRANCH DATA FOLLOWS":
        arrayToReturn = np.zeros((newArray.shape[0],4))
        arrayToReturn[:,0] = newArray[:,0]
        arrayToReturn[:,1] = newArray[:,1]
        arrayToReturn[:,2] = newArray[:,6]
        arrayToReturn[:,3] = newArray[:,7]
        
    return arrayToReturn

def branchReorder(branchData):
    newData = branchData
    lenOfArray = newData.shape[0]
    zerosCol = np.zeros((newData.shape[0],1))
    newData = np.c_[newData, zerosCol]
    newBranchDataArr = np.zeros((newData.shape[0],4))
    n=0
    duplicateRan = False
    for i in range(0, lenOfArray):
        dup = np.where(newData[:,0]==newData[i,0])
        if len(dup[0])==1 and (newData[i,4]==0):
            newBranchDataArr[n,0] = newData[i,0]
            newBranchDataArr[n,1] = newData[i,1]
            newBranchDataArr[n,2] = newData[i,2]
            newBranchDataArr[n,3] = newData[i,3]
            newData[i,4] = 1
            n=n+1            
        else:
            for j in dup[0]:
                k = j
                if (j > i) and (newData[k,4]==0):
                    
                    while(1):
                        if k+1 == lenOfArray:
                            if (newData[k,0]==newData[k-1,1]):
                                newBranchDataArr[n,0] = newData[k,0]
                                newBranchDataArr[n,1] = newData[k,1]
                                newBranchDataArr[n,2] = newData[k,2]
                                newBranchDataArr[n,3] = newData[k,3]
                                newData[k,4] = 1
                                n = n+1
                                k = k+1
                            break
                        if (newData[k,1]==newData[k+1,0]):
                            newBranchDataArr[n,0] = newData[k,0]
                            newBranchDataArr[n,1] = newData[k,1]
                            newBranchDataArr[n,2] = newData[k,2]
                            newBranchDataArr[n,3] = newData[k,3]
                            newData[k,4] = 1
                            n = n+1
                            k = k+1
                        elif (newData[k,1]!=newData[k+1,0]) and (newBranchDataArr[n-1,0] != newData[k,0]):
                            newBranchDataArr[n,0] = newData[k,0]
                            newBranchDataArr[n,1] = newData[k,1]
                            newBranchDataArr[n,2] = newData[k,2]
                            newBranchDataArr[n,3] = newData[k,3]
                            newData[k,4] = 1
                            n = n+1
                            k = k+1
                            break
                    duplicateRan = True
        if duplicateRan == True and (newData[i,4]==0):
            newBranchDataArr[n,0] = newData[i,0]
            newBranchDataArr[n,1] = newData[i,1]
            newBranchDataArr[n,2] = newData[i,2]
            newBranchDataArr[n,3] = newData[i,3]
            newData[i,4] = 1
            n=n+1
            duplicateRan = False
    return newBranchDataArr

def SBaseExtractor(arr):
    RyeFinder = arr[0][0]
    subString = "RYERSON UNIVERSITY"

    try:
        RyeFinder.index(subString)
    except ValueError:
        raise ValueError("Header with SBase is missing")
    else:
        splitRyeString = RyeFinder.split(" ")
        SBase = splitRyeString[4]
        return float(SBase)