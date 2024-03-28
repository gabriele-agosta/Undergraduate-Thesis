import tkinter as tk
import numpy as np
import random

from tkinter import filedialog
from Pyfhel import Pyfhel

class Dealer:
    def __init__(self, threshold, homomorphic=False):
        self.threshold = threshold
        self.secret = None
        self.q = None
        self.polynomials = []
        self.HE = self.manageHomomorphic() if homomorphic else None

    def manageHomomorphic(self):
        HE = Pyfhel()
        HE.contextGen(scheme='bfv', n=2**14, t_bits=20)
        HE.keyGen()
        return HE

    def chooseSecret(self, secret=None):
        ascii_secret = None
        s = []
        if secret is None:
            while True:
                choice = input("Choose what you want to encrypt: \n1.Text/Number; \n2.File content. \n")
                if choice.isdigit() and 1 <= int(choice) <= 2:
                    break
            
            ascii_secret = []
            if choice == "1":
                secret = input("Insert your secret: ")
                ascii_secret = [ord(c) for c in secret]
            else:
                root = tk.Tk()
                root.withdraw()
                file_path = filedialog.askopenfilename()
    
                if file_path:
                    with open(file_path, "r") as file:
                        secret = file.read()
                        ascii_secret = [ord(c) for c in secret]
                else:
                    print("No file selected.")
                root.destroy()
        else:
            ascii_secret = [ord(c) for c in str(secret)]
        self.secret = ascii_secret

    def chooseQ(self):
        self.q = 127

    def distributeShares(self, players, f, lastLayer):
        for i in range(len(players)):
            self.polynomials.append(f)
            val = f(players[i].x) % self.q
            players[i].y.append(players[i].HE.encryptInt(np.array([val], dtype=np.int64) )) if lastLayer else players[i].y.append(val)
    
    def recomputePolynomials(self):
        for i in range(len(self.polynomials)):
            coefficients = [random.randint(1, self.q) for _ in range(self.threshold - 1)]
            proactivePolynomial = np.polynomial.Polynomial([0] + coefficients)
            self.polynomials[i] += proactivePolynomial
    
    def recomputeShare(self, encryptedShare, x, index):
        return encryptedShare + self.polynomials[index](x)
            