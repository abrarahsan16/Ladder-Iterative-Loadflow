import numpy as np
import pandas as pd
import sys
import os, subprocess
from datetime import datetime as dt

class dataParser():
    def checkIfAllTablesExist(self, arr):
        # Check if the excel file contains all the necessary tables
        if "BUS DATA FOLLOWS" in arr:
            if "BRANCH DATA FOLLOWS" in arr:
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
            i = 3
            SBase = splitRyeString[i]
            while SBase == "":
                i = i + 1
                SBase = splitRyeString[i]
            return float(SBase)
    
    def dataExporter(self, branchData, outputArr, loss, Sb, Err):
        # Initialize the arrays
        voltageArr = np.zeros([outputArr.shape[0], 3])
        firstVoltageRow = np.zeros([1, voltageArr.shape[1]])
        firstVoltageRow[0, 0] = 1
        firstVoltageRow[0, 1] = 1
        firstVoltageRow[0, 2] = 0
        sLossArr = np.zeros([outputArr.shape[0], 4])
        
        # Calculate the PU voltage values
        voltageArr[:, 0] = np.real(outputArr[:, 1])
        voltageReal = np.real(outputArr[:, 4]) # Real Voltage
        voltageImag = np.imag(outputArr[:, 4]) # Imaginary Voltage
        voltageArr[:, 1] = np.sqrt(np.square(voltageReal) + np.square(voltageImag)) # Sqrt(Real^2+Imag^2)
        voltageArr[:, 2] = np.arctan2(voltageImag, voltageReal) # arctan(Imag/Real)
        voltageArr = np.concatenate((firstVoltageRow, voltageArr), axis = 0)
        sortedVoltageArr = voltageArr[voltageArr[:, 0].argsort()]
        #print(voltageArr)

        # Calculate the Loss in Per Units
        sLossArr[:, 1] = np.real(loss[:, 0]) # Real Voltage
        sLossArr[:, 2] = np.imag(loss[:, 0]) # Imaginary Voltage
        sLossArr[:, 3] = np.sqrt(np.square(sLossArr[:, 1]) + np.square(sLossArr[:, 2])) # Sqrt(Real^2+Imag^2)        

        # Convert from PU to real values in kW, kVar and kVA
        sLossArr = sLossArr * Sb * 1000
        sLossArr[:, 0] = np.real(outputArr[:, 1])
        sortedLossArr = sLossArr[sLossArr[:, 0].argsort()]
        sortedWithoutBus = np.delete(sortedLossArr, 0, 1)

        # Total Loss
        sLossTotalArr = np.zeros([1, 3])
        sLossTotalArr[0,0] = np.sum(sLossArr[:, 1])
        sLossTotalArr[0,1] = np.sum(sLossArr[:, 2])
        sLossTotalArr[0,2] = np.sum(sLossArr[:, 3])

        # Create To-From List to append to sLoss
        toFromList = []
        for i in range(0, len(branchData)):
            toAppend = str(branchData[i, 0].astype(np.int)) + " - " + str(branchData[i, 1].astype(np.int))
            toFromList.append(toAppend)
        
        # Convert list to Panda
        ToFromOut = pd.DataFrame(toFromList, columns = ['Bus Connection'])

        # Create all the output dataframes
        voltageOut = pd.DataFrame(sortedVoltageArr)
        voltageOut.columns = ['Bus No', 'Voltage Magnitude (PU)', 'Voltage Angle']
        sLossOut = pd.DataFrame(sortedWithoutBus)
        sLossOut.columns = ['Real Loss (KW)', 'Reactive Power Loss (KVAR)', 'Apparent Loss (KVA)']
        #print(finalsLossOut)
        sTotalLossOut = pd.DataFrame(sLossTotalArr)
        sTotalLossOut.columns = ['Total Real Losses (KW)', 'Total Reactive Losses (KVAR)', 'Total Apparent Losses (KVA)']
        errOut = pd.DataFrame({'Error Percentage': Err})
        finalsLossOut = ToFromOut.join(sLossOut)

        # Create the name of the excel file
        now = dt.now()
        excelNameToSave = now.strftime("%d%m%Y %H%M")
        dir_path = os.path.dirname(os.path.dirname(__file__))
        filePath = dir_path + "\Output Folder"
        
        writer = pd.ExcelWriter(filePath + "\\" + excelNameToSave + '.xlsx',engine='xlsxwriter')

        voltageOut.to_excel(writer, sheet_name='Voltage Output in PU')
        finalsLossOut.to_excel(writer, sheet_name='Line Power Loss')
        sTotalLossOut.to_excel(writer, sheet_name='Total Power Loss')
        errOut.to_excel(writer, sheet_name='Error Percentages')
        writer.save()

        print("File Saved!")

        #raise NotImplementedError('Implement this function/method.')