import math
import tkinter as tk
from tkinter import filedialog

class Dealer:

    def __init__(self, threshold):
        self.threshold = threshold
        self.secret = None
        self.q = None
        self.layers = None

    def chooseSecret(self, secret=None):
        ascii_secret = None
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
    
    def chooseLayers(self):
        self.layers = int(input("Insert how many layers of NSS you want to use: "))

    def distributeShares(self, players, f):
        for player in players:
            player.y = f.computePolynomial(player.x, self.q)

    def _isPrime(self, n):
        if n == 2:
            return True
        if n == 1 or n % 2 == 0:
            return False    
        i = 3    
        while i <= math.sqrt(n):
            if n % i == 0:
                return False
            i = i + 2        
        return True