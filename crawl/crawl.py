#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import getopt
import bs4
import urllib2
import urlparse
import yaml
import re
import logging
import StringIO
from pymongo import MongoClient
from PIL import Image
from threading import Thread

format = "%(asctime)-15s %(message)s"
logging.basicConfig(format=format, level=logging.DEBUG)

config_file = "config.yaml"

html = """
<html>
<head>
<meta charset=utf-8"/>
</head>
"""

class NotImplementError(Exception):
    pass


class Crawl(Thread):

    def __init__(self, webname, output=False, count=1024):
        Thread.__init__(self)
        self.level = 0
        self.read_config(webname)

        self.root = self.conf["root"]
        self.depth = self.conf["depth"]

        client = MongoClient("localhost:27017")
        self.db = client["mass"]

        # A table store the fetched web names and their aliases
        self.fetched_webs = self.db["fetched_webs"]
        if not self.fetched_webs.find_one({"name": self.conf["name"]}):
            self.fetched_webs.insert(
                {"name": self.conf["name"], "alias": self.conf["alias"]})
        self.output = output
        self.count = count
        self._remove_old()

    def _remove_old(self):
        # if keep current articles only, remove all old records and files
        keep_old = self.conf.get("keep-old", False)
        if not keep_old:
            coll = self.db[self.conf["name"]]
            coll.remove({})

            doc_root = os.path.join(
                os.path.abspath(os.curdir), "docs/%s"%self.conf["name"])
            if os.path.exists(doc_root):
                for file in os.listdir(doc_root):
                    os.remove(os.path.join(doc_root, file))
            img_dir = os.path.join("../webserver/public/images", self.conf["name"])
            if os.path.exists(img_dir):
                for file in os.listdir(img_dir):
                    os.remove(os.path.join(img_dir, file))


    def _filter(self, str):
        patterns = self.conf["article-links-filter-patterns"]
        for pattern in patterns:
            if re.search(pattern, str):
                return True
        return False

    def _fetch_conf(self, conf):
        if not isinstance(conf, dict):
            raise Exception("Config type must be dict")
        tag = conf.get("tag", "")
        cls = conf.get("class", "")
        id = conf.get("id", "")
        return (tag, cls, id)

    def get_pageid(self, url):
        _page_id = url.split("/")[-1]
        return _page_id.strip(".html")

    def stop(self, criteria=""):
        return self.level == self.depth

    def write_db(self, article):
        coll = self.db[self.conf["name"]]

        if coll.find_one({"pageid": article["pageid"]}):
            coll.replace_one({"pageid": article["pageid"]}, article)
        else:
            coll.insert_one(article)

    def get_timestamp(self, soup):
        ts_ids = self.conf.get("article-timestamp", [])
        for _id in ts_ids:
            tag, cls, id = self._fetch_conf(_id)
            ts = soup.find(tag, class_=cls, id=id)
            if ts:
                return ts.text
        return ""

    def remove_content_links(self, content):
        try:
            while True:
                content.a.extract()
        except AttributeError:
            return

    def get_comments(self, soup):
        try:
            if "article-comments" not in self.conf:
                return ""
            comments = []
            usr_date = self.conf["article-comments"]["user-date"]
            comment = self.conf["article-comments"]["comment"]

            usr_date_tag, usr_date_class, usr_date_id = \
                self._fetch_conf(usr_date)
            comment_tag, comment_class, comment_id = \
                self._fetch_conf(comment)

            usr_date = soup.find_all(
                usr_date_tag, class_=usr_date_class, id=usr_date_id)
            comment = soup.find_all(
                comment_tag, class_=comment_class, id=comment_id)
            for _usr_date, _comment in zip(usr_date, comment):
                comments.append(str(_usr_date) + str(_comment))

            return comments
        except AttributeError as e:
            logging.warning(e)
            return ""

    def get_uripath(self, uri):
        _uri = uri.split("/")[:-1]
        return "/".join(_uri)

    def adjust_resources(self, content):
        imgs = content.find_all("img")
        for img in imgs:
            if "src" in img.attrs:
                if re.search("^/", img["src"]):
                    img["src"] = urlparse.urljoin(self.root, img["src"])

    def write_file(self, title, content, pageid):
        soup = bs4.BeautifulSoup(html.decode("utf-8"), "html5lib")
        title_tag = soup.new_tag("title")
        title_tag.string = title
        soup.head.insert(1, title_tag)
        # soup.body.insert(1, content)

        doc_root = os.path.join(
            os.path.abspath(os.curdir), "docs/%s"%self.conf["name"])
        if not os.path.exists(doc_root):
            os.makedirs(doc_root)

        with open(os.path.join(doc_root, "%s.html" % pageid), "w") as f:
            f.write(str(soup))
            f.write("<body>")
            f.write("<h3>%s</h3>" % title.encode("utf-8"))
            f.write(content.encode("utf-8"))
            f.write("</body></html>")

    def parse_head_title(self, soup):
        title_trim = self.conf.get("title-trim", "")
        title = re.sub("\n\s+|\t\s+|\|", "", soup.title.text)
        title = re.sub(title_trim, "", title).strip()
        logging.info(title)
        return title


    def download_image(self, imgurl):
        try:
            img_dir = "../webserver/public/images/"

            if imgurl.startswith("/"):
                imgurl = urlparse.urljoin(self.root, imgurl)
            logging.info("downloading image: {}".format(imgurl))

            resp = urllib2.urlopen(imgurl)
            img = Image.open(StringIO.StringIO(resp.read()))
            # img = img.resize((128, 128))

            img_path = os.path.join(img_dir, self.conf["name"])
            if not os.path.exists(img_path):
                os.makedirs(img_path)

            filename = urlparse.urlparse(imgurl).path
            filename = filename.split("/")[-1]
            img.save(os.path.join(img_path, filename))
            return "%s/%s" % (self.conf["name"], filename)
        except Exception as e:
            logging.exception(e)
            pass


    def get_content(self, soup):
        content_ids = self.conf.get("article-content", [])

        for _id in content_ids:
            tag, cls, id = self._fetch_conf(_id)
            content = soup.find(tag, class_=cls, id=id)
            if content:
                break

        imgs = soup.find_all('img')
        for img in imgs:
            # patch for jianshu
            img["src"] = img["src"].split("?")[0]
            if re.search("jpeg$|jpg$", img["src"]):
                break
        else:
            img = None

        img_link = ""
        if img:
            img_link = self.download_image(img['src'])

        self.remove_content_links(content)
        content_text = re.sub("\t\s+|\n\s+", "", content.text).strip()
        summary = re.sub("\\n+", "", content.text[:self.conf["summary-len"]]) + "..."

        self.adjust_resources(content)

        comments = self.get_comments(soup)
        content = content.prettify()

        comments = "".join(comments)
        comments = "<div class='comments'>\n" + comments + "\n</div>"
        content = content + comments.decode("utf-8")

        return (summary, content, img_link)

    def parse_content(self, soup):
        article_content_containers = self.conf.get(
            "article-content-container", [])

        content_container = None
        for container in article_content_containers:
            print container
            ctner_tag, ctner_cls, ctner_id = self._fetch_conf(container)
            content_container = soup.find(
                ctner_tag, class_=ctner_cls, id=ctner_id)
            if content_container:
                break

        # cont_title_tag, cont_title_cls, cont_title_id = \
        #     self._fetch_conf(self.conf["article-content-title"])
        # content_title = content_container.find(
        #     cont_title_tag, class_=cont_title_cls, id=cont_title_id).text

        return self.get_content(content_container)

    def parse_article(self, page):
        try:
            logging.info("open %s" % page)
            page_id = self.get_pageid(page)

            content = urllib2.urlopen(page)
            soup = bs4.BeautifulSoup(content, "html5lib")

            title = self.parse_head_title(soup)

            timestamp = self.get_timestamp(soup)
            logging.info(timestamp)

            summary, content_text, content_img = self.parse_content(soup)
            if not content_img:
                content_img = "default.jpeg"
            logging.info(summary)

            if self.output:
                self.write_file(title, content_text, page_id)

            article = {
                "pageid": page_id,
                "page": page,
                "timestamp": timestamp,
                "title": title,
                "summary": summary,
                "content": content_text,
                "image": content_img
            }
            self.write_db(article)
        except AttributeError as e:
            logging.exception("Fail to parse page: %s -- %s" % (page, e))
        except urllib2.HTTPError as e:
            logging.exception("Fail to open page: %s -- %s" % (page, e))

    def parse_page(self, soup, **kwargs):
        links = []

        home_content_ids = self.conf.get("home-page-content", [{}])
        for _id in home_content_ids:
            tag, cls, id = self._fetch_conf(_id)

            # get the content division
            contents = soup.find_all(tag, class_=cls, id=id)

            for content in contents:
                _links = content.find_all("a")
                links.extend(_links)
            links = [x["href"] for x in links if "href" in x.attrs]
            # links = [urlparse.urlparse(x).path for x in links]
            links = list(set(links))

        links = filter(self._filter, links)
        return links

    def read_config(self, website):
        with open(config_file, "r") as f:
            conf = yaml.load(f)
        try:
            self.conf = conf[website]
        except KeyError:
            raise NotImplementError(
                "The website '%s' crawler is NOT implemented yet, SKIP it" % website)

    def crawl(self, page):
        if not self.conf:
            return
        try:
            if self.stop():
                self.level -= 1
                Thread(target=self.parse_article, args=(page,)).start()
                return

            content = urllib2.urlopen(page)
            soup = bs4.BeautifulSoup(content, "html5lib")
            links = self.parse_page(soup)
            count = min(self.count, len(links))
            links = links[:count]

            for link in links:
                if not re.search("^http", link):
                    link = urlparse.urljoin(page, link)
                self.level += 1
                self.crawl(link)
        except urllib2.HTTPError as e:
            logging.exception("Fail to open page: %s -- %s" % (page, e))

    def run(self):
        self.crawl(self.root)

    def join(self):
        Thread.join(self)


def print_help():
    print """usage:
    ./crawl.py <-h> <-o> web1 web2 web3 ...
        web1 web2 web3 ...: the webs need to crawl. They must be configured in config.yaml
        -h: to get usage
        -o: if create local file
        -c: The number of fetched articles for each site
    """

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hoc:")
    except getopt.GetoptError:
        print_help()
        sys.exit(2)

    output = False
    count = 1024
    for opt in opts:
        if opt[0] == "-h":
            print_help()
            sys.exit(2)
        if opt[0] == "-o":
            output = True
        if opt[0] == "-c":
            count = int(opt[1])

    if args:
        if "all" in args:
            with open(config_file, "r") as f:
                sites = yaml.load(f).keys()
        else:
            sites = args
    else:
        sites = ["zhihudaily"]

    crawlers = []
    for site in sites:
        try:
            crawler = Crawl(site, output=output, count=count)
            crawler.start()
            crawlers.append(crawler)
        except NotImplementError as e:
            logging.warning(e)
            pass

    map(lambda x: x.join(), crawlers)


if __name__ == "__main__":
    main(sys.argv[1:])
