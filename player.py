import numpy as np
from Pyfhel import Pyfhel

class Player:
    def __init__(self, x, trusted):
        self.x = x
        self.y = []
        self.trusted = trusted
        self.HE = self.manageHomomorphic()
    
    def manageHomomorphic(self):
        HE = Pyfhel()
        HE.contextGen(scheme='bfv', n=2**14, t_bits=20)
        HE.keyGen()
        return HE
    
    def setShare(self, newValue, index):
        self.y[index] = self.HE.decryptInt(newValue)[0]
    
    def getEncrypteShare(self, i):
        return self.HE.encryptInt(np.array([self.y[i]], dtype=np.int64))
        

# Il dealer stabilisce il segreto iniziale
# Se il dealer tiene i polinomi