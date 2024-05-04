import numpy as np

from Pyfhel import Pyfhel

class Player:
    __slots__ = ['x', 'y', 'layer', 'HE']

    def __init__(self, x, layer):
        self.x = x
        self.y = []
        self.layer = layer
        self.HE = self.manageHomomorphic()
    
    def manageHomomorphic(self):
        HE = Pyfhel()
        HE.contextGen(scheme='bfv', n=2**11, t_bits=20)
        HE.keyGen()
        return HE

    def addShare(self, value):
        self.y.append(value)
    
    def setShare(self, newValue, index, lastLayer):
        self.y[index] = self.HE.decryptInt(newValue)[0]
    
    def getEncrypteShare(self, i):
        return self.HE.encryptInt(np.array([self.y[i]], dtype=np.int64))