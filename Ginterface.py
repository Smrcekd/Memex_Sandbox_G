# generate interface for the publication
#import libraries
import os, json
import pdf2image, pytesseract
import functions1 
import yaml
import remove_comments

### variables
settingsFile = ".\MW.yaml"
settings = yaml.safe_load(open(settingsFile))
memexPath = settings["memex_path"]
print(settings) 
# generate interface for the publication
def generatePublicationInterface(citeKey, pathToBibFile): # function takes citation key and to bibfile as arguments 
    print("="*80)
    print(citeKey)

    #pathToBibFile = functions.dicOfRelevantFiles(memexPath, ".bib")
    #for v in pathToBibFile.items():
    #    jsonFile = v.replace(".bib", ".json")
    #return jsonFile

    print(pathToBibFile)


    jsonFile = pathToBibFile.replace(".bib", ".json")

    with open(jsonFile, encoding="utf8") as jsonData: #encodes it properly
        ocred = json.load(jsonData)
        pNums = ocred.keys()

        pageDic = functions1.generatePageLinks(pNums) #creates the links and navigation

        # load page template
        with open(settings["template_page"], "r", encoding="utf8") as ft:
            template = ft.read()

        # load individual bib record
        bibFile = pathToBibFile
        bibDic = functions1.loadBib(bibFile) #loads bibfile
        bibForHTML = functions1.prettifyBib(bibDic[citeKey]["complete"]) #prettifies bib file for this view

        orderedPages = list(pageDic.keys()) #creates list of all the keys and pagenumbers from page dic

        for o in range(0, len(orderedPages)): #loop that creates every page
          
            k = orderedPages[o]
            v = pageDic[orderedPages[o]]

            pageTemp = template # take a template
            pageTemp = pageTemp.replace("@PAGELINKS@", v) #replaces values in template
            pageTemp = pageTemp.replace("@PATHTOFILE@", "")
            pageTemp = pageTemp.replace("@CITATIONKEY@", citeKey)

            if k != "DETAILS": #one page is different from the others; this is for the regular pages
                mainElement = '<img src="@PAGEFILE@" width="100%" alt="">'.replace("@PAGEFILE@", "%s.png" % k)
                pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement)
                pageTemp = pageTemp.replace("@OCREDCONTENT@", ocred[k].replace("\n", "<br>"))
            else: # if page is details.html
                mainElement = bibForHTML.replace("\n", "<br> ")
                mainElement = '<div class="bib">%s</div>' % mainElement #class for changes in style sheet
                mainElement += '\n<img src="wordcloud.jpg" width="100%" alt="wordcloud">' #wordcloud to be generated later
                pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement)
                pageTemp = pageTemp.replace("@OCREDCONTENT@", "")

            # @NEXTPAGEHTML@ and @PREVIOUSPAGEHTML@ #links to next and previous page; and when on the last it stops
            if k == "DETAILS":
                nextPage = "0001.html"
                prevPage = ""
            elif k == "0001":
                nextPage = "0002.html"
                prevPage = "DETAILS.html"
            elif o == len(orderedPages)-1:
                nextPage = ""
                prevPage = orderedPages[o-1] + ".html"
            else:
                nextPage = orderedPages[o+1] + ".html"
                prevPage = orderedPages[o-1] + ".html"

            pageTemp = pageTemp.replace("@NEXTPAGEHTML@", nextPage) # find replace in template
            pageTemp = pageTemp.replace("@PREVIOUSPAGEHTML@", prevPage)

            pagePath = os.path.join(pathToBibFile.replace(citeKey+".bib", ""), "pages", "%s.html" % k) #saves the actual page
            with open(pagePath, "w", encoding="utf8") as f9:
                f9.write(pageTemp)

# generate the INDEX and the CONTENTS pages
def generateMemexStartingPages(pathToMemex):
    # load index template
    with open(settings["template_index"], "r", encoding="utf8") as ft:
        template = ft.read()

    # add index.html
    with open(settings["content_index"], "r", encoding="utf8") as fi:
        indexData = fi.read()
        with open(os.path.join(pathToMemex, "index.html"), "w", encoding="utf8") as f9:
            f9.write(template.replace("@MAINCONTENT@", indexData))

    # load bibliographical data for processing
    publicationDic = {} # key = citationKey; value = recordDic

    for subdir, dirs, files in os.walk(pathToMemex):
        for file in files:
            if file.endswith(".bib"):
                pathWhereBibIs = os.path.join(subdir, file)
                tempDic = functions1.loadBib(pathWhereBibIs)
                publicationDic.update(tempDic)

    # generate data for the main CONTENTS
    singleItemTemplate = '<li><a href="@RELATIVEPATH@/pages/DETAILS.html">[@CITATIONKEY@]</a> @AUTHOROREDITOR@ (@DATE@) - <i>@TITLE@</i></li>'
    contentsList = []

    for citeKey,bibRecord in publicationDic.items():
        relativePath = functions1.generatePublPath(pathToMemex, citeKey).replace(pathToMemex, "")

        authorOrEditor = "[No data]"
        if "editor" in bibRecord:
            authorOrEditor = bibRecord["editor"]
        if "author" in bibRecord:
            authorOrEditor = bibRecord["author"]

        #date = bibRecord["date"][:4]
        if "date" in bibRecord:
            date = bibRecord["date"]
        else:
            date = "no date"
            print("nodate")


        title = bibRecord["title"]

        # forming a record
        recordToAdd = singleItemTemplate
        recordToAdd = recordToAdd.replace("@RELATIVEPATH@", relativePath)
        recordToAdd = recordToAdd.replace("@CITATIONKEY@", citeKey)
        recordToAdd = recordToAdd.replace("@AUTHOROREDITOR@", authorOrEditor)
        recordToAdd = recordToAdd.replace("@DATE@", date)
        recordToAdd = recordToAdd.replace("@TITLE@", title)

        recordToAdd = recordToAdd.replace("{", "").replace("}", "")

        contentsList.append(recordToAdd)

    contents = "\n<ul>\n%s\n</ul>" % "\n".join(sorted(contentsList))
    mainContent = "<h1>CONTENTS of MEMEX</h1>\n\n" + contents

    # save the CONTENTS page
    with open(os.path.join(pathToMemex, "contents.html"), "w", encoding="utf8") as f9:
        f9.write(template.replace("@MAINCONTENT@", mainContent))

###########################################################
# FUNCTIONS TESTING #######################################
###########################################################

#generatePublicationInterface("AshkenaziHoly2014", "./_memex_sandbox/_data/a/as/AshkenaziHoly2014/AshkenaziHoly2014.bib")

###########################################################
# PROCESS ALL RECORDS: ANOTHER APPROACH ###################
###########################################################


def processAllRecords(pathToMemex):
    files = functions1.dicOfRelevantFiles(pathToMemex, ".bib")
    for citeKey, pathToBibFile in files.items():
        #print(citeKey)
        generatePublicationInterface(citeKey, pathToBibFile)
    generateMemexStartingPages(pathToMemex)

processAllRecords(settings["memex_path"])

#processAll(memexPath)