import sys
import os
import re
import string
import subprocess

#check input args
if len(sys.argv) != 3:
    print("Correct usage: wordCountTest.py <input.txt> <output.txt>")
    exit()

inName = sys.argv[1]
outName = sys.argv[2]

# Check input
if not os.path.exists(inName):
    print ("Input %s doesn't exist." % inName)
    exit()

wordDic = {}
addW = False

with open(inName, 'r') as inputFile:
    for line in inputFile:
        # get rid of newline characters
        line = line.strip()

        # split line on whitespace
        auxList = list(line.split(" "))
        
        for i in range(len(auxList)):
            # set to lowercase
            auxList[i] = auxList[i].lower()

            # remove punctuation
            strLength = len(auxList[i])
            if strLength>=1:
                # discard string if it's just punctuation
                if (auxList[i][0].isalpha()): addW = True
                # if it has punctuation at the end, remove it
                if not (auxList[i][strLength-1].isalpha()):
                    auxList[i] = auxList[i][:(strLength-1)]

            # add to dictionary or add count
            if addW:
                if not auxList[i] in wordDic:
                    wordDic[auxList[i]] = 1
                else:
                    wordDic[auxList[i]] += 1
            addW = False

# Dictionary Sort
outDic = {}
for i in sorted(wordDic):
    outDic[i] = wordDic[i]  

for i in outDic:
    print(i, outDic[i], sep=' ')

print("\nWriting to file...")

fileOut = open(outName, "w")
for i in outDic:
    fileOut.write(str(i) + " " + str(outDic[i]) + "\n")
fileOut.close()
print("\nWriting done!")