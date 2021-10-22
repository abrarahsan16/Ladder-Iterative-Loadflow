# Single-phase lateral for 1 bus system.
Tol=0.0001
z12=0.1705+ 0.3409j #The line impedanc
S2=1500 + 750j #loads power
I12=0;Vold=0;n=0
Vs= 7200 # The source voltage at node 1
while n<20:
# Forward sweep
 V2=Vs-(z12*I12) # voltage at node 2
 Err=(abs(V2.real-Vold.real)/Vs)
 if Err.real<=Tol:
     print(V2)
     print(I12)
     print(n)
     break
 else:
# Backward sweep
    Vold=V2
    I12=((S2*1000)/V2).conjugate() # New current in line segment 1–2
 n+=1