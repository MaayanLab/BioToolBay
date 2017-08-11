from time import time
import math
from random import random, randint, sample, shuffle, choice
import sys
import json
import copy

def fileToLines(path):
    '''fileToLines separates file by lines.'''
    with open(path,'r') as file:
        string=file.read()
    lines=string.split('\n')

    if lines[len(lines)-1]:
        pass
    else:
        lines.pop()
    return lines


class Node:
    '''The Node object contains the name of the drug, its weights, and
    its index among the weights.'''
    __slots__ =['index', 'name', 'weights']
    def __init__(self, index, name, weights):
        self.index = index
        self.name = name
        self.weights = weights


class Canvas:
    '''The Canvas object is the map that is actually produced. It
    keeps track of used indexes and the Node object is inside each
    object.

    SurroundIndex refers to the surrounding nodes around it.
    SurroundWeight refers to the weight - '''

    __slots__ = ['index', 'node', 'surroundIndex', 'canvasScore']
    def __init__(self, index, node, surroundIndex, canvasScore):
        self.index = index
        self.node = node
        self.surroundIndex = surroundIndex
        self.canvasScore = canvasScore

    
def NodeMaker(lines):
    '''NodeMaker creates the node objects from a mean adjacency matrix
    and stores them in a dict called "nodes." In this case, the nodes
    must have similarity scores of 1 if they match and 0 if they do not.
    '''
    nodes = {}
    for index, line in enumerate(lines[1:]):
        elements = line.split('\t')
        name = elements[0]
        weights = elements[1:]
        nodes[index]=Node(index, name, weights)
    return nodes




def CanvasMaker(nodes):
    global WIDTH
    global TOTALSPOTS
    canvas = {}
    canvasNodes = [x for x in range(len(nodes))]
    while len(canvasNodes) < TOTALSPOTS:
        addNode = int(math.floor(random() * len(nodes)))
        canvasNodes.append(addNode)


    shuffle(canvasNodes)

    
    for index in range(TOTALSPOTS):
        # Determines the indexes that surround the index of a rectangular
        # display.

        surroundIndex = surround(index)
        cIndex = canvasNodes.pop()
        canvas[index] = Canvas(index, nodes[cIndex],
                                   surroundIndex, 0.0)

 
    for index in range(TOTALSPOTS):
        # Determine surrounding weights of each index in the canvas.
        # This is computed through using the other canvas elements.
        surroundIndex = canvas[index].surroundIndex
        canvasScore = 0.0
        for sur_Index in surroundIndex:
            canvasScore += float(canvas[sur_Index].node.weights[canvas[index].node.index])

        canvas[index].canvasScore = canvasScore
        

    return canvas


def surround(index):
    ''' Determines the surrounding indexes of an index given the width
    and a pre-defined index.'''
    global WIDTH
    global TOTALSPOTS
    
    column = index%WIDTH
    overTop = 0
    overBottom = 0
    overLeft = 0
    overRight = 0
    
    #Find the four cardinal directions first

    if (index - WIDTH) < 0:
        indexTop = TOTALSPOTS + index - WIDTH
    else:
        indexTop = index - WIDTH


    if (index + WIDTH) >= TOTALSPOTS:
        indexBottom = index + WIDTH - TOTALSPOTS
    else:
        indexBottom = index + WIDTH


    if column == 0:
        indexLeft = index + WIDTH - 1
        overLeft = 1
    else:
        indexLeft = index - 1


    if column == (WIDTH - 1):
        indexRight = index - WIDTH + 1
        overRight = 1
    else:
        indexRight = index + 1

    #Find corners using the "over" Variables.
    #Separate Top and Bottom corner cases.

    if overLeft == 0:
        indexTopLeft = indexTop - 1
        indexBottomLeft = indexBottom - 1
    elif overLeft == 1:
        indexTopLeft = indexTop + WIDTH - 1
        indexBottomLeft = indexBottom + WIDTH - 1

    if overRight == 0:
        indexTopRight = indexTop + 1
        indexBottomRight = indexBottom + 1
    elif overRight == 1:
        indexTopRight = indexTop - WIDTH + 1
        indexBottomRight = indexBottom - WIDTH +1

    


        
    return [indexTop, indexBottom, indexLeft, indexRight,
            indexTopLeft, indexTopRight, indexBottomLeft, indexBottomRight]
    
    
def calc_new_canvasScore(canvas, targetIndex, modifiedIndex, newNode):
    '''Calculates canvas scores for individual nodes by adding the values
    of the eight surrounding nodes. Note that the modified index must be
    specifically named to the newNode's index; otherwise, it will use the
    original node in that canvas slot.'''
    
    
    if targetIndex == modifiedIndex:
        #Pick the value of the newNode
        targetNodeIndex = newNode.index
    else:
        targetNodeIndex = canvas[targetIndex].node.index

    canvasScore_old = canvas[targetIndex].canvasScore
    canvasScore_new = 0.0

    
    for sur in canvas[targetIndex].surroundIndex:
        #Sur is the surrounding canvas index. Runs through all eight of them
        
        if sur == modifiedIndex:
            #If the modified index is equal to the current surrounding index, use the new node
            #to calculate the score.

            
            if targetNodeIndex == newNode.index:
                #If the surrounding node and the new node are equal, default to 1.
                canvasScore_new += 1.0
            else:            
                #Otherwise, get the score of the newNode in relation to the targetNodeIndex
                canvasScore_new += float(newNode.weights[targetNodeIndex])

        else:
            #If any other canvas index...
            
            if targetNodeIndex == canvas[sur].node.index:
                canvasScore_new += 1.0
            else:
                canvasScore_new += float(canvas[sur].node.weights[targetNodeIndex])

    return canvasScore_new, canvasScore_old



def boltzman_prob(canvas, difference, time_sec, time_end):
    global globalSwap
    # Difference = SumNew - SumOld

    time_left = time_end - time()


    if difference > 0:
        globalSwap += 1
        return True

    elif time_left/time_sec < .0001:
        return False

    else:
        boltz = math.exp((-100*(-difference)/(9 * TOTALSPOTS))
                    /(time_left/time_sec))
        
        if random() < boltz:
            return True
        
        else:
            return False
        

def undo(canvas, choices, changedArray):
    
    (canvas[choices[0]].node,
     canvas[choices[1]].node) = (canvas[choices[1]].node,
                                 canvas[choices[0]].node)
    for changed in changedArray:
        canvas[changed[0]].canvasScore = changed[2]

def swap_nodes(canvas, time_sec):
    '''Determines which two canvas positions are targeted for switching.
    Random selection without replacement.'''
    global WIDTH
    global TOTALNODES
    global TOTALSPOTS
    global count
    global attemptedCount
    t = time()
    time_end = t + time_sec

    fitnessScore = 0.0
    for i in canvas:
        fitnessScore += canvas[i].canvasScore
    print(fitnessScore /(8 * TOTALSPOTS))
    
    while time() < time_end:
        attemptedCount += 1;
        choices = sample(list(canvas.keys()), 2)
        swappers = [[choices[0], choices[1]], [choices[1], choices[0]]]
        changedArray = []
        sumOld = 0
        sumNew = 0
        

        for swapper in swappers:
            # Swapper refers to the slot to be exchanged with the swapped node.
            newNode = canvas[swapper[1]].node
            canvasScore_new, canvasScore_old = calc_new_canvasScore(canvas,
                                                   swapper[0],
                                                   swapper[0],
                                                   newNode)
            sumOld += canvasScore_old
            sumNew += canvasScore_new
            
            changedArray.append((swapper[0],
                                 canvasScore_new,
                                 canvas[swapper[0]].canvasScore))
            
            for sur in canvas[swapper[0]].surroundIndex:
                canvasScore_new, canvasScore_old = calc_new_canvasScore(canvas,
                                                       sur,
                                                       swapper[0],
                                                       newNode)

                sumOld += canvasScore_old
                sumNew += canvasScore_new

                changedArray.append((sur,
                                     canvasScore_new,
                                     canvas[sur].canvasScore))
                


        (canvas[choices[0]].node,
         canvas[choices[1]].node) = (canvas[choices[1]].node,
                                     canvas[choices[0]].node)
        for changed in changedArray:
            canvas[changed[0]].canvasScore = changed[1]


        difference = sumNew - sumOld

        decision = boltzman_prob(canvas, difference, time_sec, time_end)

    
        if decision == True:
            count += 1 
        else:
            undo(canvas, choices, changedArray)
   
    fitnessScore = 0.0
    for i in canvas:
        fitnessScore += canvas[i].canvasScore
    print(fitnessScore /(8 * TOTALSPOTS))

    
    return fitnessScore


def HTMLMaker(JSONString, homeFolder, args):
    
    with open(homeFolder + "Resources/N2C_pt1.txt" , "r") as file:
        N2Cpt1 = file.read()

    with open(homeFolder + "Resources/N2C_pt2.txt" , "r") as file:
        N2Cpt2 = file.read()

    

    stringHTML = ""
    stringHTML += N2Cpt1
    stringHTML += "d3.select('select#selectCanvas').append('option').text('" + args[1] + "');\n\n"
    stringHTML += "".join(["\n\n", "var json = ", JSONString, ";", "\n\n"])
    #stringHTML += "weights = json['weights'];\n\ntextArray = json['texts'];\n\n"

    if len(args) > 3:
        stringHTML += "var infos = "
        stringHTML += GMT2JSON(args[3])
        stringHTML += "\n\n"

    else:
        stringHTML += "var infos = {};\n\n"
        stringHTML += "d3.select('textarea#genes').attr('disabled', 'true').text('No GMT File Inputted');\n\n"
        stringHTML += "d3.select('input#submitButton').attr('disabled', 'true');\n\n"
        stringHTML += "d3.select('input#exampleButton').attr('disabled', 'true');\n\n"
        
    stringHTML += N2Cpt2

    return stringHTML

def GMT2JSON(gmtName):

    gmtString = fileToLines(gmtName)

    gmtDict={}
    for line in gmtString:
        elements=line.split('\t')
        gmtDict[elements[0]] = list(set(elements[2:]))

    return json.dumps(gmtDict);

        
# -------------------------------
# Main Module to N2C
# -------------------------------


def main(args):
    

    # -------------------------------
    # Initializing - Checking Inputs
    # ------------------------------- 


    try:
        name = args[1] # Location of the mean adjacency matrix file
    except (NameError, IndexError):
        print("Error: No matrix input")
        sys.exit()
    print(args[0], "1")

    
    if args[0] == "":
        homeFolder = ""
    else:
        elements = args[0].split('\\')
        homeFolder = '/'.join(elements[0:len(elements)-1])
        print(homeFolder, "1")

        if len(homeFolder) == 0:
            pass
        elif homeFolder[-1] != "/":
            homeFolder = homeFolder + "/"

    try:
        if args[2].isdigit():
            time_sec = int(args[2])     # Duration of program
        else:
            raise ValueError
    except ValueError:
        print("Error: Please input an integer for the desired number")
        print("of shuffles (Default: 1000) or 'flip' for flipping")
        print("the desired GMT File.")
        sys.exit()

    except IndexError:
        shuffles = 1000                 # Default number of shuffles
        print("Using default number of shuffles.")


    lines = fileToLines(args[1])


    # -------------------------------
    # Define Constants
    # -------------------------------
    global TOTALNODES
    global WIDTH
    global TOTALSPOTS

    
    TOTALNODES = len(lines[1:])
    WIDTH = math.ceil(math.sqrt(TOTALNODES))
    TOTALSPOTS = int(WIDTH * WIDTH)

    # -------------------------------
    # Creating Nodes and Canvas
    # -------------------------------

    nodes = NodeMaker(lines)
    canvas = CanvasMaker(nodes)
    

    # -------------------------------
    # Swapping Nodes
    # -------------------------------
    global count
    global attemptedCount
    global globalSwap
    count = 0
    attemptedCount = 0
    globalSwap = 0
    newScore = swap_nodes(canvas, time_sec)


    # -------------------------------
    # Output to JSON
    # -------------------------------

    texts = []
    weights = []
    for index in canvas:
        texts.append(canvas[index].node.name)
        weights.append(canvas[index].canvasScore)

    JSONDict = { "texts" : texts, "weights" : weights}
    JSONString = json.dumps(JSONDict)
    HTMLString = HTMLMaker(JSONString, homeFolder, args)
    print(str(count) + " Successful Swaps")
    print(str(globalSwap) + " Swaps with Increases in Global Fitness")
    print(str(attemptedCount) + " Attempted Swaps")

    elements = name.split('/')
    filename = elements[-1][:-4]
    folder = '/'.join(elements[0:len(elements)-2])

    if len(folder) == 0:
        pass
    elif folder[-1] != "/":
        folder = folder + "/"

    
    with open(folder + "Output/" + filename + ".json", "w") as file:
        file.write(JSONString)

        
    with open(folder + "HTML Files/" + filename + ".html", "w") as file:
        file.write(HTMLString)


                                                                                                                                                                                                                                                                        
if __name__ == "__main__":
    main(sys.argv)
