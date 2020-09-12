"""\
use Q-learning - Off-policy learning algorithm - agent learns from itself
NOTE: will need alot of computation due to many states of chess board
may be able to reduce computation through a prediction systen (NN)
OR use nathans AWS cloud service
"""

import functions
import random
import numpy as np
import time
import winsound #alert when finished

def getHash(board):
    return str(board).replace("\n", "").replace(" ", "")

def printHash(hashBoard):
    for index, char in enumerate(hashBoard):
        if index % 8 == 0:
            print()
        else:
            print(char, end="")

def rate(qtable, board):
    return qtable.get(getHash(board))

def save(filename, data):
    """data should be the qtable"""
    with open(filename, "w") as f: #append to file
        for key, value in data.items():
            f.write(key+","+str(value))
            f.write("\n")

def load(filename):
    try:
        with open(filename, "r") as f:
            qtable = {}
            for line in f:
                hashBoard, value = line.strip().split(",")
                qtable[hashBoard] = float(value)
        return qtable
    except FileNotFoundError:
        return {}

FILENAME = "TDTable.txt"
qtable = load(FILENAME)
