# -*- coding: utf-8 -*-
"""
Created on Tue May 18 20:14:44 2021

@author: Bjarne Gerdes
"""
import requests


class TickerDataScraper:
    
    def __init__(self, baseurl = "https://api.pushshift.io/reddit/comment/search/?q=keyword&sort=desc&unique=1"):
        self.baseurl = baseurl
        
    def scraperNews(self,  size=100):
        data = []
        
        
        url = self.baseurl.replace("q=keyword&","")
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