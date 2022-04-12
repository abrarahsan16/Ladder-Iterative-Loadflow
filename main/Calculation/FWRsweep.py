import numpy as np
import PySimpleGUI as sg
def FWR(inputArr, Vs):
   sg.Print('Calculating Voltage in Forward Sweep')
   for i in range(len(inputArr)):
      ZZ = complex(inputArr[i,2], inputArr[i,3])
      dup = np.where(inputArr[:, 0] == inputArr[i, 0])
      if len(dup[0]) == 1:
         if i == 0:
            inputArr[i, 4] = Vs - (ZZ*inputArr[i, 6]) # voltage at node 2
         # If the current row is part of the previous row's branch
         elif inputArr[i, 0] == inputArr[i-1, 1]:
            inputArr[i, 4] = inputArr[i - 1, 4] - (ZZ*inputArr[i, 6]) # voltage at node
            #print(inputArr[i, 0])
         #else:
      # If the current row has a duplicate somewhere
      elif len(dup[0]) > 1:
         # Iterate through the entire list of duplicates
         for j in dup[0]:
            #print(dup[0])
            # If the current duplicate is also the current bus
            if j == i:
                  # Check if we are still part of the same branch
                  if inputArr[j, 0] == inputArr[j - 1, 1]:
                     inputArr[j, 4] = inputArr[j - 1, 4] - (ZZ*inputArr[j, 6]) # voltage at node
                     #print(inputArr[i, 0])
                     #print(j)
                  else:
                     # Pull the bus number of the first duplicate, to get the voltage at that point
                     k = dup[0][0]
                     # Verify that the duplicate's previous row is still part of same branch
                     if inputArr[k, 0] == inputArr[k - 1, 1]:
                        inputArr[j, 4] = inputArr[k - 1, 4] - (ZZ*inputArr[j, 6]) # voltage at node
                        #print(inputArr[j, 0])
                        #print(k)
                        #print(j)
                        #print("")


   return inputArr

'''
def FWR(inputArr, Vs):
   for i in range(len(inputArr)):
      ZZ = complex(inputArr[i,2], inputArr[i,3])
      if i == 0:
         inputArr[i, 4] = Vs - (ZZ*inputArr[i, 6]) # voltage at node 2
      else:
         inputArr[i, 4] = inputArr[i - 1, 4] - (ZZ*inputArr[i, 6]) # voltage at node 
   return inputArr
'''