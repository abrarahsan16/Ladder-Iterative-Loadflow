# Single-phase lateral for 3 bus systems.

Tol=0.0001;
Z = [0.1705+ 0.3409j,0.2273+ 0.4545j,0.2273+ 0.4545j,0.2273+ 0.4545j,0.2273+ 0.4545j,0.2273+ 0.4545j,0.2273+ 0.4545j,0.2273+ 0.4545j,0.2273+ 0.4545j]
V=[0,0,0,0,0,0,0,0,0]
S=[1500 + 750j,900 + 500j,800 + 450j,700 + 400j,600 + 350j,500 + 300j,400 + 250j,300 + 200j,200 + 100j]
I=[0,0,0,0,0,0,0,0,0]
Il=[0,0,0,0,0,0,0,0,0,0,0] 
I12=I23=I34=I45=I56=I67=I78=I89=I910=0;Vold=0;n=0 ;
Vs= 7200; # The source voltage at node 1
while n<200:
# Forward sweep
 for i in range(9):
     if i == 0:
        V[i]=Vs-(Z[i]*Il[i]); # voltage at node 2
     else:
        V[i]=V[i-1]-(Z[i]*Il[i]); # voltage at node 2

       
        
 array_length = len(V)
 Vl = V[array_length - 1]

 Err=(abs(Vl.real-Vold.real)/Vs)
 print(Err)
 if Err.real<=Tol:
    print(V);
    print(Il);
    print(n);
    break;
 else:
 # Backward sweep
    Vold=Vl;
 for i in [8,7,6,5,4,3,2,1,0]:
     I[i]=((S[i]*1000)/V[i]).conjugate()
     Il[i]=I[i]+Il[i+1]
 n=n+1;