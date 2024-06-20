import tkinter as tk
import numpy as np
import random

from tkinter import filedialog
from Pyfhel import Pyfhel, PyCtxt

class Dealer:
    __slots__ = ['threshold', 'secret', 'q', 'polynomials', 'HE']

    def __init__(self, threshold, homomorphic=False):
        self.threshold = threshold
        self.secret = None
        self.q = None
        self.polynomials = []
        self.HE = self.manageHomomorphic() if homomorphic else None

    def manageHomomorphic(self):
        HE = Pyfhel()
        HE.contextGen(scheme='bfv', n=2**11, t_bits=20)
        HE.keyGen()
        return HE

    def chooseSecret(self, secret=None, filename=None):
        ascii_secret = None
        s = []
        if secret is None:
            choice = 2 if filename else None
            while True and not filename:
                choice = int(input("Choose what you want to encrypt: \n1.Text/Number; \n2.File content. \n"))
                if 1 <= choice <= 2:
                    break
            
            ascii_secret = []
            if choice == 1:
                secret = input("Insert your secret: ")
                ascii_secret = [self.HE.encryptInt(np.array([ord(c)], dtype=np.int64)) for c in secret]
            else:
                root = tk.Tk()
                root.withdraw()
                file_path = filedialog.askopenfilename() if not filename else filename
    
                if file_path:
                    with open(file_path, "r") as file:
                        secret = file.read()
                        ascii_secret = [self.HE.encryptInt(np.array([ord(c)], dtype=np.int64)) for c in secret]
                else:
                    print("No file selected.")
                root.destroy()
        else:
            ascii_secret = [ord(c) if type(c) != PyCtxt else c for c in secret]
        self.secret = ascii_secret

    def chooseQ(self):
        self.q = 127

    def distributeShares(self, players, f, secretDigit):
        for i in range(len(players)):
            self.polynomials.append(f)
            val = (f(players[i].x) % self.q) + secretDigit
            players[i].addShare(val)
    
    def recomputePolynomials(self):
        for i in range(len(self.polynomials)):
            coefficients = [random.randint(1, self.q) for _ in range(self.threshold - 1)]
            proactivePolynomial = np.polynomial.Polynomial([0] + coefficients)
            self.polynomials[i] += proactivePolynomial
    
    def recomputeShare(self, encryptedShare, x, index):
        return encryptedShare + self.polynomials[index](x)
            