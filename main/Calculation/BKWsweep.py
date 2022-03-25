import numpy as np
import math as mth

def BKWsweep(busArr, inputArr):
  # Generate the load currents
  for i in range(len(inputArr)-1,-1,-1):
      busFinder = np.where(busArr[:, 0] == inputArr[i, 1])
      j = busFinder[0][0]
      S = complex(busArr[j,1], busArr[j, 2])
      #inputArr[i, 5] = ((S)/(inputArr[i, 4]*mth.sqrt(3))).conjugate()
      inputArr[i, 5] = ((S)/(inputArr[i, 4])).conjugate()
      inputArr[i, 6] = 0
      #print(inputArr[i, 5])

  # Calculate the currents for each bus
  for i in range(len(inputArr)-1,-1,-1):
      dup = np.where(inputArr[:, 0] == inputArr[i, 1])
      #print(dup[0])
      if len(dup[0]) <= 1:
          if len(dup[0]) == 0: # If it is the last bus of the branch, duplicate will be empty
          #if i == len(inputArr) - 1:
              inputArr[i, 6] = inputArr[i, 5] + 0 # Final bus, so all current goes into load
              #print(inputArr[i, 1])
          elif inputArr[i, 1] == inputArr[i + 1, 0]:
              inputArr[i, 6] = inputArr[i, 5] + inputArr[i + 1, 6]
              #print(inputArr[i, 1])
      elif len(dup[0]) > 1:
          k = dup[0][0] - 1
          if k != i:
              continue
          else:
              for j in dup[0]:
                  if j != i:
                      inputArr[k, 6] = inputArr[k, 6] + inputArr[j, 6]
              inputArr[k, 6] = inputArr[i, 6] + inputArr[i, 5]
  return(inputArr)

  '''
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
  '''