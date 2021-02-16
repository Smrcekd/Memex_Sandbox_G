# NEW LIBRARIES
import pdf2image    # extracts images from PDF
import pytesseract  # interacts with Tesseract, which extracts text from images

import os, yaml, json, random

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions

###########################################################
# VARIABLES ###############################################
###########################################################

settings = functions.loadYmlSettings("settings.yml") #defines and loads our settings yaml file

###########################################################
# MAIN FUNCTIONS ##########################################
###########################################################

# function OCR a PDF, saving each page as an image and
# saving OCR results into a JSON file
def ocrPublication(citationKey, language, pageLimit): #defines a function
    # generate and create necessary paths
    publPath = functions.generatePublPath(settings["path_to_memex"], citationKey) #generates the path to our PDF file
    pdfFile  = os.path.join(publPath, citationKey + ".pdf") #creates the path to the PDF file
    jsonFile = os.path.join(publPath, citationKey + ".json") # OCR results will be saved here
    saveToPath = os.path.join(publPath, "pages") # we will save processed images here

    # first we need to check whether this publication has been already processed
    if not os.path.isfile(jsonFile): #if the is no jsonFile
        # let's make sure that saveToPath also exists
        if not os.path.exists(saveToPath): #if there is no saveToPath
            os.makedirs(saveToPath) #creates saveToPath
        
        # start process images and extract text
        print("\t>>> OCR-ing: %s" % citationKey)#prints the sentence and citationkey

        textResults = {}#creates an empty dictionary
        images = pdf2image.convert_from_path(pdfFile) #iterates through the oages
        pageTotal = len(images)#counts the lenghts
        pageCount = 1#starts the count at 1
        if pageTotal <= int(pageLimit): #loops through the images
            for image in images: #for every image
                text = pytesseract.image_to_string(image, lang=language) #extracts the text from your images
                textResults["%04d" % pageCount] = text #saves the text into your dictionary

                image = image.convert('1') # binarizes image, reducing its size
                finalPath = os.path.join(saveToPath, "%04d.png" % pageCount) #reduces the size by binarizing the image
                image.save(finalPath, optimize=True, quality=10) #creates the path for your OCRed pages

                print("\t\t%04d/%04d pages" % (pageCount, pageTotal)) #prints the progress of the OCRing process
                pageCount += 1 #keeps the count of the pages

            with open(jsonFile, 'w', encoding='utf8') as f9: #creates a jsonFile for your OCRed text
                json.dump(textResults, f9, sort_keys=True, indent=4, ensure_ascii=False)  #puts the OCRed text into the jsonFile 
        #else:
            #print("\t%d: the length of the publication exceeds current limit (%d)" % (pageTotal, pageLimit))
            #print("\tIncrease `page_limit` in settings to process this publication.")
    
    else: # in case JSON file already exists
        print("\t>>> %s has already been OCR-ed..." % citationKey) #shows that yozu have already created a jsonFile for that record

#def identifyLanguage(bibRecDict, fallBackLanguage): #defines a function sorting the language of the record
 #   if "langid" in bibRecDict: #checks if there is a language key   
  #      try:
   #         language = langKeys[bibRecDict["langid"]] #tries to match the language ID with the tesseract language settings
    #        message = "\t>> Language has been successfuly identified: %s" % language #prints a message with the language name if the ID has been successfully matched
     #   except:
      #      message = "\t>> Language ID `%s` cannot be understood by Tesseract; fix it and retry\n" % bibRecDict["langid"] #tells you that the ID could not be matched with the Tesseract language settings
       #     message += "\t>> For now, trying `%s`..." % fallBackLanguage #uses the default language
        #    language = fallBackLanguage #assigns the default language as language of that record
    #else:
     #   message = "\t>> No data on the language of the publication" #there is no language key in the dictionary with your bibliography for a record
      #  message += "\t>> For now, trying `%s`..." % fallBackLanguage #uses your default language
       # language = fallBackLanguage #assigns the default language as language of that record
   # print(message) #prints the messages
    #return(language) #returns the language of that record

def processAllRecords(bibDataFile): #defines a functions for all the records
    bibData = functions.loadBib(bibDataFile) #loops through key-value-pairs in the bibData-dictionary
    keys = list(bibData.keys()) #keys from the list
    random.shuffle(keys) #randomizes the OCRing

    for key in keys: #loops through the keys
        bibRecord = bibData[key] #adds a key to the bibData
        functions.processBibRecord(settings["path_to_memex"], bibRecord) #assigns a new parameter
        language = functions.identifyLanguage(bibRecord["rCite"], "eng") #identifies a language, assigns the "eng"
        ocrPublication(bibRecord["rCite"], language, int(settings["page_limit"])) #sets a page limit, if there is such

    functions.memexStatusUpdates(settings["path_to_memex"], ".pdf")#creates a pdf
    functions.memexStatusUpdates(settings["path_to_memex"], ".bib")#creates a bib
    functions.memexStatusUpdates(settings["path_to_memex"], ".png")#creates a png
    functions.memexStatusUpdates(settings["path_to_memex"], ".json")#creates a jsonfile

#processAllRecords(settings["bib_all"])

###########################################################

processAllRecords(settings["bib_all"]) #processes all of them
print("Done!") #prints done

