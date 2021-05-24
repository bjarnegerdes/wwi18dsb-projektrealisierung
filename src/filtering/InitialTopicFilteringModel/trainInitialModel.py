# -*- coding: utf-8 -*-
"""
Created on Sun May 23 20:44:29 2021

@author: Bjarne Gerdes
"""
import spacy
import pickle
import numpy as np
import pandas as pd
from tqdm import tqdm
from xgboost import XGBClassifier

nlp = spacy.load("en_core_web_sm")


df_labeled = pd.read_csv("filtered_labelled_topic_data.csv")
df_labeled["doc"] =  [doc for doc in tqdm(nlp.pipe(df_labeled["comment"], n_process=-1))]
X =  np.array([x.vector for x in  df_labeled["doc"]])
y = df_labeled["is_topic"].values

### MODEL FILTERING TAKES PLACE HERE
### MISSING ATM
####
######
####
###
### MISSING ATM


# train and persist model
xgb = XGBClassifier()
xgb.fit(X,y)

pickle.dump(xgb, open("../models/filtering_model.pkl", "wb"))
