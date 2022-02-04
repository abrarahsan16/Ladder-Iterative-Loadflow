import os
import sys
import numpy as np
import pandas as pd
from GUI import guiInit
from Parser import parser

if __name__ == '__main__':


    event, cdfPath, tol = guiInit.gui_initial()

    readInput = pd.read_excel(cdfPath, header=None)
    numpyConversion = readInput.to_numpy()
    checker = parser.checkIfAllTablesExist(readInput)

    SBase = parser.SBaseExtractor(numpyConversion)



    if checker == False:
        raise ValueError("Excel does not contain Bus or Branch data, please double check and try again")

    busData = parser.extractData(numpyConversion, "BUS DATA FOLLOWS")
    branchData = parser.extractData(numpyConversion, "BRANCH DATA FOLLOWS")

    sortedBranchData = parser.branchReorder(branchData)

    print("Table extraction complete")


