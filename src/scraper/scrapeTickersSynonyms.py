# -*- coding: utf-8 -*-
"""
Created on Tue May 18 20:55:22 2021

@author: Bjarne Gerdes
"""
import pandas as pd
from finviz.screener import Screener
 

class IdentifyTickersAndSynonyms:
    
    def __init__(self, filters = ['cap_midover', 'ipodate_more1', 'exch_nasd']):
        self.filters = filters
        self.ticker_synonyms = {}
        self.ticker_blacklist = open("TICKERBLACKLIST").read().split()
        
        
    def scrapeTickers(self):
        stock_list = Screener(filters=self.filters, table='Overview', order='ticker')
        tickers_df = pd.DataFrame(stock_list.data)
        
        return tickers_df[~tickers_df["Ticker"].isin(self.ticker_blacklist)]
        
    def identifySynonyms(self, tickers_df):
        patterns_to_delete = [", Inc.", " Inc.", ", inc."
                              "Corporation", "Holdings",
                              "Holding", "Company",
                              "Corporated1", "Limited"
                              " & Co.", "Group",
                              "Financial", "Communities",
                              "Ltd.", " Co.", "Corp.", "Corp",
                              "Trust", " &"]

        # Extract raw company name
        tickers_df["Company"].replace({w: "" for w in patterns_to_delete},\
                                           inplace=True, regex=True)
        tickers_df["Company"].replace({" & ": " ",
                                       " &": " ",
                                       "  ": " "})
        
        tickers_df.set_index("Ticker", inplace=True)
        
        # add name of the ticker if contains more than 3 letters
        for ticker in tickers_df.index.values:
            self.ticker_synonyms[ticker] = list()

            #if len(ticker) >= 3:
            #   self. ticker_synonyms[ticker].append(ticker)
            self.ticker_synonyms[ticker].append(f"${ticker}")
            self.ticker_synonyms[ticker].append(tickers_df.T[ticker]["Company"].rstrip())
      
        return self.ticker_synonyms
        