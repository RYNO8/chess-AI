from possibleMoves import initBoard, findPiece, movePiece, possibleMoves, evaluateScore, idenPiece, getMove, distance, getKingPos, getRook, protecting, attacking, threatening, inCheck
#from possibleMoves import pawn, knight, bishop, rook, queen, king
import time
import pygame
from copy import deepcopy
from pygame.locals import *

def printBoard(board):
    for x in range(8):
        for y in range(8):
            if (x+y) % 2 == 0:
                pygame.draw.rect(windowSurface, WHITE, (x*tileLength+spacing, y*tileLength+spacing, tileLength-spacing, tileLength-spacing))
            elif (x+y) % 2 == 1:
                pygame.draw.rect(windowSurface, GREEN, (x*tileLength+spacing, y*tileLength+spacing, tileLength-spacing, tileLength-spacing))
            
    imgConversion = {"p":wP, "P":bP, "n":wN, "N":bN, "b":wB, "B":bB, "r":wR, "R":bR, "q":wQ, "Q":bQ, "k":wK, "K":bK}
    for r, row in enumerate(board):
        for c, cell in enumerate(row):
            if cell != " ":
                windowSurface.blit(imgConversion[cell], (c*tileLength+spacing*2, r*tileLength+spacing*2))

def Print(board):
    for row in board:
        print(" ".join([i.replace(" ", ".") for i in row]))
    print()

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
    
    weightings = {"p":1, "n":3, "b":3, "r":5, "q":9, "k":200}
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
    
    if rating == -0.0: #change -0.0 to 0
        rating = 0
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
    #prefered depth = 2
    #for depth 2: when depth==2 max, when depth==1 min, when depth==0 rate
    
    newBoard, score = Max(board, turn, depth, 10000, -10000)
    return newBoard

def Max(board, turn, depth, high, low): #maximise through increasing minimum
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
            #print(threats, defences)
            if len(threats) <= len(defences): #its a reasonable move
                allBoards.append((rateBoth(newboard, not turn), newboard))
            
    possibleBoards = []
    if len(allBoards) > 5:
        cutoff = len(allBoards)//2
    else:
        cutoff = -1
    for sortingScore, boardMoved in sorted(allBoards, key=lambda x:x[0])[:cutoff]: #sort by rating (do best first)
        tempBoard, score = Min(boardMoved, not turn, depth-1, high, bestScore)
        #Print(boardMoved)
        #Print(tempBoard)
        #print(sortingScore, score) #first score pertains to first board
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
            possibleBoards.append((boardMoved, score))
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
    board = [['R', ' ', ' ', 'Q', 'K', 'B', 'N', 'R'],
             ['P', 'P', 'P', ' ', 'P', 'P', 'P', 'P'],
             [' ', ' ', ' ', ' ', 'B', ' ', ' ', ' '],
             [' ', ' ', ' ', 'P', ' ', ' ', ' ', ' '],
             [' ', ' ', ' ', 'N', ' ', 'b', ' ', ' '],
             [' ', ' ', 'n', ' ', ' ', 'n', ' ', ' '],
             ['p', 'p', 'p', ' ', 'p', 'p', 'p', 'p'],
             ['r', ' ', ' ', 'q', 'k', 'b', ' ', 'r']] #shouldn't move the king
    #print(rateBoth(board, False)) #look worse
    #print(rateBoth(board, True))
    start = time.time()
    board = Minimax(board, False, 2)
    Print(board)
    #print(score)
    #print(rateBoth(board, True))
    print(time.time()-start)
    wat
    

def posToCell(pos):
    assert type(pos) == tuple
    return int(pos[1]/tileLength), int(pos[0]/tileLength)

def renderText(text, x, y, textColour=(255, 255, 255), textSize=48):
    font = pygame.font.SysFont(None, textSize)
    text = font.render("    " + text + "    ", True, textColour, BACKGROUND)
    textRect = text.get_rect()
    textRect.centerx, textRect.centery = x, y
    windowSurface.blit(text, textRect)

#test() #will terminate program wunce finished

WHITE = (255, 255, 255)
GREEN = (0, 255, 0) #(165, 42, 42)
BLACK = (0, 0, 0)
BACKGROUND = BLACK
tileLength = 70
spacing = 5
running = True
imgLength = 55
#load all pieces

pygame.init()
wP = pygame.transform.scale(pygame.image.load('white-pawn.png'), [imgLength, imgLength])
bP = pygame.transform.scale(pygame.image.load('black-pawn.png'), [imgLength, imgLength])
wN = pygame.transform.scale(pygame.image.load('white-knight.png'), [imgLength, imgLength])
bN = pygame.transform.scale(pygame.image.load('black-knight.png'), [imgLength, imgLength])
wB = pygame.transform.scale(pygame.image.load('white-bishop.png'), [imgLength, imgLength])
bB = pygame.transform.scale(pygame.image.load('black-bishop.png'), [imgLength, imgLength])
wR = pygame.transform.scale(pygame.image.load('white-rook.png'), [imgLength, imgLength])
bR = pygame.transform.scale(pygame.image.load('black-rook.png'), [imgLength, imgLength])
wQ = pygame.transform.scale(pygame.image.load('white-queen.png'), [imgLength, imgLength])
bQ = pygame.transform.scale(pygame.image.load('black-queen.png'), [imgLength, imgLength])
wK = pygame.transform.scale(pygame.image.load('white-king.png'), [imgLength, imgLength])
bK = pygame.transform.scale(pygame.image.load('black-king.png'), [imgLength, imgLength])
dot = pygame.transform.scale(pygame.image.load('dot.png'), [imgLength, imgLength])
icon = pygame.image.load("icon.png")

windowSurface = pygame.display.set_mode((900, 600), pygame.RESIZABLE)
pygame.display.set_caption("Chess")
pygame.display.set_icon(icon)
windowSurface.fill(BACKGROUND)
renderText("CHESS: By Ryan Ong", 900, 100, textSize=60)

board = initBoard()
"""board = [['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
         ['P', 'P', 'P', ' ', 'P', 'P', 'P', 'P'],
         [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
         [' ', ' ', ' ', 'P', ' ', ' ', ' ', ' '],
         [' ', ' ', ' ', 'p', ' ', 'b', ' ', ' '],
         [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
         ['p', 'p', 'p', ' ', 'p', 'p', 'p', 'p'],
         ['r', 'n', ' ', 'q', 'k', 'b', 'n', 'r']]"""
printBoard(board)
renderText(str(rateBoth(board, True)), 700, 300)
pygame.display.update()
prevMove = (None, None)
whiteMove = True #start on white
onePlayer = True
compStarts = False

if onePlayer and compStarts:
    board = Minimax(board, whiteMove, 2)
    whiteMove = not whiteMove
    printBoard(board)
    renderText(str(rateBoth(board, False)), 700, 300)
    pygame.display.update()
    
while running:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            currentMove = posToCell(pos)
            moves = possibleMoves(board, whiteMove=whiteMove)
            
            if currentMove == prevMove:
                printBoard(board)
                prevMove = (None, None)
                
            elif currentMove in moves:
                printBoard(board)
                for nR, nC in moves[currentMove]:
                    windowSurface.blit(dot, (nC*tileLength+2*spacing, nR*tileLength+2*spacing))
                prevMove = currentMove
                
            else:
                #this might be where the user wants to move the piece
                if (prevMove in moves and currentMove in moves[prevMove]): #valid move
                    board = movePiece(board, prevMove, currentMove)
                    
                    if getKingPos(board, whiteMove) == currentMove and distance(prevMove, currentMove) == 2: #this is castle
                        rookPrev, rookNew = getRook(currentMove)
                        board = movePiece(board, rookPrev, rookNew)
                        
                    prevMove = (None, None)
                    printBoard(board)
                    renderText(str(rateBoth(board, whiteMove)), 700, 300)
                    
                    if evaluateScore(board, whiteMove) in ["won", "lost", "stalemate"]:
                        pygame.quit()
                    whiteMove = not whiteMove #done turn, change to other player
                    print(board)
                    if onePlayer:
                        pygame.display.update()
                        board = Minimax(board, whiteMove, 2)
                        whiteMove = not whiteMove
                        printBoard(board)
                        renderText(str(rateBoth(board, whiteMove)), 700, 300)
                        
                        if evaluateScore(board, whiteMove) in ["won", "lost", "stalemate"]:
                            pygame.quit()
                            
            pygame.display.update()
            
        if event.type in [QUIT,K_ESCAPE]:
            pygame.quit()
            #sys.exit()"""


#oneplayer(False)
