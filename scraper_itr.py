import json
import os
import requests
from scrapy.selector import Selector as sel

class itr:
    def __init__(self, uri):
        self.uri = uri
        self.fetch()
    def fetch(self):
        print(f"fetching {self.uri}")
        self.text = requests.get(self.uri, headers={"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}).text
    def get_meta(self):
        

        res = {"model": "anon_mod", "shooter": "anon_shooter"}
        title = sel(text=self.text).css(".entry-title::text").extract_first()
        if " by " in title:
            model, rest = title.split(" by ")
            res["model"] = model
            for i in [" HQ ", " MQ ", " LQ ", " UHQ "]:
                if i in rest:
                    res["shooter"] = rest.split(i)[0]
                else:
                    continue
            return res
        else:
            return res

    def crawl(self, mode="shoot"):
        if mode == "shoot":
            res = []
            self.idx = self.uri.split("/")[-1]
            links = sel(text=self.text).css(".entry-content > p > a::attr(href)").extract()
            meta = self.get_meta()
            for i in links:
                dpath = os.path.join("downloads", meta["model"], meta["shooter"])
                os.makedirs(dpath, exist_ok=True)
                fname = i.split("/")[-1]
                fpath = os.path.join(dpath, fname)
                res.append({"fpath": fpath, "url": i})
            os.makedirs(os.path.join("eggs", "itr", meta["model"]), exist_ok=True)
            with open(os.path.join("eggs", "itr", meta["model"], self.idx+".json"), "w") as f:
                json.dump({"data": res}, f, indent=2)
        elif mode == "page":
            links = sel(text=self.text).css(".entry-title > a::attr(href)").extract()
            nxt = sel(text=self.text).css(".next::attr(href)").extract_first()
            for link in links:
                self.uri = link
                self.fetch()
                self.crawl(mode="shoot")
            if nxt is None:
                pass
            else:
                print(f"next {nxt}")
                self.uri = nxt
                self.fetch()
                self.crawl(mode=mode)


#a = itr("https://www.in-the-raw.org/archives/category/cynda-mcelvana/page/4")
a.crawl("page")
