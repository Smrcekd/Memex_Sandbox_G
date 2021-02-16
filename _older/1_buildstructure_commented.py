import os, shutil, re
import yaml

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "MW.yaml" 
settings = yaml.safe_load(open(settingsFile)) #loads the yaml

memexPath = settings["memex_path"] # creates the path to memex folder

###########################################################
# FUNCTIONS ###############################################
###########################################################

# load bibTex Data into a dictionary
def loadBib(bibTexFile):
    # function loading data in the dictionary
    bibDic = {} #creates an empty dictionary

    with open(bibTexFile, "r", encoding="utf8") as f1: #opens bibTexFile for reading
        records = f1.read().split("\n@") #splits the records at end of the line and @

        for record in records[1:]: #creates a loop leaving out the first one
           
            if ".pdf" in record.lower(): #processes only pdfs and sets record them all on small letters
                completeRecord = "\n@" + record #completes records by adding end of the line and @ and record

                record = record.strip().split("\n")[:-1] #strips record of spaces and splits them at end of the line without }
              
                rType = record[0].split("{")[0].strip() #splits record at { and strips the first letter of spaces
                rCite = record[0].split("{")[1].strip().replace(",", "") #splits record at second { and strips of free spaces, replacing them for commas and quotation marks

                bibDic[rCite] = {} #creates a definition for dictionary
                bibDic[rCite]["rCite"] = rCite ##creates a definition for dictionary
                bibDic[rCite]["rType"] = rType # #creates a definition for dictionary
                bibDic[rCite]["complete"] = completeRecord #creates a definition for dictionary

                
                
                for r in record[1:]: #loops through r in record from the first one
                    if "=" in r: #contion if = is in r
                        key = r.split("=")[0].strip() #splits it at =, strips it of free spaces at first letter
                        val = r.split("=")[1].strip() #splits it at =, strips it of free spaces at second letter
                        val = re.sub("^\{|\},?", "", val) #regular expressions to unify

                        bibDic[rCite][key] = val ##creates a definition for dictionary

                        # fix the path to PDF
                        if key == "file": #creates a condition 
                            if ";" in val: # when there is ; in val
                                #print(val)
                                temp = val.split(";") #splits it at ;

                                for t in temp: #loops through t in temp
                                    if t.endswith(".pdf"): #condition if there is .pdf
                                        val = t #sets val to t

                                bibDic[rCite][key] = val ##creates a definition for dictionary

    print("="*80)
    print("NUMBER OF RECORDS IN BIBLIGORAPHY: %d" % len(bibDic))
    print("="*80)
    return(bibDic) #returns the dictionary


def generatePublPath(pathToMemex, bibTexCode): #creates a new function
    temp = bibTexCode.lower() #sets temp as BibTexCode and low letters
    directory = os.path.join(pathToMemex, temp[0], temp[:2], bibTexCode) #I dont know
    return(directory)#returns directory

# process a single bibliographical record: 1) create its unique path; 2) save a bib file; 3) save PDF file 
def processBibRecord(pathToMemex, bibRecDict): #function to process bib records
    tempPath = generatePublPath(pathToMemex, bibRecDict["rCite"]) #generates the path

    print("="*80)
    print("%s :: %s" % (bibRecDict["rCite"], tempPath))
    print("="*80)

    if not os.path.exists(tempPath): #condition if not the existing path
        os.makedirs(tempPath) #creates file

        bibFilePath = os.path.join(tempPath, "%s.bib" % bibRecDict["rCite"]) #adds a bib file for the record with path + .bib
        with open(bibFilePath, "w", encoding="utf8") as f9: #opens the bibFilePath for writing
            f9.write(bibRecDict["complete"])#writes it and completes

        pdfFileSRC = bibRecDict["file"]#escapes betterBibLatex

        pdfFileSRC = pdfFileSRC.replace("\\:" , ":") #replecaes the line with \\: or :

        pdfFileDST = os.path.join(tempPath, "%s.pdf" % bibRecDict["rCite"]) #adds pdf file into the folder with .pdf named rCite
        if not os.path.isfile(pdfFileDST): # this is to avoid copying that had been already copied.
            shutil.copyfile(pdfFileSRC, pdfFileDST)


###########################################################
# PROCESS ALL RECORDS #####################################
###########################################################

def processAllRecords(bibData): #defines a function covering all the data
    for k,v in bibData.items(): #loops throug k, v in the data
        processBibRecord(memexPath, v) #processes bib recrod by the memexPath and v

bibData = loadBib(settings["bib_all"]) #loads them according to bib_alll in settings
processAllRecords(bibData)

print("Done!")
