from possibleMoves.possibleMoves import *
import time
from utility import unhashableDict
import pickle
import multiprocessing

weightings = {'p':1, 'n':3.2, 'b':3.3, 'r':5, 'q':9, 'k':200,
              'P':-1, 'N':-3.2, 'B':-3.3, 'R':-5, 'Q':-9, 'K':-200,
              ' ':0}

def flattened(board):
    output = []
    for row in board:
        for cell in row:
            if board.whiteMove:
                output.append(weightings[cell])
            else:
                output.append(-weightings[cell])
    return output

def getData(repeats, prevData=None):
    if prevData:
        data = prevData
    else:
        data = unhashableDict()
        
    for i in range(repeats):
        board = Board()
        whiteHistory = [] #these are awesome variable names!
        blackHistory = []
        
        while True:
            #print(board)
            if not board.findPiece("k"):
                #black has won
                whiteScore = -1
                blackScore = 1
                break
            
            elif not board.findPiece("K"):
                blackScore = -1
                whiteScore = 1
                break
            
            #print(board, board.state)
            #print(board.getMoves(board.whiteMove))
            board = board.doRandomMove()
            
            if board.whiteMove:
                whiteHistory.append(flattened(board)) #should deepcopy?
            else:
                blackHistory.append(flattened(board)) #should deepcopy?
                
        score = 1 / (len(whiteHistory) + len(blackHistory))
        
        for tempBoard in whiteHistory:
            if tempBoard in data.keys:
                curr, iterations = data[tempBoard]
                data[tempBoard] = (curr + score*whiteScore, iterations+1)
            else:
                data[tempBoard] = (score * whiteScore, 1)
        
        for tempBoard in blackHistory:
            if tempBoard in data.keys:
                curr, iterations = data[tempBoard]
                data[tempBoard] = (curr + score*blackScore, iterations+1)
            else:
                data[tempBoard] = (score * blackScore, 1)
                
    return data

def save(data):
    with open("data.txt", "wb") as f:
        return pickle.dump(data, f)
    
def load():
    with open("data.txt", "rb") as f:
        return pickle.load(f)

def runOptimise(func, *args):
    return multiprocessing.Pool(processes=3).apply_async(func, args).get(timeout=120)

if __name__ == "__main__":
    data = None #load()
    #data = getData(100, prevData=data)
    data = runOptimise(getData, 50)
    save(data)
