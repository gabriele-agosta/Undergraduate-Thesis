from player import *
from dealer import *
from polynomial import *

def delta(i, Xs, q):
    d = 1
    for j in Xs:
        if j != i:
            d = (d * (-j) * pow((i - j) % q, -1, q)) % q
    return int(d)

def reconstruct(players, q):
    secretReconstructed = 0
    Xs = [player.x for player in players]
    for player in players:
        secretReconstructed += delta(player.x, Xs, q) * player.y
    return secretReconstructed % q

def main():
    layers = int(input("Insert how many layers of NSS you want to use: "))
    players = [[] for _ in range(layers)]
    dealers = [[] for _ in range(layers)]
    # Probabilmente mi servirà un array di Dealer: i player del layer n saranno i dealer del layer n+1

    

    
    for layer in range(layers):
        n = int(input(f"Choose the number of players for layer {layer + 1}: "))
        threshold = int(input(f"Choose the threshold for layer {layer + 1}: "))
        # Attualmente sto mettendo tutti i player come trusted, per evitare di gestire fin da subito la complessità di avere trusted e non trusted
        players[layer] += [Player(i, True) for i in range(1, n + 1)]
        dealers[layer] += [Dealer(threshold) for _ in range(len(players[layer - 1]))] if ((layer - 1) >= 0) else [Dealer(threshold)]
    
    # Se voglio mostrare tutti i risultati possibili, devo organizzare per bene questa sezione qui. 
    # Intanto sarebbe buono dividere la fase di codifica da quella di decodifica
    for i in range(len(dealers)):
        j = 0
        for dealer in dealers[i]:
            if i == 0:
                dealer.chooseSecret()
            else:
                dealer.chooseSecret(players[i - 1][j].y)
                j += 1
            dealer.chooseQ()
            dealer.chooseP()
            dealer.chooseGenerator()

            for n_players in range(1, len(players[i])):
                for cipher in dealer.secret:
                    f = Polynomial(cipher, dealer.q, dealer.threshold)
                    dealer.distributeShares(players[i], f)
    
    with open('result.txt', 'w') as result:
        reconstructedSecret = ""
        for i in range(len(players) -1, -1, -1):
            for n_players in range(1, len(players[i])):
                for dealer in dealers[i]:
                    for cipher in dealer.secret:
                        f = Polynomial(cipher, dealer.q, dealer.threshold)

                        dealer.distributeShares(players[i], f)
                        reconstructedSecret += chr(reconstruct(players[i], dealer.q))
                    result.write(f"Reconstructed secret with {n_players} shares = {reconstructedSecret}\n")

if __name__ == "__main__":
    main()