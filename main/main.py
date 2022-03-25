import os
import sys
import numpy as np
import pandas as pd
import math as mth
from GUI import guiInit
from Parser import parser
from Calculation import calcMain

if __name__ == '__main__':

    '''
    event, cdfPath, tol = guiInit.gui_initial()
    '''
    cdfPath = "E:\Github\Ladder-Iterative-Loadflow\Documentations\Datasets\IEEE 33 CDF (Updated)_2.xlsx"
    tol = 0.0001
    readInput = pd.read_excel(cdfPath, header=None)
    
    numpyConversion = readInput.to_numpy()
    checker = parser.checkIfAllTablesExist(readInput)

    #SBase = (parser.SBaseExtractor(numpyConversion)/(mth.sqrt(3)))*1000
    SBase = (parser.SBaseExtractor(numpyConversion))

    if checker == False:
        raise ValueError("Excel does not contain Bus or Branch data, please double check and try again")
    
    busData = parser.extractData(numpyConversion, "BUS DATA FOLLOWS")
    branchData = parser.extractData(numpyConversion, "BRANCH DATA FOLLOWS")
    VBase = busData[0, 3]

    sortedBranchData = parser.branchReorder(branchData)
    
    print("Table extraction complete")

    calcMain.calcMain(busData, sortedBranchData, float(tol), SBase, VBase)