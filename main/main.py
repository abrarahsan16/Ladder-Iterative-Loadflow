import os
import sys
import numpy as np
import pandas as pd
import math as mth
from datetime import datetime as dt
from GUI import guiInit
from Parser import parser
from Calculation import calcMain

if __name__ == '__main__':

    
    event, cdfPath, tol = guiInit.gui_initial()
    
    #cdfPath = "E:\Github\Ladder-Iterative-Loadflow\Documentations\Datasets\IEEE 33 CDF (Updated)_2.xlsx"
    #tol = 0.0001
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

    outputArr, n = calcMain.calcMain(busData, sortedBranchData, float(tol), SBase, VBase)
    print("Output received")

    # Create output dataframe
    outputDf = pd.DataFrame(outputArr)
    now = dt.now()
    excelNameToSave = now.strftime("%d%m%Y %H%M%S")
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filePath = dir_path + ".\Output Folder"
    
    # Creating Excel Writer Object from Pandas  
    writer = pd.ExcelWriter(filePath + "\\" + excelNameToSave + '.xlsx',engine='xlsxwriter')   
    workbook=writer.book
    worksheet=workbook.add_worksheet('Output')
    writer.sheets['Output'] = worksheet
    outputDf.to_excel(writer,sheet_name='Output',startrow=0 , startcol=0)  

    #another_df.to_excel(writer,sheet_name='Validation',startrow=20, startcol=0) 
    #print("For bus %s, final voltage is %s \n" %(outputArr[:, 1], outputArr[:, 4]))
    #print("Final Voltage value :\n%s" %outputArr[:, 4])
    #print("Final Current value : \n%s" %outputArr[:, 6])
    #print("number of iterations : \n%d" %n)
