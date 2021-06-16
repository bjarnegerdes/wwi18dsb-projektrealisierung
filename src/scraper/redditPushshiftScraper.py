# -*- coding: utf-8 -*-
"""
Created on Tue May 18 20:14:44 2021

@author: Bjarne Gerdes
"""
import requests


class TickerDataScraper:
    
    def __init__(self, baseurl = "https://beta.pushshift.io/search/reddit/comments?q=keyword&sort=desc",\
		subreddits=["walltstreetbets", "pennystocks", "Stock_Picks",\
			"stocks", "StockMarket", "RobinHood", "WallStreetbetsELITE",\
            "Superstonk", "InvestmentClub", "weedstocks", "investing", "stocks"]):

        self.baseurl = baseurl
        self.subreddits = subreddits
        self.subreddit_string = "&subreddit="+"".join([s+"," for s in self.subreddits])
  
    def scraperTicker(self, ticker, synonyms, size=100):
        data = []
        
        urls = [(self.baseurl.replace("keyword", synonym)+self.subreddit_string)[:-1] for synonym in synonyms]
        for url in urls:
            if size != None:
                url += f"&size={size}"
            
            try:
                r = requests.get(url)
                posts_list = r.json()["data"]
                for post in posts_list:
                    data.append({"comment":post["body"].replace("\n", " "),
                                      "created_utc": post["created_utc"]})

            except: 
                return None
        return data