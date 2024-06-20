import random
import numpy as np
import concurrent.futures
import sys
import argparse

from player import *
from dealer import *
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

def rebuildShare(layer, n_players, players, q, HE):
    reconstructedSecret, decryptedSecret = [], ""
    n_shares = len(players[layer][0].y)

    for j in range(n_shares):
        value = reconstruct(players[layer][:n_players + 1], j, q)
        reconstructedSecret.append(value)
    for k in range(len(reconstructedSecret)):
        reconstructedSecret[k] = HE.decrypt(reconstructedSecret[k])[0] % q
    decryptedSecret = "".join(chr(c) for c in reconstructedSecret)
    return (n_players + 1, layer + 1, decryptedSecret)

def decrypt(players, dealers):
    HE = dealers[0][0].HE
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures, results = [], []
         
        for i in range(len(players) - 1, -1, -1):
            for n_players in range(0, len(players[i])):
                futures.append(executor.submit(rebuildShare, i, n_players, players, dealers[i][0].q, HE))
        for future in futures:
            results.append(future.result())
        concurrent.futures.wait(futures)
        
    with open('result.txt', 'a') as file:
        for result in results:
            nPlayers, layer, decryptedValue = result
            file.write(f"Reconstructed secret with {nPlayers} shares for layer {layer} = {decryptedValue}\n")

def splitSecret(dealer, players, prev_player):
    if prev_player:
        dealer.chooseSecret(prev_player.y)
    dealer.chooseQ()

    for secretDigit in dealer.secret:
        coefficients = [random.randint(1, dealer.q) for _ in range(dealer.threshold - 1)]
        polynomial = np.polynomial.Polynomial([0] + coefficients)
        dealer.distributeShares(players, polynomial, secretDigit)

def encrypt(players, dealers):
    for layer, dealer_layer in enumerate(dealers):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for j, dealer in enumerate(dealer_layer):
                prev_player = players[layer - 1][j] if layer > 0 else None
                futures.append(executor.submit(splitSecret, dealer, players[layer], prev_player))
            concurrent.futures.wait(futures)

def recomputePolynomials(dealer):
    return dealer.recomputePolynomials()

def recomputeShares(dealer, players):
    for player in players:
        for i in range(len(player.y)):
            encryptedShare = player.getEncrypteShare(i)
            player.setShare(dealer.recomputeShare(encryptedShare, player.x, i))

def proactive(players, dealers):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for layer in range(len(dealers)):
            futures = [executor.submit(recomputePolynomials, dealer) for dealer in dealers[layer]]
        concurrent.futures.wait(futures)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(recomputeShares, dealer_list, player_list) for dealer_list, player_list in zip(dealers[::-1], players[::-1])]
        concurrent.futures.wait(futures)

def removePlayer(players, dealers):
    choice = ""
    layer, nPlayer = 0, 0

    while True:
        choice = input("Would you like to remove a player that's not trusted anymore? (yes/no)\n")
        if choice.lower() == "no":
            break
        else:
            while choice.lower() == "yes":
                layer = int(input("Select the layer of the player you want to remove\n"))
                if layer <= len(players):
                    nPlayer = int(input("Select the player you want to remove\n"))
                    if nPlayer <= len(players[layer - 1]):
                        nonTrustedPlayer = players[layer - 1].pop(nPlayer - 1)
                        del nonTrustedPlayer
                        choice = input("Would you like to remove a player that's not trusted anymore? (yes/no)\n")
            proactive(players, dealers)
            break

def parse_arguments():
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser()
        parser.add_argument('-l', '--layers', type=int, required=False, 
                            help='Number of layers')
        parser.add_argument('-n', '--players', nargs='+', type=int, required=False, 
                            help='Number of players for each layers')
        parser.add_argument('-t', '--thresholds', nargs='+', type=int, required=False, 
                            help='Thresholds for each layer')
        parser.add_argument('-f', '--file', nargs='+', type=str, required=False, 
                            help='Name of the file to encrypt')
        parser.add_argument('-p', '--proactive', nargs='+', type=bool, required=False, 
                            help='Use proactive NSS or not')
        
        args = parser.parse_args()
        print(args)
        
        if args and len(args.players) != args.layers or len(args.thresholds) != args.layers:
            parser.error("Number of players and thresholds must be equal to the number of layers")
        return args
    return None
    
def main():
    args = parse_arguments()

    layers = args.layers if args else int(input("Insert how many layers of NSS you want to use: "))
    filename = args.file if args else None
    proactive = args.proactive if args else None
    players = []
    dealers = []
    n_players, thresholds = None, None

    if args:
        n_players = args.players
        thresholds = args.thresholds
    else:
        n_players = [int(input(f"Choose the number of players for layer {layer + 1}: ")) for layer in range(layers)]
        thresholds = [int(input(f"Choose the threshold for layer {layer + 1}: ")) for layer in range(layers)]

    first, idx = True, 0
    for n, threshold in zip(n_players, thresholds):
        players.append([Player(i) for i in range(1, n + 1)])
        dealers.append([Dealer(threshold, False) for _ in range(len(players[idx - 1]))] if not first else [Dealer(threshold, True)])
        first = False
        idx += 1
    open('result.txt', 'w').close()

    dealers[0][0].chooseSecret(filename=filename[0]) if filename else dealers[0][0].chooseSecret()
    encrypt(players, dealers)
    decrypt(players, dealers)
    if proactive == "1" or proactive is None:
        removePlayer(players, dealers)
        open('result.txt', 'w').close()
        decrypt(players, dealers)

if __name__ == "__main__":
    main()
    sys.exit(0)
