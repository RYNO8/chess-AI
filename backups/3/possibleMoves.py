def deepcopy(a):
    assert isinstance(a, list)
    return [i[:] for i in a[:]]

def initBoard():
    return [["R", "N", "B", "Q", "K", "B", "N", "R"],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            ["r", "n", "b", "q", "k", "b", "n", "r"]]
    
    return [["r", "n", "b", "q", "k", "n", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"]]

def printBoard(board, joiner="|"):
    pieceToAscii = {"k":"\u2654", "q":"\u2655", "r":"\u2656", "b":"\u2657", "n":"\u2658", "p":"\u2659",
                    "K":"\u265A", "Q":"\u265B", "R":"\u265C", "B":"\u265D", "N":"\u265E", "P":"\u265F",
                    " ":" "} #"\u2644"}
    for i, row in enumerate(board):
        print(8-i, end=" ")
        print(joiner.join([pieceToAscii[i] for i in row]))
    #print("  A\u2001 B\u2001 C\u2001 D\u2001 E\u2001 F\u2001 G\u2001 H\n")
    print("  A B C D E F G H")

def getKingPos(board, whiteMove):
    if whiteMove:
        try:
            return findPiece(board, "k")[0]
        except:
            return None
        
    elif not whiteMove:
        try:
            return findPiece(board, "K")[0]
        except:
            return None

def findPiece(board, piece):
    pieceList = []
    for r, row in enumerate(board):
        for c, cell in enumerate(row):
            if cell == piece:
                pieceList.append((r, c))
    return pieceList

def movePiece(oriBoard, pos, newPos):
    board = deepcopy(oriBoard) #makes copy to avoid error
    if isinstance(pos, bool): # a castle
        whiteMove = pos
        rowNum = 7 if whiteMove else 1
        if newPos == "O-O":
            board = movePiece(board, (rowNum, 4), (rowNum, 6)) #king moves
            board = movePiece(board, (rowNum, 7), (rowNum, 5)) #rook moves
        elif newPos == "O-O-O":
            board = movePiece(board, (rowNum, 4), (rowNum, 2)) #king moves
            board = movePiece(board, (rowNum, 0), (rowNum, 3)) #king moves
        return board
    else:
        board[newPos[0]][newPos[1]] = board[pos[0]][pos[1]]
        board[pos[0]][pos[1]] = " "
        if getCell(board, newPos[0], newPos[1]) == "p" and newPos[0] == 0: #if white pawn reached end
            board[newPos[0]][newPos[1]] = "q"
        elif getCell(board, newPos[0], newPos[1]) == "P" and newPos[0] == 7: #if black pawn reached end
            board[newPos[0]][newPos[1]] = "Q"
        return board

def flipBoard(board):
    newBoard = []
    for row in reversed(board):
        newBoard.append(row[::-1])
    return newBoard

def getCell(board, x, y):
    if x in range(0, 8) and y in range(0, 8):
        #print(x, y)
        return board[x][y]

def idenPiece(piece, whiteMove):
    return (piece.islower() and whiteMove) or (piece.isupper() and not whiteMove)

#################################################################################
#################################################################################
#################################################################################

def rook(board, r, c, whiteMove):
    moves = set()
    for dirX, dirY in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        newR, newC = r+dirX, c+dirY
        while True:
            testCell = getCell(board, newR, newC)
            if testCell == None: #N/A
                break
            elif idenPiece(testCell, not whiteMove): #opponent piece
                moves.add((newR, newC))
                break
            elif idenPiece(testCell, whiteMove): #your piece
                break
            elif testCell == " ": #blank
                moves.add((newR, newC))
            newR, newC = newR+dirX, newC+dirY
            
    if len(moves) != 0:
        return moves

def knight(board, r, c, whiteMove):
    moves = set()
    for dirX, dirY in [(-1, -2), (1, -2), (-1, 2), (1, 2), (2, -1), (2, 1), (-2, -1), (-2, 1)]:
        newR, newC = r+dirX, c+dirY
        testCell = getCell(board, newR, newC)
        if testCell == None: #N/A
            pass
        elif testCell == " " or idenPiece(testCell, not whiteMove): #opponent piece or blank
            moves.add((newR, newC))
            
    if len(moves) != 0:
        return moves

def bishop(board, r, c, whiteMove):
    moves = set()
    for dirX, dirY in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
        newR, newC = r+dirX, c+dirY
        while True:
            testCell = getCell(board, newR, newC)
            if testCell == None: #N/A
                break
            elif idenPiece(testCell, not whiteMove): #opponent piece
                moves.add((newR, newC))
                break
            elif idenPiece(testCell, whiteMove): #your piece
                break
            elif testCell == " ": #blank
                moves.add((newR, newC))
            newR, newC = newR+dirX, newC+dirY
            
    if len(moves) != 0:
        return moves

def queen(board, r, c, whiteMove):
    moves = set()
    for dirX, dirY in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
        newR, newC = r+dirX, c+dirY
        while True:
            testCell = getCell(board, newR, newC)
            if testCell == None: #N/A
                break
            elif testCell == " ":
                moves.add((newR, newC))
            elif idenPiece(testCell, not whiteMove): #opponent piece
                #print("opponent")
                moves.add((newR, newC))
                break
            elif idenPiece(testCell, whiteMove): #your piece
                break
            newR, newC = newR+dirX, newC+dirY
            
    if len(moves) != 0:
        return moves

def king(board, r, c, whiteMove):
    moves = set()
    for dirX, dirY in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
        newR, newC = r+dirX, c+dirY
        testCell = getCell(board, newR, newC)
        if testCell == None:
            pass
        elif testCell == " " or idenPiece(testCell, not whiteMove):
            moves.add((newR, newC))
    
    opponentMoves = possibleMoves(board, doKing=False, whiteMove=not whiteMove)
    movesTo = []
    for i in opponentMoves.values():
        movesTo += i
    #if black cannot move here, king will not move into check
    moves = set([i for i in moves if i not in movesTo])
        
    if len(moves) != 0:
        return moves

def pawn(board, r, c, whiteMove): #do promotion and umpa saunt
    moves = set()
    if whiteMove:
        if getCell(board, r-1, c) == " ": #step forwards
            moves.add((r-1, c))
            if r == 6 and getCell(board, r-2, c) == " ": #leaps if haven't moved
                moves.add((r-2, c))
        for dirX, dirY in [(-1, 1), (-1, -1)]: #takes piece
            testCell = getCell(board, r+dirX, c+dirY)
            if testCell not in [None, " "] and idenPiece(testCell, not whiteMove):
                moves.add((r+dirX, c+dirY))
                
    elif not whiteMove:
        if getCell(board, r+1, c) == " ": #step forwards
            moves.add((r+1, c))
            if r == 1 and getCell(board, r+2, c) == " ": #leaps if haven't moved
                moves.add((r+2, c))
        for dirX, dirY in [(1, 1), (1, -1)]: #takes piece
            testCell = getCell(board, r+dirX, c+dirY)
            if testCell not in [None, " "] and idenPiece(testCell, not whiteMove):
                moves.add((r+dirX, c+dirY))
                
    if len(moves) != 0:
        return moves

def canCastle(board, whiteMove): #assuming the king hasnt moved
    if whiteMove:
        rowNum = 7
    else:
        rowNum = 0
    kingPos = getKingPos(board, whiteMove)
    moves = []
    kingRow = [i.lower() for i in board[rowNum]]
    oppMoves = possibleMoves(board, whiteMove=not whiteMove, doKing=False)
    
    if kingRow[:5] == ["r", " ", " ", " ", "k"]:
        isChecked = False
        for pos in [(rowNum, 1), (rowNum, 2), (rowNum, 3), (rowNum, 4)]:
            if any([pos in i for i in oppMoves.values()]):
                #print(pos)
                isChecked = True
        if not isChecked:
            moves.append((rowNum, 2))
    
    if kingRow[4:] == ["k", " ", " ", "r"]:
        isChecked = False
        for pos in [(rowNum, 4), (rowNum, 5), (rowNum, 6)]:
            if any([pos in i for i in oppMoves.values()]):
                #print(pos)
                isChecked = True
        if not isChecked:
            moves.append((rowNum, 6))
    return kingPos, moves

def distance(point1, point2):
    return ((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)**0.5

def getRook(kingEnd):
    if kingEnd == (7, 6):
        return (7, 7), (7, 5)
    elif kingEnd == (7, 2):
        return (7, 0), (7, 3)
    elif kingEnd == (0, 6):
        return (0, 7), (0, 5)
    elif kingEnd == (0, 2):
        return (0, 0), (0, 3)
    else:
        raise Exception("invalid kingEnd pos")
    
#################################################################################
#################################################################################
#################################################################################
        
def possibleMoves(board, doKing=True, kingHasMoved=False, whiteMove=True):
    moves = {}
    terminalMoves = {}
    oppKing = getKingPos(board, not whiteMove)
    for r, row in enumerate(board):
        for c, cell in enumerate(row):
            if idenPiece(cell, whiteMove): #your piece
                if cell.lower() == "r":
                    moves[(r, c)] = rook(board, r, c, whiteMove)
                elif cell.lower() == "n":
                    moves[(r, c)] = knight(board, r, c, whiteMove)
                elif cell.lower() == "b":
                    moves[(r, c)] = bishop(board, r, c, whiteMove)
                elif cell.lower() == "q":
                    moves[(r, c)] = queen(board, r, c, whiteMove)
                elif cell.lower() == "k" and doKing:
                    moves[(r, c)] = king(board, r, c, whiteMove)
                elif cell.lower() == "p":
                    moves[(r, c)] = pawn(board, r, c, whiteMove)
                else:
                    break
                if moves[(r, c)] == None:
                    moves.pop((r, c))
                elif oppKing in moves[(r, c)]: #if can eat king, do that
                    terminalMoves[(r, c)] = set([oppKing])
                    
    if terminalMoves:
        return terminalMoves
    
    if not kingHasMoved and doKing: #castles
        kingPos, castleMoves = canCastle(board, whiteMove) #canCastle calls possibleMoves
        if kingPos in moves:
            [moves[kingPos].add(i) for i in castleMoves]
        else:
            moves[kingPos] = set(castleMoves)
        
    if doKing:
        #moves = go through all possible moves, keep those when king not in check
        newMoves = {}
        for start in moves:
            for finish in moves[start]:
                newBoard = movePiece(board, start, finish)
                if not inCheck(newBoard, whiteMove):
                    if start in newMoves:
                        newMoves[start].add(finish)
                    else:
                        newMoves[start] = set([finish])
            


        return newMoves
    return moves
    #dict   piece in tuple (x, y):  possible moves in set of tuples (x, y)
    #{      (6, 4):                 {(5, 4), (4, 4)}                        }

#################################################################################
#################################################################################
#################################################################################

def kingInValues(possibles, kingPos):
    for value in possibles.values():
        if kingPos in value:
            return True
    return False

def evaluateScore(board, whiteMove):
    if possibleMoves(board, whiteMove) == {}:
        return "stalemate"
    elif getKingPos(board, whiteMove) == None:
        return "lost"
    elif getKingPos(board, not whiteMove) == None:
        return "won"
    else:
        return "none"
    
def inversePawn(board, r, c, whiteMove):
    moves = set()
    directions = [(1, 1), (1, -1)] if not whiteMove else [(-1, 1), (-1, -1)]
    for dirX, dirY in directions: #takes piece
        testCell = getCell(board, r+dirX, c+dirY)
        if testCell not in [None, " "] and idenPiece(testCell, not whiteMove):
            moves.add((r+dirX, c+dirY))
                
    if len(moves) != 0:
        return moves

def attacking(board, r, c):
    #when the piece isnt there, how many other pieces can move there
    #aka, how many pieces are protecting it
    cell = board[r][c]
    if cell.isupper():
        whiteMove = False
    elif cell.islower():
        whiteMove = True
    else:
        raise Exception("cell should have piece")
    
    output = {}
    
    for pieceFunc, piece in [(inversePawn, "p"), (knight, "n"), (bishop, "b"), (rook, "r"), (queen, "q"), (king, "k")]:
        if piece == cell.lower():
            pieceMoves = pieceFunc(board, r, c, whiteMove)
            if pieceMoves:
                for endPos in pieceMoves:
                    testCell = board[endPos[0]][endPos[1]]
                    if idenPiece(testCell, not whiteMove) and testCell.lower() == piece: #opponents piece
                        output[(endPos[0], endPos[1])] = testCell
    return output

def protecting(board, r, c):
    #when the piece isnt there, how many other pieces can move there
    #aka, how many pieces are protecting it
    cell = board[r][c]
    
    if cell.isupper():
        whiteMove = False
    elif cell.islower():
        whiteMove = True
    else:
        raise Exception("cell should have piece")
    
    output = {}
    
    for pieceFunc, piece in [(inversePawn, "p"), (knight, "n"), (bishop, "b"), (rook, "r"), (queen, "q"), (king, "k")]:
        pieceMoves = pieceFunc(board, r, c, not whiteMove)
        if pieceMoves:
            for endPos in pieceMoves:
                testCell = board[endPos[0]][endPos[1]]
                #print(piece, testCell)
                if idenPiece(testCell, whiteMove) and testCell.lower() == piece: #your piece
                    output[(endPos[0], endPos[1])] = testCell
    return output

def threatening(board, r, c):
    #when the piece isnt there, how many other pieces can move there
    #aka, how many pieces are protecting it
    cell = board[r][c]
    if cell.isupper():
        whiteMove = False
    elif cell.islower():
        whiteMove = True
    else:
        raise Exception("cell should have piece")
    
    output = {}
    
    for pieceFunc, piece in [(inversePawn, "p"), (knight, "n"), (bishop, "b"), (rook, "r"), (queen, "q"), (king, "k")]:
        pieceMoves = pieceFunc(board, r, c, whiteMove)
        if pieceMoves:
            for endPos in pieceMoves:
                testCell = board[endPos[0]][endPos[1]]
                if idenPiece(testCell, not whiteMove) and testCell.lower() == piece: #opponents piece
                    output[(endPos[0], endPos[1])] = testCell
    return output

def inCheck(board, whiteMove):
    r, c = getKingPos(board, whiteMove)
    return len(attacking(board, r, c)) > 0

def getMove(whiteMove, board, move):
    move = move.lower()
    if len(move) == 2: #a3 > Pa3 (pawn to a3)
        move = "P"+move
        
    endPos = notationToIndex[move[1:3]]
    piece = move[0].lower() if whiteMove else move[0].upper()
    possibles = possibleMoves(board, whiteMove=whiteMove)
    print(possibles)
    possibleStartPos = findPiece(board, piece)
    possibleStartPos = [i for i in possibleStartPos if (i in possibles) and (endPos in possibles[i])]
    if len(possibleStartPos) == 0:
        raise Exception("Invalid Move.")
    elif len(possibleStartPos) > 1:
        raise Exception("Unclear which piece should move")
    return (possibleStartPos[0], endPos)
    
def formatNotation(notation):
    notation = notation.replace("\n", " ")
    notation = notation.replace("", "")
    notation = notation.replace("+", "")
    notation = notation.split()
    newNotation = []
    for move in notation:
        while move[0].isdigit() or move[0] == ".":
            move = move[1:]
        newNotation.append(move)
    return newNotation[:-1]

def notationToMove(notation):
    notation = formatNotation(notation)
    print(notation)
    moveList = []
    whiteMove = True
    board = initBoard()
    for move in notation:
        if move == "O-O-O": #castle on queen side
            pass
        elif move == "O-O": #castle on king side
            pass
        else:
            moveList.append(getMove(whiteMove, board, move))
            printBoard(board)
            print(board)
            whiteMove = not whiteMove
            board = movePiece(board, moveList[-1][0], moveList[-1][1])
        
    #print(moveList)


#################################################################################
#################################################################################
#################################################################################

def test():
    import time
    board = [['R', ' ', ' ', ' ', ' ', ' ', ' ', 'R'],
             ['P', 'P', ' ', 'K', ' ', 'P', 'P', 'P'],
             [' ', ' ', 'P', ' ', ' ', ' ', ' ', ' '],
             [' ', ' ', ' ', ' ', ' ', ' ', 'p', ' '],
             [' ', ' ', ' ', 'p', ' ', ' ', 'b', ' '],
             [' ', ' ', 'p', ' ', ' ', ' ', 'p', ' '],
             ['p', 'p', ' ', ' ', ' ', ' ', ' ', ' '],
             ['r', 'n', ' ', 'q', 'k', ' ', ' ', ' ']]
    start = time.time()
    #print(possibleMoves(board, whiteMove=False))
    print(attacking(board, 1, 3))
    board = [['R', 'N', 'B', ' ', 'K', 'B', 'N', 'R'],
             ['P', 'P', 'P', ' ', 'P', 'P', 'P', 'P'],
             [' ', ' ', 'Q', ' ', ' ', ' ', ' ', ' '],
             [' ', ' ', ' ', 'P', ' ', ' ', ' ', ' '],
             [' ', ' ', ' ', 'p', ' ', 'b', ' ', ' '],
             [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
             ['p', 'p', 'p', ' ', 'p', 'p', 'p', 'p'],
             ['r', 'n', ' ', 'q', 'k', 'b', 'n', 'r']]
    #print(rateBoth(board, True))
    print(protecting(board, 6, 2))
    #print(canCastle(board, False))
    #print(inCheck(board, False))
    #print(rook(board, 4, 6, False))
    print(time.time()-start)
    #print(inCheck(board, True))
    #notationToMove("1.d4 d6 2.Nf3 g6 3.e4 Bg7 4.Nc3 a6 5.Be3 b5 6.Bd3 Bb7 7.Qd2 Nd7 8.O-O-O Rc8 9.h4 c5 10.h5 c4 11.hxg6 hxg6 12.Rxh8 Bxh8 13.Rh1 Bg7 14.Be2 b4 15.Nd5 Bxd5 16.exd5 Qa5 17.Kb1 Ndf6 18.Ng5 Nxd5 19.Rh7 Kf8 20.Bg4 Nc3+ 21.bxc3 bxc3 22.Qe2 Rb8+ 23.Ka1 Qb5 24.Ne6+ fxe6 25.Qf3+ Nf6 0-1")
    #notationToMove("1.e4 e5 2.Nf3 Nc6 3.Bb5 Nf6 4.O-O d6 5.d4 Bd7 6.Nc3 Be7 7.Re1 exd4 8.Nxd4 O-O 9.Bf1 Re8 10.f3 Bf8 11.Bg5 h6 12.Bh4 g6 13.Nd5 Bg7 14.Nb5 g5 15.Ndxc7 gxh4 16.Nxa8 Qxa8 17.Nc7 Qd8 18.Nxe8 Nxe8 19.Rb1 Be6 20.c3 Bxa2 21.Ra1 Be6 22.Qd2 a6 23.Qf2 h5 24.f4 Bh6 25.Be2 Nf6 26.Qxh4 Nxe4 27.Qxd8+ Nxd8 28.Bxa6 d5 29.Be2 Bxf4 30.Bxh5 Bc7 31.Rad1 1/2-1/2")
    
notationToIndex = {'b1': (7, 1), 'f5': (3, 5), 'e8': (0, 4), 'b6': (2, 1), 'f8': (0, 5), 'e1': (7, 4), 'f6': (2, 5), 'd8': (0, 3), 'd3': (5, 3), 'b7': (1, 1), 'g5': (3, 6), 'b2': (6, 1), 'e2': (6, 4), 'b5': (3, 1), 'g6': (2, 6), 'g4': (4, 6), 'f2': (6, 5), 'f4': (4, 5), 'c1': (7, 2), 'f1': (7, 5), 'a3': (5, 0), 'e7': (1, 4), 'd1': (7, 3), 'g7': (1, 6), 'c6': (2, 2), 'c3': (5, 2), 'a8': (0, 0), 'd6': (2, 3), 'b3': (5, 1), 'a2': (6, 0), 'a4': (4, 0), 'd5': (3, 3), 'g1': (7, 6), 'c4': (4, 2), 'b8': (0, 1), 'c7': (1, 2), 'g3': (5, 6), 'e5': (3, 4), 'd4': (4, 3), 'd2': (6, 3), 'd7': (1, 3), 'e3': (5, 4), 'b4': (4, 1), 'a7': (1, 0), 'a1': (7, 0), 'g8': (0, 6), 'g2': (6, 6), 'c8': (0, 2), 'a5': (3, 0), 'f3': (5, 5), 'e4': (4, 4), 'e6': (2, 4), 'f7': (1, 5), 'c2': (6, 2), 'c5': (3, 2), 'a6': (2, 0), "h1": (7, 7), "h2":(6, 7), "h3":(5, 7), "h4": (4, 7), "h5": (3, 7), "h6": (2, 7), "h7": (1, 7), "h8": (0, 7)}
indexToNotation = {(7, 3): 'd1', (1, 3): 'd7', (6, 6): 'g2', (5, 6): 'g3', (3, 2): 'c5', (2, 1): 'b6', (0, 0): 'a8', (1, 6): 'g7', (5, 1): 'b3', (0, 3): 'd8', (2, 0): 'a6', (2, 5): 'f6', (7, 2): 'c1', (4, 0): 'a4', (1, 2): 'c7', (3, 3): 'd5', (1, 5): 'f7', (7, 6): 'g1', (4, 4): 'e4', (6, 3): 'd2', (3, 0): 'a5', (3, 6): 'g5', (2, 2): 'c6', (5, 3): 'd3', (4, 1): 'b4', (1, 1): 'b7', (6, 4): 'e2', (5, 4): 'e3', (2, 6): 'g6', (5, 0): 'a3', (7, 1): 'b1', (4, 5): 'f4', (0, 4): 'e8', (6, 0): 'a2', (1, 4): 'e7', (5, 5): 'f3', (7, 5): 'f1', (0, 5): 'f8', (4, 2): 'c4', (1, 0): 'a7', (6, 5): 'f2', (3, 5): 'f5', (0, 1): 'b8', (7, 0): 'a1', (4, 6): 'g4', (5, 2): 'c3', (6, 1): 'b2', (3, 1): 'b5', (2, 4): 'e6', (7, 4): 'e1', (0, 6): 'g8', (6, 2): 'c2', (4, 3): 'd4', (2, 3): 'd6', (3, 4): 'e5', (0, 2): 'c8', (0, 7): "h8", (1, 7): "h7", (2, 7):"h6", (3, 7): "h5", (4, 7): "h4", (5, 7): "h3", (6, 7): "h2", (7, 7):"h1"}    

if __name__ == "__main__":
    test()
    
