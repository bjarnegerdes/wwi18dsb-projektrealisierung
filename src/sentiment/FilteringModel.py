# -*- coding: utf-8 -*-
"""
Created on Wed May 19 14:09:04 2021

@author: Bjarne Gerdes
"""

import fasttext

class Model:
    
    
    def __init__(self, PRETRAINED_MODEL_PATH = '../../resource/lid.176.bin'):
        self.fasttext_model = fasttext.load_model(PRETRAINED_MODEL_PATH)
        
        
    def languageDetection(self, text):
        predictions = self.fasttext_model.predict(text)
        if type(text) == list:
            is_english = [(lang[0] == '__label__en' and prop[0] > 0.6) for lang, prop in zip(predictions[0], predictions[1])]
        
        if type(text) == str:
            is_english  = predictions[0][0][0] == '__label__en' and predictions[0][1][0] > 0.6
        
        return is_english
                
    
    def topicDetection(self, text):
        pass
    
    
    def filterComments(self, comments):
        pass
    

