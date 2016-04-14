#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bs4
import urllib2
import yaml
import re
import logging                                                                  
from pymongo import MongoClient
                                                                                
format = "%(asctime)-15s %(message)s"
logging.basicConfig(format=format, level=logging.DEBUG)

root = "http://www.wenxuecity.com/"
config_file = "config.yaml"


class Crawl(object):

    def __init__(self, uri, depth=2):
        self.home = uri
        config_id = uri[7:].strip("/")
        dbname = config_id.replace(".", "_")
        self.depth = depth
        self.level = 0

        client = MongoClient("localhost:27017")
        self.db = client[dbname]

        self.read_config(config_id)

    def _filter(self, str):
        patterns = self.conf["filter-patterns"]
        for pattern in patterns:
            if re.search(pattern, str):
                return True
        return False

    def get_pageid(self, url):
        _page_id = url.split("/")[-1]
        return _page_id.strip(".html")

    def stop(self, criteria=""):
        return self.level == self.depth

    def write_db(self, article):
        coll = self.db["articles"]
        if coll.find_one({"pageid": article["pageid"]}):
            coll.replace_one({"pageid": article["pageid"]}, article)
        else:
            coll.insert_one(article)

    def get_timestamp(self, soup):
        try:
            ts = soup.time
        except AttributeError:
            ts_tag = self.conf.get("content-timestamp-tag", "time")
            ts_class = self.conf.get("content-timestamp-class", "")
            ts_id = self.conf.get("content-timestamp-id", "")
            ts = soup.find(ts_tag, class_=ts_class, id=ts_id)
        finally:
            if not ts:
                return ""
            if isinstance(ts, bs4.element.Tag):
                return ts.text
            return str(ts)

    def parse_article(self, page):
        try:
            logging.info("open %s" % page)
            page_id = self.get_pageid(page)

            content = urllib2.urlopen(page)
            soup = bs4.BeautifulSoup(content, "html5lib")

            content_ids = self.conf.get("article-page-content", [""])
            title_trim = self.conf.get("title-trim", "")

            title = soup.title.text.strip(title_trim).strip()
            logging.info(title)
            timestamp = self.get_timestamp(soup)
            logging.info(timestamp)

            for _id in content_ids:
                content = soup.find("div", class_=_id["class"], id=_id["id"])
                if content:
                    break
            content_text = content.text.replace("\t", "").replace("\n\n", "\n")

            summary = content_text[:100] + "..."
            logging.info(summary)

            article = {
                "pageid": page_id,
                "page": page,
                "timestamp": timestamp,
                "title": title,
                "summary": summary,
                "content": content_text
            }
            self.write_db(article)
        except AttributeError as e:
            logging.warning("Fail to parse page: %s -- %s" % (page, e))
        except urllib2.HTTPError as e:
            logging.warning("Fail to open page: %s -- %s" % (page, e))

    def parse_page(self, soup, **kwargs):
        cls = self.conf.get("home-page-content-class", "")
        id = self.conf.get("home-page-content-id", "")
        # get the content division
        contents = soup.find_all("div", class_=cls, id=id)

        links = []
        for content in contents:
            _links = content.find_all("a")
            links.extend(_links)
        links = [x["href"] for x in links if "href" in x.attrs]

        return filter(self._filter, links)

    def read_config(self, website):
        with open(config_file, "r") as f:
            conf = yaml.load(f)
        self.conf = conf[website]

    def crawl(self, page):
        content = urllib2.urlopen(page)
        soup = bs4.BeautifulSoup(content, "html5lib")
        links = self.parse_page(soup)
        for link in links:
            if not re.search("^http", link):
                link = page + link
            if self.stop():
                self.level -= 1
                self.parse_article(link)
            self.level += 1
            self.crawl(link)


spider = Crawl(root, depth=1)
spider.crawl(spider.home)
