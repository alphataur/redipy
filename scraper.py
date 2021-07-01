import os
from datetime import datetime, timedelta
import json

import requests

class RedditScraper:
    TARGET = "eggs"
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

    def crawl(self):
        for day in range(self.duration, 1, -1):
            date = self.now - timedelta(days=day)
            fname = "{}-{}-{}-{}.json".format(self.name, date.year, date.month, date.day)
            dpath = self.ensure_path()
            fpath = os.path.join(dpath, fname)
            if os.path.exists(fpath):
                print("day {} already downloaded".format(date))
                continue
            print("downloading day {}".format(day))
            uri = self.base.format(day, day-1, self.name)
            data = requests.get(uri).json()

            with open(fpath, "w") as f:
                json.dump(data, f, indent=2)


handle = RedditScraper("dakini", 10)
handle.crawl()

