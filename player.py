import numpy as np

from Pyfhel import Pyfhel

class Player:
    __slots__ = ['x', 'y', 'layer', 'HE']

    def __init__(self, x, layer):
        self.x = x
        self.y = []
        self.layer = layer

    def addShare(self, value):
        self.y.append(value)
    
    def setShare(self, newValue, index):
        self.y[index] = newValue
    
    def getEncrypteShare(self, i):
        return self.y[i]