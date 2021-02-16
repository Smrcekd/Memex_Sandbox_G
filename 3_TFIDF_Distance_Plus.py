# NEW LIBRARIES
import pandas as pd # import panda library
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer) #import the features from sklearn helping to transform the data
from sklearn.metrics.pairwise import cosine_similarity #cosine_similarity feature from the sklearn

import os, yaml, json, re, sys #import other usual libraries

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions #import our functions

###########################################################
# VARIABLES ###############################################
###########################################################

settings = functions.loadYmlSettings("settings.yml") #load our yaml settings file
stopWFile = settings["stopwords"] #determine our stopwords from settingsfile
stopwordsList = open(stopWFile, "r", encoding = "utf8").read().split("\n") ## file with stopwords to get better results #ioends the stppwords, reads and splits
###########################################################
# MAIN FUNCTIONS ##########################################
###########################################################

def filterTfidfDictionary(dictionary, threshold, lessOrMore): #define a function for the filtering of the tf-idf-dictionary
    dictionaryFilt = {} #create empy dictionary
    for item1, citeKeyDist in dictionary.items():#loop through the outer dictionary which contains the title of each publication
        dictionaryFilt[item1] = {} #create empty subdictionary for each publication
        for item2, value in citeKeyDist.items(): #loop through that subdictionary
            if lessOrMore == "less": #if the treshold is lower
                if value <= threshold: #proceed if the value is below the threshold
                    if item1.split("_")[0] != item2.split("_")[0]: #proceed if it is not the same publication 
                        dictionaryFilt[item1][item2] = value #add the value 
            elif lessOrMore == "more": #if the treshold is higher
                if value >= threshold: #proceed if the value is above the threshold
                    if item1.split("_")[0] != item2.split("_")[0]: #proceed if it is not the same publication 
                        dictionaryFilt[item1][item2] = value #add the value
            else:
                sys.exit("`lessOrMore` parameter must be `less` or `more`") #if not, exit the code so you can check for errors in your code

        if dictionaryFilt[item1] == {}: #checks whether the subdictionary is empty
            dictionaryFilt.pop(item1) #remove item1 in the dictionary

    return(dictionaryFilt) #return the dictionary

import math #imports math
# a function for grouping pages into clusters of y number of pages
# x = number to round up; y = a multiple of the round-up-to number
def roundUp(x, y): #defines function roundUp
    result = int(math.ceil(x / y)) * y #creates a math equation
    return(result) #returns the result

clusterSize = 5 # 6 pages per page clusters, with 1 page overlap for smoothness (0-5, 5-10, 10-15, 15-20, etc.)
                # clusters also reduce the number of documents 

def tfidfPublications(pathToMemex, PageOrPubl): #create the tfidf-dictionary
    print("\tProcessing: %s" % PageOrPubl) #prints processing and page of the publication
    # PART 1: loading OCR files into a corpus
    ocrFiles = functions.dicOfRelevantFiles(pathToMemex, ".json") #generates a dictionary with citekeys as keys and paths to json-Files as values
    citeKeys = list(ocrFiles.keys())#[:500] #creates a list with the citeKeys

    print("\taggregating texts into documents...") #prints to inform about the processing
    corpusDic = {} #creates an empty list 
    for citeKey in citeKeys: #loops throught the citekeys
        docData = json.load(open(ocrFiles[citeKey], "r", encoding="utf8")) #loads the OCRed documents
        for page, text in docData.items(): #loops through the OCRed documents
            # text as a document
            if PageOrPubl == "publications": #if there is "publication"
                if citeKey not in corpusDic: #if there is not a citekey in the corpusDic
                    corpusDic[citeKey] = [] #creates empty list for citekeys
                corpusDic[citeKey].append(text) #appends the citeKeys

            # page cluster as a document
            elif PageOrPubl == "pages": #if there are "pages"
                pageNum = int(page) #returns the integrer page from the docs
                citeKeyNew = "%s_%05d" % (citeKey, roundUp(pageNum, clusterSize)) #creates a new cite key with page numbers and cluster Size
                if citeKeyNew not in corpusDic: #if it is not in the dictionary
                    corpusDic[citeKeyNew] = [] #create a new dictionary
                corpusDic[citeKeyNew].append(text) #append the text to citekeynew 

                # add the last page of cluster N to cluster N+1
                if pageNum % clusterSize == 0: #if the page number cluser size is 0
                    citeKeyNew = "%s_%05d" % (citeKey, roundUp(pageNum+1, clusterSize)) #creates a new cite key with page numbers +1 and cluster Size
                    if citeKeyNew not in corpusDic: #of citekeynew is not in the dictionary
                        corpusDic[citeKeyNew] = [] #create a new corpusDic dictionary
                    corpusDic[citeKeyNew].append(text) #append the text to it
            else:
                sys.exit("`PageOrPubl` parameter must be `publications` or `pages`") #if not, exit the program

    print("\t%d documents (%s) generated..." % (len(corpusDic), PageOrPubl)) #print documents are generated and pages of the publication
    print("\tpreprocessing the corpus...")#print processing of the corpus

    docList   = [] #create an empty dictionary
    docIdList = [] #create an empty list for the citeKe
    for docId, docText in corpusDic.items():
        if len(docText) > 2: # cluster of two pages mean that we would drop one last page            
            doc = " ".join(docText) #take the text of each publication
            # clean doc
            doc = re.sub(r'(\w)-\n(\w)', r'\1\2', doc)
            doc = re.sub('\W+', ' ', doc)
            doc = re.sub('_+', ' ', doc)
            doc = re.sub('\d+', ' ', doc)
            doc = re.sub(' +', ' ', doc) #clean your content with the help of regular expressions, especially remove unneccessary blanks and signs)
            # we can also drop documents with a small number of words
            # (for example, when there are many illustrations)
            # let's drop clusters that have less than 1,000 words (average for 6 pages ±2500-3000 words)
            if len(doc.split(" ")) > 1000:
                # update lists
                docList.append(doc) #add the content of each publication to the first list
                docIdList.append(docId) #add the citeKey of each publication to the second key

    # PART 3: calculate tfidf for all loaded publications and distances
    print("\tgenerating tfidf matrix & distances...") #print the phrase
    #stopWords = functions.loadMultiLingualStopWords(["eng", "deu", "fre", "spa"])
    vectorizer = CountVectorizer(ngram_range=(1,1), min_df=5, max_df=0.5, stop_words = stopwordsList) #create a vectorizer (use only unigrams, use only words that appear in at least five documents, use only words that appear in less than half of all documents)
    countVectorized = vectorizer.fit_transform(docList) #create the vectors
    tfidfTransformer = TfidfTransformer(smooth_idf=True, use_idf=True) #adjust the transformer
    vectorized = tfidfTransformer.fit_transform(countVectorized) # generates a sparse matrix
    cosineMatrix = cosine_similarity(vectorized) #generate a matrix with cosine distance values

    # PART 4: saving TFIDF --- only for publications!
    if PageOrPubl == "publications": #if there is "publivation in PageorPubl
        print("\tsaving tfidf data...") #print phrase
        tfidfTable = pd.DataFrame(vectorized.toarray(), index=docIdList, columns=vectorizer.get_feature_names()) #transform the matrix into a dataframe
        tfidfTable = tfidfTable.transpose() #transposes rows and columns for document and information
        print("\ttfidfTable Shape: ", tfidfTable.shape) #prints the dataframe shape
        tfidfTableDic = tfidfTable.to_dict() #creates a dictionary with the tfidf-values

        tfidfTableDicFilt = filterTfidfDictionary(tfidfTableDic, 0.05, "more") #previously defined function only for the tf-idf dictionar including only the tf-idf value higher than 0.05 
        pathToSave = os.path.join(pathToMemex, "results_tfidf_%s.dataJson" % PageOrPubl) #creates the filepath and filename
        with open(pathToSave, 'w', encoding='utf8') as f9: #opens pathToSave and writes into it
            json.dump(tfidfTableDicFilt, f9, sort_keys=True, indent=4, ensure_ascii=False) #creates the json-File which saves your filtered tfidf dictionary

    # PART 4: saving cosine distances --- for both publications and page clusters
    print("\tsaving cosine distances data...") #prints the phrase
    cosineTable = pd.DataFrame(cosineMatrix) #the metrix transformed into dataframe
    print("\tcosineTable Shape: ", cosineTable.shape) #prints the cosineTable shape
    cosineTable.columns = docIdList #Takes the list with the citeKeys as columns
    cosineTable.index = docIdList #Takes the list with the CiteKeys as index
    cosineTableDic = cosineTable.to_dict() #creates a dictionary with the cosine similarity

    tfidfTableDicFilt = filterTfidfDictionary(cosineTableDic, 0.25, "more") #previously defined function meassuring cosine similarities dictionary including only publications with a cosine similarity value higher than 0.25
    pathToSave = os.path.join(pathToMemex, "results_cosineDist_%s.dataJson" % PageOrPubl) #creates the filepath and the filename
    with open(pathToSave, 'w', encoding='utf8') as f9:
        json.dump(tfidfTableDicFilt, f9, sort_keys=True, indent=4, ensure_ascii=False) #creates the json-File saving the filtered cosine similarities dict

tfidfPublications(settings["path_to_memex"], "publications") #starts the function for publications, puts it to path_to_memex
tfidfPublications(settings["path_to_memex"], "pages") #starts the function for pages, puts it to path_to_memex