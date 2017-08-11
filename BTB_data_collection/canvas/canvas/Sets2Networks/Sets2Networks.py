'''Sets2Networks

Sets2Networks takes in the location of a GMT File and the number of
shuffles as inputs. This program calculates the strength of an
interaction between two elements for all possible element pairs in a GMT
file. It then outputs a matrix of network inference values, a matrix of
significance scores, and a list of element-element interactions with
scores. All outputs are appended to the same folder as the original file.

To use Sets2Networks, pass the location of the GMT file and the number
of shuffles as part of the program arguments. The default number of
shuffles for Sets2Networks is 1000.

    > python Sets2Networks.py [location of GMT file] [# of shuffles]

Sets2Networks also has a function to flip a GMT file. To flip a GMT
file, type in 'flip' instead of the # of desired shuffles. A flipped GMT
file has the original GMT's elements as its line labels and the original
GMT's labels as its line elements.

NOTE: If you want to see the connections between the terms (labels), you
must flip the GMT File first so that the terms become the elements. S2N
works by finding the connection between the elements.

'''

import collections
import sys
import random
import math

from operator import itemgetter
from itertools import repeat
from collections import defaultdict as ddict, Counter

def GMT_flipper(name):
    '''GMT_flipper flips a GMT file used as the input. Elements in the
    original GMT are the line labels for the Flipped GMT, and the line labels
    in the original GMT are the line elements.'''

    print("GMT Flipper - Starting")
    
    with open(name,'r') as GMT:
        string = GMT.read()
        
    GMT_List = string.split('\n')
    
    if not GMT_List[len(GMT_List)-1]:      # Removes empty line at
        GMT_List.pop()                     # end if present.

    reverseDict=ddict(set)
    
    for line in GMT_List:
        elements=line.split('\t')
        for element in elements[2:]:
            reverseDict[element].add(elements[0])

    
    flippedGMT=[]
    for key in reverseDict.keys():
        line=[key, "na"]
        line.extend(list(reverseDict[key]))
        flippedGMT.append(line)

    with open(name[:-4]+'_flipped.txt','w') as file:
        for line in flippedGMT:
            file.write(('\t'.join(line)))
            file.write('\n')

    print("Flipped GMT Created - ", name[:-4]+"_flipped.txt")



    
def GMT_cleaner(name):
    '''GMT_Cleaner reads a GMT File and converts it to a list. It then
    removes any line that contains only one element.'''
    
    with open(name,'r') as GMT:
        string = GMT.read()
        
    GMT_List = string.split('\n')
    
    if not GMT_List[len(GMT_List)-1]:      # Removes empty line at
        GMT_List.pop()                     # end if present.
    
    cleaned_GMT = []
    
    for line in GMT_List:
        elements = line.split('\t')
        if len(elements)>3:         # elements[0] is the line's label.
            cleaned_GMT.append(line)

    return cleaned_GMT




def Preprocessing(name, cleaned_GMT):
    '''Creates dictionaries using the GMT File. These dictionaries
    are used by the Network Inference algorithm and the Shuffled
    Algorithm for quick look-up.

    element_to_lines and line_elementCount used by the Network Inference
    function to calculate element-element interaction strength.

    elementCount, line_elementCount, and random_heap are used by the
    Shuffled Algorithm.'''


    element_to_lines = ddict(list)    # Maps an element to the
                                      # lines that contain it. Uses
                                      # collections.defaultdict for
                                      # quick append.


    line_elementCount = Counter() # Stores how many elements are in
                                  # a line for all lines.

                              
    elementCount = Counter()      # Stores how many times an element
                                  # appears in a GMT file for all
                                  # elements.

    

    items = []                    # Used as input for rws_heap


    # -------------------------
    # Create dictionaries
    # -------------------------
    
    for i, line in enumerate(cleaned_GMT):
        elements = line.split('\t')
        line_elementCount[i] = len(elements[2:])
        items.append((len(elements[2:]), i))    # Creates rws_heap input
        
        for element in elements[2:]:
            element_to_lines[element].append(i)
            elementCount[element] += 1

    
    elementList = sorted(list(element_to_lines.keys()))


    # -------------------------
    # Create random heap for weighted random sample
    # -------------------------


    items.sort(key=itemgetter(0))   
    items.reverse()                 # Items with the most weight are
                                    # placed on top of heap so less
                                    # nodes need to be fixed overall
                                    # during selection and at sampling's
                                    # end.
                                    
    random_heap = rws_heap(items)

    print("Preprocessing Done. Dictionaries and random heap created.")

    return(element_to_lines, line_elementCount, elementList, elementCount,
           random_heap)




def NI_Algorithm(intersect, line_elementCount):    
    '''Network Inference Algorithm calculates the strength of the
    interaction between the two elements using the lengths of the
    intersecting lines.'''

    value = 1.0
    alpha = .001
    
    for line in intersect:
        value *= 1.0 - (2.0 * alpha / float(line_elementCount[line]))

    out = 1.0 - value
    
    return out




def NI_Unshuffled(name, element_to_lines, line_elementCount,
                                 elementList):
    '''Network_Inference_Unshuffled creates a matrix with row and
    column labels equal to the elementList. This matrix is populated
    by scores from the network inference algorithm for every element
    to element intersection. A pair that consists of the same element
    twice is given 1 as a value.'''
    

    print("Network Inference Unshuffled - Starting")

    #----------------------------
    # Create the Top Row of the Matrix (Column Labels)
    #----------------------------

    
    matrixSchema = ['']
    matrixSchema.extend(elementList)
    matrix = []
    matrix.append('\t'.join(matrixSchema))


    valueDict={}            # Stores the values of element-element pairs
                            # that intersect. For calculating
                            # significance scores in the shuffled part,
                            # pairs that are not in this dict are given
                            # 0.0 as values.

    #----------------------------
    # Running Network Inference Algorithm for Unshuffled
    #----------------------------
    rowCount=1
    rowAll=len(element_to_lines.keys())
    
    for element1 in elementList:
        line = [element1]
        
        if not element_to_lines.get(element1):
            element1_Set = set()
        else:
            element1_Set = set(element_to_lines.get(element1))


        for element2 in elementList:

            if element2 == element1:
                line.append('1')

            else:
                
                if not element_to_lines.get(element2):
                    element2_Set = set()
                else:
                    element2_Set = set(element_to_lines.get(element2))
                    
                intersect = element2_Set.intersection(element1_Set)

                if intersect:
                    value =NI_Algorithm(intersect,line_elementCount)
                    valueDict[frozenset([element1, element2])] = value
                    line.append(str(round(value,8)))
                else:
                    line.append('0')

                
        
        matrix.append('\t'.join(line))

        if rowCount%100 == 0:
            print(rowCount, ' out of ', rowAll)
        rowCount += 1

    

    with open(name[:-4]+'_network_inference_scores.txt','w') as file:
        file.write('\n'.join(matrix))


    print("Network Inference Unshuffled - Done")
        
    return valueDict




def NI_Shuffled(name, shuffles, elementList, valueDict,
                elementCount, line_elementCount, random_heap):
    '''NI_Shuffled creates a matrix with row and column names as the
    elements and calculates a significance score equal to (1 - pvalue)
    for every element pair. The significance score is calculated by
    comparing the original network inference value for an
    element-element pair to the network inference values of permuted
    GMTs (the number of permuted GMTs = shuffles). Pairs that have 0
    for their network inference value in NI_Unshuffled are given a value
    of 0 for their significance score.'''

    print("Network Inferenced Shuffle - Starting")
    print("- This section will take a long time for large GMTs.")
    print("- If you are working with a large GMT, think of using PyPy.")

    mirrorDict={}         # Stores significance scores for each unique
                          # element-element pair. If the same pair is
                          # found, the value stored in mirrorDict is
                          # used instead of recalculating the value.

                                
    #----------------------------
    #Create the Top Row of the Matrix (Column Labels)
    #----------------------------

    
    matrixSchema=['']
    matrixSchema.extend(elementList)

    matrix_scores=[]
    matrixAppend=matrix_scores.append
    matrixAppend('\t'.join(matrixSchema))


    #---------------------------
    # Removing dot functions with a referenced function to improve speed
    #---------------------------


    dictGet=elementCount.get
    setIntersect=set.intersection
    mirrorGet=mirrorDict.get    
    valueGet=valueDict.get


    #----------------------------
    # Running Network Inference Algorithm for Shuffled
    #----------------------------


    lineCount=1
    lineCountAll=len(elementList)

    
    for element1 in elementList:
        line=[element1]
        lineAppend=line.append      
        element1_Count=dictGet(element1)


        for element2 in elementList:
            check=frozenset([element1, element2])
            
            value=valueGet(check)   

            if value:       # Checks that the element-element pair has
                            # a non-zero entry from Network Inference
                            # Unshuffled. If it does, Shuffle proceeds.
                            # If not, its significance score is made 0.
    
                if mirrorGet(check):            # Checks if the pair has
                    lineAppend(mirrorGet(check))# already been processed

                else:
                    element2_Count=dictGet(element2)                
                    valueCounter=0
                    
                    for _ in repeat(1,shuffles):
                        element1_Set = rws_heap_pop(random_heap,
                                                    element1_Count)
                        element2_Set = rws_heap_pop(random_heap,
                                                    element2_Count)
                        intersect = setIntersect(element1_Set,
                                                 element2_Set)
                        out = NI_Algorithm(intersect, line_elementCount)
                        
                        if value > out:
                            # Calculates significance score using
                            # original value. valueCounter used to
                            # calculate score which is equal to
                            # (1 - p-value)
                            
                            valueCounter += 1
      
                    score = str(round(float(valueCounter)/shuffles,5))
                    lineAppend(score)
                    mirrorDict[check] = score
            else:
                lineAppend('0')
                
                  
        matrixAppend('\t'.join(line))

        print(lineCount, ' out of ', lineCountAll)        
        lineCount += 1

 
    with open(name[:-4]+'_significance_scores_matrix.txt','w') as file:
        file.write('\n'.join(matrix_scores))

    print("Shuffled Network Inference - Done")

    return matrix_scores


class Node:
    '''Every node in the heap has weight, value, total weight, and a
    tuple containing the original values of the previous three.

    Total weight of a node includes the total weight of its children
    plus its own weight. Original Weighted Random Sample code
    attributed to Stack Overflow from Jason Orendorff:
    http://stackoverflow.com/questions/2140787'''

    __slots__ = ['w', 'v', 'tw', 'save']
    def __init__(self, w, v, tw, save=()):
        self.w, self.v, self.tw, self.save= w, v, tw, save

    
def rws_heap(items):
    '''h is the heap. It's like a binary tree that lives in an array.
    It has a Node for each pair in `items`. h[1] is the root. Each
    other Node h[i] has a parent at h[i>>1]. Each node has up to 2
    children, h[i<<1] and h[(i<<1)+1].  To get this nice simple
    arithmetic, we have to leave h[0] vacant.

    Original unmodified code attributed to Jason Orendorff
    as indicated by the Node comments.'''

    h = [None]                          # leave h[0] vacant
    for w, v in items:
        h.append(Node(w, v, w))
    for i in range(len(h) - 1, 1, -1):  # total up the tws
        h[i>>1].tw += h[i].tw           # add h[i]'s total to its
                                        # parent
                                        
    for node in h[1:]:                  # Stores original values
        node.save= (node.w, node.tw)    # of node.

    return h


def rws_heap_pop(h,n):
    '''Randomly samples n times from the heap generated by rws_heap.
    Original code modified so that it generates a set and that the
    heap can be reused bypassing the large cost of remaking the heap.
    
    Original unmodified code attributed to Jason Orendorff
    as indicated by the docstring of Node.'''
    

    aChoice=set([])     # Sampled lines go here.
    
    aIndex=set([])      # Stores nodes that need repair after sampling
                        # is done.

    if n == 1:          # If n=1, no need to modify heap after sample
        
        gas = h[1].tw * random.random()    
        i = 1                    
        while gas > h[i].w:
            gas -= h[i].w         
            i <<= 1               
            if gas > h[i].tw:     
                gas -= h[i].tw    
                i += 1            
        aChoice.add(h[i].v)

    else:
        for _ in repeat(1, n):
            gas = h[1].tw * random.random()     # start with random
                                                # amount of gas

            i = 1                       # start driving at the root h[1]
            while gas > h[i].w:         # while gas > node i:                                            #                           node i:
                gas -= h[i].w           #   drive past node i
                i <<= 1                 #   move to first child
                if gas > h[i].tw:       #   if enough gas is present:
                    gas -= h[i].tw      #     go past first child
                                        #               and descendants
                    i += 1              #     move to second child
            w = h[i].w
            

            aChoice.add(h[i].v)         # Out of gas! node i selected
                                        # Node added to chosen list.

            h[i].w = 0                # Removes node from selection

            while i:                  # Fix total weights
                h[i].tw -= w
                aIndex.add(i)         # Stores index of modified node
                i >>= 1

        for i in aIndex:                  # Revert all changed nodes to
            h[i].w, h[i].tw = h[i].save   # original values at end


    return aChoice



def scores_to_interactions(name, matrix_scores):
    '''scores_to_interactions takes in a matrix of scores and outputs
    a tab-delimited list of element-element interactions with non-zero
    significance score in descending order. Duplicate entries for a
    unique element-element pair are not included.

        elementx elementy sigScore_xy
        elementz elementa sigScore_za
        ...'''
    

    elementNameList = [x for x in matrix_scores[0][1:].split('\t')]
    interactionList = []
    trackSet = set()            # Stores already-finished pairs so that
                                # there are no repetitions in the list.
    rowCount = 1
    totalRows=len(elementNameList)
    
    for row in matrix_scores[1:]:
        columns = row.split('\t')
        element1 = columns[0]
        for sigScore, element2 in zip(columns[1:], elementNameList):

            if sigScore == "0" or sigScore == "0.0":
                pass

            else:
                checkSet = frozenset([element1, element2])            
                if checkSet not in trackSet:
                    trackSet.add(checkSet)
                    interactionList.append([element1, element2,
                                            float(sigScore)])
                else:
                    pass

        rowCount += 1
        if rowCount%100 == 0:
            print(rowCount, ' out of ', totalRows)



    interactionList=sorted(interactionList, key=itemgetter(2))
    interactionList.reverse()
    
    with open(name[:-4]+'_interactions.txt', 'w') as file:
        for line in interactionList:
            file.write('\t'.join([line[0], line[1], str(line[2])]))
            file.write('\n')
            


    print("Interaction List Maker - Done")



# -------------------------------
# Main Module to Sets2Networks
# -------------------------------


def main(args):

    try:
        name = args[1] # Location of the GMT File
    except (NameError, IndexError):
        print("Error: No GMT input")
        sys.exit()

        
    try:
        if isinstance(args[2], str):
            if args[2].lower() == 'flip': 
                GMT_flipper(name)
                sys.exit() 
            else:
                raise ValueError
        elif isinstance(args[2],int):
            shuffles = args[2]      # Number of permuted GMTs to be
                                    # created for p-value calculation
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

    print("Shuffles: ", shuffles)
   


    cleaned_GMT = GMT_cleaner(name)

    (element2line,
     line_elementCount,
     elementList,
     elementCount, random_heap) = Preprocessing(name, cleaned_GMT)

    valueDict = NI_Unshuffled(name, element2line, line_elementCount,
                              elementList)   

    matrix_scores = NI_Shuffled(name, shuffles, elementList,
                                valueDict, elementCount,
                                line_elementCount, random_heap)

    scores_to_interactions(name, matrix_scores)



# -------------------------------
# -------------------------------


if __name__=="__main__":
    main(sys.argv)
