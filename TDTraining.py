"""\
use Q-learning - Off-policy learning algorithm - agent learns from itself
NOTE: will need alot of computation due to many states of chess board
may be able to reduce computation through a prediction systen (NN)
OR use nathans AWS cloud service
"""

import random
from functions.functions import Board
from q_functions import getHash, printHash, rate, save, load
from pygameDisplay import pygameDisplay

import numpy as np
import time

FILENAME = "TDTable.txt"
qtable = load(FILENAME)

def getBestMove(qtable, board):
    assert board.findPiece("k") and board.findPiece("K")
    values = {}
    for startPos, possibleEnd in board.getMoves(board.whiteMove).items():
        for endPos in possibleEnd:
            key = getHash(board.move(startPos, endPos))
            if key in qtable:
                values[qtable[key]] = (startPos, endPos)
            else:
                values[0] = (startPos, endPos)
                
    maxValue = max(values.keys())
    action = values[maxValue]
    return action, maxValue

def getRandomMove(board):
    moves = board.getMoves(board.whiteMove)
    moveFrom = random.choice(list(moves.keys()))
    moveTo = random.choice(list(moves[moveFrom]))
    return (moveFrom, moveTo)

def training(total_episodes, qtable={}):
    # TODO: change qtable to a grid: rows are the state, each element in the row is the rating of the action
    # there are 16 pieces on 64 squares, there are 64C16 + 64C15 + ... + 64C2
    # 12 unique pieces
    
    # Exploration parameters
    epsilon = 1.0 # Exploration rate
    max_epsilon = 0.01 #1.0 # Exploration probability at start
    min_epsilon = 0.01 # Minimum exploration probability
    decay_rate = 0.01 # Exponential decay rate for exploration prob
    
    max_steps = 99 # Max steps per episode
    learning_rate = 0.7 # Learning rate
    gamma = 0.618 # Discounting rate

    rewardValues = {"k":200, "q":8, "r":5, "b":3.3, "n":3.2, "p":1, " ":-1}
    
    # run for total_episodes repeats
    for episode in range(total_episodes):
        print("Progress:", round((episode+1)/total_episodes*100, ndigits=5), "%")
        # Reset the boardironment
        board = Board()
        state = getHash(board)
        step = 0
        
        while True:
            # 3. Choose an action a in the current world state (s)
            ## First we randomize a number
            exp_exp_tradeoff = random.uniform(0,1)
        
            ## If this number > greater than epsilon --> exploitation (taking the biggest Q value for this state)
            if exp_exp_tradeoff > epsilon:
                #board.getMoves(board.whiteMove)
                action, _ = getBestMove(qtable, board)
        
            # Else doing a random choice --> exploration
            else:
                action = getRandomMove(board)
            
            # Take the action (a) and observe the outcome state(s') and reward (r)
            newBoard = board.move(action[0], action[1])
            if len(newBoard.findPiece("k")) == 1 and len(newBoard.findPiece("K")) == 1:
                pass
            else:
                # player has won, no king
                break
            
            newState = getHash(newBoard)
            reward = rewardValues[board.getCell(action[1]).lower()] #get the piece previously moveTo cell - square with piece captured
            #OR calculate reward using rate function (should use full board rate or move rate)
            
            _, currValue = getBestMove(qtable, newBoard) #the current value is the best next value
            
            
            # Update Q(s,a):= Q(s,a) + lr [R(s,a) + gamma * max Q(s',a') - Q(s,a)]
            if not newState in qtable:
                qtable[newState] = 0
            if not state in qtable:
                qtable[state] = 0
                
            learnedValue = reward + gamma * currValue - qtable[state] * learning_rate
            qtable[newState] -= qtable[newState] * learning_rate
            qtable[newState] += learnedValue * learning_rate
            #print(qtable[newState])
        
            # Our new state is state
            state = newState #state is the hash of board
            board = newBoard
            
            # Reduce epsilon (because we need less and less exploration)
            #TODO: what does np.exp don there is 1 arg
            epsilon = min_epsilon + (max_epsilon - min_epsilon)*np.exp(-decay_rate*episode)
            
    return qtable
            
def testPlay(qtable):
    board = Board()
    while True:
        print(board)
        action, _ = getBestMove(qtable, board)
        board = board.move(action[0], action[1])

def doTraining():
    while True:
        start = time.time()
        save(FILENAME, training(200, qtable=load(FILENAME)))
        print("Time taken:", time.time()-start)

def rateDisplay(board, whiteMove):
    return rate(qtable, board)

def Minimax(board, whiteMove, depth):
    action, _ = getBestMove(qtable, board)
    newBoard = board.move(action[0], action[1])
    return newBoard

def debug():
    display = pygameDisplay()
    display.debug(rateDisplay)
    
def play():
    display = pygameDisplay()
    display.main(Minimax, rateDisplay)

def seeTable():
    for board in qtable:
        board = [i.replace(".", " ") for i in list(board)]
        board = [board[i*8:i*8+8] for i in range(8)]
        board = Board(board)
        
        display = pygameDisplay()
        try:
            display.debug(rateDisplay, board=board)
        except:
            continue

if __name__ == "__main__":
    doTraining()
    #debug()
    #play()
    #seeTable()
    #testPlay()
    
    
    
    
    
        
