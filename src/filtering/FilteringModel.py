# -*- coding: utf-8 -*-
"""
Created on Wed May 19 14:09:04 2021

@author: Bjarne Gerdes
"""

import spacy
import pickle
import fasttext
import numpy as np
import sys
sys.path.append("..")
    
class Model:

    def __init__(self, SPACY_MODEL="en_core_web_sm",\
                 PRETRAINED_MODEL_PATH = '../../resource/lid.176.bin',\
                 TOPIC_MODEL_PATH = "../../resource/models/filtering_model.pkl"):
        
        self.fasttext_model = fasttext.load_model(PRETRAINED_MODEL_PATH)
        self.nlp = spacy.load(SPACY_MODEL)
        self.topic_model = pickle.load(open(TOPIC_MODEL_PATH, "rb"))

        
    def languageDetection(self, text):
        predictions = self.fasttext_model.predict(text)
        if type(text) == list:
            is_english = [(lang[0] == '__label__en' and prop[0] > 0.6) for lang, prop in zip(predictions[0], predictions[1])]
        
        if type(text) == str:
           is_english  = predictions[0][0] == '__label__en' and predictions[1][0] > 0.6
        
        
        return np.array(is_english)
                
    
    def topicDetection(self, text, n_cores):
        # preprocess text using space nlp
        if type(text) == list:
            preprocessed_text = self.nlp.pipe(text, n_process=n_cores)
            vectors = np.array([v.vector for v in preprocessed_text])
            
        if type(text) == str:
            preprocessed_text= self.nlp(text)
            vectors = np.array([preprocessed_text.vector])
        
        return self.topic_model.predict(vectors)
        
    
    def filterComments(self, text, n_cores):
        
        try:
            language_filter = self.languageDetection(text)
            topic_filter = self.topicDetection(text, n_cores)
            
            return (language_filter.astype(int) + topic_filter.astype(int)) == 2
            
        except:
            print("Text is type", type(text))
            
            
            