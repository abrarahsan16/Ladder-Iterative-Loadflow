import numpy as np
import pandas as pd
import math as mth
from Calculation import FWRsweep, BKWsweep

def calcMain(busArr, branchArr, Tol, Sb, Vb):
    Sb = Sb * 10**6
    Vb = Vb * 10**3
    Zb = (Vb**2)/Sb

    outputArr = np.zeros([branchArr.shape[0], 7], dtype=np.complex_)
    busDataArr = np.zeros([busArr.shape[0], busArr.shape[1]], dtype=np.float)
    
    busDataArr[:, 0] = busArr[:, 0] # Bus Number
    busDataArr[:, 1] = busArr[:, 1] * 10**6 # P
    busDataArr[:, 2] = busArr[:, 2] * 10**6 # Q
    busDataArr[:, 3] = busArr[:, 3] # Vb

    outputArr[:,0] = branchArr[:,0] # From Node
    outputArr[:,1] = branchArr[:,1] # To Node
    outputArr[:,2] = branchArr[:,2] * Zb # R
    outputArr[:,3] = branchArr[:,3] * Zb # X
    # outputArr[:,4] # Voltage
    # outputArr[:,5] # Load Current
    # outputArr[:,6] # Current
    n = 0 # Number of iterations
    Vold = 0 # Old Voltage Value
    Vs = 1 * Vb # Source Voltage
    #Vs = 7200 # Source Voltage

    while (1):
        outputArr = FWRsweep.FWR(outputArr, Vs) # Run the forward sweep
        Vl = outputArr[len(outputArr)-1, 4] # The last load on the radial system
        Err = ((abs(Vl.real - Vold.real))/Vs) # Calculate the error in the end
        print("Error value after %s iteration : %f" %(n,Err))
        if Err.real<=Tol:
            print("Final Voltage value :\n%s" %outputArr[:, 4])
            print("Final Current value : \n%s" %outputArr[:, 6])
            print("number of iterations : \n%d" %n)
            break
        else:
            Vold = Vl # Replace the old with the calculated load
            outputArr = BKWsweep.BKWsweep(busDataArr, outputArr) # Run backward sweep
        n += 1
        if n == 50: # If the iteration exceeds 50 iterations, end run
            print("Failed to converge. Report has not been created")
            break
    '''
    BU = busArr[:, 0] #Counts the number of buses
    

    BU = busArr[:,0] #Number of buses
    dfObj = pd.DataFrame(branchArr, columns=['Bus1', 'Bus2', 'R', 'X']) #Create a DataFrame object
    duplicateRowsDF = dfObj[dfObj.duplicated(['Bus1'])]   # Select all duplicate rows based on multiple column names in list
    print("Duplicate Rows based on 2 columns are:", duplicateRowsDF, sep='\n')   # Print all duplicate rows based on multiple column names in list
    I12=I23=I34=I45=I56=I67=I78=I89=I910=0;Vold=0;n=0 ;
    Vs= 7200; # The source voltage at node 1
    while (1):
        FWRsweep(V,Z,I)    # Forward sweep    
        array_length = len(V)
        Vl = V[array_length - 1]
        Err=(abs(Vl.real-Vold.real)/Vs)
        print("Error value after %s iteration : %f" %(n,Err));
        if Err.real<=Tol:
            print("Final Voltage value :\n%s" %V);
            print("Final Current value : \n%s" %Il[:n-1]);
            print("number of iterations : \n%d" %n);
            break;
        else:
        Vold=Vl;   
        BKWsweep(V,Z,I)   # Backward sweep
        n=n+1;
        '''