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


hand_labelled_paths = ["topic_labelling_dataframe_anabel_v1.xlsx",
                       "topic_labelling_dataframe_johannes_v1.xlsx",
                       "topic_labelling_dataframe_nina_v1.xlsx",
                       "topic_labelling_dataframe_anabel_v1.xlsx"]


dfs_hand_labelled = [pd.read_excel(path) for path in hand_labelled_paths]
         
for df in dfs_hand_labelled :
    df = df.rename(columns={"__label__": "is_topic"})
    is_str = df["comment"].apply(lambda x: type(x) == str)
    df = df[is_str].drop(["ticker"], axis=1)
    df["is_topic"] = df["is_topic"].apply(lambda x: x == 1)

    df_labeled = df_labeled.append(df, ignore_index=True)

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

pickle.dump(xgb, open("../resource/models/filtering_model.pkl", "wb"))
