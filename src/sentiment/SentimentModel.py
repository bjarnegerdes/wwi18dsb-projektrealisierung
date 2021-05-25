# -*- coding: utf-8 -*-
"""
Created on Wed May 19 14:09:04 2021

@author: Bjarne Gerdes
"""

import spacy
import pickle
import numpy as np
import sys
sys.path.append("..")
    
class Model:

    def __init__(self, SPACY_MODEL="en_core_web_sm",\
                 SENTIMENT_MODEL_PATH = "./resource/models/sentiment_model.pkl"):
        
        self.nlp = spacy.load(SPACY_MODEL)
        self.sentiment_model = pickle.load(open(SENTIMENT_MODEL_PATH, "rb"))

    def sentimentPrediction(self, text, n_cores):
        # preprocess text using space nlp
        if type(text) == list:
            preprocessed_text = self.nlp.pipe(text, n_process=n_cores)
            vectors = np.array([v.vector for v in preprocessed_text])
            
        if type(text) == str:
            preprocessed_text= self.nlp(text)
            vectors = np.array([preprocessed_text.vector])
        
        sentiment_scores = self.sentiment_model.predict_proba(vectors)
        return sentiment_scores[:,0]*-1 +  sentiment_scores[:,1]
         
    