import time 
import os
import tkinter as tk

from tkinter import filedialog

def get_filename():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()

    return file_path if file_path else exit()
            

def get_execution_time(command):
    start_time = time.time()
    os.system(command)
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    return elapsed_time


n_tests = int(input("Insert how many tests you want to conduct: "))
results = list()

for _ in range(n_tests):
    n_layers = int(input("Insert how many layers you want to use: "))
    filename = get_filename()
    launch_expression = f"python3 nss.py -l {n_layers} -n "
    n_players, thresholds = list(), list()

    for i in range(n_layers):
        n_players.append(int(input(f"Insert players number for layer {i + 1}: ")))
        thresholds.append(int(input(f"Insert threshold for layer {i + 1}: ")))


    for layer_dim in n_players:
        launch_expression += f"{layer_dim} "

    launch_expression += "-t "
    for threshold in thresholds:
        launch_expression += f"{threshold} "


    launch_expression += f"-f {filename} "
    
    while True:
        proactive = input("Would you like to remove a player that's not trusted anymore? (yes/no)\n")
        if proactive.lower() in ["yes", "no"]:
            launch_expression += f"-p 1" if proactive == "yes" else f"-p 0"
            break

    results.append((get_execution_time(launch_expression), n_players, thresholds, filename))

for elapsed_time, n_players, threshold, filename in results:
    print(f"Execution time: {elapsed_time} seconds for {filename}, while having {sum(n_players)} players with {threshold} as thresholds")