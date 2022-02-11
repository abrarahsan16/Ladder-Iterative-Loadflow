def FWRsweep(V,Z,Il,Vs):
    for i in range(9):
        if i == 0:
           V[i]=Vs-(Z[i]*Il[i]); # voltage at node 2
        else:
           V[i]=V[i-1]-(Z[i]*Il[i]); # voltage at node 
    return(V)

def BKWsweep(V,Z,I,S,Il):
  for i in [8,7,6,5,4,3,2,1,0]:
    I[i]=((S[i]*1000)/V[i]).conjugate()
    Il[i]=I[i]+Il[i+1]
  return(Il)