from network import *
import random
from math import e
from copy import deepcopy

def sigmoid(x): #input -inf to +inf, output 0 to 1
    try:
        return 1/(1+e**(-x))
    
    except OverflowError:
        if x > 0:
            return 1
        else:
            return 0
        

def step(x): #input -inf to +inf, output 0 to 1
    if x > 0:
        return 1
    else:
        return 0

def normalise(value):
    # value is between 0 and 1
    # returns value between -1 and 1
    return round(value*2 - 1, ndigits=3)

class AI:
    def __init__(self, netPattern): #netPattern is the pattern of the nn
        if len(netPattern) < 2:
            raise Exception("Need at least 2 layers in nueral network")
        
        net = Network(Node("start"))
        for x, numLayerNodes in enumerate(netPattern):
            previousLayer = net.depthNodes(x)
            #print(x, previousLayer)
            for y in range(numLayerNodes):
                newNode = Node(str(x)+"."+str(y))
                newNode.setInfo([randInt() for _ in range(len(previousLayer)+1)])
                
                for parent in previousLayer:
                    net.addchild(parent, newNode)
                    
        self._net = net
        self._inputNodes = self._net.depthNodes(1)
        self._outputNodes = self._net.depthNodes(-1)
        self._netPattern = netPattern
        self._learningfunction = lambda x:normalise(sigmoid(x))
        #self._learningfunction = step
    
    def predict(self, values): #type(value) == str, int(value) does not raise error
        if not isinstance(values, list):
            raise TypeError("value should be of type str")
        elif len(values) != len(self._inputNodes):
            raise ValueError("value should be length of inputNodes")
        
        outputs = {}
        for i, value in enumerate(values):
            outputs[self._inputNodes[i]] = value
        
        for layerNum in range(2, len(self._net)):
            #print(layerNum)
            #print(self._net.depthNodes(layerNum))
            
            for i, node in enumerate(self._net.depthNodes(layerNum)):
                info = node.info
                
                weights, bias = info[:-1], info[-1]
                parentOutputs = [outputs[i] for i in node.parents]
                assert len(weights) == len(parentOutputs)
                #weights from -100 to 100
                #parentOutputs from -64 to 64
                nodeOutput = sum([weights[i] * parentOutputs[i] for i in range(len(weights))])/len(weights) + bias
                #print([weights[i] * parentOutputs[i] for i in range(len(weights))], "/", len(weights), bias)
                #print(nodeOutput, self._learningfunction(nodeOutput))
                outputs[node] = self._learningfunction(nodeOutput)
        
        return [outputs[outputNode] for outputNode in self._outputNodes]
    
    def getMutation(self):
        new = deepcopy(self._net)
        for layer in new:
            for node in layer:
                info = node.info
                newInfo = [getMutation(i) for i in info]
                node.setInfo(newInfo)
        return new
    
    def save(self, filename):
        """with open(filename, "r") as f:
            f.write(netPattern)
            for layer in self._net:
                for """
        pass

def randInt():
    # is there a better way to do this
    #return random.random()*2 - 1 #random number between 1 and -1
    return random.choice([-100, 100, -8, 8, -5, 5, -3.3, 3.3, -3.2, 3.2, -1, 1])

def randBoard():
    board = []
    for i in range(64):
        board.append(randInt())
    return board

#random.seed(69)
NN = AI([64, 79, 79, 79, 79, 2])

print(NN.predict(randBoard()))
    
