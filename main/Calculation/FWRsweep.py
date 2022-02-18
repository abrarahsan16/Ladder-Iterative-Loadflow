import numpy as np

def FWR(inputArr, Vs):
   for i in range(len(inputArr)):
      ZZ = complex(inputArr[i,2], inputArr[i,3])
      if i == 0:
         inputArr[i, 4] = Vs - (ZZ*inputArr[i, 6]) # voltage at node 2
      else:
         inputArr[i, 4] = inputArr[i - 1, 4] - (ZZ*inputArr[i, 6]) # voltage at node 
   return inputArr