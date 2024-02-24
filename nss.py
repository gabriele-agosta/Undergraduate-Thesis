from player import *
from dealer import *
from polynomial import *
import threading

semaphore = threading.Semaphore(0)

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

def process_dealer(dealer, players, player):
    if player:
        dealer.chooseSecret(player.y)
    dealer.chooseQ()

    for n_players in range(1, len(players)):
        for cipher in dealer.secret:
            f = Polynomial(cipher, dealer.q, dealer.threshold)
            dealer.distributeShares(players, f)
    
    

def main():
    layers = int(input("Insert how many layers of NSS you want to use: "))
    players = [[] for _ in range(layers)]
    dealers = [[] for _ in range(layers)]

    for layer in range(layers):
        n = int(input(f"Choose the number of players for layer {layer + 1}: "))
        threshold = int(input(f"Choose the threshold for layer {layer + 1}: "))
        # Attualmente sto mettendo tutti i player come trusted, per evitare di gestire fin da subito la complessità di avere trusted e non trusted
        players[layer] += [Player(i, True) for i in range(1, n + 1)]
        dealers[layer] += [Dealer(threshold) for _ in range(len(players[layer - 1]))] if ((layer - 1) >= 0) else [Dealer(threshold)]
    
    # Encryption
        
    # Potrei prendere il segreto fuori dal ciclo, e poi fare un thread per ogni player del layer, e aspettando che finiscano
    '''
    for i in range(len(dealers)):
        j = 0
        for dealer in dealers[i]:
            if i == 0:
                dealer.chooseSecret()
            else:
                dealer.chooseSecret(players[i - 1][j].y)
                j += 1
            dealer.chooseQ()

            for n_players in range(1, len(players[i])):
                for cipher in dealer.secret:
                    f = Polynomial(cipher, dealer.q, dealer.threshold)
                    dealer.distributeShares(players[i], f)
    '''

    dealers[0][0].chooseSecret()
    threads = []
    for layer in range(0, len(dealers)):
        j = 0
        for dealer in dealers[layer]:
            prev_player = players[layer - 1][j] if layer > 0 else None
            thread = threading.Thread(target=process_dealer, args=(dealer, players[layer], prev_player))
            threads.append(thread)
            thread.start()
            
            j += 1
    for thread in threads:
        thread.join()

    
    
    # Decryption
    with open('result.txt', 'w') as result:
        reconstructedSecret = None
        for i in range(len(players) -1, -1, -1):
            for n_players in range(0, len(players[i])):
                reconstructedSecret = ""
                for dealer in dealers[i]:
                    for cipher in dealer.secret:
                        f = Polynomial(cipher, dealer.q, dealer.threshold)

                        dealer.distributeShares(players[i], f)
                        reconstructedSecret += chr(reconstruct(players[i][:n_players + 1], dealer.q))
                result.write(f"Reconstructed secret with {n_players + 1} shares for layer {i + 1} = {reconstructedSecret}\n")
            result.write("----------------------------------------------------------------------------------------------\n")

if __name__ == "__main__":
    main()