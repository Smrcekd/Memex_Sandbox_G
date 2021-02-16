import os, json, unicodedata #import those libraries

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions #import our functions page

###########################################################
# VARIABLES ###############################################
###########################################################

settings = functions.loadYmlSettings("settings.yml") #load our settings yaml file

###########################################################
# MINI TEMPLATES ##########################################
###########################################################

connectionsTemplate = """
<button class="collapsible">Similar Texts (<i>tf-idf</i> + cosine similarity)</button>
  <div class="content">
  <ul>
    <li>
    <b>Sim*</b>: <i>cosine similarity</i>; 1 is a complete match, 0 — nothing similar;
    cosine similarity is calculated using <i>tf-idf</i> values of top keywords.</li>
  </ul>
  </div>
<table id="publications" class="mainList">
<thead>
    <tr>
        <th>link</th>
        <th>Sim*</th>
        <th>Author(s), Year, Title, Pages</th>
    </tr>
</thead>
<tbody>
@CONNECTEDTEXTSTEMP@
</tbody>
</table>
"""
#This part defines the connections template
ocrTemplate = """
<button class="collapsible">OCREDTEXT</button>
<div class="content">
  <div class="bib">
  @OCREDCONTENTTEMP@
  </div>
</div>
"""
#This part defines the ocrTemplate
generalTemplate = """
<button class="collapsible">@ELEMENTHEADER@</button>
<div class="content">
@ELEMENTCONTENT@
</div>
"""
#This part defines the generalTemplate
###########################################################
# MINI FUNCTIONS ##########################################
###########################################################

import math
# a function for grouping pages into clusters of y number of pages
# x = number to round up; y = a multiple of the round-up-to number
def roundUp(x, y):
    result = int(math.ceil(x / y)) * y
    return(result)

# formats individual references to publications
def generateDoclLink(bibTexCode, pageVal, distance): #defines the function to format individual references
    pathToPubl = functions.generatePublPath(settings["path_to_memex"], bibTexCode) #takes the bibTex-Code
    bib = functions.loadBib(os.path.join(pathToPubl, "%s.bib" % bibTexCode)) #loads it
    bib = bib[bibTexCode] #defines a variable

    author = "N.d." #no information on the author as default
    if "editor" in bib: #if there is editor data
        author = bib["editor"] #add it
    if "author" in bib: #if there is author data 
        author = bib["author"] #add it
    date = "N.d." #no date as default
    if "date" in bib: #if there is date
        date = bib["date"] #add it
    reference = "%s (%s). <i>%s</i>" % (author, date, bib["title"]) #takes information about a publication and formats it
    search = unicodedata.normalize('NFKD', reference).encode('ascii','ignore') #replace diacritica with their ascii
    search = " <div class='hidden'>%s</div>" % search #repeats the information and hide it
    
    if pageVal == 0: # links to the start of the publication
        htmlLink = os.path.join(pathToPubl.replace(settings["path_to_memex"], "../../../../"), "pages", "DETAILS.html") #creates link to the details page
        htmlLink = "<a href='%s'><i>read</i></a>" % (htmlLink) #adds the link
        page = "" #defines the variable page
        startPage = 0 #defines the startPage as 0
    else:
        startPage = pageVal - 5 #defines the startPage
        endPage   = pageVal #defines the endPage
        if startPage == 0: #if the startPage is the details page
            startPage += 1 #adds one to SP
        htmlLink = os.path.join(pathToPubl.replace(settings["path_to_memex"], "../../../../"), "pages", "%04d.html" % startPage) #creates an html-link to it
        htmlLink = "<a href='%s'><i>read</i></a>" % (htmlLink) #adds the html-page
        page = ", pdfPp. %d-%d</i></a>" % (startPage, endPage) #add the pagecounter with startPage and endPage

    publicationInfo = reference + page + search #joins the variables together
    publicationInfo = publicationInfo.replace("{", "").replace("}", "") #removes the curly brackets
    singleItemTemplate = '<tr><td>%s</td><td>%f</td><td data-order="%s%05d">%s</td></tr>' % (htmlLink, distance, bibTexCode, startPage, publicationInfo) #creates a template for the indvidual item

    return(singleItemTemplate) #returns this variable

def generateReferenceSimple(bibTexCode): #takes the bibTexCode
    pathToPubl = functions.generatePublPath(settings["path_to_memex"], bibTexCode) #takes the bibTexCode
    bib = functions.loadBib(os.path.join(pathToPubl, "%s.bib" % bibTexCode)) #loads it
    bib = bib[bibTexCode] #defines a variable

    author = "N.d." #no author as default
    if "editor" in bib: #if editor
        author = bib["editor"] #add it
    if "author" in bib: #if author
        author = bib["author"] #add it
    date = "N.d." #no date as default
    if "date" in bib: #if date
        date = bib["date"] #add it
    reference = "%s (%s). <i>%s</i>" % (author, date, bib["title"]) #takes information about a publication and formats it
    reference = reference.replace("{", "").replace("}", "") #removes the curly brackets
    return(reference) #returns it

# convert json dictionary of connections into HTML format
def formatDistConnections(pathToMemex, distanceFile): #defines a function to convert dict connections into HTML
    print("Formatting distances data from `%s`..." % distanceFile) #prints the sentence and distanceFile
    distanceFile = os.path.join(pathToMemex, distanceFile) #takes the jsonFile with the cosine similarity
    distanceDict = json.load(open(distanceFile)) #loads this jsonFile
    
    formattedHTML = {} #creates an empty dictionary

    for doc1, doc1Dic in distanceDict.items(): #loops through the jsonFile
        formattedHTML[doc1] = [] #creates an empty list
        for doc2, distance in doc1Dic.items(): #loops through the cosine similarity-values
            doc2 = doc2.split("_") #takes the citeKey
            if len(doc2) == 1: #if the len in doc2 is 1
                tempVar = generateDoclLink(doc2[0], 0, distance) #creates a temporary variable
            else:
                tempVar = generateDoclLink(doc2[0], int(doc2[1]), distance) #otherwise creates a temporary variable with int(doc2[1])

            formattedHTML[doc1].append(tempVar) #adds the temporary variable
            #input(formattedHTML)
    print("\tdone!") #print the phrase
    return(formattedHTML) #returns formatted HTML

###########################################################
# MAIN FUNCTIONS ##########################################
###########################################################

publConnData = formatDistConnections(settings["path_to_memex"], settings["publ_cosDist"]) #defines the settings for the similarity between publications
pageConnData = formatDistConnections(settings["path_to_memex"], settings["page_cosDist"]) #defines the settings for the similarity between pages

# generate interface for the publication and pages
def generatePublicationInterface(citeKey, pathToBibFile): #defines function to generate public interface
    print("="*80) #prints = 80x
    print(citeKey) #prints cite key of the publications

    jsonFile = pathToBibFile.replace(".bib", ".json") #takes the bibFile
    with open(jsonFile, "r", encoding ="utf8") as jsonData:
        ocred = json.load(jsonData) #loads the bibFile
        pNums = ocred.keys() #takes the ocred citation keys
        pageDic = functions.generatePageLinks(pNums) #loads the function which generates links to all pages in a publication

        # load page template
        with open(settings["template_page"], "r", encoding="utf8") as ft:
            template = ft.read() #loads the page template
            
        # load individual bib record
        bibFile = pathToBibFile #takes the pathToBibFile
        bibDic = functions.loadBib(bibFile) #loads the loadBib-function which loads the bibTex data into a dictionary
        bibForHTML = functions.prettifyBib(bibDic[citeKey]["complete"]) #loads the prettifyBib-function to make the bib record more readable

        orderedPages = list(pageDic.keys()) #creates a list of keys to receive all page numbers

        for o in range(0, len(orderedPages)): #loops through the pages
            #print(o)
            k = orderedPages[o]  #takes the number of the page as key
            #input(k)
            v = pageDic[orderedPages[o]] #takes the links to the other pages as value

            pageTemp = template #assigns the page template to a temporary variable
            pageTemp = pageTemp.replace("@PAGELINKS@", v) #replaces the Pagelinks item with the links to the other pages
            pageTemp = pageTemp.replace("@PATHTOFILE@", "") #replaces the Pathtofile item with a blank
            pageTemp = pageTemp.replace("@CITATIONKEY@", citeKey) #replaces the Citationkey item with the citation key

            emptyResults = '<tr><td><i>%s</i></td><td><i>%s</i></td><td><i>%s</i></td></tr>' #creates a template for the similarity values

            if k != "DETAILS": #if the page is not the details page
                mainElement = '<img src="@PAGEFILE@" width="100%" alt="">'.replace("@PAGEFILE@", "%s.png" % k) #takes the .png of the OCRed text of this page

                pageKey = citeKey+"_%05d" % roundUp(int(k), 5) #takes the citationKey and the pageNumbers
                #print(pageKey)
                if pageKey in pageConnData: #checks if there are any similar pageclusters
                    formattedResults = "\n".join(pageConnData[pageKey]) #adds the similar pageclusters
                    #input(formattedResults)
                else:
                    formattedResults = emptyResults % ("no data", "no data", "no data") #adds the info about no similar pageclusters

                mainElement += connectionsTemplate.replace("@CONNECTEDTEXTSTEMP@", formattedResults) #replaces the wildcard in the template with the actual values for simliar texts
                mainElement += ocrTemplate.replace("@OCREDCONTENTTEMP@", ocred[k].replace("\n", "<br>")) #replaces the wildcard in the template with the OCRed text of the page
                pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement) #repaces the wildcard with the added actual values
            else: #if the page is the details page
                reference = generateReferenceSimple(citeKey) #takes the information about the publication we've generated
                mainElement = "<h3>%s</h3>\n\n" % reference #adds it as a header

                bibElement = '<div class="bib">%s</div>' % bibForHTML.replace("\n", "<br> ") #takes the bibliogaphical data
                bibElement = generalTemplate.replace("@ELEMENTCONTENT@", bibElement) #replaces the wildcard in the general template with the bibliographical data
                bibElement = bibElement.replace("@ELEMENTHEADER@", "BibTeX Bibliographical Record") #adds a meaningful description
                mainElement += bibElement + "\n\n" #adds a new line

                wordCloud = '\n<img src="../' + citeKey + '_wCloud.jpg" width="100%" alt="wordcloud">'  #takes the generated WordCloud
                wordCloud = generalTemplate.replace("@ELEMENTCONTENT@", wordCloud) #replaces the wildcard in the general template with the Word Cloud
                wordCloud = wordCloud.replace("@ELEMENTHEADER@", "WordCloud of Keywords (<i>tf-idf</i>)") #adds thos description
                mainElement += wordCloud + "\n\n" #new line

                if citeKey in publConnData: #checks if there are any similar texts
                    formattedResults = "\n".join(publConnData[citeKey]) #add the similar texts
                    #input(formattedResults)
                else:
                    formattedResults = emptyResults % ("no data", "no data", "no data") #otherwise, adds that there are no similar texts

                mainElement += connectionsTemplate.replace("@CONNECTEDTEXTSTEMP@", formattedResults) #replaces the wildcard in the template with the existing information about similar texts


                pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement) #replaces the wildcard in the pagetemplate with the added content

            # @NEXTPAGEHTML@ and @PREVIOUSPAGEHTML@
            if k == "DETAILS": #if the page is the Details page
                nextPage = "0001.html" #the next page is the first one
                prevPage = "" #previous is not-existing
            elif k == "0001": #if the page is the first page of the record
                nextPage = "0002.html" #next page is the second one
                prevPage = "DETAILS.html" #previous is the Details page
            elif o == len(orderedPages)-1: #if the page is the last page of the record
                nextPage = "" #next page is non-existant
                prevPage = orderedPages[o-1] + ".html" #previous page is the one_before_last
            else:
                nextPage = orderedPages[o+1] + ".html" #the next page is the page behind in the record
                prevPage = orderedPages[o-1] + ".html" #the previous page is the page before in the record

            pageTemp = pageTemp.replace("@NEXTPAGEHTML@", nextPage) #replaces the wildcard with a link to the page assigned
            pageTemp = pageTemp.replace("@PREVIOUSPAGEHTML@", prevPage) #replaces the Previouspagehtml with a link to the page assigned

            pagePath = os.path.join(pathToBibFile.replace(citeKey+".bib", ""), "pages", "%s.html" % k) #creates a filepath to each page in the pages-folder of each publication
            with open(pagePath, "w", encoding="utf8") as f9:
                f9.write(pageTemp) #creates and saves each page in pages folder

###########################################################
# FUNCTIONS TESTING #######################################
###########################################################

functions.memexStatusUpdates(settings["path_to_memex"], ".html") #executes the memexStatusUpdates-function
def processAllRecords(pathToMemex): #defines the process all records function
    files = functions.dicOfRelevantFiles(pathToMemex, ".bib") #takes the bibFiles
    for citeKey, pathToBibFile in files.items(): #loops through them
        if os.path.exists(pathToBibFile.replace(".bib", ".json")): #search for the files with .bib and .json extentions
            generatePublicationInterface(citeKey, pathToBibFile) #starts the function

processAllRecords(settings["path_to_memex"]) #processes all records into the "path_to_memex"
exec(open("9_Interface_IndexPage.py").read())