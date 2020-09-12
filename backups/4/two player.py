from possibleMoves import *

def submain():
    whiteMove = True
    board = initBoard()
    printBoard(board)
    while score(board, whiteMove) == "none":
        while True:
            try:
                pos, newPos = getMove(whiteMove, board, input("Enter move > "))
            except: #invalid move
                print("This is not a valid move. REEEEEE!")
            else:
                break
        board = movePiece(board, pos, newPos)
        printBoard(board)
        whiteMove = not whiteMove
        
    print("White:", score(board, True))
    print("Black:", score(board, True))

if __name__ == "__main__":
    submain()
    
