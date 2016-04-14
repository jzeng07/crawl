#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import bs4
import urllib2
import yaml
import re
import logging
from pymongo import MongoClient

format = "%(asctime)-15s %(message)s"
logging.basicConfig(format=format, level=logging.DEBUG)

config_file = "config.yaml"
html = """
<html>
<head>
<meta http-equiv="X-UA-Compatible" content="IE=9; IE=8; IE=7; IE=EDGE">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</head>
"""

class Crawl(object):

    def __init__(self, webname):
        self.level = 0
        self.read_config(webname)

        self.home = self.conf["uri"]
        self.depth = self.conf["depth"]

        client = MongoClient("localhost:27017")
        self.db = client[webname]


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
        ts_ids = self.conf.get("article-timestamp", [{}])
        for _id in ts_ids:
            tag = _id.get("tag", "")
            cls = _id.get("class", "")
            id = _id.get("id", "")
            ts = soup.find(tag, class_=cls, id=id)
            if ts:
                return ts.text

    def remove_content_links(self, content):
        try:
            while True:
                content.a.extract()
        except AttributeError:
            return

    def get_content(self, soup, uri):
        content_ids = self.conf.get("article-page-content", [{}])
        for _id in content_ids:
            tag = _id.get("tag", "")
            cls = _id.get("class", "")
            id = _id.get("id", "")
            content = soup.find(tag, class_=cls, id=id)
            if content:
                break
        self.remove_content_links(content)
        content_text = re.sub("\t\s+|\n\s+", "", content.text).strip()
        summary = content_text[:100] + "..."
        self.absolute_resources(content, uri)
        return (summary, content.prettify())

    def get_uripath(self, uri):
        _uri = uri.split("/")[:-1]
        return "/".join(_uri)

    def absolute_resources(self, content, uri):
        imgs = content.find_all("img")
        for img in imgs:
            if "src" in img.attrs:
                print img["src"]
                if re.search("^/", img["src"]):
                    img["src"] = self.home + img["src"]

    def write_file(self, title, content, pageid):
        soup = bs4.BeautifulSoup(html.decode("utf-8"), "html5lib")
        title_tag = soup.new_tag("title")
        title_tag.string = title
        soup.head.insert(1, title_tag)
        # soup.body.insert(1, content)

        doc_root = os.path.join(os.path.abspath(os.curdir), "docs")
        if not os.path.exists(doc_root):
            os.makedirs(doc_root)
        with open(os.path.join(doc_root, "%s.html" % pageid), "w") as f:
            f.write(str(soup))
            f.write("<body>")
            f.write(content.encode("utf-8"))
            f.write("</body></html>")

    def parse_article(self, page):
        try:
            logging.info("open %s" % page)
            page_id = self.get_pageid(page)

            content = urllib2.urlopen(page)
            soup = bs4.BeautifulSoup(content, "html5lib")

            title_trim = self.conf.get("title-trim", "")
            title = re.sub("\n\s+|\t\s+|\|", "", soup.title.text)
            title = re.sub(title_trim, "", title).strip()
            logging.info(title)

            timestamp = self.get_timestamp(soup)
            logging.info(timestamp)

            summary, content_text = self.get_content(soup, page)
            logging.info(summary)

            if os.getenv("DEBUG"):
                self.write_file(title, content_text, page_id)

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
        links = []

        home_content_ids = self.conf.get("home-page-content", [{}])
        for _id in home_content_ids:
            tag = _id.get("tag", "")
            cls = _id.get("class", "")
            id = _id.get("id", "")

            # get the content division
            contents = soup.find_all(tag, class_=cls, id=id)

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
        try:
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
        except urllib2.HTTPError as e:
            logging.warning("Fail to open page: %s -- %s" % (page, e))


spider = Crawl("wenxuecity")
spider.crawl(spider.home)
