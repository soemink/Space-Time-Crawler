import re
import nltk
nltk.download('stopwords')
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

def scraper(url, resp):
    linksList = list()
    valid = False
    print("start scraping")
    # Check if the response is valid
    if resp.raw_response != None:
        print("valid response") 
        #204 means No Content
        if resp.raw_response.status_code != 204: 
            # b'' means 0 byte
            # Detect and avoid dead URLs that return a 200 status but no data 
            # Check if redirect urls are valid, since the raw url does not contain a redirect

            if is_valid(resp.raw_response.url):
                if (resp.raw_response.status_code == 200 and resp.raw_response.content != b''):
                        linksList = extract_next_links(url, resp)
                        valid = True
                elif ((resp.raw_response.status_code > 200) and (resp.raw_response.status_code < 400)):
                        linksList = extract_next_links(url, resp)
                        valid = True

    if valid:
        writeToReportFiles(url, resp)
    
    return linksList

    #links = extract_next_links(url, resp)
    #return [link for link in links if is_valid(link)]
    
def writeToReportFiles(url, resp):
    page_length = tokenize_page(url, resp)
    
    #open and write to files for report
    lenFile = open('text/length.txt', 'a+')
    urlFile = open('text/URLs.txt', 'a+')
    urlLenFile = open('text/urlLen.txt', 'a+')

    lenFile.write(str(page_length) + ' ')
    urlFile.write(url + '\n')
    urlLenFile.write(url + ' ' + str(page_length) + '\n')
    print(url)

    urlLenFile.close()
    urlFile.close()
    lenFile.close()
    
    return

def tokenize_page(url, resp):
    try:
        # bad_urls.txt contains urls with low information content
        # If the url is in bad_urls, don't crawl it
        # should have an empty bad_urls.txt file if using open 'r' in project folder

        # Initialize BeautifulSoup parser
        soup = BeautifulSoup(resp.raw_response.content, 'lxml')
        # Tokenize the page with regex split
        soupText = soup.get_text().lower()
        tokens_raw = list(re.split(r'[^a-z0-9]', soupText))

        print("PAGE TOKENIZED")
        
        # Initialize list of stop words from NLTK
        stop_words = getStopWords()
        tokens_filtered = list()

        # Filter out stop words, append text to tokens.txt
        for token in tokens_raw:
            #token's length equal to 1 could be like .,!
            if token not in stop_words: 
                if len(token) > 1: 
                    tokens_filtered.append(str(token))
        print("STOP WORDS FILTERED")

        # Use to determine low information pages, compare ratio of tags to tokens
        # If the tags comprise of more than 70%, insert into bad_urls.txt for later reference
        html_tags = list(soup.find_all())
        print("SOUP FIND ALL")

        contentLen = float(len(tokens_filtered)) + float(len(html_tags))
        info_ratio = 0
        if contentLen != 0:
            info_ratio = (float(len(html_tags)) / contentLen) 

        # print("INFO CONTENT")

        # if info_ratio > 0.70:
        #     with open('text/bad_urls.txt', mode='a+') as file:
        #         file.write(url + ' ')


        f = open('text/tokens.txt', '+a')
        for token in tokens_filtered:
            f.write(str(token) + ' ')
        f.close()

        # Return the number of tokens in the page after stop word filter
        return len(tokens_filtered)
    
    except Exception as ex:
        print(ex)
        f = open("text/errors.txt","a+")
        f.write("Has tokenize error: " + url + "\n")
        f.close()
        
    return 0
    
def getStopWords():
    stopWordsSet = set()
    stopWordsSet = stopwords.words('english')
    return stopWordsSet

def extract_next_links(url, resp):
    res = []

    # parse web page, representing the document as a nested data structure
    soup = BeautifulSoup(resp.raw_response.text, 'lxml')
    
    # parse links from page content
    for link in soup.find_all('a'):
        # extracting all the URLs found within a page’s <a> tags:
        link = link.get('href')

        if link != None:
            # If the page has no schema add http, if the page supports https, it should automatically redirect
            if re.match(r'\/\/', link):    #link[0] == "/" and link[1] == "/":
                link = 'http:' + link
                
            
            # If the link is just /path/query?parameters etc, turn it into a full link
            if link != None: 
                if re.match(r'\/.*', link):
                    parsed = urlparse(url)
                    link = str(parsed.scheme) + '://' + str(parsed.netloc) + str(link)
                    link = urlparse(link)
                    link = str(link.scheme) + str(link.netloc) + str(link.path) + str(link.query) + str(link.params)

            if is_valid(link):
                res.append(link)
    return res



def is_valid(url):
    try:
        
        
        parsed = urlparse(url)
        #Checks to see if the parsed url is from the approved domains
        #potential optimization by splitting apart the O(n**2) for loop
        #regexp = re.compile(r'(ics\.uci\.edu)|(cs\.uci\.edu)|(stats\.uci\.edu)|(informatics\.uci\.edu)|(today\.uci\.edu\/department\/information_computer_sciences\/)')
        
        f = open('bad_urls.txt', 'r')
            
        listBadURLs = list()
        setBadURLs = set()
        
        for line in f:
            listBadURLs.append(list(line.split()))
        
        listBadURLs = sum(listBadURLs,[])
        for each in listBadURLs:
            setBadURLs.add(each.lower())
        f.close()

        if parsed.geturl().lower() in setBadURLs:
            return False
        

        
        # if not regexp.search(parsed.geturl()):
        #     return False
        #make sure we're in the main domains
        print(parsed.netloc.lower() + parsed.path.lower())
        # if not re.match(r'^(?:www)?(\.ics\.uci\.edu|\.cs\.uci\.edu|\.informatics\.uci\.edu|\.stat\.uci\.edu)$', parsed.netloc.lower())\
        #     and not re.match(r'^(?:www.)?today\.uci\.edu\/department\/information_computer_sciences$', parsed.geturl().lower()):
        #     return False
        #blacklist swiki queries
        if re.match(r'^(?:www.)?(swiki\.ics\.uci\.edu)', parsed.netloc.lower()) \
            and len(parsed.query.lower()):
            return False

        if re.match(r'^(?:www.)?(grape\.ics\.uci\.edu)', parsed.netloc.lower()) \
            and len(parsed.query.lower()):
            return False

        if re.match(r'^(?:www.)?(cbcl\.ics\.uci\.edu)', parsed.netloc.lower()) \
            and len(parsed.query.lower()):
            return False

        if re.match(r'^(?:www.)?(archive\.ics\.uci\.edu)', parsed.netloc.lower()) \
            and len(parsed.path.lower()):
            return False

        if re.match(r'^(?:www.)?(intranet\.ics\.uci\.edu)', parsed.netloc.lower()) \
            and len(parsed.path.lower()):
            return False

        if not re.match(r'^(?:www.)?ics\.uci\.edu|.+\.ics\.uci\.edu' +
                         r'|^(?:www.)?cs\.uci\.edu|.+\.cs\.uci\.edu' +
                         r'|^(?:www.)?informatics\.uci\.edu|.+\.informatics\.uci\.edu' +
                         r'|^(?:www.)?stat\.uci\.edu|.+\.stat\.uci\.edu', parsed.netloc.lower())\
            and not re.match(r'^(?:www.)?today\.uci\.edu\/department\/information_computer_sciences$', parsed.geturl().lower()):
            return False

        if parsed.scheme not in set(["http", "https"]):
            return False
        if "pdf" in parsed.geturl():
            return False
        if "#comment" in parsed.geturl():
            return False
        if "?replytocom" in parsed.geturl():
            return False
        if "#respond" in parsed.geturl():
            return False
        if "?share" in parsed.geturl():
            return False
        if "?ical" in parsed.geturl():
            return False

        if re.search(r'\/calendar\/.+|\/event\/.+|\/events\/.+', parsed.path.lower()):
            return False
        #add files and directory that are bad in the re.match function
        #.*\.
        if re.search(
            r"(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mf|jaso|arff|rtr|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ical)$", parsed.path.lower() + parsed.query.lower()):
            return False
        print(parsed.geturl())

        return True
    except TypeError:
        print ("TypeError for ", parsed)
        raise
