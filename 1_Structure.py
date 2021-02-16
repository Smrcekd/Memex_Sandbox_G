import os, shutil, re
import yaml #Import relevant addons

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "./settings.yml" #settingsfile is "settings.yml"
settings = yaml.safe_load(open(settingsFile)) #loads the settingsFile

memexPath = settings["path_to_memex"] #sets MemexPath on "Path_to_memex"

###########################################################
# FUNCTIONS ###############################################
###########################################################

# load bibTex Data into a dictionary
def loadBib(bibTexFile): #creates function

    bibDic = {} #creates empty dictionary

    with open(bibTexFile, "r", encoding="utf8") as f1: #opens bibFile
        records = f1.read().split("\n@") #splits into records

        for record in records[1:]: #loops through all of them
            # let process ONLY those records that have PDFs
            if ".pdf" in record.lower():
                completeRecord = "\n@" + record #new line and @ at the beginning

                record = record.strip().split("\n")[:-1] #splits at the new line, deletes the last empty element

                rType = record[0].split("{")[0].strip() #first element record type
                rCite = record[0].split("{")[1].strip().replace(",", "") #second element citekey

                bibDic[rCite] = {} #creates an empty dict at the key citekey
                bibDic[rCite]["rCite"] = rCite #adds the citekey of the record at the key "citekey"
                bibDic[rCite]["rType"] = rType #adds the recordtype as value at the key "recordtype" 
                bibDic[rCite]["complete"] = completeRecord #adds the complete record at the citekey complete
                 # we have a single-record dictionary for each record
                for r in record[1:]: #loops through the rest of single record
                    key = r.split("=")[0].strip() #get the key of each key-value-pair of the single record
                    val = r.split("=")[1].strip() #get the value of each key-value-pair of the single record
                    val = re.sub("^\{|\},?", "", val) #get rid of the potentially flawing characters

                    bibDic[rCite][key] = val #connects the key-value-pairs

                    # fix the path to PDF
                    if key == "file": # looks for the file-key in the record
                        if ";" in val: #check if there is one or two paths
                            #print(val)
                            temp = val.split(";") #creates a new variable with the both paths, splits at ;

                            for t in temp: #loops through temp
                                if t.endswith(".pdf"): #check if one path ends with a .pdf-extension
                                    val = t #assign that path to the value for the key "file"

                            bibDic[rCite][key] = val #connect the key-value-pairs

    print("="*80) #print 80 equal signs
    print("NUMBER OF RECORDS IN BIBLIGORAPHY: %d" % len(bibDic)) #print the number of records in my dictioanry
    print("="*80)#print 80 equal signs 
    return(bibDic) #returns the dictionary

# generate path from bibtex code, and create a folder, if does not exist;
# if the code is `SavantMuslims2017`, the path will be pathToMemex+`/s/sa/SavantMuslims2017/`
def generatePublPath(pathToMemex, bibTexCode): #defines a function with the needed parameters
    temp = bibTexCode.lower() #create a temporary variable for your bibTexCode, which is your citation key
    directory = os.path.join(pathToMemex, temp[0], temp[:2], bibTexCode) #generates a unique path
    return(directory) #returns it

# process a single bibliographical record: 1) create its unique path; 2) save a bib file; 3) save PDF file 
def processBibRecord(pathToMemex, bibRecDict): #defines a function and the necessary parameters
    tempPath = generatePublPath(pathToMemex, bibRecDict["rCite"]) #generate a unique path

    print("="*80) #prints equal sign 80x
    print("%s :: %s" % (bibRecDict["rCite"], tempPath)) #prints the unique path
    print("="*80) #prints equal sign 80x

    if not os.path.exists(tempPath): #checks if the path exists
        os.makedirs(tempPath) #creates it, if it doesn't

        bibFilePath = os.path.join(tempPath, "%s.bib" % bibRecDict["rCite"]) #creates a path for the bibliographical record
        with open(bibFilePath, "w", encoding="utf8") as f9: #creates a bibfile with the bibliographical record
            f9.write(bibRecDict["complete"]) #inserts the complete bibliographical record
        
        pdfFileSRC = bibRecDict["file"]         #creates a variable for the path to the pdf-File

        #betterbibtex escaped : amd \, this replaces \: with : 
        pdfFileSRC = pdfFileSRC.replace("\\:", ":") #deletes the and : backslashes

        pdfFileDST = os.path.join(tempPath, "%s.pdf" % bibRecDict["rCite"]) #create a unique path for the pdf-File
        if not os.path.isfile(pdfFileDST): # this is to avoid copying that had been already copied.
            shutil.copyfile(pdfFileSRC, pdfFileDST) #copies the file from the old destination to the new one


###########################################################
# PROCESS ALL RECORDS #####################################
###########################################################

def processAllRecords(bibData): #function to process all the bibliographical records
    for k,v in bibData.items(): #for each record
        processBibRecord(memexPath, v) #process each with our generated function

bibData = loadBib(settings["bib_all"])  #data from all bibliographical records
processAllRecords(bibData) #processes the data

print("Done!") #prints "done"