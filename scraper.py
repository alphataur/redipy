import os
from datetime import datetime, timedelta
import json

import requests

class RedditScraper:
    TARGET = "eggs"
    DPATH = "downloads"
    def __init__(self, name, duration):
        #presently supporting only subreddit
        self.name = name
        self.duration = duration
        self.base = "http://api.pushshift.io/reddit/submission/search/?after={}d&before={}d&sort_type=score&sort=desc&subreddit={}"
        self.now = datetime.now()

    def ensure_path(self):
        fpath = os.path.join(self.TARGET, self.name)
        if not os.path.exists(fpath):
            os.makedirs(fpath, exist_ok=True)
        return fpath

    def enrich_data(self, data):
        results = {}
        results["data"] = []
        for datum in data["data"]:
            try:
                if datum["post_hint"] == "image":
                    temp = {}
                    name = datum["title"].replace("/", "-")
                    temp["title"] = name
                    temp["url"] = datum["url"]
                    ext = datum["url"].split(".")[-1]
                    temp["fpath"] = os.path.join(self.DPATH, self.name, name+"."+ext)
                    os.makedirs(os.path.join(self.DPATH, self.name), exist_ok=True)
                    results["data"].append(temp)
            except:
                continue
        return results

    def crawl(self):
        print(self.name)
        for day in range(1, self.duration, 1):
            date = self.now - timedelta(days=day)
            fname = "{}-{}-{}-{}.json".format(self.name, date.year, date.month, date.day)
            dpath = self.ensure_path()
            fpath = os.path.join(dpath, fname)
            if os.path.exists(fpath):
                print("day {} already downloaded".format(date))
                continue
            print("{} downloading day {}".format(self.name, day))
            uri = self.base.format(day, day-1, self.name)
            data = requests.get(uri).json()
            data = self.enrich_data(data)
            with open(fpath, "w") as f:
                json.dump(data, f, indent=2)

#subs = ["alexistexas", "Celebritypussy", "CelebrityButts", "mombod", "tessafowler", "remylacroix", "rileyreid", "angelawhite", "miakhalifa", "abelladanger", "highresnsfw", "pawg",
#        "celebnsfw", "extramile", "innie", "godpussy", "wifesharing", "barbarapalvin"]
subs = ["ProgrammerHumor"]
for sub in subs:
    handle = RedditScraper(sub, 2000)
    handle.crawl()

