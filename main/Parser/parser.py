import numpy as np
import pandas as pd
import sys
import os
from datetime import datetime as dt

class dataParser():
    def checkIfAllTablesExist(self, arr):
        # Check if the excel file contains all the necessary tables
        if "BUS DATA FOLLOWS" or "BRANCH DATA FOLLOWS" in arr:
            return True
        else:
            return False

    def extractData(self, npArr, txt):

        lenOfArray = npArr.shape[0] # Length of the array
        widthOfArray = npArr.shape[1] # Width of the array
        forLoopStartValue = int(np.where(npArr==txt)[0])+1 # The loop will start from the row after the specified text
        for i in range(forLoopStartValue, lenOfArray):
            if npArr[i][0] == -999: # Loop ends when the -999 is found
                newArray = npArr[forLoopStartValue:i] # This the table extracted
                break

        if txt == "BUS DATA FOLLOWS":
            arrayToReturn = np.zeros((newArray.shape[0],4))
            arrayToReturn[:,0] = newArray[:,0] # Bus number
            arrayToReturn[:,1] = newArray[:,7] # P
            arrayToReturn[:,2] = newArray[:,8] # Q
            arrayToReturn[:,3] = newArray[:,11] # V Base
        elif txt == "BRANCH DATA FOLLOWS":
            arrayToReturn = np.zeros((newArray.shape[0],4))
            arrayToReturn[:,0] = newArray[:,0] # From
            arrayToReturn[:,1] = newArray[:,1] # To
            arrayToReturn[:,2] = newArray[:,6] # R
            arrayToReturn[:,3] = newArray[:,7] # X
            
        return arrayToReturn

    def branchReorder(self, branchData):
        newData = branchData
        lenOfArray = newData.shape[0]
        zerosCol = np.zeros((newData.shape[0],1))
        newData = np.c_[newData, zerosCol]
        newBranchDataArr = np.zeros((newData.shape[0],4))
        n=0
        duplicateRan = False
        
        i = 0
        while i < lenOfArray:
            
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
            
            i = i + 1
        return newBranchDataArr

    def SBaseExtractor(self, arr):
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
    
    def dataExporter(self, outputArr, loss, Sb, Err):
        voltageArr = np.zeros([outputArr.shape[0], 3])
        firstVoltageRow = np.zeros([1, voltageArr.shape[1]])
        firstVoltageRow[0, 0] = 1 
        firstVoltageRow[0, 2] = 1
        toFromArr = np.zeros([outputArr.shape[0], 3])
        sLossArr = np.zeros([outputArr.shape[0], 3])
        
        # Calculate the PU voltage values
        voltageArr[:, 0] = np.real(outputArr[:, 4]) # Real Voltage
        voltageArr[:, 1] = np.imag(outputArr[:, 4]) # Imaginary Voltage
        voltageArr[:, 2] = np.sqrt(np.square(voltageArr[:, 0]) + np.square(voltageArr[:, 1])) # Sqrt(Real^2+Imag^2)
        voltageArr = np.concatenate((firstVoltageRow, voltageArr), axis = 0)
        #print(voltageArr)

        # Calculate the Loss in Per Units
        sLossArr[:, 0] = np.real(loss[:, 0]) # Real Voltage
        sLossArr[:, 1] = np.imag(loss[:, 0]) # Imaginary Voltage
        sLossArr[:, 2] = np.sqrt(np.square(sLossArr[:, 0]) + np.square(sLossArr[:, 1])) # Sqrt(Real^2+Imag^2)        
        #print(sLossArr)

        # Convert from PU to real values in kW, kVar and kVA
        sLossArr = sLossArr * Sb * 1000
        #print(sLossArr)

        # Create all the output dataframes
        voltageOut = pd.DataFrame(voltageArr)
        voltageOut.columns = ['Real', 'Imaginary', 'Final']
        sLossOut = pd.DataFrame(sLossArr)
        sLossOut.columns = ['Real', 'Imaginary', 'Apparent']
        errOut = pd.DataFrame({'Error Percentage': Err})

        # Create the name of the excel file
        now = dt.now()
        excelNameToSave = now.strftime("%d%m%Y %H%M%S")
        dir_path = os.path.dirname(os.path.dirname(__file__))
        filePath = dir_path + "\Output Folder"
        #filePath = os.path.abspath(os.path.join(dir_path, "\Output Folder"))
        #filePath = Path(dir_path).parents[0]
        
        writer = pd.ExcelWriter(filePath + "\\" + excelNameToSave + '.xlsx',engine='xlsxwriter')

        voltageOut.to_excel(writer, sheet_name='Voltage Output in PU')
        sLossOut.to_excel(writer, sheet_name='Power Loss')
        errOut.to_excel(writer, sheet_name='Error Percentages')
        writer.save()

        print("File Saved!")
        '''
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
        '''
        raise NotImplementedError('Implement this function/method.')