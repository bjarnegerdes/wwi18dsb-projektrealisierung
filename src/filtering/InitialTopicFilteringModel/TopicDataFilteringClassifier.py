# -*- coding: utf-8 -*-
"""
Created on Sun May 23 18:14:18 2021

@author: Bjarne Gerdes
"""
import sys
sys.path.append("..")
import spacy
import numpy as np
import pandas as pd
from tqdm import tqdm
from xgboost import XGBClassifier
from sklearn.model_selection import KFold
from sklearn.metrics import classification_report

# spacy
nlp = spacy.load("en_core_web_sm")


df_labeled = pd.read_csv("topic_label_dataset.csv")
df_labeled["doc"] =  [doc for doc in tqdm(nlp.pipe(df_labeled["comment"], n_process=-1))]

# extract validation fold
valid = df_labeled.sample(int(df_labeled.shape[0]*0.2),random_state=0)
df_labeled = df_labeled[~df_labeled.index.isin(valid.index)]

# X,y split
X = np.array([x.vector for x in  df_labeled["doc"]])
y = df_labeled["is_topic"].values

# split data into 3 folds
fold = KFold(n_splits=3, random_state=0, shuffle=True).split(df_labeled)

k_folds = [(X[train_index], X[test_index],\
           y[train_index], y[test_index],\
           df_labeled.iloc[test_index]) for train_index, test_index in fold]

# extract good and bad samples from fold
    
class FindSureSamples:
    
    def __init__(self, k_fold):
        # store folds for model training and eval
        self.X_train = k_fold[0]
        self.X_test = k_fold[1]
        self.y_train = k_fold[2]
        self.y_test = k_fold[3]
        
        # store data for sample extractions
        self.df_labeled_test = k_fold[4]
        
    def fit(self, clf):
        self.clf = clf
        self.clf.fit(self.X_train, self.y_train)
        
    def evaluate(self):
        self.y_pred_class = self.clf.predict(self.X_test)
        self.y_pred_continous = self.clf.predict_proba(self.X_test)

        print(classification_report(self.y_test, self.y_pred_class))


    def extractSamples(self):
        # take all samples where the algo was sure and right 
        self.samples_sure_pos_idx = (self.y_pred_continous[:,1] > 0.8) + self.y_test
        self.samples_neg_pos_idx = (self.y_pred_continous[:,0] >  0.8) + (self.y_test == 0).astype(int)
        self.sure_samples = self.df_labeled_test[(self.samples_sure_pos_idx == 2) | (self.samples_neg_pos_idx == 2) ] 


    def process(self, clf):
        self.fit(clf)
        self.evaluate()
        self.extractSamples()  
        
        return self.sure_samples

# finde usefull samples per k fold and merge them
useable_samples = [FindSureSamples(k).process(XGBClassifier()) for k in k_folds]
usefull_samples_merged = pd.concat(useable_samples)
train = df_labeled[df_labeled.index.isin(usefull_samples_merged.index)]
test = df_labeled[~df_labeled.index.isin(usefull_samples_merged.index)]

X_train =  np.array([x.vector for x in  train["doc"]])
y_train = train["is_topic"].values
X_test = np.array([x.vector for x in  test["doc"]])
y_test = test["is_topic"].values

# use filtered data to filter again
useable_samples.append(FindSureSamples([X_train, X_test, y_train, y_test, test]).process(XGBClassifier()))
usefull_samples_merged = pd.concat(useable_samples)

# induce bias by appending hard to predict data
train = df_labeled[df_labeled.index.isin(usefull_samples_merged.index)]
bias_samples = int((df_labeled.shape[0] - train.shape[0])*0.33333)
train = train.append(df_labeled[~df_labeled.index.isin(usefull_samples_merged.index)].sample(bias_samples))

# final model check on validation dataset
X_train =  np.array([x.vector for x in train["doc"]])
y_train = train["is_topic"].values
X_valid = np.array([x.vector for x in  valid["doc"]])
y_valid = valid["is_topic"].values


# final model check
samples = FindSureSamples([X_train, X_valid, y_train, y_valid, valid])
useable_samples.append(samples.process(XGBClassifier()))

# check wrong predictions
wrong_preds = samples.df_labeled_test[samples.y_pred_class != samples.y_test]

# export filtered dataset
usefull_samples_merged = pd.concat(useable_samples)
usefull_samples_merged[["comment","is_topic"]].to_csv("./filtered_labelled_topic_data.csv", index=False)