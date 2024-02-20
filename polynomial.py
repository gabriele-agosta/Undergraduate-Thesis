import random

class Polynomial:
    def __init__(self, secret, q, threshold):
        self.order = threshold - 1
        self.coefficients = [secret] + self.computeCoefficients(q, self.order)
        self.exponents = self.computeExponents(self.order + 1)
    
    def computeCoefficients(self, q, order):
        coefficients = []
        for i in range(order):
            coefficients.append(random.randint(1, q))
        return coefficients

    def computeExponents(self, order):
        exponents = [i for i in range(order)]
        return exponents
    
    def computePolynomial(self, x, q):
        res = 0
        for i in range(self.order + 1):
            res += self.coefficients[i] * (x ** self.exponents[i])
        return res % q
    
    def printPolynomial(self):
        for i in range(self.order):
            print(f"{self.coefficients[i]}x^{self.exponents[i]} + ", end="")
        print(f"{self.coefficients[i+1]}x^{self.exponents[i+1]}")