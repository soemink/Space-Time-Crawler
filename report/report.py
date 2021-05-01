import re
from urllib.parse import urlparse

def uniquePages():
    f = open("../text/URLs.txt", "r")
    pages = f.readlines()
    pageset = set()
    f.close()
    for each in pages:
        parsed = urlparse(each)
        link = str(parsed.scheme)+ '://'  + str(parsed.netloc) + str(parsed.path) + str(parsed.query) + str(parsed.params)
        pageset.add(link)
    writef = open("uniquepages.txt", 'w')
    writef.write(str(len(pageset)))
    return

def longestPage(): 
    f = open("../text/urlLen.txt", "r")
    sortedDict = dict()
    data = f.readlines()
    for lines in data:
        newLine = lines.split()
        if len(newLine) > 2:
            sortedDict[" ".join(newLine[:-1])] = int(newLine[-1])
        else:
            sortedDict[newLine[0]] = int(newLine[1])
    sortedDict = sorted(sortedDict.items(), key = lambda x : x[1], reverse = True)
    writef = open("longestPage.txt", 'w')
    printStr = ""
    printStr += sortedDict[0][0]
    writef.write(printStr)
    writef.close()
    return

def top50Words(): #O(n^2) complexity due to the 2 for loops inside each having O(n) complexity
    tokens = []
    f = open("../text/tokens.txt", "r")
    for line in f:
        for word in re.split('[^a-zA-Z0-9]', line):
            if word:
                tokens.append(word)
    f.close()
    tokenCount = dict() 
    for token in tokens:
        if token not in tokenCount:
            tokenCount[token] = 1
        else:
            tokenCount[token] += 1
    sortedDict = sorted(tokenCount.items(), key= lambda x : x[-1], reverse = True)
    writef = open('top50Tokens.txt', 'w')
    #print(sortedDict)
    for i in range(50):
        writef.write(sortedDict[i][0] +": " + str(sortedDict[i][1]) + '\n')
    writef.close()
    return

def subdomains():
    domain = ".ics.uci.edu"
    urlset = set()
    uniqueDict = {}
    urlCount = 0
    f = open('../text/URLs.txt', "r")
    urls = f.readlines()
    for each in urls:
        each = each.strip('\n')
        parsed = urlparse(each)
        link = str(parsed.scheme)+ '://'  + str(parsed.netloc) + str(parsed.path) + str(parsed.query) + str(parsed.params)
        # print(link)
        urlset.add(link.lower())
    for url in urlset:
        if domain in url:
            parsed = urlparse(url)
            subdomain = parsed.netloc.strip('\n')
            if subdomain in uniqueDict:
                uniqueDict[subdomain] += 1
            else:
                uniqueDict[subdomain] = 1
    writef = open("subdomains.txt", "w")
    uniqueDict = sorted(uniqueDict.items(), key = lambda x : x[0])
    for domains in uniqueDict:
        writef.write(str(domains[0]) + ' ' + str(domains[1]) +'\n')
    writef.close()
    f.close()
    return
    
#dictionary => {ics.uci.edu : 1, vision.ics.uci.edu : 3, openlab.ics.uci.edu: 2}

if __name__ == "__main__":
    uniquePages()
    longestPage()
    top50Words()
    subdomains()