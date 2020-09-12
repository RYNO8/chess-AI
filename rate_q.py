from q_functions import load, getHash
qtable = load(r"D:\programming\Python\new programs\chess\TDTable.txt")

def rateMove(board, turn, startPos, endPos, newboard):
    hashed = getHash(board.move(startPos, endPos))
    return qtable.get(hashed, 0) #0 score if board not in database
