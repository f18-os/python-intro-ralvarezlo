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

# Check output and delete if necessary
if os.path.exists(outName):
    os.remove(outName)
    print("removing output file")

wordDic = {}

with open(inName, 'r') as inputFile:
    for line in inputFile:
        # get rid of newline characters
        line = line.strip()
        #change hyphens and apostrophes to spaces
        line = line.replace("-", " ")
        line = line.replace("\'", " ")
        #remove punctuation
        for i in string.punctuation:
            line = line.replace(i, "")

        # split line on whitespace
        auxList = list(line.split(" "))
        
        for i in range(len(auxList)):
            # set to lowercase
            auxList[i] = auxList[i].lower()

            if len(auxList[i])>=1 and auxList[i][0].isalpha():
                # add to dictionary or to count
                if not auxList[i] in wordDic:
                    wordDic[auxList[i]] = 1
                else:
                    wordDic[auxList[i]] += 1

# Dictionary Sort
outDic = {}
for i in sorted(wordDic):
    outDic[i] = wordDic[i]

# Write to file
fileOut = open(outName, "w")
for i in outDic:
    fileOut.write(str(i) + " " + str(outDic[i]) + "\n")
fileOut.close()