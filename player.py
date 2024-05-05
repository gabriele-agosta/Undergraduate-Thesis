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
    
    def setShare(self, newValue, index):
        self.y[index] = newValue
    
    def getEncrypteShare(self, i):
        return self.y[i]