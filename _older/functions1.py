# program to import functions
# code reuse ; has to be in folder with other scripts
#############################
# STORING FUNCTIONS #########
#############################

import os
import PyPDF2
import functions
import yaml 
import re
import shutil
# generate path from bibtex code:
def generatePublPath(pathToMemex, bibTexCode):
    temp = bibTexCode.lower()
    directory = os.path.join(pathToMemex, temp[0], temp[:2], bibTexCode)
    return(directory)


# progarm to create a dictionary
def loadBib(bibTexFile):

    bibDic = {}
    recordsNeedFixing = []

    with open("MyLibrary2.bib", "r", encoding="utf8") as f1:
        records = f1.read().split("\n@")

        for record in records[1:]:
            # let process ONLY those records that have PDFs
            if ".pdf" in record.lower():
                completeRecord = "\n@" + record

                record = record.strip().split("\n")[:-1]

                rType = record[0].split("{")[0].strip()
                rCite = record[0].split("{")[1].strip().replace(",", "")

                bibDic[rCite] = {}
                bibDic[rCite]["rCite"] = rCite
                bibDic[rCite]["rType"] = rType
                bibDic[rCite]["complete"] = completeRecord

                for r in record[1:]:
                    key = r.split("=")[0].strip()
                    val = r.split("=")[1].strip()
                    val = re.sub("^\{|\},?", "", val)

                    bibDic[rCite][key] = val

                    # fix the path to PDF
                    if key == "file":
                        if ";" in val:
                            #print(val)
                            temp = val.split(";")

                            for t in temp:
                                if ".pdf" in t:
                                    val = t

                            bibDic[rCite][key] = val

    print("="*80)
    print("NUMBER OF RECORDS IN BIBLIGORAPHY: %d" % len(bibDic))
    print("="*80)
    return(bibDic)

# function to generate page links
def generatePageLinks(pNumList):
    listMod = ["DETAILS"]
    listMod.extend(pNumList)

    toc = []
    for l in listMod:
        toc.append('<a href="%s.html">%s</a>' % (l, l))
    toc = " ".join(toc)

    pageDic = {}
    for l in listMod:
        pageDic[l] = toc.replace('>%s<' % l, ' style="color: red;">%s<' % l)

    return(pageDic)

# html friendly BIB; makes bib record more readable 
def prettifyBib(bibText):
    bibText = bibText.replace("{{", "").replace("}}", "")
    bibText = re.sub(r"\n\s+file = [^\n]+", "", bibText)
    bibText = re.sub(r"\n\s+abstract = [^\n]+", "", bibText)
    return(bibText)

# dictionary of citation keys; paths to specific files
def dicOfRelevantFiles(pathToMemex, extension):

    dic = {}
    for subdir, dirs, files in os.walk(pathToMemex):
        for file in files:
            # process publication tf data
            if file.endswith(extension):
                key = file.replace(extension, "")
                value = os.path.join(subdir, file)
                dic[key] = value
    return(dic)

## function for bibrecord

def processBibRecord(pathToMemex, bibRecDict):
    tempPath = generatePublPath(pathToMemex, bibRecDict["rCite"])

    print("="*80)
    print("%s :: %s" % (bibRecDict["rCite"], tempPath))
    print("="*80)

    if not os.path.exists(tempPath):
        os.makedirs(tempPath)

        bibFilePath = os.path.join(tempPath, "%s.bib" % bibRecDict["rCite"])
        with open(bibFilePath, "w", encoding="utf8") as f9:
            f9.write(bibRecDict["complete"])

        pdfFileSRC = bibRecDict["file"]

        #betterbibtex escaped: , this line replaces "\:" with ":"
        pdfFileSRC = pdfFileSRC.replace("\\:", ":")
        pdfFileDST = os.path.join(tempPath, "%s.pdf" % bibRecDict["rCite"])
        if not os.path.isfile(pdfFileDST): # this is to avoid copying that had been already copied.
            shutil.copyfile(pdfFileSRC, pdfFileDST)
        return(bibFilePath)

    # load settings from our YML-like file
# - the format of our YML is more relaxed than that of the
#   original YML (YML does not support comments)
def loadYmlSettings(ymlFile):
    with open(ymlFile, "r", encoding="utf8") as f1:
        data = f1.read()
        data = re.sub(r"#.*", "", data) # remove comments
        data = re.sub(r"\n+", "\n", data) # remove extra linebreaks used for readability
        data = re.split(r"\n(?=\w)", data) # splitting
        dic = {}
        for d in data:
            if ":" in d:
                d = re.sub(r"\s+", " ", d.strip())
                d = re.split(r"^([^:]+) *:", d)[1:]
                key = d[0].strip()
                value = d[1].strip()
                dic[key] = value
    #input(dic)
    return(dic)

###########################################################
# INTERFACE-RELATED FUNCTIONS #############################
###########################################################

# HTML: generates TOCs for each page; the current page is highlighted with red
def generatePageLinks(pNumList):
    listMod = ["DETAILS"]
    listMod.extend(pNumList)

    toc = []
    for l in listMod:
        toc.append('<a href="%s.html">%s</a>' % (l, l))
    toc = " ".join(toc)

    pageDic = {}
    for l in listMod:
        pageDic[l] = toc.replace('>%s<' % l, ' style="color: red;">%s<' % l)

    return(pageDic)

# HTML: makes BIB more HTML friendly
def prettifyBib(bibText):
    bibText = bibText.replace("{{", "").replace("}}", "")
    bibText = re.sub(r"\n\s+file = [^\n]+", "", bibText)
    bibText = re.sub(r"\n\s+abstract = [^\n]+", "", bibText)
    return(bibText)

###########################################################
############## STEP 4 FUNCTIONS ###########################
###########################################################

def filterDic(dic, thold):
    retDic = {}    #empty Dictonary to copy filterd values into
    for k,v in dic.items():     #loop through outer first dic, containig the titles
        retDic[k]={}            #create a subDic for each title
        for key,val in v.items():   #loop through the entries of each title
            if val > thold:         #check threshold
                if val < 0.97:        #check to not match the publication with itself
                    retDic[k][key] = val    #add value
    return(retDic)
