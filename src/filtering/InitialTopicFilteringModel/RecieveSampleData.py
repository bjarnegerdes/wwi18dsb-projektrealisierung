# -*- coding: utf-8 -*-
"""
Created on Wed May 19 21:02:00 2021

@author: Bjarne Gerdes
"""
import sys
sys.path.append("..")
import time
import pandas as pd
from tqdm import tqdm
from random import uniform
from FilteringModel import Model
from sqlalchemy import create_engine
from negativSentimentScraper import TickerDataScraper as TDS




# Load lines from db
engine = create_engine("postgresql://admin:password@h2933354.stratoserver.net:3000/admin")
conn = engine.connect()
df = pd.read_sql_query('SELECT * FROM redditposts', conn) 


# extract english texts
lang_filter_model = Model()
is_english = lang_filter_model.languageDetection(list(df["comment"].values))
df_eng = df[is_english]
df_eng = df_eng[df_eng["comment"].str.len() > 10]
df_eng = df_eng.drop_duplicates("comment")


# define filtering keywords:
filter_words = "stock|earnings|market|company|positions|portfolio"
# filter positive examples
keywords = df_eng["ticker"].drop_duplicates().apply(lambda x : "$"+x)

# filter positive examples
filter_ticker_dollar = df_eng["comment"].apply(lambda x: sum([(k in x) for k in keywords]))
filter_ticker_dollar = filter_ticker_dollar.between(1,7)
filter_keywords = df_eng["comment"].str.contains(filter_words)
filter_ges = (filter_ticker_dollar + filter_keywords) > 0
                                               
positives_sure = df_eng[filter_ges]

print("Filtered", len(positives_sure), "positive elements", flush=True)
# filter negative examples
negatives_sure = set()
tds = TDS()

n_negative = int(len(positives_sure)*1.2)
pbar = tqdm(total = n_negative)
pbar.update(len(negatives_sure))

while len(negatives_sure) <= n_negative:
    news = tds.scraperNews() 
    if len(news) > 0:
        scraped_batch = [c["comment"] for c in news if len(c["comment"]) > 10]
        nb_old = len(negatives_sure)
        negatives_sure = negatives_sure.union(scraped_batch)
        nb_new = len(negatives_sure)
        nb_gain= nb_new - nb_old
        pbar.set_description(f"{len(negatives_sure)} of {n_negative} scraped")
        pbar.update(nb_gain)
    time.sleep(10)
    
# clean negatives
negatives_sure = pd.Series(list(negatives_sure))
negatives_sure = negatives_sure[~negatives_sure.str.contains(filter_words)]
negatives_sure = negatives_sure [~negatives_sure.apply(lambda x: any([(k in x) for k in keywords]))]

# filter non english in negatives
is_english = lang_filter_model.languageDetection(list(negatives_sure.values))
negatives_sure = negatives_sure[is_english]


# build df out of samples and export
data = [(n,0) for n in negatives_sure] + [(p,1) for p in positives_sure["comment"]]
df_labelled = pd.DataFrame(data, columns=["comment", "is_topic"])

# excludes keywords from data to prevent bais
def exclude(comment, keywords):
    
    for k in keywords:
        if uniform(0,1) < 0.90:
            comment = comment.replace(k,"")
            
    return comment

filter_words_kw = filter_words.split("|")
df_labelled["comment"] = df_labelled["comment"].apply(lambda x: exclude(x, filter_words_kw))
df_labelled.to_csv("topic_label_dataset.csv")
