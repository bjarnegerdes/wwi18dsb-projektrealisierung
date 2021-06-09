# -*- coding: utf-8 -*-
"""
Created on Wed May 19 21:02:00 2021

@author: Bjarne Gerdes
"""
from time import sleep
from FilteringModel import Model
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Boolean, Column, DateTime, Float, String

Base = automap_base()
metadata = Base.metadata

class Redditpost(Base):
    __tablename__ = 'redditposts'

    ticker = Column(String, primary_key=True, nullable=False)
    created_utc = Column(DateTime, primary_key=True, nullable=False)
    comment = Column(String, nullable=False)
    passed_filter_checks = Column(Boolean)
    sentiment = Column(Float(53))

class DatabaseFilteringHandler:
    
    def __init__(self, db_con = "postgresql://admin:password@postgres_container/admin"):
        self.engine = create_engine(db_con)
        self.conn = self.engine.connect()
        self.filter_model = Model()
 
        Base.prepare(self.engine, reflect=True)
        Base.metadata.create_all(bind=self.engine)
        self.session = Session(self.engine)       
 
    def getData(self, limit=None):
        query = self.session.query(Redditpost).filter(Redditpost.passed_filter_checks == None)
        if limit != None:
            data = query.limit(limit)
        if limit == None:
            data = query.limit(10_000)
        return data


    def filterData(self, data, n_cores):
        filtered_data = self.filter_model.filterComments(list(data), n_cores)
        return filtered_data 
    
    def process(self, limit=None):
        
        while True:
            data = self.getData(limit)
            
            if type(data) != None:     
                comments = [d.comment for d in data]
                if len(comments) == 0:
                    sleep(60)
                else:

                    filter_condition = self.filterData(comments, -1)
                    
                    for d, f in zip(data, filter_condition):
                        if f == False:
                            d.passed_filter_checks = False
                        if f == True:
                            d.passed_filter_checks = True
    
                    
                    self.session.commit()
                    
                            
            
                
if __name__ == '__main__':
    dbfilter = DatabaseFilteringHandler()
    dbfilter.process()
    