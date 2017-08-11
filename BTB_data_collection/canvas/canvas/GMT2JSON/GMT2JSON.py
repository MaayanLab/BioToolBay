'''GMT2JSON converts a GMT File into a JSON Dictionary. The keys for the JSON
dictionary are the labels of the lines in the GMT file, and the values
are the elements in each line.

Syntax on IDLE: GMT2JSON.main(["", location_of_GMT_file"])
Syntax on Command Line: python GMT2JSON.py location_of_GMT_file

'''

import json
import sys

def fileToList(path):
    #Separates by line. If it cannot find hard returns, it will separate by '\n'
    with open(path,'r') as file:
        string=file.read()
    aList=string.split('\n')

    if aList[len(aList)-1]:
        pass
    else:
        aList.pop()
    return aList


def main(args):
    
    name = args[1]
    aList = fileToList(name)

    aDict={}
    for line in aList:
        elements=line.split('\t')
        aDict[elements[0]] = list(set(elements[2:]))


    elements = name.split('/')
    filename = elements[-1][:-4]
    folder = '/'.join(elements[0:len(elements)-2])

    if len(folder) == 0:
        pass
    elif folder[-1] != "/":
        folder = folder + "/"

            
    with open(folder + "Output/" + filename  + "_dict.json", "w") as file:
        file.write(json.dumps(aDict))



                                                                                                                                                                                                                                                                        
if __name__ == "__main__":
    main(sys.argv)

