# NEW LIBRARIES
import pandas as pd
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer)
from sklearn.metrics.pairwise import cosine_similarity

import os, json, re, random #import all the libraries, similar as in TF_IDF.py

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions #import our functions
###########################################################
# VARIABLES ###############################################
###########################################################

settings = functions.loadYmlSettings("settings.yml") #load our settings yaml file

###########################################################
# MAIN FUNCTIONS ##########################################
###########################################################

from wordcloud import WordCloud #imports WordCloud function from WordCloud library
import matplotlib.pyplot as plt #imports the matplotlib library

def generateWordCloud(citeKey, pathToFile): #defines a function that creates wordclouds
    # aggregate dictionary
    data = json.load(open(pathToFile)) #loads the data from the OCRed publications
    dataNew = {} #creates a new dictionary
    for page,pageDic in data.items(): #loops through the pages in the publivations
        for term, tfIdf in pageDic.items(): #loops through term and tfidf values
            if term in dataNew: #checks if the term is in the new dictionary
                dataNew[term] += tfIdf #add additional the tfidf value
            else:
                dataNew[term]  = tfIdf #add the tfidf value

def filterTfidfDictionary(dictionary, threshold, lessOrMore):  #function to filter our tf-idf-dictionary
    dictionaryFilt = {} #creates empty dictionrary
    for item1, citeKeyDist in dictionary.items(): #loops through the outer dictionary which contains the title of each publication
        dictionaryFilt[item1] = {} #creates a subdictionary for each publication
        for item2, value in citeKeyDist.items(): #loops through that subdictionary
            if lessOrMore == "less": #checks for the lower threshold
                if value <= threshold: #proceeds if the value is below the threshold
                    if item1 != item2: #proceeds if it is not the same publication 
                        dictionaryFilt[item1][item2] = value #adds the value 
            elif lessOrMore == "more": #checks for the upper threshold
                if value >= threshold: #proceeds if the value is above the threshold
                    if item1 != item2: #proceeds if it is not the same publication 
                        dictionaryFilt[item1][item2] = value #add the value
            else:
                sys.exit("`lessOrMore` parameter must be `less` or `more`") #exits the code

        if dictionaryFilt[item1] == {}: #checks if the subdictionary is empty
            dictionaryFilt.pop(item1) #removes this item from the dictionary    
    return(dictionaryFilt) #returns the dictionary


def generateTfIdfWordClouds(pathToMemex): #function that creates wordclouds according to the tfidf values
    # PART 1: loading OCR files into a corpus
    ocrFiles = functions.dicOfRelevantFiles(pathToMemex, ".json") #generates a dictionary with citekeys as keys and paths to json-Files as values
    citeKeys = list(ocrFiles.keys())#[:500] #creates a list with the citeKeys

    print("\taggregating texts into documents...") #print the line
    docList   = [] #createss an empty dictionary for concent
    docIdList = [] #createss an empty dictionary for citekeys

    for citeKey in citeKeys: #loops through the citekeys
        docData = json.load(open(ocrFiles[citeKey],"r", encoding= "utf8")) #loads the OCRed content
        
        docId = citeKey #Puts into the dictionary citeKey of each publication
        doc   = " ".join(docData.values()) #takes the OCRed content of each publication

        # clean doc
        doc = re.sub(r'(\w)-\n(\w)', r'\1\2', doc)
        doc = re.sub('\W+', ' ', doc)
        doc = re.sub('_+', ' ', doc)
        doc = re.sub('\d+', ' ', doc)
        doc = re.sub(' +', ' ', doc) #cleans the content with the help of regular expressions to remove unneccessary blanks and signs)


        # update lists
        docList.append(doc) #add the content of each publication to the first list
        docIdList.append(docId) #add the citeKey of each publication to the second key

    print("\t%d documents generated..." % len(docList)) #print the number of publications

    # PART 2: calculate tfidf for all loaded publications and distances
    print("\tgenerating tfidf matrix & distances...") #print to inform about the processing

    vectorizer = CountVectorizer(ngram_range=(1,1), min_df=2, max_df=0.5) #creates a vectorizer (use only unigrams, use only words that appear in at least five documents, use only words that appear in less than half of all documents)
    countVectorized = vectorizer.fit_transform(docList) #creates the vectors
    tfidfTransformer = TfidfTransformer(smooth_idf=True, use_idf=True) #adjusts the transformer
    vectorized = tfidfTransformer.fit_transform(countVectorized) # generates a sparse matrix

    print("\tconverting and filtering tfidf data...") #prints to inform about the processing
    tfidfTable = pd.DataFrame(vectorized.toarray(), index=docIdList, columns=vectorizer.get_feature_names()) #transforms the matrix into a dataframe
    tfidfTable = tfidfTable.transpose() #transposes rows and columns to document and information
    tfidfTableDic = tfidfTable.to_dict() #creates a dictionary with the tfidf-values
    tfidfTableDic = filterTfidfDictionary(tfidfTableDic, 0.02, "more") #the previously created function filters the tf-idf dictionary, including only words with a tf-idf value higher than 0.02
    

    #tfidfTableDic = json.load(open("/Users/romanovienna/Dropbox/6.Teaching_New/BUILDING_MEMEX_COURSE/_memex_sandbox/_data/results_tfidf_publications.dataJson"))

    # PART 4: generating wordclouds
    print("\tgenerating wordclouds...") #print to inform about the processing
    wc = WordCloud(width=1000, height=600, background_color="white", random_state=2,
                relative_scaling=0.5, #color_func=lambda *args, **kwargs: (179,0,0)) # single color
                #colormap="copper") # Oranges, Reds, YlOrBr, YlOrRd, OrRd; # copper
                colormap="Blues") # binary, gray
                # https://matplotlib.org/3.1.1/gallery/color/colormap_reference.html

    counter = len(tfidfTableDic) #counts the number of dictionaries with the tfidf-values
    citeKeys = list(tfidfTableDic.keys()) #sorts the citationKeys
    random.shuffle(citeKeys) #shuffles your citationKeys

    for citeKey in citeKeys: #loops through your citationKeys
        savePath = functions.generatePublPath(pathToMemex, citeKey) #takes the filepath generated by one of our previous function
        savePath = os.path.join(savePath, "%s_wCloud.jpg" % citeKey) #saves the wordcloud as jpg-file

        if not os.path.isfile(savePath): #check if the jpg-file exists
            wc.generate_from_frequencies(tfidfTableDic[citeKey]) #if not, generate the wordcloud
            # plotting
            plt.imshow(wc, interpolation="bilinear") #plots the wordcloud
            plt.axis("off")
            #plt.show() # this line shows the plot
            plt.savefig(savePath, dpi=200, bbox_inches='tight') #saves the wordcloud

            print("\t%s (%d left...)" % (citeKey, counter)) #print how many wordclouds are left for saving
            counter -= 1 #minus one for every file
        
        else:
            print("\t%s --- already done" % (citeKey)) #prints that a jpg-file with the wordcloud has already been saved
            counter -= 1 #minus one for every file

        # WordCloud:
        #   colormap: https://matplotlib.org/3.3.3/tutorials/colors/colormaps.html
        #   font_path="./fonts/Baskerville.ttc" (path to where your font is)
        #   Documentation: https://amueller.github.io/word_cloud/index.html
        #input("Check the plot!")

###########################################################
# PROCESS ALL RECORDS: WITH PROMPT ########################
###########################################################

print("""
============= GENERATING WORDCLOUDS ===============
   Type "YES", if you want to regenerate new files;
Old files will be deleted and new ones regenerated;
Press `Enter` to continue generating missing files.
===================================================
""") #prints the statement
response = input() #asks you to type yes

if response.lower() == "yes": #if yes
    print("Deleting existing files...") #starts deleting existing files
    functions.removeFilesOfType(settings["path_to_memex"], "_wCloud.jpg") #calls to the function from functionsfile, removes the _wCloud.jpg".
    print("Generating new files...") #prints the line
    generateTfIdfWordClouds(settings["path_to_memex"]) #generates the new files to path_to_memex
else:
    print("Getting back to generating missing files...") #if not, prints this
    generateTfIdfWordClouds(settings["path_to_memex"])#generates the new files to path to memex