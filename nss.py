from player import *
from dealer import *

import random
import numpy as np
import concurrent.futures

def delta(i, Xs, q):
    d = 1
    for j in Xs:
        if j != i:
            d = (d * (-j) * pow((i - j) % q, -1, q)) % q
    return int(d)

def reconstruct(players, q, i):
    secretReconstructed = 0
    Xs = [player.x for player in players]
    for player in players:
        secretReconstructed += delta(player.x, Xs, q) * player.y[i]
    return secretReconstructed % q

def rebuildShare(i, n_players, players, q):
    reconstructedSecret = ""
    with open('result.txt', 'a') as result:
        n_shares = len(players[i][0].y)
        for j in range(n_shares):
            value = reconstruct(players[i][:n_players + 1], q, j)
            reconstructedSecret += chr(int(value))
        result.write(f"Reconstructed secret with {n_players + 1} shares for layer {i + 1} = {reconstructedSecret}\n")

def decrypt(players, dealers):
    with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = []
            for i in range(len(players) - 1, -1, -1):
                for n_players in range(0, len(players[i])):
                    futures.append(executor.submit(rebuildShare, i, n_players, players, dealers[i][0].q))
                concurrent.futures.wait(futures)

def splitSecret(dealer, players, prev_player):
    if prev_player:
        dealer.chooseSecret(prev_player.y[-1])
    dealer.chooseQ()

    for cipher in dealer.secret:
        coefficients = [random.randint(1, dealer.q) for _ in range(dealer.threshold - 1)]
        polynomial = np.polynomial.Polynomial([cipher] + coefficients)
        dealer.distributeShares(players, polynomial)

def encrypt(players, dealers):
    with concurrent.futures.ThreadPoolExecutor() as executor:  
        futures = []
        for layer in range(len(dealers)):
            j = 0
            for dealer in dealers[layer]:
                prev_player = players[layer - 1][j] if layer > 0 else None
                futures.append(executor.submit(splitSecret, dealer, players[layer], prev_player))
                j += 1
            concurrent.futures.wait(futures)

def proactive(players, dealers):
    for layer in range(len(players)):
        for player in players[layer]:
            player.recomputePolynomials(dealers[layer][0].q, dealers[layer][0].threshold - 1)
    
    for i in range(len(players) - 1, -1, -1):
        proactivePolynomials = []
        for player in players[i]:
            proactivePolynomials.append(player.proactivePolynomials)
        
        for j in range(len(proactivePolynomials)):
            for player in players[i]:
                player.recomputeSecret(proactivePolynomials, j)

def removePlayer(players, dealers):
    choice = ""
    layer, nPlayer = 0, 0

    while True:
        choice = input("Would you like to remove a player that's not trusted anymore? (yes/no)\n")
        if choice.lower() == "yes":
            while True:
                layer = int(input("Select the layer for the player you want to remove\n"))
                if layer <= len(players):
                    nPlayer = int(input("Select the player you want to remove\n"))
                    if nPlayer <= len(players[layer - 1]):
                        players[layer - 1].pop(nPlayer - 1)
                        proactive(players, dealers)
                        break
        elif choice.lower() == "no":
            break
    
def main():
        layers = int(input("Insert how many layers of NSS you want to use: "))
        players = [[] for _ in range(layers)]
        dealers = [[] for _ in range(layers)]
        open('result.txt', 'w').close()

        for layer in range(layers):
            n = int(input(f"Choose the number of players for layer {layer + 1}: "))
            threshold = int(input(f"Choose the threshold for layer {layer + 1}: "))
            players[layer] += [Player(i, True) for i in range(1, n + 1)] if layer < 1 else [Player(i, False) for i in range(1, n + 1)]
            dealers[layer] += [Dealer(threshold) for _ in range(len(players[layer - 1]))] if (layer - 1) >= 0 else [Dealer(threshold)]
        
        dealers[0][0].chooseSecret()
        encrypt(players, dealers)
        decrypt(players, dealers)
        removePlayer(players, dealers)
        open('result.txt', 'w').close()
        decrypt(players, dealers)


if __name__ == "__main__":
    main()