from possibleMoves import printBoard, initBoard, findPiece, movePiece, possibleMoves, evaluateScore, getMove
import time


def rateboard(board, turn): #make this better
    #takes 0.014 +- 0.001 s
    #print("s")
    rating = 0
    state = evaluateScore(board, turn)
    if state == "won":
        rating += 1000000
    allMoves, allMovesValues = possibleMoves(board, whiteMove=turn), []
    [allMovesValues.extend(i) for i in allMoves.values()]
    #oppMoves, oppMovesValues = possibleMoves(board, whiteMove=not turn), []
    #[oppMovesValues.extend(i) for i in allMoves]
    
    weightings = {"p":1, "n":3, "b":3, "r":5, "q":8, "k":10000}
    #print(time.time())
    if turn:
        func = lambda x: x.lower()
    elif not turn:
        func = lambda x: x.upper()
        
    #points for every piece pieces
    for piece in weightings:
        rating += len(findPiece(board, func(piece))) * weightings[piece] * 4
    
    #more moves are better
    rating += len(allMovesValues)*0.5
    #are all pieces protected
    """for r, row in enumerate(board):
        for c, cell in enumerate(row):
            if func(cell) == cell and cell != " ": #this is your piece
                piecesProtecting = allMovesValues.count((r, c))
                piecesAttacking = oppMovesValues.count((r, c))
                if piecesProtecting >= piecesAttacking:
                    rating += weightings[cell.lower()]"""
    #is the opponents king trapped
    
    #your pieces in centre is good
    for x, y in [(3, 3), (3, 4), (4, 3), (4, 4)]:
        cell = board[x][y]
        if func(cell) == cell and cell != " ":
            rating += 5
    #castling?
    return rating

def Minimax(board, turn, depth):
    newBoard, score = Max(board, turn, depth, 10000, -10000)
    return newBoard

def Max(board, turn, depth, high, low): #maximise through increasing minimum
    if depth == 0 or evaluateScore(board, turn) in ["won", "tie"]:
        return board, rateboard(board, turn)-rateboard(board, not turn)
    
    moves = possibleMoves(board, whiteMove=turn)
    bestScore = low
    bestBoard = None
    possibleBoards = []
    for startPos in moves:
        for endPos in moves[startPos]:
            newboard = movePiece(board, startPos, endPos)
            tempBoard, score =Min(newboard, not turn, depth-1, high, bestScore)
            if not bestBoard:
                possibleBoards.append((newboard, score))
            if score > bestScore:
                bestScore = score
                bestBoard = newboard
            if score > high: #this is pruning, dont have to search after finding this
                return bestBoard, high
    
    try:
        return bestBoard, bestScore #this doesnt exist, no score is higher than "low"
    except:
        bestBoard, lowerScore = sorted(possibleBoards, key=lambda x: x[1])[0]
        return bestBoard, bestScore

def Min(board, turn, depth, high, low):
    if depth == 0 or evaluateScore(board, turn) in ["won", "tie"]:
        return board, rateboard(board, turn)-rateboard(board, not turn)
    
    moves = possibleMoves(board, whiteMove=turn)
    bestScore = high
    bestBoard = None
    possibleBoards = []
    for startPos in moves:
        for endPos in moves[startPos]:
            newboard = movePiece(board, startPos, endPos)
            tempBoard, score = Max(newboard, not turn, depth-1, bestScore, low)
            if not bestBoard:
                possibleBoards.append((newboard, score))
            if score < bestScore:
                bestScore = score
                bestBoard = newboard
            if score < low: #this is pruning, dont have to search after finding this
                return bestBoard, low
    
    try:
        return bestBoard, bestScore #this doesnt exist, no score is lower than "high"
    except:
        bestBoard, lowerScore = sorted(possibleBoards, key=lambda x: x[1])[0]
        return bestBoard, bestScore

def oneplayer(computerTurn):
    board = initBoard()
    """board =[["K", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", "r", " ", " ", "P", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            ["k", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "]]"""
    printBoard(board)
    whiteMove = True #white starts
    while True:
        if computerTurn==whiteMove:
            print("computer turn - thinking...")
            #loop = asyncio.new_event_loop()
            #board = loop.run_until_complete(Minimax(board, whiteMove, 3))[0]
            start = time.time()
            
            board = Minimax(board, whiteMove, 2)
            
            print(time.time()-start)
            printBoard(board)
            
            
            if evaluateScore(board, whiteMove) in ["won", "lost", "stalemate"]:
                return
            whiteMove = not whiteMove
            
        else:
            print("your turn")
            while True:
                userInput = input("Enter move as chess notation: ")
                if not userInput:
                    return
                try:
                    move = getMove(whiteMove, board, userInput)
                except Exception as e: #invalid move, raised error
                    print(e)
                    continue
                board = movePiece(board, move[0], move[1])
                printBoard(board)
                break
            
            if evaluateScore(board, whiteMove) in ["won", "lost", "stalemate"]:
                return
            whiteMove = not whiteMove

def test():
    board = [["R", "N", "B", "Q", "K", "B", " ", "R"],
             ["P", "P", "P", " ", "P", "P", "P", "P"],
             [" ", " ", " ", "P", " ", " ", " ", "N"],
             [" ", " ", " ", " ", " ", " ", " ", " "],
             [" ", " ", " ", "p", " ", " ", " ", " "],
             [" ", " ", " ", " ", " ", " ", " ", " "],
             ["p", "p", "p", " ", "p", "p", "p", "p"],
             ["r", "n", " ", "q", "k", "b", "n", "r"]]
    print(Minimax(board, False, 2))
    
oneplayer(False)
