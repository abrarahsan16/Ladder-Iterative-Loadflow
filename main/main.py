import os
import sys
import numpy as np
import pandas as pd
import math as mth
from GUI import guiInit
from Parser.parser import dataParser
from Calculation import calcMain

if __name__ == '__main__':

    
    #event, cdfPath, tol = guiInit.gui_initial()
    dataParser = dataParser()
    cdfPath = "C:\\Users\\erzum\\Documents\\GitHub\\Ladder-Iterative-Loadflow\\Documentations\\Datasets\\IEEE 33 CDF (Updated)_2.xlsx"
    tol = 0.0001
    readInput = pd.read_excel(cdfPath, header=None)
    
    numpyConversion = readInput.to_numpy()
    checker = dataParser.checkIfAllTablesExist(numpyConversion)

    if checker == False:
        raise ValueError("Excel does not contain Bus or Branch data, please double check and try again")
    
    #SBase = (parser.SBaseExtractor(numpyConversion)/(mth.sqrt(3)))*1000
    SBase = (dataParser.SBaseExtractor(numpyConversion))

    busData = dataParser.extractData(numpyConversion, "BUS DATA FOLLOWS")
    branchData = dataParser.extractData(numpyConversion, "BRANCH DATA FOLLOWS")
    VBase = busData[0, 3]

    sortedBranchData = dataParser.branchReorder(branchData)
    
    print("Table extraction complete")

    outputArr, sLoss, Err,loop = calcMain.calcMain(busData, sortedBranchData, float(tol), SBase, VBase)
    print("Output received")
    
    dataParser.dataExporter(branchData, outputArr, sLoss, SBase, Err,loop)
    
    #another_df.to_excel(writer,sheet_name='Validation',startrow=20, startcol=0) 
    #print("For bus %s, final voltage is %s \n" %(outputArr[:, 1], outputArr[:, 4]))
    #print("Final Voltage value :\n%s" %outputArr[:, 4])
    #print("Final Current value : \n%s" %outputArr[:, 6])
    #print("number of iterations : \n%d" %n)
