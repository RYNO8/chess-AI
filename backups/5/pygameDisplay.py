import pygame
from copy import deepcopy
from pygame.locals import *
from possibleMoves.possibleMoves import *

class main:
    def posToCell(self, pos):
        return Pos(int(pos[1]/self.tileLength), int(pos[0]/self.tileLength))

    def renderText(self, text, x, y, textColour=(255, 255, 255), textSize=48):
        font = pygame.font.SysFont(None, textSize)
        text = font.render("    " + text + "    ", True, textColour, self.BACKGROUND)
        textRect = text.get_rect()
        textRect.centerx, textRect.centery = x, y
        self.windowSurface.blit(text, textRect)

    def printBoard(self, board):
        for x in range(8):
            for y in range(8):
                if (x+y) % 2 == 0:
                    pygame.draw.rect(self.windowSurface, self.TILECOL1, (x*self.tileLength+self.spacing, y*self.tileLength+self.spacing, self.tileLength-self.spacing, self.tileLength-self.spacing))
                elif (x+y) % 2 == 1:
                    pygame.draw.rect(self.windowSurface, self.TILECOL2, (x*self.tileLength+self.spacing, y*self.tileLength+self.spacing, self.tileLength-self.spacing, self.tileLength-self.spacing))
                
        
        for r, row in enumerate(board):
            for c, cell in enumerate(row):
                if cell != " ":
                    self.windowSurface.blit(self.imgConversion[cell], (c*self.tileLength+self.spacing*2, r*self.tileLength+self.spacing*2))

    def __init__(self,  Minimax, rate, onePlayer=True, compStarts=False, whiteMove=True, depth=2):
        """provide these functions before calling this function:
Minimax(board, whiteMove, depth) -> Board
rate(board, whiteMove) -> int, float (not important)
"""
        self.Minimax = Minimax
        self.rate = rate
        
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0) #(165, 42, 42)
        self.BLACK = (0, 0, 0)
        self.GREY = (128, 128, 128)
        self.RED1 = (200, 75, 75)
        self.RED2 = (165, 42, 42)
        self.BLUE = (60, 60, 255)
        self.TILECOL1 = self.WHITE
        self.TILECOL2 = self.RED1
        self.BACKGROUND = self.BLACK
        self.tileLength = 70
        self.spacing = 5
        self.imgLength = 55

        self.whiteMove = whiteMove #start on white
        self.compStarts = compStarts
        self.onePlayer = onePlayer
        self.prevMove = Pos(-1, -1)
        self.DEPTH = depth
        
        #load all pieces
        pygame.init()
        self.wP = pygame.transform.scale(pygame.image.load('white-pawn.png'), [self.imgLength, self.imgLength])
        self.bP = pygame.transform.scale(pygame.image.load('black-pawn.png'), [self.imgLength, self.imgLength])
        self.wN = pygame.transform.scale(pygame.image.load('white-knight.png'), [self.imgLength, self.imgLength])
        self.bN = pygame.transform.scale(pygame.image.load('black-knight.png'), [self.imgLength, self.imgLength])
        self.wB = pygame.transform.scale(pygame.image.load('white-bishop.png'), [self.imgLength, self.imgLength])
        self.bB = pygame.transform.scale(pygame.image.load('black-bishop.png'), [self.imgLength, self.imgLength])
        self.wR = pygame.transform.scale(pygame.image.load('white-rook.png'), [self.imgLength, self.imgLength])
        self.bR = pygame.transform.scale(pygame.image.load('black-rook.png'), [self.imgLength, self.imgLength])
        self.wQ = pygame.transform.scale(pygame.image.load('white-queen.png'), [self.imgLength, self.imgLength])
        self.bQ = pygame.transform.scale(pygame.image.load('black-queen.png'), [self.imgLength, self.imgLength])
        self.wK = pygame.transform.scale(pygame.image.load('white-king.png'), [self.imgLength, self.imgLength])
        self.bK = pygame.transform.scale(pygame.image.load('black-king.png'), [self.imgLength, self.imgLength])
        self.dot = pygame.transform.scale(pygame.image.load('dot.png'), [self.imgLength, self.imgLength])
        self.icon = pygame.image.load("icon.png")
        self.imgConversion = {"p":self.wP, "P":self.bP, "n":self.wN, "N":self.bN, "b":self.wB, "B":self.bB, "r":self.wR, "R":self.bR, "q":self.wQ, "Q":self.bQ, "k":self.wK, "K":self.bK}

        self.windowSurface = pygame.display.set_mode((900, 600), pygame.RESIZABLE)
        pygame.display.set_caption("Chess")
        pygame.display.set_icon(self.icon)
        self.windowSurface.fill(self.BACKGROUND)
        self.renderText("CHESS: By Ryan Ong", 900, 100, textSize=60)

        self.board = Board(self.whiteMove)
        self.printBoard(self.board)
        self.renderText(str(self.rate(self.board, True)), 700, 300)
        pygame.display.update()


        if self.onePlayer and self.compStarts:
            self.board = self.Minimax(self.board, self.whiteMove, self.DEPTH)
            self.whiteMove = not self.whiteMove
            self.printBoard(self.board)
            self.renderText(str(self.rate(board, False)), 700, 300)
            pygame.display.update()
            
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.currentMove = self.posToCell(pygame.mouse.get_pos())
                    self.moves = self.board.getMoves(self.board.whiteMove)
                    
                    if self.currentMove == self.prevMove:
                        self.printBoard(self.board)
                        self.prevMove = Pos(-1, -1)
                        
                    elif self.currentMove in self.moves:
                        self.printBoard(self.board)
                        for nC, nR in self.moves[self.currentMove]:
                            self.windowSurface.blit(self.dot, (nR*self.tileLength+2*self.spacing, nC*self.tileLength+2*self.spacing))
                        self.prevMove = self.currentMove
                        
                    else:
                        #this might be where the user wants to move the piece
                        if (self.prevMove in self.moves and self.currentMove in self.moves[self.prevMove]): #valid move
                            self.board = self.board.move(self.prevMove, self.currentMove)
                            assert self.board
                            
                            self.prevMove = Pos(-1, -1)
                            self.printBoard(self.board)
                            self.renderText(str(self.rate(self.board, self.whiteMove)), 700, 300)
                            
                            if self.board.state in ["won", "lost", "stalemate"]:
                                pygame.quit()
                            self.whiteMove = not self.whiteMove #done turn, change to other player
                            repr(self.board)
                            
                            if self.onePlayer:
                                pygame.display.update()
                                assert self.board
                                self.board = self.Minimax(self.board, self.whiteMove, self.DEPTH)
                                self.whiteMove = not self.whiteMove
                                self.printBoard(self.board)
                                self.renderText(str(self.rate(self.board, self.whiteMove)), 700, 300)
                                
                                if evaluateScore(self.board, self.whiteMove) in ["won", "lost", "stalemate"]:
                                    pygame.quit()
                                    
                    pygame.display.update()
                    
                elif event.type in [QUIT,K_ESCAPE]:
                    pygame.quit()
                    #sys.exit()"""
