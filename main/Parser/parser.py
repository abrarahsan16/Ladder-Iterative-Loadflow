import numpy as np
import pandas as pd
import sys
import os, subprocess
from datetime import datetime as dt
import PySimpleGUI as sg
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
    
    def dataExporter(self, branchData, outputArr, loss, Sb, Err,loop):
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




        #Creating Tab 1 (Bus, Voltage, Voltage Angle)
        #Tab1 data
        bus=voltageOut['Bus No'].tolist()
        voltage_mag=voltageOut['Voltage Magnitude (PU)'].tolist()
        voltage_angle=voltageOut['Voltage Angle'].tolist()

        #Tab 2: bus, real line loss, reactive line loss, apparent line loss
        real_loss=finalsLossOut['Real Loss (KW)'].tolist()
        img_loss=finalsLossOut['Reactive Power Loss (KVAR)'].tolist()
        app_loss=finalsLossOut['Apparent Loss (KVA)'].tolist()

        #Tab 3: total loss- real, reactive apparent line loss
        total_real_loss=sTotalLossOut['Total Real Losses (KW)'].tolist()
        total_reactive_loss=sTotalLossOut['Total Reactive Losses (KVAR)'].tolist()
        total_apparent_loss=sTotalLossOut['Total Apparent Losses (KVA)'].tolist()
        #Tab 4: power injection

        #Tab 5: Error- iteration number, error percentages
        err_val=errOut['Error Percentages'].tolist()
            #call loop for iteration number (variable in calcMain)
        loop

        #Converting Data inside lists to string
        for i in range(len(voltage_mag)):
            #Tab1
            bus[i]=str(bus[i])
            voltage_mag[i]=str(voltage_mag[i])
            voltage_angle[i]=str(voltage_angle[i])
            #Tab2
            real_loss[i]=str(real_loss[i])
            img_loss[i]=str(img_loss[i])
            app_loss[i]=str(app_loss[i])
            toFromList[i]=str(toFromList[i])
            #Tab3
            total_real_loss[i]=str(total_real_loss[i])
            total_reactive_loss[i]=str(total_reactive_loss[i])
            total_apparent_loss[i]=str(total_apparent_loss[i])
            #Tab4
            
            #Tab5
            err_val[i]=str(err_val[i])
            loop[i]=str(loop[i])
            
        #Convering string list to numpy array
            #Tab1 Data
        bus_arr=np.array(bus)
        volt_mag=np.array(voltage_mag)
        volt_angle=np.array(voltage_angle)

            #Tab2 Data
        real_loss_arr=np.array(real_loss)
        img_loss_arr=np.array(img_loss)
        app_loss_arr=np.array(app_loss)

            #Tab3 Data
        total_real_loss_arr=np.array(total_real_loss)
        total_reactive_loss_arr=np.array(total_reactive_loss)
        total_apparent_loss_arr=np.array(total_apparent_loss)
            
            #Tab4 Data
            
            #Tab5 Data
        err_val_arr=np.array(errOut)
        loop_arr=np.array(loop)

        #Stacking voltage input,transposing it, and converting it 
            #Tab1 final data
        volt_data=np.stack((bus_arr,volt_mag,volt_angle))
        volt_data=np.transpose(volt_data)
        volt_data_input=volt_data.tolist()

            #Tab2 final data
        loss_data=np.stack((bus_arr,real_loss_arr,img_loss_arr,app_loss_arr))
        loss_data=np.transpose(loss_data)
        loss_data_input=loss_data.tolist()

            #Tab3 final data
        total_loss_data=np.stack((total_real_loss_arr,total_reactive_loss,total_apparent_loss))
        total_loss_data=np.transpose(total_loss_data)
        total_loss_data_input=total_loss_data.tolist()

            #Tab4 final data
            
            #Tab5 final data
        err_data=np.stack((loop_arr,err_val_arr))
        err_data=np.transpose(err_data)
        err_data_input=err_data.tolist()


        def Preview_Window():
            #headings = ['Voltage' , 'Voltage Angle', 'Line Power', 'Load per Bus', 'Power Loss']
            heading_volt=['Bus', 'Voltage Magnitude (PU)', 'Voltage Angle']
            heading_loss=['Bus', 'Reactive Power Loss (KVAR)','Apparent Loss (KVA)']
            heading_total_loss=['Total Real Losses (KW)','Total Reactive Power Losses (KVAR)', 'Total Apparent Losses (KVA)']
            heading_error=['Iteration Number', 'Error Percentage']
            
            
        # layout=[
        #       [sg.Table(values= volt_data_input, headings = heading_volt, max_col_width=35,
        #                  auto_size_columns=True,
        #                  display_row_numbers=True,
        #                  justification='right',
        #                  num_rows=10,
        #                  key='-VOLT_TABLE-',
        #                  row_height=35)]
        #
        #        ]
            #start of tab code
            tab1_layout =  [[sg.Table(values=volt_data_input, headings = heading_volt, max_col_width=35,
                            auto_size_columns=True,
                            display_row_numbers=True,
                            justification='right',
                            num_rows=10,
                            key='-VOLT_TABLE-',
                            row_height=35)]]    

            tab2_layout = [[sg.Table(values=loss_data_input, headings = heading_loss, max_col_width=35,
                            auto_size_columns=True,
                            display_row_numbers=True,
                            justification='right',
                            num_rows=10,
                            key='-LOSS_TABLE-',
                            row_height=35)]]
            
            tab3_layout=[[sg.Table(values=total_loss_data_input, headings = heading_total_loss, max_col_width=35,
                            auto_size_columns=True,
                            display_row_numbers=True,
                            justification='right',
                            num_rows=10,
                            key='-TOTAL_LOSS_TABLE--',
                            row_height=35)]]
            
            #tab4_layout=[[]]
            
            tab5_layout=[[sg.Table(values=err_data_input, headings = heading_error, max_col_width=35,
                            auto_size_columns=True,
                            display_row_numbers=True,
                            justification='right',
                            num_rows=10,
                            key='-ERROR_TABLE--',
                            row_height=35)]]

            layout = [[sg.TabGroup([[sg.Tab('Tab 1', tab1_layout, tooltip='tip'), sg.Tab('Tab 2', tab2_layout),sg.Tab('Tab 3', tab3_layout),sg.Tab('Tab 5', tab5_layout)]], tooltip='TIP2')],    
                    [sg.Button('Open File')]]    

            window = sg.Window('Load Flow Calculator Output', layout, default_element_size=(12,1))    

            while True:    
                event, values = window.read()    
                print(event,values) 

                if event =='Open FIle':
                    print("Beep Boop") 
                if event == sg.WIN_CLOSED:           # always,  always give a way out!    
                    break  
            #end of tab code
        #raise NotImplementedError('Implement this function/method.')