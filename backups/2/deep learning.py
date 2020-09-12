pieces = {"P":"pawn", "N":"knight", "B":"bishop", "R":"rook", "Q":"queen", "K":"king"}

def func(board0, whiteMove): #2 layer
    opPossibles = possibleMoves(board0, whiteMove=not whiteMove)
    for key in opPossibles.keys():
        for value in opPossibles[key]:
            print("", key, value)
            board1 = movePiece(board0, key, value)
            yoPossibles = possibleMoves(board1, whiteMove=whiteMove)
            for key in yoPossibles.keys():
                for value in yoPossibles[key]:
                    print(key, value)
    
def rateBoardSub(boards, whiteMove, moveLen):
    newBoards = []
    for board in boards:
        possibles = possibleMoves(board, whiteMove=whiteMove)
        #print(possibles)
        for key in possibles.keys():
            for value in possibles[key]:
                
                newBoard = movePiece(board, key, value)
                #printBoard(newBoard)
                
                if whiteMove and len(findPiece(board, "K")) == 0: #no more king
                    #print(moveLen)
                    return moveLen
                elif not whiteMove and len(findPiece(board, "k")): #no more king
                    #print(moveLen)
                    return moveLen
                
                newBoards.append(newBoard)
                
    print("Depth: " + str(moveLen))
    print("Boards searched: " + str(len(boards)))
    print("")
    return rateBoardSub(newBoards, whiteMove, moveLen+1)

def rateBoard(board, whiteMove):
    if not won(board, whiteMove): #safety net
        yourMoveLen = rateBoardSub([board], whiteMove, 0)
        opponentMoveLen = rateBoardSub([board], not whiteMove, 0)
        return yourMoveLen - opponentMoveLen

if __name__ == "__main__":
    import random
    from possibleMoves import *
    board =[[" ", "K", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", "k", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "]]
    print(won(board, True))
    #board = initBoard()
    #print(rateBoard(board, True))
