import pygameDisplay
from possibleMoves.possibleMoves import *

rate = lambda *args:0 #temporary rate function
#requires rate and Minimax functions
pygameDisplay.main(Minimax, rate, onePlayer=True, compStarts=False, whiteMove=True, depth=2)
