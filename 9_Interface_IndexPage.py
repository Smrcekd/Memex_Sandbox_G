import os, json
import unicodedata #imports those libraries

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions #imports our functions

###########################################################
# VARIABLES ###############################################
###########################################################

settings = functions.loadYmlSettings("settings.yml") #loads our settings yaml file

###########################################################
# MINI TEMPLATES ##########################################
###########################################################

generalTemplate = """
<button class="collapsible">@ELEMENTHEADER@</button>
<div class="content">
@ELEMENTCONTENT@
</div>
"""
# defines general template
searchesTemplate = """
<button class="collapsible">SAVED SEARCHES</button>
<div class="content">
<table id="" class="display" width="100%">
<thead>
    <tr>
        <th><i>link</i></th>
        <th>search string</th>
        <th># of publications with matches</th>
        <th>time stamp</th>
    </tr>
</thead>
<tbody>
@TABLECONTENTS@
</tbody>
</table>
</div>
"""
#defines the searchesTemplate for the searches on our index page
publicationsTemplate = """
<button class="collapsible">PUBLICATIONS INCLUDED INTO MEMEX</button>
<div class="content">
<table id="" class="display" width="100%">
<thead>
    <tr>
        <th><i>link</i></th>
        <th>citeKey, author, date, title</th>
    </tr>
</thead>
<tbody>
@TABLECONTENTS@
</tbody>
</table>
</div>
"""
#defines the publicationsTemplate for the publications on our index page
###########################################################
# MINI FUNCTIONS ##########################################
###########################################################

# generate search pages and TOC
def formatSearches(pathToMemex): #defines function to format the searches
    with open(settings["template_search"], "r", encoding="utf8") as f1: #opens from "teplate_search"
        indexTmpl = f1.read() #opens the searchTemplate
    dof = functions.dicOfRelevantFiles(pathToMemex, ".searchResults") #chooses the files with the search results
    # format individual search pages
    toc = [] #creates an empty list
    for file, pathToFile in dof.items(): #loops through all the files with searches
        searchResults = [] #creates an empty list
        data = json.load(open(pathToFile, "r", encoding="utf8")) #loads the files with the search results
        # collect toc
        template = "<tr> <td>%s</td> <td>%s</td> <td>%s</td> <td>%s</td></tr>" #creates the format of the table

        # variables
        linkToSearch = os.path.join("searches", file+".html") #adds the link to searches with .html
        pathToPage = '<a href="%s"><i>read</i></a>' % linkToSearch #creates the link in the table to the html-file with our search results
        searchString = '<div class="searchString">%s</div>' % data.pop("searchString") #take the searchstring from the files with our search results 
        timeStamp = data.pop("timestamp") #takes the timestamp
        tocItem = template % (pathToPage, searchString, len(data), timeStamp) #adds the variables to the template
        toc.append(tocItem) #adds the template to the table of contents

        # generate the results page
        keys = sorted(data.keys(), reverse=True) #sorts the citation keys with the number of pages, results in reverse order
        for k in keys: #loops through citation keys
            searchResSingle = [] #create an empty list
            results = data[k] #creates an empty list
            temp = k.split("::::") #splits the citation keys and the number of pages with results
            header = "%s (pages with results: %d)" % (temp[1], int(temp[0])) #creates a header for each publication with citation key and the number of pages with results
            #print(header)
            for page, excerpt in results.items(): #loops through the results
                #print(excerpt["result"])
                pdfPage = int(page) #takes the page with the searchstring
                linkToPage = '<a href="../%s"><i>go to the original page...</i></a>' % excerpt["pathToPage"] #adds a link to the original page with the search result
                searchResSingle.append("<li><b><hr>(pdfPage: %d)</b><hr> %s <hr> %s </li>" % (pdfPage, excerpt["result"], linkToPage)) #adds the text and the link to the list
            searchResSingle = "<ul>\n%s\n</ul>" % "\n".join(searchResSingle) #joins the single pages together
            searchResSingle = generalTemplate.replace("@ELEMENTHEADER@", header).replace("@ELEMENTCONTENT@", searchResSingle) #replaces the wildcards in the headers
            searchResults.append(searchResSingle) #appends the results of the search
        
        searchResults = "<h2>SEARCH RESULTS FOR: <i>%s</i></h2>\n\n" % searchString + "\n\n".join(searchResults) #creates a header for the html-page and join the search results
        with open(pathToFile.replace(".searchResults", ".html"), "w", encoding="utf8") as f9:
            f9.write(indexTmpl.replace("@MAINCONTENT@", searchResults)) #creates the html-page
        #os.remove(pathToFile)
        
    #input("\n".join(toc))
    toc = searchesTemplate.replace("@TABLECONTENTS@", "\n".join(toc)) #replaces the wildcard in the table of contents
    return(toc) #returns it


def formatPublList(pathToMemex): #defines a function for the formatting of the publications
    ocrFiles = functions.dicOfRelevantFiles(pathToMemex, settings["ocr_results"]) #takes the files with the OCRed pages
    bibFiles = functions.dicOfRelevantFiles(pathToMemex, ".bib") #takes the bibFiles

    contentsList = [] #creates an empty list

    for key, value in ocrFiles.items(): #loops through the OCRed pages
        if key in bibFiles: #searches for the key in the bibFile
            bibRecord = functions.loadBib(bibFiles[key]) #loads the bibliographical data for this item
            bibRecord = bibRecord[key] #takes the key

            relativePath = functions.generatePublPath(pathToMemex, key).replace(pathToMemex, "") #takes the relative path to the publication

            authorOrEditor = "[No data]" #takes "no data" as default setting
            if "editor" in bibRecord: #checks if there is information about the editor
                authorOrEditor = bibRecord["editor"] #adds it
            if "author" in bibRecord: #checks for info on "author"
                authorOrEditor = bibRecord["author"] #adds it

            date = "[No data]" #"No data" as default
            if "date" in bibRecord: #if there is date
                date = bibRecord["date"][:4] #adds the date
            title = bibRecord["title"] #inserts the title

            # formatting template
            citeKey = '<div class="ID">[%s]</div>' % key #takes the citeKey
            publication = '%s (%s) <i>%s</i>' % (authorOrEditor, date, title) #takes the information about the publication and format it
            search = unicodedata.normalize('NFKD', publication).encode('ascii','ignore') #replaces diacritical characters with their ascii equivalents
            publication += " <div class='hidden'>%s</div>" % search #repeats the information and hide it
            link = '<a href="%s/pages/DETAILS.html"><i>read</i></a>' % relativePath #adds the link to the details page of each publication

            singleItemTemplate = '<tr><td>%s</td><td>%s %s</td></tr>' % (link, citeKey, publication) #collects the information in a single template
            recordToAdd = singleItemTemplate.replace("{", "").replace("}", "") #removes curly brackets

            contentsList.append(recordToAdd) #adds the single records to the content list

    contents = "\n".join(sorted(contentsList)) #joins the sorted content list
    final = publicationsTemplate.replace("@TABLECONTENTS@", contents) #replace the Wildcards in the template with the actual content
    return(final) #returns it

###########################################################
# MAIN FUNCTIONS ##########################################
###########################################################

# generate index pages: index with stats; search results pages
def generateIngexInterface(pathToMemex):
    print("\tgenerating main index page...") #print the phrase
    # generate the main index page with stats
    with open(settings["template_index"], "r", encoding="utf8") as f1:
        indexTmpl = f1.read() #opens the index page template
    with open(settings["content_index"], "r", encoding="utf8") as f1:
        indexCont = f1.read() #opens the index content page

    # - PREAMBLE
    mainElement   = indexCont + "\n\n" #adds the index content
    # - SEARCHES
    mainElement += formatSearches(pathToMemex) #adds the searches table
    # - PUBLICATION LIST
    mainElement += formatPublList(pathToMemex) #adds the publication table

    # - FINALIZING INDEX PAGE
    indexPage     = indexTmpl #takes the index page template
    indexPage     = indexPage.replace("@MAINCONTENT@", mainElement) #replaces the index page wildcard wth the main element - content

    pathToIndex   = os.path.join(pathToMemex, "index.html") #takes the html-page as a file
    with open(pathToIndex, "w", encoding="utf8") as f9:
        f9.write(indexPage) #creates an html-file and save into the memex_sandbox file
###########################################################
# FUNCTIONS TESTING #######################################
###########################################################

generateIngexInterface(settings["path_to_memex"]) #starts the function