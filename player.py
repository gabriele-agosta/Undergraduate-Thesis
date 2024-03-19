import numpy as np
import random

class Player:
    def __init__(self, x, trusted):
        self.x = x
        self.y = []
        self.polynomials = []
        self.proactivePolynomials = []
        self.trusted = trusted
    
    def recomputePolynomials(self, q, threshold):
        self.proactivePolynomials.clear()
        for _ in range(len(self.polynomials)):
            coefficients = [random.randint(1, q) for _ in range(threshold - 1)]
            polynomial = np.polynomial.Polynomial([0] + coefficients)
            self.proactivePolynomials.append(polynomial)
    
    def recomputeSecret(self, othersProactivePolynomials, i):
        value = 0
        for polynomials in othersProactivePolynomials:
            value += polynomials[i](self.x)
        self.polynomials[i] += value
        