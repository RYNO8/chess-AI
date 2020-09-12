from __future__ import print_function #needed for compile
import asyncio
import time
#import concurrent.futures
from copy import deepcopy
import random
import multiprocessing
from utility import unhashableDict

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

##################################################################################
##################################################################################
##################################################################################
#BASIC FUNCTIONS

def initBoard():
    return [['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']]

def printBoard(board, joiner='|'):
    pieceToAscii = {'k':'\u2654', 'q':'\u2655', 'r':'\u2656', 'b':'\u2657', 'n':'\u2658', 'p':'\u2659',
                    'K':'\u265A', 'Q':'\u265B', 'R':'\u265C', 'B':'\u265D', 'N':'\u265E', 'P':'\u265F',
                    ' ':' '} #'\u2644'}
    for i, row in enumerate(board):
        print(8-i, end=' ')
        print(joiner.join([pieceToAscii[i] for i in row]))
    #print('  A\u2001 B\u2001 C\u2001 D\u2001 E\u2001 F\u2001 G\u2001 H\n')
    print('  A B C D E F G H')

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

def findPiece(board, piece):
    '''try to use as little as possible, this looks through every cell on the board'''
    pieceList = []
    for pos in [Pos(0, 4), Pos(7, 4)] + allPos:
        cell = getCell(board, pos)
        if cell == piece:
            pieceList.append(pos)
    return pieceList

def movePiece(oriBoard, pos, newPos):
    board = deepcopy(oriBoard) #makes copy to avoid error
    board[newPos.row][newPos.col] = board[pos.row][pos.col]
    board[pos.row][pos.col] = ' '
    if getCell(board, newPos) == 'p' and newPos.row == 0: #if white pawn reached end
        board[newPos.col][newPos.row] = 'q'
    elif getCell(board, newPos) == 'P' and newPos.row == 7: #if black pawn reached end
        board[newPos.col][newPos.row] = 'Q'
    return board

def flipBoard(board): #this function isn't used but will be used later
    newBoard = []
    for row in reversed(board):
        newBoard.append(row[::-1])
    return newBoard

def getCell(board, pos):
    if pos.isvalid():
        #print(x, y)
        return board[pos.row][pos.col]

def idenPiece(piece, whiteMove):
    return (piece.islower() and whiteMove) or (piece.isupper() and not whiteMove)

def distance(point1, point2):
    return ((point1[0]-point2[0])*2 + (point1[1]-point2[1])**2)**0.5

def getRook(kingEnd):
    kingToRook = {Pos(7, 6):[Pos(7, 7), Pos(7, 5)],
                  Pos(7, 2):[Pos(7, 0), Pos(7, 3)],
                  Pos(0, 6):[Pos(0, 7), Pos(0, 5)],
                  Pos(0, 2):[Pos(0, 0), Pos(0, 3)]}
    if kingEnd not in kingToRook:
        raise Exception('invalid kingEnd pos')
    return kingToRook[kingEnd]

##################################################################################
##################################################################################
##################################################################################
#POSSIBLE MOVES

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
    
    if len(moves) != 0:
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

    if len(moves) != 0:
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

    if len(moves) != 0:
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

    if len(moves) != 0:
        return moves

def king(board, pos, whiteMove):
    moves = set()
    for direction in queenDir: #queenDir will be the same as kingDir
        new = pos+direction
        testCell = getCell(board, new)
        if testCell == None:
            pass
        elif testCell == " " or idenPiece(testCell, not whiteMove):
            moves.add(new)

    if len(moves) != 0:
        return moves

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

    if kingRow[:5] == ['r', ' ', ' ', ' ', 'k']:
        isChecked = False
        for pos in [Pos(rowNum, 1), Pos(rowNum, 2), Pos(rowNum, 3), Pos(rowNum, 4)]:
            if any([pos in i for i in oppMoves.values()]):
                #print(pos)
                isChecked = True
        if not isChecked:
            moves.append(Pos(rowNum, 2))

    if kingRow[4:] == ['k', ' ', ' ', 'r']:
        isChecked = False
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
            if cell.lower() == "r":
                moves[pos] = rook(board, pos, whiteMove)
            elif cell.lower() == "n":
                moves[pos] = knight(board, pos, whiteMove)
            elif cell.lower() == "b":
                moves[pos] = bishop(board, pos, whiteMove)
            elif cell.lower() == "q":
                moves[pos] = queen(board, pos, whiteMove)
            elif cell.lower() == "k" and doKing:
                moves[pos] = king(board, pos, whiteMove)
            elif cell.lower() == "p":
                moves[pos] = pawn(board, pos, whiteMove)
            else:
                break
            if moves[pos] == None:
                moves.pop(pos)
            elif oppKing in moves[pos]: #if can eat king, do that
                terminalMoves[pos] = set([oppKing])

    if terminalMoves:
        return terminalMoves

    if not kingHasMoved and doKing: #castles
        kingPos, castleMoves = canCastle(board, whiteMove)
        if kingPos in moves:
            moves[kingPos] = moves[kingPos].union(castleMoves)
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
    
    #dict   piece in Pos type (row, col):  possible moves in set of Pos (row, col)
    #{      (6, 4)                      :  {(5, 4), (4, 4)}                        }
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

def inCheck(board, whiteMove):
    kingPos = getKingPos(board, whiteMove)
    return len(threatening(board, kingPos)) > 0

def evaluateScore(board, whiteMove):
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
        return 'none'

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

    for pieceFunc, piece in [(inversePawn, 'p'), (knight, 'n'), (bishop, 'b'), (rook, 'r'), (queen, 'q'), (king, 'k')]:
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

#################################################################################
#################################################################################
#################################################################################
#FORMATTING CHESS NOTATION

notationToIndex = {'b1': Pos(7, 1), 'f5': Pos(3, 5), 'e8': Pos(0, 4), 'b6': Pos(2, 1), 'f8': Pos(0, 5), 'e1': Pos(7, 4), 'f6': Pos(2, 5), 'd8': Pos(0, 3), 'd3': Pos(5, 3), 'b7': Pos(1, 1), 'g5': Pos(3, 6), 'b2': Pos(6, 1), 'e2': Pos(6, 4), 'b5': Pos(3, 1), 'g6': Pos(2, 6), 'g4': Pos(4, 6), 'f2': Pos(6, 5), 'f4': Pos(4, 5), 'c1': Pos(7, 2), 'f1': Pos(7, 5), 'a3': Pos(5, 0), 'e7': Pos(1, 4), 'd1': Pos(7, 3), 'g7': Pos(1, 6), 'c6': Pos(2, 2), 'c3': Pos(5, 2), 'a8': Pos(0, 0), 'd6': Pos(2, 3), 'b3': Pos(5, 1), 'a2': Pos(6, 0), 'a4': Pos(4, 0), 'd5': Pos(3, 3), 'g1': Pos(7, 6), 'c4': Pos(4, 2), 'b8': Pos(0, 1), 'c7': Pos(1, 2), 'g3': Pos(5, 6), 'e5': Pos(3, 4), 'd4': Pos(4, 3), 'd2': Pos(6, 3), 'd7': Pos(1, 3), 'e3': Pos(5, 4), 'b4': Pos(4, 1), 'a7': Pos(1, 0), 'a1': Pos(7, 0), 'g8': Pos(0, 6), 'g2': Pos(6, 6), 'c8': Pos(0, 2), 'a5': Pos(3, 0), 'f3': Pos(5, 5), 'e4': Pos(4, 4), 'e6': Pos(2, 4), 'f7': Pos(1, 5), 'c2': Pos(6, 2), 'c5': Pos(3, 2), 'a6': Pos(2, 0), 'h1': Pos(7, 7), 'h2':Pos(6, 7), 'h3':Pos(5, 7), 'h4': Pos(4, 7), 'h5': Pos(3, 7), 'h6': Pos(2, 7), 'h7': Pos(1, 7), 'h8': Pos(0, 7)}
indexToNotation = {Pos(7, 3): 'd1', Pos(1, 3): 'd7', Pos(6, 6): 'g2', Pos(5, 6): 'g3', Pos(3, 2): 'c5', Pos(2, 1): 'b6', Pos(0, 0): 'a8', Pos(1, 6): 'g7', Pos(5, 1): 'b3', Pos(0, 3): 'd8', Pos(2, 0): 'a6', Pos(2, 5): 'f6', Pos(7, 2): 'c1', Pos(4, 0): 'a4', Pos(1, 2): 'c7', Pos(3, 3): 'd5', Pos(1, 5): 'f7', Pos(7, 6): 'g1', Pos(4, 4): 'e4', Pos(6, 3): 'd2', Pos(3, 0): 'a5', Pos(3, 6): 'g5', Pos(2, 2): 'c6', Pos(5, 3): 'd3', Pos(4, 1): 'b4', Pos(1, 1): 'b7', Pos(6, 4): 'e2', Pos(5, 4): 'e3', Pos(2, 6): 'g6', Pos(5, 0): 'a3', Pos(7, 1): 'b1', Pos(4, 5): 'f4', Pos(0, 4): 'e8', Pos(6, 0): 'a2', Pos(1, 4): 'e7', Pos(5, 5): 'f3', Pos(7, 5): 'f1', Pos(0, 5): 'f8', Pos(4, 2): 'c4', Pos(1, 0): 'a7', Pos(6, 5): 'f2', Pos(3, 5): 'f5', Pos(0, 1): 'b8', Pos(7, 0): 'a1', Pos(4, 6): 'g4', Pos(5, 2): 'c3', Pos(6, 1): 'b2', Pos(3, 1): 'b5', Pos(2, 4): 'e6', Pos(7, 4): 'e1', Pos(0, 6): 'g8', Pos(6, 2): 'c2', Pos(4, 3): 'd4', Pos(2, 3): 'd6', Pos(3, 4): 'e5', Pos(0, 2): 'c8', Pos(0, 7): 'h8', Pos(1, 7): 'h7', Pos(2, 7):'h6', Pos(3, 7): 'h5', Pos(4, 7): 'h4', Pos(5, 7): 'h3', Pos(6, 7): 'h2', Pos(7, 7):'h1'}

def getMove(whiteMove, board, move):
    '''move should be provided as a string of chess notation (e.g. a3)'''
    move = move.lower()
    if len(move) == 2: #a3 > Pa3 (pawn to a3)
        move = 'P'+move

    endPos = notationToIndex[move[1:3]]
    piece = move[0].lower() if whiteMove else move[0].upper()
    possibles = possibleMoves(board, whiteMove=whiteMove)
    possibleStartPos = findPiece(board, piece)
    possibleStartPos = [i for i in possibleStartPos if (i in possibles) and (endPos in possibles[i])]
    if len(possibleStartPos) == 0:
        raise Exception('Invalid Move.')
    elif len(possibleStartPos) > 1:
        raise Exception('Unclear which piece should move')
    return (possibleStartPos[0], endPos)

def formatNotation(notation):
    notation = notation.replace('\n', ' ')
    notation = notation.replace(', ', '')
    notation = notation.replace('+', '')
    notation = notation.split()
    newNotation = []
    for move in notation:
        while move[0].isdigit() or move[0] == '.':
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
        if move == 'O-O-O': #castle on queen side
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
    return board

#################################################################################
#################################################################################
#################################################################################
#FINAL STAGE - BOARD CLASS - A SIMPLE CLASS WHICH EMCOMPASSES EVERYTHING
#DON'T BOTHER WITH ALL PREVIOUS CODE - USE THIS
weightings = {'p':1, 'n':3.2, 'b':3.3, 'r':5, 'q':9, 'k':200,
              'P':1, 'N':3.2, 'B':3.3, 'R':5, 'Q':9, 'K':200,
              ' ':0}
class Board:
    def __init__(self, *args, computeAll=False): #white is lower, black is upper
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

        self._weightings = weightings
        self.computeAll = computeAll
        self._pieceStats = {}
        self._pieceList = {} #whoops, not actually a list
        if self.computeAll:
            self.update() #creates self._moves, self._pieceStats and self._pieceList

    def __str__(self): #proper board representation
        output = ''
        for row in self._board:
            output += ' '.join([i.replace(' ', '.') for i in row])
            output += '\n'
        return output

    def __repr__(self): #list board representation with pretty print
        output = '[\n'
        for row in self._board:
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
        return self._board.__sizeof__() + self._whiteMove.__sizeof__() + self._weightings.__sizeof__() + self._moves.__sizeof__() + self._state.__sizeof__() + self._pieceStats.__sizeof__() + self._pieceList.__sizeof__()

    def __len__(self):
        return 8

    def update(self, onlyMoves=False): #computationally expensive (do only when necessary) ~0.043s +- 0.02s
        '''WARNING: internal function - don't use'''
        whitePiecesWeighted = sum([sum([self._weightings[i] for i in row if i.islower()]) for row in self._board])
        blackPiecesWeighted = sum([sum([self._weightings[i] for i in row if i.isupper()]) for row in self._board])
        whitePieces = sum([sum([1 for i in row if i.islower()]) for row in self._board])
        blackPieces = sum([sum([1 for i in row if i.isupper()]) for row in self._board])
        self._moves = {True:{'moves':possibleMoves(self._board, whiteMove=True),
                             'sum':  whitePiecesWeighted,
                             'num':  whitePieces},

                       False:{'moves':possibleMoves(self._board, whiteMove=False),
                              'sum':  blackPiecesWeighted,
                              'num':  blackPieces}}
        self._state = evaluateScore(self._board, self._whiteMove)

        if not onlyMoves:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tasks = []
            for pos in allPos:
                tasks.append(self.doTasks(pos))
            
            loop.run_until_complete(*tasks)
            
            
            
            
            
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
            self._weightings[attack[i]] > self._weightings[cell]) # their piece is worth move than yours, good sacrifice
                  } #you are attacking this cell and its a good trade

        attack = {i:attack[i] for i in attack if i not in free} #you are attacking this cell and its a bad trade
        defend = protecting(self._board, pos)
        threat = threatening(self._board, pos) #these are not threats if they are in free
        atRisk = len(threat) > len(defend) or min([self._weightings[i] for i in threat.values()]+[300]) < self._weightings[cell]

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

    @property
    def state(self):
        if not self.computeAll:
            self.update(onlyMoves=True)
        return deepcopy(self._state)

    @property
    def weightings(self):
        return deepcopy(self._weightings)

    @property
    def stats(self):
        if not self.computeAll:
            self.update()
            self.computeAll = True #for future, since already updated
        return deepcopy(self._pieceStats)
    def getStats(self, pos):
        if not self.computeAll:
            asyncio.run(self.doTasks(pos))
        return deepcopy(self._pieceStats.get(pos, None))

    @property
    def pieces(self):
        if not self.computeAll:
            self.update()
            self.computeAll = True #for future, since already updated
        return deepcopy(self._pieceList)
    def findPiece(self, piece, whiteMove=None, default=None):
        if whiteMove == True:
            testPiece = piece.lower()
        elif whiteMove == False:
            testPiece = piece.upper()
        else:
            testPiece = deepcopy(piece)
        if not self.computeAll:
            self.update()
            self.computeAll = True
        return deepcopy(self._pieceList.get(testPiece, default))

    @property
    def moves(self):
        return deepcopy(self._moves)
    def getMoves(self, whiteMove):
        if not self.computeAll:
            self.update(onlyMoves=True)
        return deepcopy(self._moves.get(whiteMove, None)['moves'])

    @property
    def board(self):
        return deepcopy(self._board)
    def getRow(self, rowNum):
        return deepcopy(self._board[rowNum])
    def getCol(self, colNum):
        return deepcopy([row[colNum] for row in self._board])
    def getCell(self, pos):
        return getCell(self._board, pos)
    def flipBoard(self):
        '''flipBoard() -> new board object (original stays the same)'''
        return Board(flipBoard(self._board), not self._whiteMove, computeAll=self.computeAll)

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

        return Board(board, not self._whiteMove, computeAll=False) #this there a way to avoid calling Board() ?

    def deepcopy(self):
        '''deepcopy() -> copy of board'''
        newBoard = deepcopy(self._board)
        return Board(newBoard, not self._whiteMove, computeAll=self.computeAll)

#################################################################################
#################################################################################
#################################################################################
#minimax test

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
weightings = {"p":1, "n":3, "b":3, "r":5, "q":9, "k":200,
              "P":1, "N":3, "B":3, "R":5, "Q":9, "K":200,
              " ":0,}

#encourage movement to center
center4 = [Pos(3, 3), Pos(3, 4), Pos(4, 3), Pos(4, 4)]
#and away from the corners, esp for king
corners = [Pos(0, 0), Pos(0, 7), Pos(7, 0), Pos(7, 7)]

#all the tables are for white
pawnTable = [i.replace(" ", "").split(",") for i in """\
 0,  0,  0,  0,  0,  0,  0,  0
50, 50, 50, 50, 50, 50, 50, 50



 5, -5,-10,  0,  0,-10, -5,  5
 5, 10, 10,-20,-20, 10, 10,  5
 0,  0,  0,  0,  0,  0,  0,  0""".split("\n")]
knightTable = [i.replace(" ", "").split(",") for i in """\
-50,-40,-30,-30,-30,-30,-40,-50
-40,-20,  0,  0,  0,  0,-20,-40



-30,  5, 10, 15, 15, 10,  5,-30
-40,-20,  0,  5,  5,  0,-20,-40
-50,-40,-30,-30,-30,-30,-40,-50""".split("\n")]
bishopTable = [i.replace(" ", "").split(",") for i in """\
-20,-10,-10,-10,-10,-10,-10,-20
-10,  0,  0,  0,  0,  0,  0,-10



-10, 10, 10, 10, 10, 10, 10,-10
-10,  5,  0,  0,  0,  0,  5,-10
-20,-10,-10,-10,-10,-10,-10,-20""".split("\n")]
rookTable = [i.replace(" ", "").split(",") for i in """\
  0,  0,  0,  0,  0,  0,  0,  0
  5, 10, 10, 10, 10, 10, 10,  5



 -5,  0,  0,  0,  0,  0,  0, -5
 -5,  0,  0,  0,  0,  0,  0, -5
  0,  0,  0,  5,  5,  0,  0,  0""".split("\n")]
queenTable = [i.replace(" ", "").split(",") for i in """\
-20,-10,-10, -5, -5,-10,-10,-20
-10,  0,  0,  0,  0,  0,  0,-10



-10,  5,  5,  5,  5,  5,  0,-10
-10,  0,  5,  0,  0,  0,  0,-10
-20,-10,-10, -5, -5,-10,-10,-20""".split("\n")]
kingTableMidgame = [i.replace(" ", "").split(",") for i in """\
-30,-40,-40,-50,-50,-40,-40,-30
-30,-40,-40,-50,-50,-40,-40,-30



-10,-20,-20,-20,-20,-20,-20,-10
 20, 20,  0,  0,  0,  0, 20, 20
 20, 30, 10,  0,  0, 10, 30, 20""".split("\n")]
kingTableEndgame = [i.replace(" ", "").split(",") for i in """\
-50,-40,-30,-20,-20,-30,-40,-50
-30,-20,-10,  0,  0,-10,-20,-30



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

def rateMove(board, whiteMove, moveFrom, moveTo, tempboard):
    """this function is better than rateboard, since it only looks at the piece moving, not the whole board"""
    # this function isnt called with the same variables twice (no point using hash tables)
    # TODO: optimise this
    if not board: #game has finished
        score = evaluateScore(tempboard, whiteMove)
        return {"won":10000, "lost":-10000, "stalemate":100}[score]

    #init variables
    board.setWhiteMove(whiteMove)
    newBoard = board.move(moveFrom, moveTo)
    newBoard.setWhiteMove(whiteMove)

    allMoves = board.getMoves(whiteMove)
    newMoves = newBoard.getMoves(whiteMove)
    rating = 0

    #justify decision for weightings... ?
    POSSIBLES = 0.1     # each possible move is not very important
    ATRISK = -1         # it can be taken and will be bad for you. the piece might as well be dead
    FREE = 1            # opposite of ATRISK. if the opp piece is free, might as well be dead
    DEFEND = 0.1        # who cares if its beign defended (e.g. defending king). ATRISK is more important
    TRNASPOSITION = 0   # sort this out first (normalise tables) since king scores are higher than pawn scores
    STATE = 1000        # you want to win
    KINGATTACK = 2.5    # should not be worth more than a "good" piece, but is still good
    DOUBLEDPAWNS = 0.5  # pawns are worth half value if doubled
    ISOLATEDPAWNS = 0.5 # pawns with no pawns next to it

    # this variable is not used
    # LOST LINE?
    
    # scores relating to moving of piece
    if getCell(board, moveTo) != " ": #the place your moving to is not empty, this is a capture
        rating += weightings[getCell(board, moveTo)]
    if moveTo in center4: #moving to centre 4, this is development in early game
        rating += 5
    
    # other changes to score due to moving the piece
    # LOST LINE
    # LOST LINE
    # LOST LINE 
    
    # calculate at beginning to save costs in repeating
    beforeStats = board.getStats(moveFrom)
    afterStats = newBoard.getStats(moveTo)

    # possible moves
    if moveFrom in allMoves:
        rating -= len(allMoves[moveFrom]) * .1 #POSSIBLES
    if moveTo in newMoves:
        rating += len(newMoves[moveTo]) * .1 #POSSIBLES

    # is the piece at risk
    #interprets True, False as 1, 0 respectively
    rating -= beforeStats["atRisk"] * -1 #ATRISK
    rating += afterStats["atRisk"] * -1 #ATRISK

    # is the piece defended
    rating -= len(beforeStats["defend"]) * .1 #DEFEND
    rating += len(afterStats["defend"]) * .1 #DEFEND

    # can it capture pieces which will benefit
    rating -= sum([weightings[i] for i in beforeStats["free"].values() if i.lower() != "k"]) #* 1 #FREE
    if getCell(board, moveTo) != " ": #the place yur moving to is not empty, this is a capture
        rating += weightings[getCell(board, moveTo)] #* 1 #FREE

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
    #rating -= pieceTables(board.getCell(moveFrom), moveFrom, whiteMove) * 0 #TRNASPOSITION
    #rating += pieceTables(newBoard.getCell(moveTo), moveTo, whiteMove) * 0 #TRNASPOSITION

    # has won
    #rating -= 0 #has not won yet by default
    rating += {"won":1, "lost":-1, "none":0, "stalemate":0.5}[board.state] * 1000 #STATE

    # attacking opp king
    #rating -= len(board.getStats(board.findPiece("k", not whiteMove)[0])["threat"]) * 2.5 #KINGATTACK
    #rating += len(newBoard.getStats(newBoard.findPiece("k", not whiteMove)[0])["threat"]) * 2.5 #KINGATTACK

    #print(rating)
    return round(rating, ndigits=11) #prevents dodgy stuff like 4.499999999999999

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

    global maxScore
    maxScore = Score(-float("inf"), [])
    global moveChoice
    moveChoice = unhashableDict()

    allBoards = generateAllBoards(board, turn)
    """if len(allBoards) > 5: #5 is a random number
        cutoff = len(allBoards)//2
    else:
        cutoff = -1"""
    cutoff = depth+1 #an interesting idea
    assert cutoff > 0

    for oriboard, newBoard, rating, moveFrom, moveTo in sorted(allBoards, key=lambda x:x[2], reverse=True)[:cutoff]:
        score = -Max(newBoard, not turn, depth-1, Score(10000, []), Score(-10000, []), moveFrom, moveTo, [oriboard])
        score.addScore(rating)
        #print(newBoard, score.score[0])
        if score > maxScore:
            maxScore = score
            bestBoard = newBoard

    maxScore.addScore("?") #this is for the starting position, cannot rate because unknown move
    if timeit:
        print(time.time()-start)

    # then https://www.chessprogramming.org/Quiescence_Search for more advanced system
    # is this the after search? ^
    moveChoice.add(board, bestBoard)
    return bestBoard

def generateAllBoards(board, turn): #slowest times = ~2.35s
    #TODO: optimise this
    moves = board.getMoves(turn)
    #print(time.time())
    priority1, priority2 = [], []
    for startPos in moves:
        for endPos in moves[startPos]:
            newboard = board.move(startPos, endPos)
            # if not at risk or just traded (e.g. I captured, you are going to capture back)
            # this prunes search tree
            if newboard.getStats(endPos)["atRisk"] == False or (board.getStats(endPos)["isWhite"] == (not turn) and board.getStats(endPos)["atRisk"]):
                # what about greek gift sacrifices? https://en.wikipedia.org/wiki/Greek_gift_sacrifice
                # print(startPos, endPos, rateMove(board, turn, startPos, endPos))if CERTAIN_CONDITION:
                priority1.append((board.deepcopy(),
                                  newboard,
                                  rateMove(board, turn, startPos, endPos, newboard),
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
    #[(board, newboard, rating, startPos, endPos), ...]

def Print(*args):
    assert type(args[-1]) == int #this is the depth
    if args[-1] == 1:
        print(*args[:-1])

#implementation of Negamax alogorithm, where Min(low, high) = -Max(-high, -low)
def Max(board, turn, depth, high, low, moveFrom, moveTo, history): #maximise through increasing minimum
    assert high >= low
    #board.setWhiteMove(turn)
    #moveFrom, moveTo and prevBoard are not used when depth > 0
    if depth == 0 or evaluateScore(board, turn) in ["won", "tie", "stalemate"]:
        #print(board, rateBoth(board, turn))
        return Score(rateMove(history[-1], not turn, moveFrom, moveTo, board), history+[board])

    bestScore = low
    allBoards = generateAllBoards(board, turn)

    """if len(allBoards) > 5: #5 is a random number

    else:
        cutoff = -1"""
    cutoff = depth #an interesting idea
    #print([i[0] for i in allBoards]) #sorting score

    # optimisation if theres only 1 board? return board, score (whats the score?)
    for oriBoard, boardMoved, sortingScore, startPos, endPos in sorted(allBoards, key=lambda x:x[2], reverse=True)[:cutoff]:
        if depth == 1:
            moveChoice.add(oriBoard, boardMoved)
            return Score(sortingScore, history+[oriBoard, boardMoved]) #go for highest sortingScore (very fast)
        Print("before", boardMoved, depth)
        score = -Max(boardMoved, not turn, depth-1, -bestScore, -high, startPos, endPos, history+[oriBoard]) #swaped alpha and beta
        score.addScore(sortingScore)
        Print("scoring", sortingScore, score, depth) #first score pertains to first board
        
        bestScore = max(bestScore, score)
        if bestScore > high: #this is pruning, dont have to search after finding this
            moveChoice.add(oriBoard, bestScore.history[-1])
            return bestScore

    moveChoice.add(board, bestScore.history[-1])
    return bestScore

def randBoard():
    board = Board()
    for i in range(random.randint(10, 20)):
        startPos = random.choice(list(board.getMoves(board.whiteMove).keys()))
        endPos = random.choice(list(board.getMoves(board.whiteMove)[startPos]))
        board.move(startPos, endPos)
    #returns valid board, but not good position
    return board

def timeit(func, *args, totalTime=4):
    initTime = time.time()
    times = set()
    while True:
        start = time.time()
        func(*args)
        times.add(time.time()-start)
        if start-initTime > totalTime:
            break
    print("average time:", sum(times)/len(times), "no. trials:", len(times))


    
def runOptimise(func, *args):
    return multiprocessing.Pool(processes=3).apply_async(func, args).get(timeout=1)

def test():
    board = [['R', 'N', ' ', ' ', 'K', 'B', 'N', 'R'],
             ['P', 'P', 'P', 'b', 'P', 'P', 'P', 'P'],
             [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
             [' ', ' ', ' ', ' ', ' ', 'B', ' ', ' '],
             [' ', ' ', ' ', 'p', 'P', ' ', ' ', ' '],
             [' ', ' ', 'n', ' ', ' ', ' ', ' ', 'p'],
             ['p', 'p', 'p', ' ', ' ', 'p', 'p', ' '],
             ['r', ' ', 'b', 'q', 'k', ' ', 'n', 'r']] # this should eat knight on 5 5
    board = Board(True)
    board = board.move(Pos(6, 3), Pos(4, 3))
    board = board.move(Pos(0, 1), Pos(2, 2))
    board = board.move(Pos(7, 2), Pos(4, 5))
    print(board)
    new = Minimax(board, board.whiteMove, 2)
    print(new)
    #board = board.move(Pos(1, 3), Pos(3, 3))
    #board = board.move(Pos(7, 1), Pos(5, 2))
    #board = board.move(Pos(0, 6), Pos(2, 5))
    #board = board.move(Pos(5, 2), Pos(3, 1))
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
    #TODO: backup to home
    #TODO: create objects for individual pieces?
    test()
