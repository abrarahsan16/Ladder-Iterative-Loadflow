import pandas as pd
import numpy as np

test = pd.read_excel('test.xlsx')
nptest = test.to_numpy()
#test


#For loop method
lenOfNp = np.shape(nptest)
npflipped = np.transpose(nptest)
startNode=(npflipped[:][0])
endNode=(npflipped[:][1])
for i in range(nptest.shape[0]):
  duplicateFound = False
  if startNode[i] != -999:
    startingNode = startNode[i]
    endingNode = endNode[i]
    for j in range(i, nptest.shape[0]):
      #j = i-1
      if i != j:
        if startingNode == startNode[j]:
          duplicateFound = True
          break
    if duplicateFound == True:
      
      print(startNode[i])

#Unique values
values, counts = np.unique(startNode, return_counts=True)
values