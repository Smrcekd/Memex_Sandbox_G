# part 4 of building memex
# connections in the text;
import os, json
import functions1 
import yaml
import re
import pandas as pd
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer)
from sklearn.metrics.pairwise import cosine_similarity

### variables
settingsFile = ".\MW.yaml"
settings = yaml.safe_load(open(settingsFile))

memexPath = settings["memex_path"]


##code to process all .json files from memex;
def generatetfidfvalues():
    ocrFiles = functions1.dicOfRelevantFiles(memexPath, ".json") #function that creates a dictionary of citationKey:Path pairs - pre-done
    citeKeys = list(ocrFiles.keys()) #citekeys list

    docList   = [] #empty list
    docIdList = [] #empty list
    
    for citeKey in citeKeys: #loops through citekey list
        docData = json.load(open(ocrFiles[citeKey],"r",encoding= "utf8")) #reads in the data of the each citekey 

        docId = citeKey #sets variable docID to the respective citekey of each loop run
        doc   = " ".join(docData.values()) #connects docData values with whitespace
        
        doc = re.sub(r'(\w)-\n(\w)', r'\1\2', doc) #replaces pattern of "alphanumeric character - alphanumeric characters" 
        doc = re.sub('\W+', ' ', doc) #replaces non-word characters for whitespace 
        doc = re.sub('\d+', ' ', doc) #replaces digits for whitespace
        doc = re.sub(' +', ' ', doc) #replaces multiple whitespaces for whitespace

        docList.append(doc)
        docIdList.append(docId)
    
   
    ## convert our data into a differnt format
    vectorizer = CountVectorizer(ngram_range=(1,1), min_df= 1, max_df= 0.5) # vecrotizes it
    countVectorized = vectorizer.fit_transform(docList)
    tfidfTransformer = TfidfTransformer(smooth_idf=True, use_idf=True)
    vectorized = tfidfTransformer.fit_transform(countVectorized) 
    cosineMatrix = cosine_similarity(vectorized)

    ## matrixes
    tfidfTable = pd.DataFrame(vectorized.toarray(), index=docIdList, columns=vectorizer.get_feature_names())
    print("tfidfTable Shape: ", tfidfTable.shape) # optional
    tfidfTable = tfidfTable.transpose()
    tfidfTableDic = tfidfTable.to_dict()
    ##
    cosineTable = pd.DataFrame(cosineMatrix)
    print("cosineTable Shape: ", cosineTable.shape) # prints the shape
    cosineTable.columns = docIdList
    cosineTable.index = docIdList
    cosineTableDic = cosineTable.to_dict() #puts the cosineTable into our dict 
    


 
    filteredDic = {}                                                                  ## create empty dictionary 

    filteredDic = functions1.filterDic(tfidfTableDic, 0.05)                            ## with the filterd function in functions1.py filter through dic, with 0.05 as threshold

    with open("tfidfTableDic_filtered.txt", 'w', encoding='utf8') as f9:              ## save it into a textfile; avoid extension .json;
        json.dump(filteredDic, f9, sort_keys=True, indent=4, ensure_ascii=False)

    filteredDic = {}                                                                  ## same for the other dictionary
 
    filteredDic = functions1.filterDic(cosineTableDic, 0.25)

    with open("cosineTableDic_filtered.txt", 'w', encoding='utf8') as f9:
        json.dump(filteredDic, f9, sort_keys=True, indent=4, ensure_ascii=False)

generatetfidfvalues()
