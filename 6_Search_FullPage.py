import re, os, yaml, json, random #imports those libraries
from datetime import datetime #imports the timestamp extension from the datetime library

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions #imports our functions file

###########################################################
# VARIABLES ###############################################
###########################################################

settings = functions.loadYmlSettings("settings.yml") #loads our settings yaml file

###########################################################
# FUNCTIONS ###############################################
###########################################################

def searchOCRresults(pathToMemex, searchString): #defines a new function to search through OCRed results
    print("SEARCHING FOR: `%s`" % searchString) #prints phrase and the search String
    files = functions.dicOfRelevantFiles(pathToMemex, ".json") #generates a dictionary with citekeys as keys and paths to json-Files as values
    results = {} #creates an empty dictionary

    for citationKey, pathToJSON in files.items(): #loops through all called files
        data = json.load(open(pathToJSON,"r", encoding="utf8")) #loads each OCRed publication
        #print(citationKey)
        count = 0 #counts the matches in each publication

        for pageNumber, pageText in data.items(): #loops through each page in the publication
            if re.search(r"\b%s\b" % searchString, pageText, flags=re.IGNORECASE): #checks if our searchphrase is matched on the page, ignore capitals
                if citationKey not in results: #checks if the citationKey is already in the results, if not:
                    results[citationKey] = {} #assigns the citationKey as key to our dictionary

                # relative path
                a = citationKey.lower() #creates a variable for the citationKey, using only lowercase letters
                relPath = os.path.join(a[:1], a[:2], citationKey, "pages", "%s.html" % pageNumber) #assigns the relative path to the html-page where the searchphrase is matched
                countM = len(re.findall(r"\b%s\b" % searchString, pageText, flags=re.IGNORECASE)) #counts the matches for the searchphrase on the page
                pageWithHighlights = re.sub(r"\b(%s)\b" % searchString, r"<span class='searchResult'>\1</span>", pageText, flags=re.IGNORECASE) #highlights the match on the page

                results[citationKey][pageNumber] = {} #creates a subdictionary with the pageNumber as key
                results[citationKey][pageNumber]["pathToPage"] = relPath #adds the relative path to the html-page into this subdictionary
                results[citationKey][pageNumber]["matches"] = countM #adds the relative path to the html-page into this subdictionary
                results[citationKey][pageNumber]["result"] = pageWithHighlights.replace("\n", "<br>") #adds the formatted page with the highlighted matches

                count  += 1 #increases the number for each publication

        if count > 0: #if there is at least one match in the publication
            print("\t", citationKey, " : ", count) #prints the citationKey of the publication and the number of matches in the publication
            newKey = "%09d::::%s" % (count, citationKey) #creates a  new key for each publication, which combines the number of matches and the citationKey
            results[newKey] = results.pop(citationKey) #replaces the citationKey in the dictionary with the new key

            # add time stamp
            currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #saves the current timestamp
            results["timestamp"] = currentTime #adds the timestamp
            # add search string (as submitted)
            results["searchString"] = searchString  #adds the searchphrase to the dictionary

    saveWith = re.sub("\W+", "", searchString) #removes nonletter characters and add the searchphrase
    saveTo = os.path.join(pathToMemex, "searches", "%s.searchResults" % saveWith) #creates a filepath and a filename
    with open(saveTo, 'w', encoding='utf8') as f9c:
        json.dump(results, f9c, sort_keys=True, indent=4, ensure_ascii=False) #creates a file that saves the dictionary with the results of our search and save it

###########################################################
# RUN THE MAIN CODE #######################################
###########################################################

#searchPhrase  = r"corpus\W*based"
#searchPhrase  = r"corpus\W*driven"
#searchPhrase  = r"multi\W*verse"
#searchPhrase  = r"text does ?n[o\W]t exist"
#searchPhrase  = r"corpus-?based"

searchOCRresults(settings["path_to_memex"], "Wolf") #start the function with this searchPhrase
exec(open("9_Interface_IndexPage.py").read()) #read it into the IndexPage