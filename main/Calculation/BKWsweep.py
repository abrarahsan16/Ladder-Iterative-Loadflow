import numpy as np

def BKWsweep(busArr, inputArr):
  for i in range(len(inputArr)-1,-1,-1):
    S = complex(busArr[i+1,1], busArr[i+1,2])  
    inputArr[i, 5] = ((S)/inputArr[i, 4]).conjugate()
    #inputArr[i, 5] = ((S*1000)/inputArr[i, 4]).conjugate()
    if i == len(inputArr)-1:
      inputArr[i, 6] = inputArr[i, 5] + 0
    else:
      inputArr[i, 6] = inputArr[i, 5] + inputArr[i+1, 6]
  return(inputArr)