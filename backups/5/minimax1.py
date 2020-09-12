from possibleMoves import initBoard, findPiece, movePiece, possibleMoves, evaluateScore, idenPiece, getMove, distance, getKingPos, getRook, protecting, attacking, threatening, inCheck, Board
#from possibleMoves import pawn, knight, bishop, rook, queen, king
import time
from copy import deepcopy

def rateboard(board, turn): #more discenment
    #takes 0.013s to 0.015s
    #instead of playing your turn (turn being “turn”), return rating
    rating = 0
    state = evaluateScore(board, turn)
    if state == "won":
        rating += 10000

    whiteMoves = possibleMoves(board, whiteMove=True) #doing this here saves computational time
    whiteMoveValues = []
    [whiteMoveValues.extend(i) for i in whiteMoves.values()]
    blackMoves = possibleMoves(board, whiteMove=False)
    blackMoveValues = []
    [blackMoveValues.extend(i) for i in blackMoves.values()]
    
    """
Source			Year	Pawn	Knight	Bishop	Rook	Queen
H. S. M. Coxeter	1940		300	350	550	1000
Max Euwe and Hans Kramer1944	100	350	350	550	1000
Claude Shannon		1949	100	300	300	500	900
Alan Turing		1953	100	300	350	500	1000
Mac Hack		1967	100	325	350	500	975
Chess 4.5		1977	100	325	350	500	900
Tomasz Michniewski	1995	100	320	330	500	900
Hans Berliner		1999	100	320	333	510	880
Larry Kaufman		1999	100	325	325	500	975
Fruit and others    	2005	100	400	400	600	1200
Larry Kaufman		2012	100	350	350	525	1000"""
    weightings = {"p":1, "n":3.2, "b":3.3, "r":5, "q":9, "k":200}
    
    #mobilityBias = {"p":1, "n":1, "b":0.25, "r":0.75, "q": 0.1, "k":1} #edit biases
    whitePieces = sum([sum([weightings[i.lower()] for i in row if i.replace(" ", "").islower()]) for row in board])
    blackPieces = sum([sum([weightings[i.lower()] for i in row if i.replace(" ", "").isupper()]) for row in board])
    #print(time.time())
    
    if turn:
        func = lambda x: x.lower()
    elif not turn:
        func = lambda x: x.upper()
    
    center4 = [(3, 3), (3, 4), (4, 3), (4, 4)]
    
    for r, row in enumerate(board):
        for c, cell in enumerate(row):
            cellrating = []
            isWhite = False if cell.isupper() else True
            if cell == " ":
                pass
            else:
                defences = protecting(board, r, c)
                attacks = attacking(board, r, c)
                threats = threatening(board, r, c)
                freePieces = {i:attacks[i] for i in attacks if len(protecting(board, i[0], i[1])) == 0} #attacking and not being defended
                attacks = {i:attacks[i] for i in attacks if i not in freePieces} #attacking and not free
                
                if len(threats) > len(defences):
                    #print(r, c)
                    cellrating.append(-weightings[cell.lower()] * 2)
                    
                cellrating.append(len(attacks) * 1) #this makes queen advance early on
                #cellrating.append(len(defences) * 1) #this makes queen advance early on
                
                if threats and min([weightings[i.lower()] for i in threats.values()]) < weightings[cell.lower()]:
                    #piece attackers are worth less than you (will be bad trade)
                    #print(r, c, cell, attacking)
                    cellrating.append(-weightings[cell.lower()]*2)

                    
                #0.1 for doubled, blocked and isolated pawns instead of 1
                #0.1 for pawn past half way line in early game
                cellrating.append(weightings[cell.lower()]*1) #piece is not captured
                    
                if ((r != 7 and cell.islower()) or (r != 0 and cell.isupper())) and cell.lower() in ["b", "n"]: #back row pieces moving forwards
                    #print(cell, r)
                    cellrating.append(2)
                    
                if (cell == "k" and r==7 and c==4) or (cell == "K" and r==0 and c==4): #king hasnt moved
                    cellrating.append(15)
                    
                if freePieces and isWhite == turn: #its your turn, can take free piece
                    for cell in freePieces.values():
                        cellrating.append(weightings[cell.lower()]*0.5)
                        
                elif freePieces and isWhite != turn: #not your turn
                    #forcing trade (is this good? depends on no. pieces)
                    yourPieces = whitePieces if turn else blackPieces
                    oppPieces = blackPieces if turn else whitePieces
                    
                    if yourPieces >= blackPieces: #therefore trading is good
                        cellrating.append(weightings[cell.lower()]*2)
                    else: #your down on pieces
                        pass
                    
                
                        
                allMoves = whiteMoves if isWhite else blackMoves
                if (r, c) in allMoves: #this piece can move
                    cellrating.append(len(allMoves[(r, c)])*0.1) #mobility
                    #in opening: mobility of bishops, knights is more important than that of the rooks
                    #forward mobility is scored higher than backward mobility
                    #rooks: vertical mobility gets priority over horizontal mobility
                    #implement https://www.chessprogramming.org/Simplified_Evaluation_Function
                    
                    if allMoves[(r, c)] in center4: #piece can move to center
                        cellrating.append(2)
                        
                if (r, c) in center4: #piece in centre
                    cellrating.append(5)
                    
            #print(r, c, cell, cellrating)
            if func(cell) == cell: #your piece
                rating += sum(cellrating)
            else:
                rating -= sum(cellrating)
    #castled
    """rookCols = [i[1] for i in findPiece(board, func("r"))]
    try:
        kingCol = findPiece(board, func("k"))[0][1]
    except: #king doesnt exist
        rating -= 100
    else:
        if inCheck(board, not turn):
            rating += 100
        if kingCol < min(rookCols) or kingCol > max(rookCols): 
            rating  += 4 #castled"""
        
    #development - early game
    """backCol = 7 if turn else 0
    for row in [1, 2, 5, 6]:
        if board[backCol][row] == " ":
            rating += 3"""
            
    #king safety
    kingPos = getKingPos(board, turn)
    #print(len(whiteMoves[kingPos]))
    #print(len(blackMoves[kingPos]))
    if turn == True and kingPos in whiteMoves:
        rating += len(whiteMoves[kingPos])*2
    elif turn == False and kingPos in whiteMoves:
        rating += len(blackMoves[kingPos])*2
        
    return rating

def rateBoth(board, turn):
    yourKing, oppKing = findPiece(board, "k"), findPiece(board, "K")
    if yourKing and oppKing:
        return round(rateboard(board, turn), ndigits=3)
    else: # a king doesnt exist
        assert not(yourKing and oppKing)
        if not yourKing:
            return -100000000
        elif not oppKing:
            return 100000000

def Minimax(board, turn, depth):
    #do transposition tables (store scores of past positions)
    #do Iterative Deeper Depth-First Search (IDDFS) - shallow search on "best move" to get alpha beta values
    #prefered depth = 2
    #for depth 2: when depth==2 max, when depth==1 min, when depth==0 rate
    
    newBoard, score = Max(board, turn, depth, 10000, -10000)
    #then https://www.chessprogramming.org/Quiescence_Search for more advanced system
    return newBoard

def Max(board, turn, depth, high, low): #maximise through increasing minimum
    weightings = {"p":1, "n":3, "b":3, "r":5, "q":9, "k":200, " ":0}
    if depth == 0 or evaluateScore(board, turn) in ["won", "tie"]:
        #print(board, rateBoth(board, turn))
        return board, rateBoth(board, turn)
    
    moves = possibleMoves(board, whiteMove=turn)
    bestScore = low
    bestBoard = None
    allBoards = []
    for startPos in moves:
        for endPos in moves[startPos]:
            newboard = movePiece(board, startPos, endPos)
            
            if getKingPos(newboard, turn) == endPos and distance(startPos, endPos) == 2: #this is castle
                rookPrev, rookNew = getRook(endPos)
                newboard = movePiece(newboard, rookPrev, rookNew)
            
            threats = threatening(newboard, endPos[0], endPos[1])
            defences = protecting(newboard, endPos[0], endPos[1])
            if board[endPos[0]][endPos[1]] != " ":
                piecesProtectingEnd = bool(len(protecting(board, endPos[0], endPos[1])))
            else:
                piecesProtectingEnd = False
                
            #if free piece or safe move or fair trade
            if  piecesProtectingEnd or len(threats) <= len(defences) or weightings[board[endPos[0]][endPos[1]].lower()] >= weightings[newboard[endPos[0]][endPos[1]].lower()]: #its a reasonable move
                #what about greek gift sacrifices? https://en.wikipedia.org/wiki/Greek_gift_sacrifice
                allBoards.append((rateBoth(newboard, not turn), newboard))
            
    possibleBoards = []
    if len(allBoards) > 5:
        cutoff = len(allBoards)//2
    else:
        cutoff = -1
    for sortingScore, boardMoved in sorted(allBoards, key=lambda x:x[0]): #[:cutoff]: #sort by rating (do best first)
        tempBoard, score = Min(boardMoved, not turn, depth-1, high, bestScore)
        Print(boardMoved)
        Print(tempBoard)
        print(sortingScore, score) #first score pertains to first board
        if not bestBoard: #this helps find the best move when no score is better than low
            possibleBoards.append((score, boardMoved))
        if score > bestScore:
            bestScore = score
            bestBoard = boardMoved
        if score > high: #this is pruning, dont have to search after finding this
            return bestBoard, high
    
    if bestBoard:
        return bestBoard, bestScore #this doesnt exist, no score is higher than "low"
    else:
        bestBoard, lowerScore = max(possibleBoards, key=lambda x: x[0]) #get the best board based on the score
        return bestBoard, bestScore

def Min(board, turn, depth, high, low): #minimise through decreasing maximum (search space decresaes)
    weightings = {"p":1, "n":3, "b":3, "r":5, "q":9, "k":200, " ":0}
    if depth == 0 or evaluateScore(board, turn) in ["won", "tie"]:
        return board, rateBoth(board, turn)
    
    moves = possibleMoves(board, whiteMove=turn)
    bestScore = high
    bestBoard = None
    allBoards = []
    for startPos in moves:
        for endPos in moves[startPos]:
            newboard = movePiece(board, startPos, endPos)
            
            if getKingPos(newboard, turn) == endPos and distance(startPos, endPos) == 2: #this is castle
                rookPrev, rookNew = getRook(endPos)
                newboard = movePiece(newboard, rookPrev, rookNew)
                
            allBoards.append((rateBoth(newboard, not turn), newboard))
            
            threats = threatening(newboard, endPos[0], endPos[1])
            defences = protecting(newboard, endPos[0], endPos[1])
            if board[endPos[0]][endPos[1]] != " ":
                piecesProtectingEnd = bool(len(protecting(board, endPos[0], endPos[1])))
            else:
                piecesProtectingEnd = False
                
            #if free piece or safe move or fair trade
            if piecesProtectingEnd or len(threats) <= len(defences) or weightings[board[endPos[0]][endPos[1]].lower()] >= weightings[newboard[endPos[0]][endPos[1]].lower()]: #its a reasonable move
                allBoards.append((rateBoth(newboard, not turn), newboard))
                
    possibleBoards = []
    if len(allBoards) > 5:
        cutoff = len(allBoards)//2
    else:
        cutoff = 1000
    for sortingScore, boardMoved in sorted(allBoards, key=lambda x:x[0])[:cutoff]: #sort by rating (do best first)
        tempBoard, score = Max(boardMoved, not turn, depth-1, bestScore, low)
        #Print(board)
        #Print(boardMoved)
        #print(score)
        
        if not bestBoard:
            possibleBoards.append((boardMoved, -score))
        if score < bestScore:
            bestScore = score
            bestBoard = boardMoved
        if score < low: #this is pruning, dont have to search after finding this
            return bestBoard, low
    
    if bestBoard:
        return bestBoard, bestScore #this doesnt exist, no score is lower than "high"
    else:
        bestBoard, lowerScore = min(possibleBoards, key=lambda x: x[0])
        return bestBoard, bestScore

def test():
    board = [['R', 'b', 'B', 'Q', 'K', 'B', ' ', 'R'],
             ['P', 'P', ' ', 'P', 'P', 'P', 'P', 'P'],
             [' ', ' ', 'P', ' ', ' ', ' ', ' ', ' '],
             [' ', ' ', ' ', 'N', ' ', ' ', ' ', ' '],
             [' ', ' ', ' ', 'p', ' ', ' ', ' ', ' '],
             [' ', ' ', ' ', ' ', 'p', ' ', ' ', ' '],
             ['p', 'p', 'p', ' ', ' ', 'p', 'p', 'p'],
             ['r', 'n', ' ', 'q', 'k', 'b', 'n', 'r']]
    #print(rateBoth(board, True))
    start = time.time()
    #board = Minimax(board, False, 2)# this should eat knight on 5 5
    #Print(board)
    board = Board(board)
    #print(possibleMoves(board, whiteMove=False))
    #print(score)
    #rateBoth(board, True)
    print(time.time()-start)
    wat
    

test()
