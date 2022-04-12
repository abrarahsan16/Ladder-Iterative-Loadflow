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
        sg.print('Excel Tables Exist')
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
        sg.print('Reordering Branch Data')
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
    
    def powerFlowCalculation(self, busArr, inputArr, sLossArr, powerInjection, Sb):
        sg.print('Starting Power Flow Calculations')
        sFlow = np.zeros([inputArr.shape[0], 1], dtype = np.complex_)
        for i in range(0, len(inputArr)):
            busFinder = np.where(inputArr[i, 1] == busArr[:, 0])
            j = busFinder[0][0]
            sLoad = complex(busArr[j, 1], busArr[j, 2]) * 1000 # kVA
            if i == 0:
                sFlow[i, 0] = powerInjection[i, 1] - sLoad - complex(sLossArr[i, 1], sLossArr[i, 2])
            elif inputArr[i, 0] == inputArr[i - 1, 1]:
                sFlow[i, 0] = powerInjection[i, 1] - sLoad - complex(sLossArr[i, 1], sLossArr[i, 2])
            elif inputArr[i, 0] != inputArr[i - 1, 1]:
                dup = np.where(inputArr[:, 0] == inputArr[i, 0])
                k = dup[0][0]
                sFlow[i, 0] = powerInjection[k, 1] - sLoad - complex(sLossArr[i, 1], sLossArr[i, 2])
        return sFlow
        raise NotImplementedError('Implement this function/method.')

    def dataExporter(self, busData, branchData, outputArr, loss, Sb, Vb, Err, loop):
        # Initialize the arrays
        sg.print('Starting Data Export')
        voltageArr = np.zeros([outputArr.shape[0], 4])
        firstVoltageRow = np.zeros([1, voltageArr.shape[1]])
        firstVoltageRow[0, 0] = 1
        firstVoltageRow[0, 1] = 1
        firstVoltageRow[0, 2] = 1 * Vb
        firstVoltageRow[0, 3] = 0
        sLossArr = np.zeros([outputArr.shape[0], 7])
        powerInjection = np.zeros([outputArr.shape[0], 2], dtype=np.complex_)
        firstPowerInjectionRow = np.zeros([1, powerInjection.shape[1]], dtype=np.complex_)
        firstPowerInjectionRow[0, 0] = 1
        firstPowerInjectionRow[0, 1] = np.conjugate(outputArr[0, 6]) * 1 * Sb * 1000
        
        # Calculate the PU voltage values
        voltageArr[:, 0] = np.real(outputArr[:, 1])
        voltageReal = np.real(outputArr[:, 4]) # Real Voltage
        voltageImag = np.imag(outputArr[:, 4]) # Imaginary Voltage
        voltageArr[:, 1] = np.around(np.sqrt(np.square(voltageReal) + np.square(voltageImag)), 4) # Sqrt(Real^2+Imag^2)
        voltageArr[:, 2] = np.around(voltageArr[:, 1] * Vb, 4)
        voltageArr[:, 3] = np.around(np.arctan2(voltageImag, voltageReal) * (180/np.pi), 4) # arctan(Imag/Real)
        voltageArr = np.concatenate((firstVoltageRow, voltageArr), axis = 0)
        sortedVoltageArr = voltageArr[voltageArr[:, 0].argsort()]

        # Calculate the Loss in Per Units
        sLossArr[:, 4] = np.real(loss[:, 0]) # Real Power
        sLossArr[:, 5] = np.imag(loss[:, 0]) # Imaginary Power
        sLossArr[:, 6] = np.sqrt(np.square(sLossArr[:, 4]) + np.square(sLossArr[:, 5])) # Sqrt(Real^2+Imag^2)        

        # Convert from PU to real values in kW, kVar and kVA
        sLossArr = np.around(sLossArr * Sb * 1000, 4)
        sLossArr[:, 0] = np.real(outputArr[:, 1])
        

        # Calculate power injection for each bus
        powerInjectionV = outputArr[:, 4]
        powerInjectionI = outputArr[:, 6]
        powerInjection[:, 1] = np.around((powerInjectionV * np.conjugate(powerInjectionI)) * Sb * 1000, 4)
        powerInjection[:, 0] = np.real(outputArr[:, 1])
        powerInjection = np.concatenate((firstPowerInjectionRow, powerInjection), axis = 0)
        sortedpowerInjection = powerInjection[powerInjection[:, 0].argsort()]
        sPowerInjection = np.zeros((sortedpowerInjection.shape[0], 4))
        sPowerInjection[:, 0] = np.real(sortedpowerInjection[: ,0])
        sPowerInjection[:, 1] = np.around(np.real(sortedpowerInjection[:, 1]), 4) # Real Power
        sPowerInjection[:, 2] = np.around(np.imag(sortedpowerInjection[:, 1]), 4) # Imaginary Power
        sPowerInjection[:, 3] = np.around(np.sqrt(np.square(sPowerInjection[:, 1]) + np.square(sPowerInjection[:, 2])), 4) # Sqrt(Real^2+Imag^2)
        
        # Power Flow
        sFlow = self.powerFlowCalculation(busData, outputArr, sLossArr, powerInjection, Sb)
        sLossArr[:, 1] = np.real(sFlow[:, 0])
        sLossArr[:, 2] = np.imag(sFlow[:, 0])
        sLossArr[:, 3] = np.sqrt(np.square(sLossArr[:, 1]) + np.square(sLossArr[:, 2]))
        sortedLossArr = sLossArr[sLossArr[:, 0].argsort()]
        sortedWithoutBus = np.delete(sortedLossArr, 0, 1)

        # Total Loss
        sLossTotalArr = np.zeros([1, 3])
        sLossTotalArr[0,0] = np.around(np.sum(sLossArr[:, 4]), 4)
        sLossTotalArr[0,1] = np.around(np.sum(sLossArr[:, 5]), 4)
        sLossTotalArr[0,2] = np.around(np.sum(sLossArr[:, 6]), 4)

        # Create To-From List to append to sLoss
        toFromList = []
        for i in range(0, len(branchData)):
            toAppend = str(branchData[i, 0].astype(np.int)) + " - " + str(branchData[i, 1].astype(np.int))
            toFromList.append(toAppend)
        
        # Convert list to Panda
        ToFromOut = pd.DataFrame(toFromList, columns = ['Bus Connection'])

        # Create all the output dataframes
        voltageOut = pd.DataFrame(sortedVoltageArr)
        voltageOut.columns = ['Bus No', 'Voltage Magnitude (PU)', 'Voltage Magnitude (V)', 'Voltage Angle (Degree)']
        sLossOut = pd.DataFrame(sortedWithoutBus)
        sLossOut.columns = ['Real Power Flow (KW)', 'Reactive Power Flow (KVAR)', 'Apparent Power Flow (KVA)', 'Real Power Loss (KW)', 'Reactive Power Loss (KVAR)', 'Apparent Power Loss (KVA)']
        sinjectionOut = pd.DataFrame(sPowerInjection)
        sinjectionOut.columns = ['Bus No', 'Real Power Injection (KW)', 'Reactive Power Injection (KVAR)', 'Apparent Power Injection (KVA)']
        sTotalLossOut = pd.DataFrame(sLossTotalArr)
        sTotalLossOut.columns = ['Total Real Power Losses (KW)', 'Total Reactive Power Losses (KVAR)', 'Total Apparent Power Losses (KVA)']
        errOut = pd.DataFrame({'Error Percentage': Err})
        finalsLossOut = ToFromOut.join(sLossOut)

        # Create the name of the excel file
        now = dt.now()
        excelNameToSave = now.strftime("%d%m%Y %H%M")
        dir_path = os.path.dirname(os.path.dirname(__file__))
        filePath = dir_path + "\Output Folder"

        if not os.path.exists(filePath):
            os.makedirs(filePath)
        
        writer = pd.ExcelWriter(filePath + "\\" + excelNameToSave + '.xlsx',engine='xlsxwriter')

        voltageOut.to_excel(writer, sheet_name='Voltage Output in PU')
        finalsLossOut.to_excel(writer, sheet_name='Power Flow')
        sinjectionOut.to_excel(writer, sheet_name='Power Injection')
        sTotalLossOut.to_excel(writer, sheet_name='Power Flow', startrow=finalsLossOut.shape[0] + 1, startcol=1+3)
        errOut.to_excel(writer, sheet_name='Error Percentage')
        writer.save()

        print("File Saved!")


        #Creating Tab 1 (Bus, Voltage, Voltage Angle)
        #Tab1 data
        bus=voltageOut['Bus No'].tolist()
        voltage_mag=voltageOut['Voltage Magnitude (PU)'].tolist()
        voltage_mag_v=voltageOut['Voltage Magnitude (V)'].tolist()
        voltage_angle=voltageOut['Voltage Angle (Degree)'].tolist()

        #Tab 2: bus, real line loss, reactive line loss, apparent line loss
        real_PF=finalsLossOut['Real Power Flow (KW)'].tolist()
        reactive_PF=finalsLossOut['Reactive Power Flow (KVAR)'].tolist()
        apparent_PF=finalsLossOut[ 'Apparent Power Flow (KVA)'].tolist()
        real_loss=finalsLossOut['Real Power Loss (KW)'].tolist()
        img_loss=finalsLossOut['Reactive Power Loss (KVAR)'].tolist()
        app_loss=finalsLossOut['Apparent Power Loss (KVA)'].tolist()

        #Tab 3: total loss- real, reactive apparent line loss
        total_real_loss=sTotalLossOut['Total Real Power Losses (KW)'].tolist()
        total_reactive_loss=sTotalLossOut['Total Reactive Power Losses (KVAR)'].tolist()
        total_apparent_loss=sTotalLossOut['Total Apparent Power Losses (KVA)'].tolist()
        
        #Tab 4: power injection
        injected_bus=sinjectionOut['Bus No'].tolist()
        injected_real=sinjectionOut['Real Power Injection (KW)'].tolist()
        injected_reactive=sinjectionOut['Reactive Power Injection (KVAR)'].tolist()
        injected_apparent=sinjectionOut['Apparent Power Injection (KVA)'].tolist()

        #Tab 5: Error- iteration number, error percentages
        err_val=errOut['Error Percentage'].tolist()
            #call loop for iteration number (variable in calcMain)
        loop

        #Converting Data inside lists to string
        for i in range(len(voltage_mag)):
            #Tab1 This is largest number of rows
            bus[i]=str(bus[i])
            voltage_mag[i]=str(voltage_mag[i])
            voltage_angle[i]=str(voltage_angle[i])
            voltage_mag_v[i]=str(voltage_mag_v[i])
            
            #Tab4 len = Len(voltage)
            injected_bus[i]=str(injected_bus[i])
            injected_real[i]=str(injected_real[i])
            injected_reactive[i]=str(injected_reactive[i])
            injected_apparent[i]=str(injected_apparent[i])
            
                #Tab2 len = Len(voltage) - 1
            if(i<(len(voltage_mag)-1)):
                real_loss[i]=str(real_loss[i])
                img_loss[i]=str(img_loss[i])
                app_loss[i]=str(app_loss[i])
                toFromList[i]=str(toFromList[i])
                real_PF[i]=str(real_PF[i])
                reactive_PF[i]=str(reactive_PF[i])
                apparent_PF[i]=str(apparent_PF[i])
            #Tab3 Len = 1
            if(i<1):
                total_real_loss[i]=str(total_real_loss[i])
                total_reactive_loss[i]=str(total_reactive_loss[i])
                total_apparent_loss[i]=str(total_apparent_loss[i])
            
            #Tab5 len(err)
            if(i<(len(err_val))):
                err_val[i]=str(err_val[i])
                loop[i]=str(loop[i])
            
        #Convering string list to numpy array
            #Tab1 Data
        bus_arr=np.array(bus)
        volt_mag=np.array(voltage_mag)
        volt_angle=np.array(voltage_angle)
        volt_mag_v=np.array(voltage_mag_v)

            #Tab2 Data
        real_loss_arr=np.array(real_loss)
        img_loss_arr=np.array(img_loss)
        app_loss_arr=np.array(app_loss)
        real_PF_arr=np.array(real_PF)
        reactive_PF_arr=np.array(reactive_PF)
        apparent_PF_arr=np.array(apparent_PF)
    
            #Tab3 Data
        total_real_loss_arr=np.array(total_real_loss)
        total_reactive_loss_arr=np.array(total_reactive_loss)
        total_apparent_loss_arr=np.array(total_apparent_loss)
            
            #Tab4 Data
        injected_bus_arr=np.array(injected_bus)
        injected_real_arr=np.array(injected_real)
        injected_reactive_arr=np.array(injected_reactive)
        injected_apparent_arr=np.array(injected_apparent)

            #Tab5 Data
        err_val_arr = np.reshape(np.array(errOut), (len(errOut)))
        #err_val_arr=np.array(errOut)
        #loop_arr[:,0] = loop
        loop_arr=np.array(loop)
        #loop_arr = np.reshape(loop_arr,(loop_arr.shape[0],1))

        #Stacking voltage input,transposing it, and converting it 
            #Tab1 final data
        volt_data=np.stack((bus_arr,volt_mag,volt_mag_v,volt_angle))
        volt_data=np.transpose(volt_data)
        volt_data_input=volt_data.tolist()

            #Tab2 final data
        loss_data=np.stack((toFromList,real_PF_arr,reactive_PF_arr,apparent_PF_arr,real_loss_arr,img_loss_arr,app_loss_arr))
        loss_data=np.transpose(loss_data)
        loss_data_input=loss_data.tolist()

            #Tab3 final data
        total_loss_data=np.stack((total_real_loss_arr,total_reactive_loss_arr,total_apparent_loss_arr))
        total_loss_data=np.transpose(total_loss_data)
        total_loss_data_input=total_loss_data.tolist()
        
            #Tab4 final data
        injected_data=np.stack((injected_bus_arr,injected_real_arr,injected_reactive_arr,injected_apparent_arr))
        injected_data=np.transpose(injected_data)
        injected_data_input=injected_data.tolist() 
            #Tab5 final data
        err_data=np.stack((loop_arr,err_val_arr))
        err_data=np.transpose(err_data)
        err_data_input=err_data.tolist()
        
        #print(loop_arr)
        #print(err_data_input)
        #print(app_loss_arr)
        self.Preview_Window(volt_data_input, loss_data_input, total_loss_data_input, injected_data_input,err_data_input)


    def Preview_Window(self, volt_data_input, loss_data_input, total_loss_data_input, injected_data_input, err_data_input):
        sg.print('Generating Preview Window')
        #headings = ['Voltage' , 'Voltage Angle', 'Line Power', 'Load per Bus', 'Power Loss']
        heading_volt=['Bus', 'Voltage Magnitude (PU)', 'Voltage Magnitude (V)','Voltage Angle (Degree)']
        heading_loss=['Bus','Real Power Flow (KW)', 'Reactive Power Flow (KVAR)', 'Apparent Power Flow (KVA)', 'Real Power Loss (KW)','Reactive Power Loss (KVAR)','Apparent Power Loss (KVA)']
        heading_total_loss=['Total Real Power Losses (KW)','Total Reactive Power Losses (KVAR)', 'Total Apparent Power Losses (KVA)']
        heading_injection=['Bus No','Real Power Injection (KW)','Reactive Power Injection (KVAR)','Apparent Power Injection (KVA)']
        heading_error=['Iteration Number', 'Error Percentage']
        
        sg.theme('DarkAmber')
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
                        justification='center',
                        num_rows=10,
                        key='-VOLT_TABLE-',
                        row_height=35)]]    

        tab2_layout = [[sg.Table(values=loss_data_input, headings = heading_loss, max_col_width=35,
                        auto_size_columns=True,
                        display_row_numbers=True,
                        justification='center',
                        num_rows=10,
                        key='-LOSS_TABLE-',
                        row_height=35)]]
        
        tab3_layout=[[sg.Table(values=total_loss_data_input, headings = heading_total_loss, max_col_width=35,
                        auto_size_columns=True,
                        display_row_numbers=True,
                        justification='center',
                        num_rows=10,
                        key='-TOTAL_LOSS_TABLE--',
                        row_height=35)]]
        
        tab4_layout=[[sg.Table(values=injected_data_input, headings = heading_injection, max_col_width=35,
                        auto_size_columns=True,
                        display_row_numbers=True,
                        justification='center',
                        num_rows=10,
                        key='-TOTAL_LOSS_TABLE--',
                        row_height=35)]]
        
        tab5_layout=[[sg.Table(values=err_data_input, headings = heading_error, max_col_width=35,
                        auto_size_columns=True,
                        display_row_numbers=True,
                        justification='center',
                        num_rows=10,
                        key='-ERROR_TABLE--',
                        row_height=35)]]

        layout = [[sg.TabGroup([[sg.Tab('Voltage', tab1_layout, tooltip='tip'), sg.Tab('Power Flow', tab2_layout),sg.Tab('Total Power Loss', tab3_layout),sg.Tab('Power Injection', tab4_layout),sg.Tab('Error per Iteration', tab5_layout)]], tooltip='TIP2')],    
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
