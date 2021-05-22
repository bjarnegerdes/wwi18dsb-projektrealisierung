# -*- coding: utf-8 -*-
"""
Created on Tue May 18 21:49:50 2021

@author: Bjarne Gerdes
"""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from redditPushshiftScraper import TickerDataScraper as TDS
from sqlalchemy import create_engine, Column, DateTime, String
from scrapeTickersSynonyms import IdentifyTickersAndSynonyms as ITS

Base = automap_base()
metadata = Base.metadata


class Redditpost(Base):
    __tablename__ = 'redditposts'

    ticker = Column(String, primary_key=True, nullable=False)
    created_utc = Column(DateTime, primary_key=True, nullable=False)
    comment = Column(String, nullable=False)

class DatabaseInteraction:
    
    def __init__(self):
        # connect to db
        self.engine = create_engine("postgresql://admin:password@postgres_container/admin")
        Base.prepare(self.engine, reflect=True)
        Base.metadata.create_all(bind=self.engine)
        self.session = Session(self.engine)
        
        self.redditpost = Redditpost()
        
        # scrape tickers and synonyms
        self.ITS = ITS()
        self.tickers_df = self.ITS.scrapeTickers()
        self.ticker_synonyms = self.ITS.identifySynonyms(self.tickers_df)
        
        # news scraper instance
        self.TDS = TDS()
        
    def scrapeInsertOne(self, ticker):
        data = self.TDS.scraperTicker(ticker, self.ticker_synonyms[ticker])
        
        if data != None:
            self.data = data
            for d in data:
                d["ticker"] = ticker
                d["created_utc"] = datetime.fromtimestamp(d["created_utc"])
                
    
            db_objects = [Redditpost(ticker=d["ticker"],\
                                     created_utc=d["created_utc"],
                                     comment=d["comment"]) for d in data]
            self.db_objects = db_objects
            for obj in db_objects:
                self.session.merge(obj)
            self.session.commit()
        
    def roundRobinScrape(self):
        tickers = list(self.tickers_df.index.values)
        n_tickers = len(tickers)
        
        n_iter = 0
        while True:
            ticker = tickers[n_iter % n_tickers]
            n_iter += 1
        
            self.scrapeInsertOne(ticker)
        
            
if __name__ == '__main__':
    di = DatabaseInteraction()
    di.roundRobinScrape()
    
    
