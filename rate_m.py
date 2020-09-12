from functions.functions import Pos

"""
Source			Year	Pawn	Knight	Bishop	Rook	Queen
H. S. M. Coxeter	1940	???	300	350	550	1000
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
weightings = {"p":100, "n":300, "b":350, "r":500, "q":900, "k":20000,
              "P":100, "N":300, "B":350, "R":500, "Q":900, "K":20000,
              " ":0,}
scoring = {"won":1, "lost":-1, "none":0, "stalemate":0.5}

#encourage movement to center
center4 = [Pos(3, 3), Pos(3, 4), Pos(4, 3), Pos(4, 4)]
#and away from the corners, esp for king
corners = [Pos(0, 0), Pos(0, 7), Pos(7, 0), Pos(7, 7)]

#all the tables are for white
pawnTable = [i.replace(" ", "").split(",") for i in """\
 0,  0,  0,  0,  0,  0,  0,  0
50, 50, 50, 50, 50, 50, 50, 50
10, 10, 20, 30, 30, 20, 10, 10
 5,  5, 10, 25, 25, 10,  5,  5
 0,  0,  0, 20, 20,  0,  0,  0
 5, -5,-10,  0,  0,-10, -5,  5
 5, 10, 10,-20,-20, 10, 10,  5
 0,  0,  0,  0,  0,  0,  0,  0""".split("\n")]
knightTable = [i.replace(" ", "").split(",") for i in """\
-50,-40,-30,-30,-30,-30,-40,-50
-40,-20,  0,  0,  0,  0,-20,-40
-30,  0, 10, 15, 15, 10,  0,-30
-30,  5, 15, 20, 20, 15,  5,-30
-30,  0, 15, 20, 20, 15,  0,-30
-30,  5, 10, 15, 15, 10,  5,-30
-40,-20,  0,  5,  5,  0,-20,-40
-50,-40,-30,-30,-30,-30,-40,-50""".split("\n")]
bishopTable = [i.replace(" ", "").split(",") for i in """\
-20,-10,-10,-10,-10,-10,-10,-20
-10,  0,  0,  0,  0,  0,  0,-10
-10,  0,  5, 10, 10,  5,  0,-10
-10,  5,  5, 10, 10,  5,  5,-10
-10,  0, 10, 10, 10, 10,  0,-10
-10, 10, 10, 10, 10, 10, 10,-10
-10,  5,  0,  0,  0,  0,  5,-10
-20,-10,-10,-10,-10,-10,-10,-20""".split("\n")]
rookTable = [i.replace(" ", "").split(",") for i in """\
  0,  0,  0,  0,  0,  0,  0,  0
  5, 10, 10, 10, 10, 10, 10,  5
 -5,  0,  0,  0,  0,  0,  0, -5
 -5,  0,  0,  0,  0,  0,  0, -5
 -5,  0,  0,  0,  0,  0,  0, -5
 -5,  0,  0,  0,  0,  0,  0, -5
 -5,  0,  0,  0,  0,  0,  0, -5
  0,  0,  0,  5,  5,  0,  0,  0""".split("\n")]
queenTable = [i.replace(" ", "").split(",") for i in """\
-20,-10,-10, -5, -5,-10,-10,-20
-10,  0,  0,  0,  0,  0,  0,-10
-10,  0,  5,  5,  5,  5,  0,-10
 -5,  0,  5,  5,  5,  5,  0, -5
  0,  0,  5,  5,  5,  5,  0, -5
-10,  5,  5,  5,  5,  5,  0,-10
-10,  0,  5,  0,  0,  0,  0,-10
-20,-10,-10, -5, -5,-10,-10,-20""".split("\n")]
kingTableMidgame = [i.replace(" ", "").split(",") for i in """\
-30,-40,-40,-50,-50,-40,-40,-30
-30,-40,-40,-50,-50,-40,-40,-30
-30,-40,-40,-50,-50,-40,-40,-30
-30,-40,-40,-50,-50,-40,-40,-30
-20,-30,-30,-40,-40,-30,-30,-20
-10,-20,-20,-20,-20,-20,-20,-10
 20, 20,  0,  0,  0,  0, 20, 20
 20, 30, 10,  0,  0, 10, 30, 20""".split("\n")]
kingTableEndgame = [i.replace(" ", "").split(",") for i in """\
-50,-40,-30,-20,-20,-30,-40,-50
-30,-20,-10,  0,  0,-10,-20,-30
-30,-10, 20, 30, 30, 20,-10,-30
-30,-10, 30, 40, 40, 30,-10,-30
-30,-10, 30, 40, 40, 30,-10,-30
-30,-10, 20, 30, 30, 20,-10,-30
-30,-30,  0,  0,  0,  0,-30,-30
-50,-30,-30,-30,-30,-30,-30,-50""".split("\n")]

tables = {"p":pawnTable, "n":knightTable, "b":bishopTable, "r":rookTable, "q":queenTable, "k":kingTableMidgame}

def pieceTables(piece, pos, whiteTurn):
    #TODO: incomplete pawn tables
    r, c = pos
    if not whiteTurn:
        r = 7-r
    #TODO: normalise the return value
    return int(tables[piece.lower()][r][c])

def sumPiece(pieces):
    return sum(weightings[i] for i in pieces)

def isGoodMove(board, startPos, endPos):
    # what about greek gift sacrifices? https://en.wikipedia.org/wiki/Greek_gift_sacrifice
    startPosCell = board.getCell(startPos)
    endPosCell = board.getCell(endPos)
    
    if not board.getStats(endPos)["atRisk"]:
        return True #not at risk
    
    elif not board.isYourPiece(endPosCell) and isHigher(startPosCell, endPosCell):
        return True #at risk since taken a piece of higher or equal value
    
    #any other conditions?
    return False

def isHigher(piece1, piece2):
    #doesn't distinguish different coloured pieces
    return weightings[piece1] > weightings[piece2]

def getAffected(beforeStats, afterStats, moveFrom, moveTo, board, newBoard, turn):
    #dont understand, wouldnt it be easier to look at board.getCell(moveTo+behindDir) and check for pawns
    rating = 0
    behindDir = Pos(1, 0) if turn else Pos(-1, 0)
    # the piece previously could not move to this square, bc obscured by the moving piece
    for pos in beforeStats:
        value = beforeStats[pos]
        if value not in ("p", "P"):
            rating += 1
    
    pieceBehind = board.getCell(moveFrom+behindDir)
    if pieceBehind in ("p", "P"):
        # add the number of possibleMoves the pawn has
        rating += len(newBoard.getPieceMoves(moveFrom+behindDir))
    
    # the piece could previously move to this square, now obscured by the moving piece
    for pos in afterStats:
        value = afterStats[pos]
        if value not in ("p", "P"):
            rating -= 1
            
    pieceBehind = newBoard.getCell(moveTo+behindDir)
    if pieceBehind in ("p", "P"):
        # minus the number of possibleMoves the pawn has
        rating -= len(board.getPieceMoves(moveTo+behindDir))
    
    return rating

def rateMove(board, whiteMove, moveFrom, moveTo, tempboard):
    """this function is better than rateboard, since it only looks at the piece moving, not the whole board"""
    # this function isnt called with the same variables twice (no point using hash tables)
    # TODO: optimise this
    # TODO: greatest flaw of this function:
    # unprotected pieces should be protected, how to check for?
    if not board: #game has finished
        score = evaluateScore(tempboard, whiteMove)
        return {"won":10000, "lost":-10000, "stalemate":100}[score]

    #init variables
    board.setWhiteMove(whiteMove)
    newBoard = tempboard or board.move(moveFrom, moveTo)
    newBoard.setWhiteMove(whiteMove)
    
    #beforeMoves = board.getMoves(whiteMove) # THIS TAKES A WHILE
    #afterMoves = newBoard.getMoves(whiteMove) # THIS TAKES A WHILE
    beforeStats = board.getStats(moveFrom)
    afterStats = newBoard.getStats(moveTo)
    afterCell = board.getCell(moveTo)
    rating = 0

    #justify decision for weightings... ?
    POSSIBLES = 0.1     # each possible move is not very important
    ATRISK = -1         # it can be taken and will be bad for you. the piece might as well be dead
    FREE = 1            # opposite of ATRISK. if the opp piece is free, might as well be dead
    CAPTURED = 1.5      # more than FREE, incentive to capture
    DEFEND = 0.1        # who cares if its beign defended (e.g. defending king). ATRISK is more important
    TRNASPOSITION = 0   # sort this out first (normalise tables) since king scores are higher than pawn scores
    STATE = 1000        # you want to win
    KINGATTACK = 2.5    # should not be worth more than a "good" piece, but is still good
    DOUBLEDPAWNS = 0.5  # pawns are worth half value if doubled
    ISOLATEDPAWNS = 0.5 # pawns with no pawns next to it
    BLOCK_OPP = 10      # good to block opponents pieces? TODO: justify that number
    # this variable is not used
    # LOST LINE?
    
    # scores relating to moving of piece
    if afterCell != " ": #the place your moving to is not empty, this is a capture
        rating += weightings[afterCell] * 1.5 #CAPTURED
        
    if moveTo in center4: #moving to centre 4, this is development in early game
        rating += 5
        
    # TODO: implement DOUBLEDPAWNS and ISOLATED PAWNS
    
    # calculate at beginning to save costs in repeating
    
    
    # LOST LINE
    rating += (sumPiece(afterStats["free"].values())-sumPiece(beforeStats["free"].values())) #* 1 #FREE
    
    # possible moves
    #rating += (len(afterMoves.get(moveFrom, ()))-len(beforeMoves.get(moveTo, ()))) * .1 #POSSIBLES

    # is the piece at risk
    #interprets True, False as 1, 0 respectively
    rating += (afterStats["atRisk"]-beforeStats["atRisk"]) * -1 #ATRISK

    # is the piece defended
    rating += (len(afterStats["defend"])-len(beforeStats["defend"])) * .1 #DEFEND
    
    # is the piece preventing the opponents pawns from moving
    #print(whiteMove, newBoard.getCell(moveTo+Pos(0, -1)))
    if whiteMove and newBoard.getCell(moveTo+Pos(-1, 0)) == "P" or not whiteMove and newBoard.getCell(moveTo+Pos(1, 0)) == "p":
        rating += 10 #BLOCK_OPP
        
    # can it capture pieces which will benefit
    rating -= sum([weightings[i] for i in beforeStats["free"].values() if i.lower() != "k"]) #* 1 #FREE
    if afterCell != " ": #the place yur moving to is not empty, this is a capture
        rating += weightings[afterCell] * 100 #* 1 #FREE
    
    # the moveTo creates a fork, of which you will benefit
    freeAttacking = afterStats["free"].values()
    if len(freeAttacking) > 1 and afterStats["atRisk"] == False: #possiblility for a fork
        #first = sorted(freeAttacking, key=lambda x:weightings[x])[-1]
        second = sorted(freeAttacking, key=lambda x:weightings[x])[-2]
        # opponent will optimally move the first, and leave the second (which has more value than your piece)
        rating += weightings[second] #* 1 #FREE
        
        if False: # in a certain case, when moveTo is not defended and attacked by opponent, it becomes their free piece
            pass #something happens - LOST LINE
    
    # transposition boards
    rating -= pieceTables(board.getCell(moveFrom), moveFrom, whiteMove) * 0 #TRNASPOSITION
    rating += pieceTables(newBoard.getCell(moveTo), moveTo, whiteMove) * 0 #TRNASPOSITION

    # has won
    #rating -= 0 #has not won yet by default
    rating += scoring[board.state] * 1000 #STATE

    # attacking opp king
    #rating -= len(board.getStats(board.findPiece("k", not whiteMove)[0])["threat"]) * 2.5 #KINGATTACK
    #rating += len(newBoard.getStats(newBoard.findPiece("k", not whiteMove)[0])["threat"]) * 2.5 #KINGATTACK
    
    #print(rating)
    
    # the below gets the pieces which will have more/less possibleMoves when the piece moves
    #rating += getAffected(beforeStats["defend"], afterStats["defend"], moveFrom, moveTo, board, newBoard, whiteMove) * 0.1 #TRNASPOSITION
    
    return round(rating, ndigits=11) #prevents dodgy stuff like 4.499999999999999

if __name__ == "__main__":
    pass
    
