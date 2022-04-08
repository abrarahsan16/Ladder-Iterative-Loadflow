import numpy as np
import math as mth

def LossEquation(branchArr, Sb):
    sLoss = np.zeros([branchArr.shape[0], 1], dtype = np.complex_)
    for i in range(len(branchArr)):
        ZZ = complex(branchArr[i, 2], branchArr[i, 3])
        if i == 0:
            Vk = 1
            Vm = branchArr[i, 4]
            sLoss[i] = (Vk * np.conjugate((Vk - Vm)/ZZ)) + (Vm * np.conjugate((Vm - Vk)/ZZ))
        elif branchArr[i, 0] == branchArr[i-1, 1]:
            Vk = branchArr[i-1, 4]
            Vm = branchArr[i, 4]
            sLoss[i] = (Vk * np.conjugate((Vk - Vm)/ZZ)) + (Vm * np.conjugate((Vm - Vk)/ZZ))
        elif branchArr[i, 0] != branchArr[i-1, 1]:
            dup = np.where(branchArr[:, 0] == branchArr[i, 0])
            k = dup[0][0] - 1
            Vk = branchArr[k, 4]
            Vm = branchArr[i, 4]
            sLoss[i] = (Vk * np.conjugate((Vk - Vm)/ZZ)) + (Vm * np.conjugate((Vm - Vk)/ZZ))
    #print(sLoss*Sb*1000)
    return sLoss
    #raise NotImplementedError('Implement this function/method.')