#!/usr/bin/env python

import urllib.parse
import scrapy
from scrapy.crawler import CrawlerProcess
import warnings
import os
import re

os.chdir("/NetMath/nlab/data")
if os.path.exists('nlab_pages.json'):
    os.remove('nlab_pages.json')
if os.path.exists('nlab_scrape.json'):
    os.remove('nlab_scrape.json')

warnings.filterwarnings("ignore", category=scrapy.exceptions.ScrapyDeprecationWarning)

delete_cnt = 0
ignore_cnt = 0
empty_cnt = 0
page_cnt = 0

class nLabPagesSpider(scrapy.Spider):
    name = "nlab_pages"    
    start_urls = [
        "https://ncatlab.org/nlab/all_pages",
    ]
    custom_settings = {
        # Be nice to nLab.
        "DOWNLOAD_DELAY": 1, # in secs
        # For debugging.
        "CLOSESPIDER_PAGECOUNT": 0,
        "LOG_LEVEL": "WARNING",
    }

    def parse(self, response):
        page_names = response.css("ul li a::text").getall()
        with open("nlab_page_names_raw.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(page_names))

        page_links = response.css("ul li a::attr(href)").getall()
        source_links = [ url.replace("/show/", "/source/")
                         for url in page_links ]
        yield from response.follow_all(source_links, self.parse_page_source)

    def parse_page_source(self, response):
        global delete_cnt
        global ignore_cnt
        global page_cnt
        global empty_cnt 

        page_name = urllib.parse.unquote_plus(response.url.rsplit("/",1)[-1])
        if "Sandbox" in page_name or " > history" in page_name:
            page_name = "DELETE"
            source = ""
            delete_cnt += 1
        else: 
            try:
                source = response.css("textarea::text").get()
                source = re.sub("\r\n", "\n", source) 
                match = re.search("category: {people|joke|svg|meta}", source)
                if match:
                    page_name = "IGNORE"
                    source = ""    
                    ignore_cnt += 1
                else:
                    page_cnt += 1                   
            except Exception as err:
                page_name = "EMPTY"
                source = ""    
                empty_cnt += 1    
        yield {
            "name": page_name,
            "url": response.url,
            "source": source,
        }

if __name__ == "__main__":
    process = CrawlerProcess(settings={
        "FEEDS": {
            "nlab_scrape.json": {"format": "json"},
        },
    })
    process.crawl(nLabPagesSpider)
    process.start()

    print("Good pages: ", page_cnt)
    print("Empty: ", empty_cnt)
    print("Delete: ", delete_cnt)
    print("Ignore: ", ignore_cnt)
    os.system('echo \a')

