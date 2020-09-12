import time
from network import Network, Node

from functions.functions import Pos, Board, idenPiece, runOptimise
from rate_m import isGoodMove, isHigher
from rate_m import rateMove as rateMove_m
from rate_q import rateMove as rateMove_q

rateMove = rateMove_m
#rateMove = rateMove_q

class Score:
    def __init__(self, score, boards):
        self.history = boards
        if isinstance(score, (float, int)):
            score = [score]
        self.score = score
    def __gt__(self, other):
        return self.score[-1] > other.score[-1]
    def __lt__(self, other):
        return self.score[-1] < other.score[-1]
    def __ge__(self, other):
        return self.score[-1] >= other.score[-1]
    def __le__(self, other):
        return self.score[-1] <= other.score[-1]
    def __eq__(self, other):
        return self.score[-1] == other.score[-1]
    def __ne__(self, other):
        return self.score[-1] != other.score[-1]
    def __str__(self):
        return str(self.score) + " " + str(self.history)
    def __repr__(self):
        return self.__str__()
    def __neg__(self):
        return Score(self.score[:-1] + [-self.score[-1]], self.history)
    def addScore(self, score):
        self.score = [score] + self.score

def generateAllBoards(board, turn): #slowest times = ~2.35s
    #TODO: optimise this
    #print(time.time())
    priority1, priority2 = [], []
    moves = board.getMoves(turn)
    for startPos in moves:
        for endPos in moves[startPos]:
            newBoard = board.move(startPos, endPos)
            # if not at risk or just traded (e.g. I captured, you are going to capture back)
            # this prunes search tree
            
            #print(newBoard.getStats(endPos)["atRisk"], newBoard)
            if isGoodMove(newBoard, startPos, endPos): 
                priority1.append((board.deepcopy(),
                                  newBoard,
                                  rateMove(board, turn, startPos, endPos, newBoard),
                                  startPos,
                                  endPos))
            
            """else:
                priority2.append(board,
                                 newBoard,
                                 rateMove(board, board.whiteMove, startPos, endPos),
                                 startPos,
                                 endPos)"""
            
    if priority1:
        return priority1
    else:
        assert priority2 #if priority1 doesnt exist, priority2 has to exist
        return priority2
    #[(board, newBoard, rating, startPos, endPos), ...]
    
def Minimax(board, turn, depth, timeit=True):
    # do transposition tables (store scores of past positions)
    # do Iterative Deeper Depth-First Search (IDDFS) - shallow search on "best move" to get alpha beta values
    # LOST LINE
    # LOST LINE
    # depth = 3 (48s)
    #for depth 2: when depth==2 max, when depth==1 min, when depth==0 rate
    assert depth > 0

    if timeit:
        start = time.time()
    
    maxScore = -float("inf")
    startNode = Node("0")
    startNode.setInfo((board, None))
    boardNet = Network(startNode)
    print(repr(boardNet))
    
    allBoards = generateAllBoards(board, turn)
    """if len(allBoards) > 5: #5 is a random number
        cutoff = len(allBoards)//2
    else:
        cutoff = -1"""
    #print(allBoards)
    cutoff = 3 #depth+1 #an interesting idea
    assert cutoff > 0

    for oriboard, newBoard, rating, moveFrom, moveTo in sorted(allBoards, key=lambda x:x[2], reverse=True)[:cutoff]:
        #print(newBoard)
        if depth == 1:
            return newBoard
        
        score = -Max(newBoard, not turn, depth-1, Score(10000, []), Score(-10000, []), moveFrom, moveTo, [oriboard])
        score.addScore(rating)
        # in score.score, left most is shallow depth, right most is deepest depth
        #print(score.score)
        if sum(score.score) > sum(maxScore.score):
            maxScore = score
            bestBoard = newBoard

    maxScore.addScore("?") #this is for the starting position, cannot rate because unknown move
    if timeit:
        print(time.time()-start)

    # then https://www.chessprogramming.org/Quiescence_Search for more advanced system
    # is this the after search? ^
    bestBoard.setWhiteMove(not turn)
    return bestBoard



def Max(board, turn, depth, high, low, moveFrom, moveTo, history): #maximise through increasing minimum
    assert high >= low
    
    #board.setWhiteMove(turn)
    #moveFrom, moveTo and prevBoard are not used when depth > 0
    if depth == 0 or board.state in ["won", "tie", "stalemate"]:
        #print(board, rateBoth(board, turn))
        return Score(rateMove(history[-1], not turn, moveFrom, moveTo, board), history+[board])

    bestScore = low
    allBoards = generateAllBoards(board, turn)

    """if len(allBoards) > 5: #5 is a random number

    else:
        cutoff = -1"""
    cutoff = depth #an interesting idea
    #print([i[0] for i in allBoards]) #sorting score
    
    for oriBoard, boardMoved, sortingScore, startPos, endPos in sorted(allBoards, key=lambda x:x[2], reverse=True)[:cutoff]:
        if depth == 1:
            return -Score(sortingScore, history+[oriBoard, boardMoved]) #go for highest sortingScore (very fast)
        
        #implementation of Negamax alogorithm, where Min(low, high) = -Max(-high, -low)
        score = -Max(boardMoved, not turn, depth-1, -bestScore, -high, startPos, endPos, history+[oriBoard]) #swaped alpha and beta
        score.addScore(sortingScore)
        
        bestScore = max(bestScore, score, key=lambda x:x.score)
        if sum(bestScore.score) > sum(high.score): #this is pruning, dont have to search after finding this
            return bestScore
    
    return bestScore


def test():
    global board
    board = ['R', 'N', 'B', ' ', 'K', 'B', 'N', 'R',
             'P', 'P', 'P', ' ', 'P', 'P', 'P', 'P',
             ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
             ' ', ' ', ' ', 'Q', ' ', ' ', ' ', ' ',
             ' ', ' ', ' ', ' ', 'p', ' ', ' ', ' ',
             ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
             'p', 'p', 'p', 'p', ' ', 'p', 'p', 'p',
             'r', ' ', 'b', 'q', 'k', 'b', 'n', 'r']
    board = Board(True)
    
    #print(board.getMoves(board.whiteMove))
    #return
    #print(possibleMoves(board.board, True)[Pos(7, 2)])
    #print(board.getMoves(True)[Pos(7, 3)])
    #return
    #board = board.move(Pos(6, 3), Pos(4, 3))
    """board = board.move(Pos(6, 3), Pos(4, 3))
    board = board.move(Pos(0, 1), Pos(2, 2))
    print(rateMove(board, board.whiteMove, Pos(7, 2), Pos(5, 4), None))
    print(board)
    board = board.move(Pos(7, 2), Pos(5, 4))
    print(board)
    return
    board = board.move(Pos(1, 3), Pos(3, 3))
    board = board.move(Pos(7, 1), Pos(5, 2))
    board = board.move(Pos(0, 6), Pos(2, 5))
    board = board.move(Pos(5, 2), Pos(3, 1))"""
    
    while True:
        #print(board)
        board = Minimax(board, board.whiteMove, 2, timeit=False)
        #board = runOptimise(Minimax, board, board.whiteMove, 2)
        print(board)
        #return
    #print(new)
    
    
    #board = board.move(Pos(0, 2), Pos(3, 5))
    #timeit(runOptimise, rateMove, board, board.whiteMove, Pos(0, 2), Pos(3, 5), None)
    #timeit(rateMove, board, board.whiteMove, Pos(0, 2), Pos(3, 5), None)
    #timeit(board.move, Pos(0, 2), Pos(3, 5))
    #timeit(generateAllBoards, board, board.whiteMove)
    #start = time.time()
    #timeit(generateAllBoards, board, True)
    #print(time.time()-start)
    #print(board)
    
    # now exit program gracefully
    raise Exception
    #exit()


if __name__ == '__main__':
    #TODO: fill in gaps
    #TODO: create objects for individual pieces?
    test()
