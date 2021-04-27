import re
import sys
import os

def printFreq(tokenCount): # O(n log n) complexity due to the sorted() method
    sortedDict = sorted(tokenCount.items(), key= lambda x : x[1], reverse= True)
    for k,v in sortedDict:
        print(k, v)


def computeWordFrequencies(tokens): # O(n) complexity because of the for loops and the for loops are not nested
    tokenCount = dict() 
    sametokens = []
    for each in tokens:
        each = each.lower()
        sametokens.append(each)
    for token in sametokens:
        if token not in tokenCount:
            tokenCount[token] = 1
        else:
            tokenCount[token] += 1

    return printFreq(tokenCount)

def tokenize(textfilepath): #O(n^2) complexity due to the 2 for loops inside each having O(n) complexity
    tokens = []
    f = open(textfilepath, "r")
    for line in f:
        for word in re.split('[^a-zA-Z0-9]', line):
            if word:
                tokens.append(word)
    f.close()
    return computeWordFrequencies(tokens)

if __name__ == "__main__":
    if len(sys.argv) < 2:
    	print("File not given to run")
    	sys.exit()
    if not os.path.isfile(sys.argv[1]):
    	print("File not found")
    	sys.exit()

    tokenize(sys.argv[1])

