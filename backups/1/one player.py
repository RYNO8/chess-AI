from possibleMoves import printBoard, initBoard, findPiece, movePiece, possibleMoves, evaluateScore, getMove

def rateboard(board, turn): #make this better
    rating = 0
    state = evaluateScore(board, turn)
    if state == "won":
        rating += 10000
        
    if turn:
        func = lambda x: x.upper()
    elif not turn:
        func = lambda x: x.lower()
    
    rating += len(findPiece(board, func("p")))*1
    rating += len(findPiece(board, func("n")))*3 #is knight or bishop worth more
    rating += len(findPiece(board, func("b")))*3
    rating += len(findPiece(board, func("r")))*5
    rating += len(findPiece(board, func("q")))*8
    
    rating += len(possibleMoves(board, whiteMove=turn).values())*0.5
    #are all pieces protected
    #is the opponents king trapped
    return rating

def Minimax(board, turn, depth):
    board, score = Max(board, turn, depth, 100000, -100000)
    print(score)
    return board

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
            tempBoard, score = Min(newboard, not turn, depth-1, high, bestScore)
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
    for startPos in moves:
        for endPos in moves[startPos]:
            newboard = movePiece(board, startPos, endPos)
            tempBoard, score = Max(newboard, not turn, depth-1, bestScore, low)
            if score < bestScore:
                bestScore = score
                bestBoard = newboard
            if score < low: #this is pruning, dont have to search after finding this
                return bestBoard, low
    
    assert bestBoard #is this doesnt exist, no score is lower than "high"
    
    return bestBoard, bestScore

def oneplayer(computerTurn):
    board = initBoard()
    printBoard(board)
    whiteMove = True #white starts
    while True:
        if computerTurn==whiteMove:
            print("computer turn - thinking...")
            board = Minimax(board, whiteMove, 3)
            printBoard(board)
            
            if evaluateScore(board, whiteMove) in ["won", "lost", "stalemate"]:
                return
            whiteMove = not whiteMove
            
        else:
            print("your turn")
            while True:
                userInput = input("Enter move as chess notation: ")
                try:
                    move = getMove(whiteMove, board, userInput)
                except: #invalid move, raised error
                    continue
                board = movePiece(board, move[0], move[1])
                printBoard(board)
            
            if evaluateScore(board, whiteMove) in ["won", "lost", "stalemate"]:
                            return
            whiteMove = not whiteMove
        computerTurn = True

if __name__ == "__main__":
    
    oneplayer(True)
    board =[["K", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", "r", " ", " ", "P", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            ["k", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "]]
    #print(gameScore(board, False))
    #board = initBoard()
    #printBoard(board)
    #print(evaluateScore(board, True))
