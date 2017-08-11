'''List2Matrix takes in an interaction list and outputs an adjacency
matrix built from that interaction list.'''

import sys
from collections import defaultdict as ddict

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


def main(args):

    try:
        name = args[1] # Location of the interaction list
    except (NameError, IndexError):
        print("Error: No matrix input")
        sys.exit()

    #Sending to output folder
    lines = fileToLines(name)
    elements = name.split('/')
    filename = elements[-1][:-4]
    folder = '/'.join(elements[0:len(elements)-2])
    if len(folder) == 0:
        pass
    elif folder[-1] != "/":
        folder = folder + "/"

    
    valueDict = {}
    elementSet = set([])

    for line in lines:
        elements = line.split('\t')
        valueDict[frozenset([elements[0], elements[1]])] = elements[2]
        elementSet.add(elements[0])
        elementSet.add(elements[1])
    print("Find All Nodes. Done.")

    elementList = sorted(list(elementSet))
    matrixSchema = [""]
    matrixSchema.extend(elementList)
    with open(folder + "Output/" + filename + "_matrix.txt", "w") as file:
        file.write('\t'.join(matrixSchema))
        file.write('\n')
    
    valueGet = valueDict.get
    
    for element1 in elementList:
        line = [element1]
        lineAppend = line.append
        for element2 in elementList:
            if valueGet(frozenset([element1, element2])):
                lineAppend(valueGet(frozenset([element1, element2])))
            else:
                lineAppend('0')
    
        with open(folder + "Output/" + filename + "_matrix.txt", "a") as file:
            file.write('\t'.join(line))
            file.write('\n')
    
if __name__ == "__main__":
    main(sys.argv)
