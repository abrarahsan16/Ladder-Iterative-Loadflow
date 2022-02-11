def FWRsweep(V,Z,Il):
    for i in range(9):
        if i == 0:
           V[i]=Vs-(Z[i]*Il[i]); # voltage at node 2
        else:
           V[i]=V[i-1]-(Z[i]*Il[i]); # voltage at node 
    return(V)

def BKWsweep(V,Z,I):
  for i in [8,7,6,5,4,3,2,1,0]:
    I[i]=((S[i]*1000)/V[i]).conjugate()
    Il[i]=I[i]+Il[i+1]
  return(Il)           
"""
Initialization

"""
Tol=0.0001;
Z = [0.1705+ 0.3409j,0.2273+ 0.4545j,0.2273+ 0.4545j,0.2273+ 0.4545j,0.2273+ 0.4545j,0.2273+ 0.4545j,0.2273+ 0.4545j,0.2273+ 0.4545j,0.2273+ 0.4545j]
V=[0,0,0,0,0,0,0,0,0]
S=[1500 + 750j,900 + 500j,800 + 450j,700 + 400j,600 + 350j,500 + 300j,400 + 250j,300 + 200j,200 + 100j]
I=[0,0,0,0,0,0,0,0,0]
Il=[0,0,0,0,0,0,0,0,0,0,0] 
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
   print("Final Current value : \n%s" %Il);
   print("number of iterations : \n%d" %n);
   break;
 else:
  BKWsweep(V,Z,I)   # Backward sweep
  Vold=Vl;
 n=n+1;