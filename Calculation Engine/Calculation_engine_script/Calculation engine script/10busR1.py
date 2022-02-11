# Single-phase lateral for 3 bus systems.
import function
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
 function.FWRsweep(V,Z,I,Vs)    # Forward sweep    
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
  function.BKWsweep(V,Z,I,S,Il)   # Backward sweep
  Vold=Vl;
 n=n+1;