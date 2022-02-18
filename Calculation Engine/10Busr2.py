import numpy as np
import pandas as pd

def BKWsweep(V,Z,I):

  for i in range(len(BU)-1,-1,-1):
 #  for j in range(len(Z)-1,-1,-1):
    S=complex(Arr1[i,1],Arr1[i,2])  
    I[i]=((S*1000)/V[i]).conjugate()
    Il[i]=I[i]+Il[i+1]
  return(Il)  

def FWRsweep(V,Z,I):
    for i in range(len(BU)):
        ZZ = complex(Arr2[i,2],Arr2[i,3])
        if i == 0:
           V[i]=Vs-(ZZ*Il[i]); # voltage at node 2
        else:
           V[i]=V[i-1]-(ZZ*Il[i]); # voltage at node 
   
"""
Initialization

"""
Tol=0.0001;
Z = [0.1705+ 0.3409j,0.2273+ 0.4545j]
V=[0,0]
I=[0,0] #Bus current
Il=[0,0,0] #Load current
Arr1 = np.array([[1,1500,750],[2,900,500]]);  ### #input1
Arr2 = np.array([[1, 2, 0.1705, 0.3409],[2, 3, 0.2273, 0.4545]]); ### #input2
BU=Arr1[:, 0] #number of buses
dfObj = pd.DataFrame(Arr2, columns=['Bus1', 'Bus2', 'R', 'X']) #Create a DataFrame object
duplicateRowsDF = dfObj[dfObj.duplicated(['Bus1'])]   # Select all duplicate rows based on multiple column names in list
print("Duplicate Rows based on 2 columns are:", duplicateRowsDF, sep='\n')   # Print all duplicate rows based on multiple column names in list
I12=I23=I34=I45=I56=I67=I78=I89=I910=0;Vold=0;n=0 ;
Vs= 7200; # The source voltage at node 1
"""
Main 

"""
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