from player import *
from dealer import *

import random
import numpy as np
import concurrent.futures

from Pyfhel import Pyfhel

def delta(i, Xs, q):
    d = 1
    for j in Xs:
        if j != i:
            d = (d * (-j) * pow((i - j) % q, -1, q)) % q
    return int(d)

def reconstruct(players, i, q):
    secretReconstructed = 0
    Xs = [player.x for player in players]
    for player in players:
        secretReconstructed += delta(player.x, Xs, q) * player.y[i]
    return secretReconstructed

def rebuildShare(i, n_players, players, q, HE):
    reconstructedSecret, decryptedSecret = [], ""
    n_shares = len(players[i][0].y)

    for j in range(n_shares):
        value = reconstruct(players[i][:n_players + 1], j, q)
        reconstructedSecret.append(value) if HE else reconstructedSecret.append(chr(int(value % q)))
    if HE:
        for k in range(len(reconstructedSecret)):
            reconstructedSecret[k] = HE.decryptInt(reconstructedSecret[k])[0] % q
        for val in reconstructedSecret:
            decryptedSecret += chr(val)
    else:
        decryptedSecret = "".join(reconstructedSecret)
    return (n_players + 1, i + 1, decryptedSecret)

def decrypt(players, dealers):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures, results = [], []
         
        for i in range(len(players) - 1, -1, -1):
            for n_players in range(0, len(players[i])):
                futures.append(executor.submit(rebuildShare, i, n_players, players, dealers[i][0].q, dealers[i][0].HE))
        for future in futures:
            results.append(future.result())
        
        with open('result.txt', 'a') as file:
            for result in results:
                nPlayers, layer, decryptedValue = result
                file.write(f"Reconstructed secret with {nPlayers} shares for layer {layer} = {decryptedValue}\n")

def splitSecret(dealer, players, prev_player, lastLayer):
    if prev_player:
        dealer.chooseSecret(prev_player.y[-1])
    dealer.chooseQ()

    for cipher in dealer.secret:
        coefficients = [random.randint(1, dealer.q) for _ in range(dealer.threshold - 1)]
        polynomial = np.polynomial.Polynomial([cipher] + coefficients)
        dealer.distributeShares(players, polynomial, lastLayer)

def encrypt(players, dealers):
    lastLayer = False
    for layer, dealer_layer in enumerate(dealers):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            lastLayer = True if layer == len(players) - 1 else False
            for j, dealer in enumerate(dealer_layer):
                prev_player = players[layer - 1][j] if layer > 0 else None
                futures.append(executor.submit(splitSecret, dealer, players[layer], prev_player, lastLayer))
            concurrent.futures.wait(futures)

def recomputePolynomials(dealer):
    return dealer.recomputePolynomials()

def recomputeShares(dealers, players, lastLayer):
    for dealer in dealers:
        for player in players:
            for i in range(len(player.y)):
                encryptedShare = player.getEncrypteShare(i)
                player.setShare(dealer.recomputeShare(encryptedShare, player.x, i), lastLayer)

def proactive(players, dealers):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for layer in enumerate(dealers):
            for dealer in dealers:
                futures.append(executor.submit(recomputePolynomials, dealer))
        concurrent.futures.wait(futures)

    for i in range(len(dealers) - 1, -1, -1):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            lastLayer = True if i == len(dealers) - 1 else False
            futures.append(executor.submit(recomputeShares, dealers[i], players[i], lastLayer))
            concurrent.futures.wait(futures)

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
            
            if (layer - 1) >= 0:
                dealers[layer] += [Dealer(threshold) for _ in range(len(players[layer - 1]))] if layer < layers - 1 else [Dealer(threshold, True) for _ in range(len(players[layer - 1]))]
            else:
                dealers[layer] += [Dealer(threshold)]

        dealers[0][0].chooseSecret()
        encrypt(players, dealers)
        decrypt(players, dealers)
        removePlayer(players, dealers)
        open('result.txt', 'w').close()
        decrypt(players, dealers)


if __name__ == "__main__":
    main()