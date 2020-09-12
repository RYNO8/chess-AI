from __future__ import print_function #needed for compile
import asyncio
import time
#import concurrent.futures
from copy import deepcopy
import random
import multiprocessing
from utility import unhashableDict
import multiprocessing

def timeit(func, *args, totalTime=4, **kwargs):
    initTime = time.time()
    times = set()
    while True:
        start = time.time()
        func(*args, **kwargs)
        times.add(time.time()-start)
        if start-initTime > totalTime:
            break
        
    print("average time:", sum(times)/len(times), "no. trials:", len(times))

def runOptimise(func, *args):
    return multiprocessing.Pool(processes=3).apply_async(func, args).get(timeout=None)

class Pos: #the restof the code is built on this class
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return '('+str(self.x)+', '+str(self.y)+')'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iter__(self):
        for i in [self.x, self.y]:
            yield i

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y

    def __add__(self, other):
        return Pos(self.x+other.x, self.y+other.y)

    def __sub__(self, other):
        return Pos(self.x+other.x, self.y+other.y)

    def __hash__(self): #this is needed so it can be used in dictionaries and sets
        return self.x*10 + self.y

    def isvalid(self):
        return 0 <= self.x <= 7 and 0 <= self.y <= 7

    @property
    def row(self):
        return self.x

    @property
    def col(self):
        return self.y

rookDir = [Pos(1, 0), Pos(-1, 0), Pos(0, 1), Pos(0, -1)]
bishopDir = [Pos(1, 1), Pos(1, -1), Pos(-1, 1), Pos(-1, -1)]
knightDir = [Pos(-1, -2), Pos(1, -2), Pos(-1, 2), Pos(1, 2), Pos(2, -1), Pos(2, 1), Pos(-2, -1), Pos(-2, 1)]
queenDir = bishopDir + rookDir
allPos = [Pos(0, 0), Pos(0, 1), Pos(0, 2), Pos(0, 3), Pos(0, 4), Pos(0, 5), Pos(0, 6), Pos(0, 7), Pos(1, 0), Pos(1, 1), Pos(1, 2), Pos(1, 3), Pos(1, 4), Pos(1, 5), Pos(1, 6), Pos(1, 7), Pos(2, 0), Pos(2, 1), Pos(2, 2), Pos(2, 3), Pos(2, 4), Pos(2, 5), Pos(2, 6), Pos(2, 7), Pos(3, 0), Pos(3, 1), Pos(3, 2), Pos(3, 3), Pos(3, 4), Pos(3, 5), Pos(3, 6), Pos(3, 7), Pos(4, 0), Pos(4, 1), Pos(4, 2), Pos(4, 3), Pos(4, 4), Pos(4, 5), Pos(4, 6), Pos(4, 7), Pos(5, 0), Pos(5, 1), Pos(5, 2), Pos(5, 3), Pos(5, 4), Pos(5, 5), Pos(5, 6), Pos(5, 7), Pos(6, 0), Pos(6, 1), Pos(6, 2), Pos(6, 3), Pos(6, 4), Pos(6, 5), Pos(6, 6), Pos(6, 7), Pos(7, 0), Pos(7, 1), Pos(7, 2), Pos(7, 3), Pos(7, 4), Pos(7, 5), Pos(7, 6), Pos(7, 7)]
extAllPos = [Pos(0, 4), Pos(7, 4)] + allPos

##################################################################################
##################################################################################
##################################################################################
#BASIC FUNCTIONS

_startingBoard = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
def initBoard():
    return _startingBoard

pieceToAscii = {'k':'\u2654', 'q':'\u2655', 'r':'\u2656', 'b':'\u2657', 'n':'\u2658', 'p':'\u2659',
                'K':'\u265A', 'Q':'\u265B', 'R':'\u265C', 'B':'\u265D', 'N':'\u265E', 'P':'\u265F',
                ' ':' '} #'\u2644'}
def printBoard(board, joiner='|'):
    for i in range(0, 64, 8):
        print(i//8 + 1, "".join(pieceToAscii[piece] for piece in board[i:i+8]))
        
    #print('  A\u2001 B\u2001 C\u2001 D\u2001 E\u2001 F\u2001 G\u2001 H\n')
    print('  A B C D E F G H')


def getCell(board, pos):
    if pos.isvalid():
        #print(x, y)
        return board[pos.row*8 + pos.col]

def findPiece(board, piece):
    '''try to use as little as possible, this looks through every cell on the board'''
    """pieceList = []
    for pos in [Pos(0, 4), Pos(7, 4)] + allPos:
        cell = getCell(board, pos)
        if cell == piece:
            pieceList.append(pos)"""
    
    return [pos for pos in extAllPos if getCell(board, pos) == piece]

def getKingPos(board, whiteMove):
    '''try to use as little as possible, this looks through every cell on the board'''
    if whiteMove:
        try:
            return findPiece(board, 'k')[0]
        except: #king dissapeared?
            return None
    
    else:
        try:
            return findPiece(board, 'K')[0]
        except: #king dissapeared?
            return None

def movePiece(oriBoard, pos, newPos):
    board = deepcopy(oriBoard) #makes copy to avoid error
    board[newPos.row*8 + newPos.col] = board[pos.row*8 + pos.col]
    board[pos.row*8 + pos.col] = ' '
    if getCell(board, newPos) == 'p' and newPos.row == 0: #if white pawn promotion
        board[newPos.row*8 + newPos.col] = 'q'
    elif getCell(board, newPos) == 'P' and newPos.row == 7: #if black pawn promotion
        board[newPos.row*8 + newPos.col] = 'Q'
    return board

def flipBoard(board): #this function isn't used but will be used later
    newBoard = []
    for row in reversed(board):
        newBoard.append(row[::-1])
    return newBoard

def idenPiece(piece, whiteMove):
    return (piece.islower() and whiteMove) or (piece.isupper() and not whiteMove)

def distance(point1, point2):
    return ((point1[0]-point2[0])*2 + (point1[1]-point2[1])**2)**0.5

kingToRook = {Pos(7, 6):[Pos(7, 7), Pos(7, 5)],
              Pos(7, 2):[Pos(7, 0), Pos(7, 3)],
              Pos(0, 6):[Pos(0, 7), Pos(0, 5)],
              Pos(0, 2):[Pos(0, 0), Pos(0, 3)]}
def getRook(kingEnd):
    if kingEnd not in kingToRook:
        raise Exception('invalid kingEnd pos')
    return kingToRook[kingEnd]

##################################################################################
##################################################################################
##################################################################################
#PIECE FUNCTIONS (BASIC)

def pawn(board, pos, whiteMove): #do promotion and umpa saunt
    moves = set()
    if whiteMove:
        oneForwards, twoForwards = pos+Pos(-1, 0), pos+Pos(-2, 0)
        startingRow = 6
        attacking = [Pos(-1, 1), Pos(-1, -1)]

    elif not whiteMove:
        oneForwards, twoForwards = pos+Pos(1, 0), pos+Pos(2, 0)
        startingRow = 1
        attacking = [Pos(1, 1), Pos(1, -1)]

    if getCell(board, oneForwards) == ' ': #step forwards
        moves.add(oneForwards)
        if pos.row == startingRow and getCell(board, twoForwards) == ' ': #leaps if haven't moved
            moves.add(twoForwards)

    for direction in attacking: #takes piece
        testCell = getCell(board, pos+direction)
        if testCell not in [None, ' '] and idenPiece(testCell, not whiteMove):
            moves.add(pos+direction)
    
    return moves

def knight(board, pos, whiteMove):
    moves = set()
    for direction in knightDir:
        new = pos+direction
        testCell = getCell(board, new)
        if testCell == None: #N/A
            pass
        elif testCell == " " or idenPiece(testCell, not whiteMove):
            moves.add(new)
    
    return moves

def bishop(board, pos, whiteMove):
    moves = set()
    for direction in bishopDir:
        new = pos+direction
        for i in range(8):
            testCell = getCell(board, new)
            if testCell == None: #N/A
                break
            elif idenPiece(testCell, not whiteMove): #opponent piece
                moves.add(new)
                break
            elif idenPiece(testCell, whiteMove): #your piece
                break
            elif testCell == " ": #blank
                moves.add(new)
            new += direction
    
    return moves

def rook(board, pos, whiteMove):
    moves = set()
    for direction in rookDir:
        new = pos+direction
        for i in range(8):
            testCell = getCell(board, new)
            if testCell == None: #N/A
                break
            elif idenPiece(testCell, not whiteMove): #opponent piece
                moves.add(new)
                break
            elif idenPiece(testCell, whiteMove): #your piece
                break
            elif testCell == " ": #blank
                moves.add(new)
            new += direction
    
    return moves

def queen(board, pos, whiteMove):
    moves = set()
    for direction in queenDir:
        new = pos+direction
        for i in range(8):
            testCell = getCell(board, new)
            if testCell == None: #N/A
                break
            elif testCell == " ":
                moves.add(new)
            elif idenPiece(testCell, not whiteMove): #opponent piece
                #print("opponent")
                moves.add(new)
                break
            elif idenPiece(testCell, whiteMove): #your piece
                break
            new += direction
    
    return moves

def king(board, pos, whiteMove):
    moves = set()
    for direction in queenDir: #queenDir will be the same as kingDir
        new = pos+direction
        testCell = getCell(board, new)
        if testCell and (testCell == " " or idenPiece(testCell, not whiteMove)):
            moves.add(new)
    
    return moves

##################################################################################
##################################################################################
##################################################################################
#PIECE FUNCTIONS (COMPLEX)

def inversePawn(board, pos, whiteMove):
    moves = set()
    if whiteMove:
        directions = [Pos(1, 1), Pos(1, -1)]
    else:
        directions = [Pos(-1, 1), Pos(-1, -1)]

    for direction in directions: #takes piece
        new = pos+direction
        testCell = getCell(board, new)
        if testCell not in [None, " "] and idenPiece(testCell, not whiteMove):
            moves.add(new)

    if len(moves) != 0:
        return moves

def attacking(board, pos, getEmpty=False):
    '''pieces this square attacks'''
    cell = getCell(board, pos)
    #assert cell != None

    if cell.isupper():
        whiteMove = False
    elif cell.islower():
        whiteMove = True
    else:
        return {} #cell should have piece

    output = {}

    pieceToFunc = {'p':pawn, 'n':knight, 'b':bishop, 'r':rook, 'q':queen, 'k':king}
    pieceMoves = pieceToFunc[cell.lower()](board, pos, whiteMove)
    if pieceMoves:
        for endPos in pieceMoves:
            testCell = getCell(board, endPos)
            if idenPiece(testCell, not whiteMove) or (getEmpty and testCell==' '): #opponents piece
                output[endPos] = testCell
    return output

def protecting(board, pos):
    '''pieces protecting this square (square doesnt have to be occupied)'''
    cell = getCell(board, pos)
    #assert cell != None
    if cell.isupper():
        whiteMoves = [False]
    elif cell.islower():
        whiteMoves = [True]
    else:
        whiteMoves = [True, False]

    output = {}

    for pieceFunc, piece in [(pawn, 'p'), (knight, 'n'), (bishop, 'b'), (rook, 'r'), (queen, 'q'), (king, 'k')]:
        for whiteMove in whiteMoves:
            pieceMoves = pieceFunc(board, pos, not whiteMove)
            if pieceMoves:
                for endPos in pieceMoves:
                    testCell = getCell(board, endPos)
                    #print(piece, testCell)
                    if idenPiece(testCell, whiteMove) and testCell.lower() == piece: #your piece
                        output[endPos] = testCell
    return output

def threatening(board, pos):
    '''pieces threatening this square'''
    cell = getCell(board, pos)
    if cell.isupper():
        whiteMove = False
    elif cell.islower():
        whiteMove = True
    else:
        return {} #cell should have piece
    
    output = {}
    
    for pieceFunc, piece in [(pawn, 'p'), (knight, 'n'), (bishop, 'b'), (rook, 'r'), (queen, 'q'), (king, 'k')]:
        pieceMoves = pieceFunc(board, pos, whiteMove)
        if pieceMoves:
            for endPos in pieceMoves:
                testCell = getCell(board, endPos)
                if testCell.lower() == piece and idenPiece(testCell, not whiteMove): #opponents piece
                    output[endPos] = testCell
    return output

def canCastle(board, whiteMove, kingPos): #assuming the king hasnt moved
    if whiteMove:
        rowNum = 7
    else:
        rowNum = 0
    moves = []
    kingRow = [i.lower() for i in board[rowNum]]
    isChecked = False
    
    if kingRow[:5] == ['r', ' ', ' ', ' ', 'k']:
        for pos in [Pos(rowNum, 1), Pos(rowNum, 2), Pos(rowNum, 3), Pos(rowNum, 4)]:
            if any([pos in i for i in oppMoves.values()]):
                #print(pos)
                isChecked = True
        if not isChecked:
            moves.append(Pos(rowNum, 2))

    if kingRow[4:] == ['k', ' ', ' ', 'r']:
        for pos in [Pos(rowNum, 4), Pos(rowNum, 5), Pos(rowNum, 6)]:
            if any([pos in i for i in oppMoves.values()]):
                #print(pos)
                isChecked = True
        if not isChecked:
            moves.append(Pos(rowNum, 6))
    return kingPos, moves

def possibleMoves(board, whiteMove, doKing=True, kingHasMoved=False):
    moves = {}
    terminalMoves = {}
    oppKing = getKingPos(board, not whiteMove) #assuming opponents king is still on board
    for pos in allPos:
        cell = getCell(board, pos)
        if idenPiece(cell, whiteMove): #your piece
            
            if cell.lower() == "p":
                movementSquares = pawn(board, pos, whiteMove)
            elif cell.lower() == "n":
                movementSquares = knight(board, pos, whiteMove)
            elif cell.lower() == "b":
                movementSquares = bishop(board, pos, whiteMove)
            elif cell.lower() == "r":
                movementSquares = rook(board, pos, whiteMove)
            elif cell.lower() == "q":
                movementSquares = queen(board, pos, whiteMove)
            elif cell.lower() == "k" and doKing:
                movementSquares = king(board, pos, whiteMove)
                kingPos = pos
            
            if movementSquares:
                moves[pos] = movementSquares
                if oppKing in movementSquares: #if can eat king, do that
                    terminalMoves[pos] = {oppKing}
    
    assert kingPos #if this fails, that means whiteMove's king does not exist
    
    if terminalMoves: #you must make sure that the piece capturing the king is not pinned
        return terminalMoves

    if not kingHasMoved and doKing: #castles
        kingPos, castleMoves = canCastle(board, whiteMove, kingPos)
        #print(moves)
        if kingPos in moves:
            moves[kingPos] = moves[kingPos].union(castleMoves)
        elif castleMoves:
            moves[kingPos] = set(castleMoves)

    if doKing:
        #moves = go through all possible moves, keep those when king not in check
        newMoves = {}
        for start in moves:
            for finish in moves[start]:
                newBoard = movePiece(board, start, finish)
                if not threatening(newBoard, kingPos):
                    if start in newMoves:
                        newMoves[start].add(finish)
                    else:
                        newMoves[start] = set([finish])
        return newMoves
    
    #dict   piece in Pos type (row, col):  possible moves in set of Pos (row, col)
    #{      (6, 4)                      :  {(5, 4), (4, 4)}                       , ...}
    return moves

#################################################################################
#################################################################################
#################################################################################
#COMPLEX FUNCTIONS - relies on all above code

def kingInValues(possibles, kingPos): #is this used?
    for value in possibles.values():
        if kingPos in value:
            return True
    return False
    #OR return any([kingPos in value for value in possibles.values()])

def inCheck(board, whiteMove, kingPos=None):
    kingPos = kingPos or getKingPos(board, whiteMove)
    return len(threatening(board, kingPos)) > 0

def evaluateScore(board, whiteMove):
    """the state of the board is before the player (whiteMove) makes its move"""
    #wat? player cannot win before making move
    #TODO: think about evaluate logic, dont work on anything else yet
    #return "none"
    #TODO: optmise the below
    #TODO: do stalemates (when possibleMoves is none and nothing threatening king
    if len(possibleMoves(board, whiteMove)) == 0:
        return "lost"
    elif len(possibleMoves(board, not whiteMove)) == 0:
        return "won"
    else:
        return "none"
    
    """printBoard(board)
    print(whiteMove)
    moves = possibleMoves(board, whiteMove)
    yourKing, oppKing = getKingPos(board, whiteMove), getKingPos(board, not whiteMove)
    yourKingThreats = threatening(board, yourKing)
    oppKingThreats = threatening(board, oppKing)

    #don't use inCheck, since it would have to calculate kingPos twice

    if yourKingThreats and not attacking(board, getKingPos(board, whiteMove)) and (len(yourKingThreats) > 1 or threatening(board, list(yourKingThreats.keys())[0])):
        #something threatening you king and the king cant move and (more than 1 attacker or nothing can stop threatener)
        return 'lost'
    elif oppKingThreats and not attacking(board, getKingPos(board, not whiteMove)) and (len(oppKingThreats) > 1 or threatening(board, list(oppKingThreats.keys())[0])):
        return 'won'
    elif moves == {}:
        return 'stalemate'
    else:
        return 'none'"""

#################################################################################
#################################################################################
#################################################################################
#FINAL STAGE - BOARD CLASS - A SIMPLE CLASS WHICH EMCOMPASSES EVERYTHING
#DON'T BOTHER WITH ALL PREVIOUS CODE - USE THIS INSTEAD

weightings = {'p':1, 'n':3.2, 'b':3.3, 'r':5, 'q':9, 'k':200,
              'P':1, 'N':3.2, 'B':3.3, 'R':5, 'Q':9, 'K':200,
              ' ':0}
class Board:
    def __init__(self, *args): #white is lower, black is upper
        '''\
Board([whiteMove])
Board(boardList, [whiteMove])'''
        #defaults
        self._board = initBoard()
        self._whiteMove = True

        for i in args:
            if isinstance(i, bool):
                self._whiteMove = i
            elif isinstance(i, list):
                self._board = i
            elif isinstance(i, Board):
                self._board = i._board
                self._whiteMove = i._whiteMove
        
        self.computeAll = False
        self._pieceStats = {}
        self._pieceList = {} #whoops, not actually a list

    def __str__(self): #proper board representation
        output = ''
        for rowNum in range(8):
            row = self.getRow(rowNum)
            output += str(8-rowNum) + "| "
            output += ' '.join([i.replace(' ', '.') for i in row])
            output += '\n'
        output += "   ---------------\n"
        output += "   A B C D E F G H"
        return output

    def __repr__(self): #list board representation with pretty print
        output = '[\n'
        for rowNum in range(8):
            row = self.getRow(rowNum)
            output += ' '
            output += str(row)
            output += ', \n'
        output += ']'
        return output

    def __iter__(self):
        for row in self._board:
            yield row

    def __getitem__(self, i):
        return self.getRow(i)

    def __sizeof__(self):
        return self._board.__sizeof__() + self._whiteMove.__sizeof__() + self._moves.__sizeof__() + self._state.__sizeof__() + self._pieceStats.__sizeof__() + self._pieceList.__sizeof__()

    def __len__(self):
        return 8
    
    def __copy__(self):
        return self.deepcopy()
    
    def update(self, onlyMoves=False): #computationally expensive (do only when necessary) ~0.043s +- 0.02s
        '''WARNING: internal function - don't use'''
        whitePiecesWeighted = sum([sum([weightings[i] for i in row if i.islower()]) for row in self._board])
        blackPiecesWeighted = sum([sum([weightings[i] for i in row if i.isupper()]) for row in self._board])
        whitePieces = sum([sum([1 for i in row if i.islower()]) for row in self._board])
        blackPieces = sum([sum([1 for i in row if i.isupper()]) for row in self._board])
        self._moves = {True:{'moves':possibleMoves(self._board, True),
                             'sum':  whitePiecesWeighted,
                             'num':  whitePieces},

                       False:{'moves':possibleMoves(self._board, False),
                              'sum':  blackPiecesWeighted,
                              'num':  blackPieces}}
        self._state = evaluateScore(self._board, self._whiteMove)

        if not onlyMoves:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tasks = [asyncio.ensure_future(self.doTasks(pos)) for pos in allPos]
            loop.run_until_complete(asyncio.gather(*tasks))
            
            
        #print(self._pieceStats)

    async def doTasks(self, pos):
        #print(pos)
        #await asyncio.sleep(1)
        cell = getCell(self._board, pos) #the value at the pos

        if cell.isupper():
            isWhite = False
        elif cell.islower():
            isWhite = True
        elif cell == ' ':
            isWhite = None
        else:
            raise Exception('what is this cell')

        #TODO: make the below section neater
        attack = attacking(self._board, pos)
        free   = {i:attack[i] for i in attack if (
            len(threatening(self._board, i)) > len(protecting(self._board, i)) or # more pieces attacking than those defending
            weightings[attack[i]] > weightings[cell]) # their piece is worth move than yours, good sacrifice
                  } #you are attacking this cell and its a good trade

        attack = {i:attack[i] for i in attack if i not in free} #you are attacking this cell and its a bad trade
        defend = protecting(self._board, pos)
        threat = threatening(self._board, pos) #these are not threats if they are in free
        atRisk = len(threat) + len(free) > len(defend) or min([weightings[i] for i in threat.values()]+[300]) < weightings[cell]
        
        self._pieceStats[pos] = {'isWhite':isWhite,
                                 'attack':attack,
                                 'free'  :free,
                                 'defend':defend,
                                 'threat':threat,
                                 'atRisk':atRisk}

        if cell in self._pieceList:
            self._pieceList[cell].append(pos)
        else:
            self._pieceList[cell] = [pos]

    @property
    def whiteMove(self):
        return self._whiteMove #don't need to deepcopy booleans
    def setWhiteMove(self, whiteMove):
        self._whiteMove = whiteMove
        self.computeAll = False

    @property
    def state(self):
        if not self.computeAll:
            self.update(onlyMoves=True)
        return self._state #deepcopy(self._state)
    
    @property
    def stats(self):
        if not self.computeAll:
            self.update()
            self.computeAll = True #for future, since already updated
        return self._pieceStats #deepcopy(self._pieceStats)
    def getStats(self, pos):
        if not pos in self._pieceStats:
            asyncio.run(self.doTasks(pos))
        return self._pieceStats.get(pos, None) #deepcopy(self._pieceStats.get(pos, None))
    
    def isYourPiece(self, cell):
        return idenPiece(cell, self.whiteMove)

    @property
    def pieces(self):
        if not self.computeAll:
            self.update()
            self.computeAll = True #for future, since already updated
        return self._pieceList #deepcopy(self._pieceList)
    def findPiece(self, piece, whiteMove=None, default=None):
        if whiteMove == True:
            testPiece = piece.lower()
        elif whiteMove == False:
            testPiece = piece.upper()
        else:
            testPiece = piece #deepcopy(piece)
        if self.computeAll:
            return set(self._pieceList.get(testPiece, default)) #deepcopy(self._pieceList.get(testPiece, default))
        else:
            return set(findPiece(self._board, testPiece))

    @property
    def moves(self):
        return self._moves #deepcopy(self._moves)
    def getMoves(self, whiteMove):
        if not self.computeAll:
            self.update(onlyMoves=True)
        return self._moves.get(whiteMove, None)['moves'] #deepcopy(self._moves.get(whiteMove, None)['moves'])
    def getPieceMoves(self, piecePos, whiteMove=None):
        if whiteMove:
            return self.getMoves(whiteMove).get(piecePos, None)
        else:
            return self.getMoves(True).get(piecePos, None) or self.getMoves(False).get(piecePos, None)
        
    def doRandomMove(self):
        moves = self.getMoves(self._whiteMove)
        start = random.choice(list(moves.keys()))
        end = random.choice(list(moves[start]))
        return self.move(start, end)
    def doRandomMoves(self, numMoves):
        """\
returns valid board after numMoves random moves
however, not good position"""
        board = self.deepcopy()
        for i in range(numMoves):
            board = board.doRandomMove()
        return board
    
    @property
    def board(self):
        return self._board #deepcopy(self._board)
    @property
    def rows(self):
        return [self.getRow(i) for i in range(8)]
    def getRow(self, rowNum):
        return self._board[rowNum*8:(rowNum+1)*8] #deepcopy(self._board[rowNum])
    @property
    def cols(self):
        return [self.getCol(i) for i in range(8)]
    def getCol(self, colNum):
        return [self._board[index+colNum] for index in range(0, 64, 8)] #deepcopy([self._board[index+colNum] for index in range(0, 64, 8)])
    def getCell(self, pos):
        return getCell(self._board, pos)
    
    def move(self, startPos, endPos, checkValid=False):
        '''returns the new board with moved piece. this board object doesn't change'''
        if checkValid:
            assert isinstance(startPos, Pos) and isinstance(endPos, Pos)
            if self.computeAll:
                assert self._pieceStats[startPos]['isWhite'] == self._whiteMove
                assert self._pieceStats[endPos]['isWhite'] != self._whiteMove
            else:
                assert idenPiece(getCell(self._board, startPos), self._whiteMove) == True
                assert idenPiece(getCell(self._board, endPos), self._whiteMove) == False
            assert startPos in self.getMoves(self._whiteMove)
            assert endPos in self.getMoves(self._whiteMove)[startPos]

        board = movePiece(self._board, startPos, endPos)

        #check for castling
        if getKingPos(board, self._whiteMove) == endPos and distance(startPos, endPos) == 2: #this is castle
                rookPrev, rookNew = getRook(endPos)
                board = movePiece(board, rookPrev, rookNew)
                
        return Board(board, not self._whiteMove) #this there a way to avoid calling Board() ?

    def deepcopy(self):
        '''deepcopy() -> copy of board'''
        newBoard = deepcopy(self._board)
        return Board(newBoard, not self._whiteMove)


#################################################################################
#################################################################################
#################################################################################
#FORMATTING CHESS NOTATION

notationToIndex = {'b1': Pos(7, 1), 'f5': Pos(3, 5), 'e8': Pos(0, 4), 'b6': Pos(2, 1), 'f8': Pos(0, 5), 'e1': Pos(7, 4), 'f6': Pos(2, 5), 'd8': Pos(0, 3), 'd3': Pos(5, 3), 'b7': Pos(1, 1), 'g5': Pos(3, 6), 'b2': Pos(6, 1), 'e2': Pos(6, 4), 'b5': Pos(3, 1), 'g6': Pos(2, 6), 'g4': Pos(4, 6), 'f2': Pos(6, 5), 'f4': Pos(4, 5), 'c1': Pos(7, 2), 'f1': Pos(7, 5), 'a3': Pos(5, 0), 'e7': Pos(1, 4), 'd1': Pos(7, 3), 'g7': Pos(1, 6), 'c6': Pos(2, 2), 'c3': Pos(5, 2), 'a8': Pos(0, 0), 'd6': Pos(2, 3), 'b3': Pos(5, 1), 'a2': Pos(6, 0), 'a4': Pos(4, 0), 'd5': Pos(3, 3), 'g1': Pos(7, 6), 'c4': Pos(4, 2), 'b8': Pos(0, 1), 'c7': Pos(1, 2), 'g3': Pos(5, 6), 'e5': Pos(3, 4), 'd4': Pos(4, 3), 'd2': Pos(6, 3), 'd7': Pos(1, 3), 'e3': Pos(5, 4), 'b4': Pos(4, 1), 'a7': Pos(1, 0), 'a1': Pos(7, 0), 'g8': Pos(0, 6), 'g2': Pos(6, 6), 'c8': Pos(0, 2), 'a5': Pos(3, 0), 'f3': Pos(5, 5), 'e4': Pos(4, 4), 'e6': Pos(2, 4), 'f7': Pos(1, 5), 'c2': Pos(6, 2), 'c5': Pos(3, 2), 'a6': Pos(2, 0), 'h1': Pos(7, 7), 'h2':Pos(6, 7), 'h3':Pos(5, 7), 'h4': Pos(4, 7), 'h5': Pos(3, 7), 'h6': Pos(2, 7), 'h7': Pos(1, 7), 'h8': Pos(0, 7)}
indexToNotation = {Pos(7, 3): 'd1', Pos(1, 3): 'd7', Pos(6, 6): 'g2', Pos(5, 6): 'g3', Pos(3, 2): 'c5', Pos(2, 1): 'b6', Pos(0, 0): 'a8', Pos(1, 6): 'g7', Pos(5, 1): 'b3', Pos(0, 3): 'd8', Pos(2, 0): 'a6', Pos(2, 5): 'f6', Pos(7, 2): 'c1', Pos(4, 0): 'a4', Pos(1, 2): 'c7', Pos(3, 3): 'd5', Pos(1, 5): 'f7', Pos(7, 6): 'g1', Pos(4, 4): 'e4', Pos(6, 3): 'd2', Pos(3, 0): 'a5', Pos(3, 6): 'g5', Pos(2, 2): 'c6', Pos(5, 3): 'd3', Pos(4, 1): 'b4', Pos(1, 1): 'b7', Pos(6, 4): 'e2', Pos(5, 4): 'e3', Pos(2, 6): 'g6', Pos(5, 0): 'a3', Pos(7, 1): 'b1', Pos(4, 5): 'f4', Pos(0, 4): 'e8', Pos(6, 0): 'a2', Pos(1, 4): 'e7', Pos(5, 5): 'f3', Pos(7, 5): 'f1', Pos(0, 5): 'f8', Pos(4, 2): 'c4', Pos(1, 0): 'a7', Pos(6, 5): 'f2', Pos(3, 5): 'f5', Pos(0, 1): 'b8', Pos(7, 0): 'a1', Pos(4, 6): 'g4', Pos(5, 2): 'c3', Pos(6, 1): 'b2', Pos(3, 1): 'b5', Pos(2, 4): 'e6', Pos(7, 4): 'e1', Pos(0, 6): 'g8', Pos(6, 2): 'c2', Pos(4, 3): 'd4', Pos(2, 3): 'd6', Pos(3, 4): 'e5', Pos(0, 2): 'c8', Pos(0, 7): 'h8', Pos(1, 7): 'h7', Pos(2, 7):'h6', Pos(3, 7): 'h5', Pos(4, 7): 'h4', Pos(5, 7): 'h3', Pos(6, 7): 'h2', Pos(7, 7):'h1'}

def getMove(whiteMove, board, move):
    '''move should be provided as a string of chess notation (e.g. a3)'''
    if move == "O-O":
        king = board.findPiece("k", whiteMove=whiteMove).pop()
        endPos = king + Pos(0, 2)
        return king, endPos
    
    elif move == "O-O-O":
        king = board.findPiece("k", whiteMove=whiteMove).pop()
        endPos = king - Pos(0, 3)
        return king, endPos
    
    move = list(move[:-2]) + [move[-2:], None, None]
    if "x" in move: #["N", "x", "a3"] => ["N", "a3"]
        assert move[1] == "x"
        move.pop(1)
        if move[0].islower():
            move[2] = move.pop(0)
    
    if len(move) == 3: #["a3", None] => ["P", "a3", None]
        move = ["P"] + move
        
    elif len(move) > 4: #['N', '1', 'c3', None, None] => ['N', 'c3', None, '1']
        move[3] = move.pop(1)
        
    #         piece, endPos, pieceRow, pieceCol
    # move = ["P",   "a3",   None,     None]
    piece = move[0].lower() if whiteMove else move[0].upper()
    endPos = notationToIndex[move[1]]
    pieceId = (move[2], move[3])
    
    possibles = board.getMoves(whiteMove)
    possibleStartPos = board.findPiece(piece)
    possibleStartPos = [i for i in possibleStartPos if (i in possibles) and (endPos in possibles[i])]
    
    if len(possibleStartPos) == 0:
        raise Exception('Invalid Move.')
    
    elif len(possibleStartPos) == 1:
        return possibleStartPos[0], endPos
    
    elif len(possibleStartPos) > 1:
        if not any(pieceId):
            raise Exception('Unclear which piece should move')
        
        # use pieceId to determine the appropriate piece the move
        return random.choice(possibleStartPos), endPos
    

def formatNotation(notation):
    #TODO: add headers
    notation = notation.replace('\n', ' ')
    notation = notation.replace(', ', '')
    notation = notation.replace('+', '') #should do this?
    notation = notation.split()
    newNotation = []
    for move in notation:
        while move[0].isdigit() or move[0] == '.':
            move = move[1:]
        newNotation.append(move)
    return newNotation[:-1]

def displayGame(notation):
    notation = formatNotation(notation)
    board = Board()
    
    for move in notation:
        print(board)
        print(move)
        startPos, endPos = getMove(board.whiteMove, board, move)
        board = board.move(startPos, endPos)
        

if __name__ == "__main__":
    notation = """1.e4 c5 2.Nf3 e6 3.d4 cxd4 4.Nxd4 Nc6 5.Nb5 d6 6.c4 Nf6 7.N1c3
    a6 8.Na3 d5 9.cxd5 exd5 10.exd5 Nb4 11.Be2 Bc5 12.O-O O-O
    13.Bf3 Bf5 14.Bg5 Re8 15.Qd2 b5 16.Rad1 Nd3 17.Nab1 h6 18.Bh4
    b4 19.Na4 Bd6 20.Bg3 Rc8 21.b3 g5 22.Bxd6 Qxd6 23.g3 Nd7
    24.Bg2 Qf6 25.a3 a5 26.axb4 axb4 27.Qa2 Bg6 28.d6 g4 29.Qd2
    Kg7 30.f3 Qxd6 31.fxg4 Qd4+ 32.Kh1 Nf6 33.Rf4 Ne4 34.Qxd3 Nf2+
    35.Rxf2 Bxd3 36.Rfd2 Qe3 37.Rxd3 Rc1 38.Nb2 Qf2 39.Nd2 Rxd1+
    40.Nxd1 Re1+ 0-1"""

    displayGame(notation)
    #board = Board()

