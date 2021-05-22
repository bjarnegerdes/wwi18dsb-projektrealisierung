# -*- coding: utf-8 -*-
"""
Created on Wed May 19 21:02:00 2021

@author: Bjarne Gerdes
"""
from sqlalchemy import create_engine
from FilteringModel import Model
import pandas as pd

# Load 10k lines from db
engine = create_engine("postgresql://admin:password@h2933354.stratoserver.net/admin")
conn = engine.connect()
df = pd.read_sql_query('SELECT * FROM redditposts ORDER BY RANDOM() LIMIT 10000', conn) 


# extract english texts
lang_filter_model = Model()
is_english = lang_filter_model.languageDetection(list(df["comment"].values))
df_eng = df[is_english]
df_eng = df_eng[df_eng["comment"].str.len() > 10]
df_eng = df_eng.drop_duplicates("comment")
# prepare data for export and export
df_eng["__label__"] = [None]*df_eng.shape[0]
df_eng = df_eng.sample(5000, random_state=42)

teammembers = ["simone", "nina", "johannes", "anabel", "bjarne"]

for i in range(len(teammembers)):
    df_eng[i*1000:(i+1)*1000].to_excel(f"topic_labelling_dataframe_{teammembers[i]}.xlsx")
    