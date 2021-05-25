# -*- coding: utf-8 -*-
"""
Created on Tue May 25 12:31:53 2021

@author: Bjarne Gerdes
"""

import spacy
import pickle
import numpy as np
import pandas as pd
from tqdm import tqdm
from xgboost import XGBClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

df_sentiment = pd.read_csv("training.1600000.processed.noemoticon.csv", names=["target", "id", "date",\
                                                                                "flag","user", "text"])
    
# transform target variable
df_sentiment["target"] = (df_sentiment["target"]/2)-1

# create vectors for data

nlp = spacy.load("en_core_web_sm")
df_sentiment["doc"] =  [doc for doc in tqdm(nlp.pipe(df_sentiment["text"], n_process=-1))]


X =  np.array([x.vector for x in  df_sentiment["doc"]])
y = df_sentiment["target"].values

del(df_sentiment)


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

# train xgbclassifier
xgb = XGBClassifier()
xgb.fit(X_train, y_train)

# predictions
y_pred = xgb.predict(X_test)

print(classification_report(y_test, y_pred))


pickle.dump(xgb, open("../resource/models/sentiment_model.pkl", "wb"))
