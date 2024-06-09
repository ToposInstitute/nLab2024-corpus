#!/usr/bin/env python

import urllib.parse
import scrapy
from scrapy.crawler import CrawlerProcess
import warnings
import os
import re

os.chdir("/NetMath/nLab2024/2024")
if os.path.exists('nlab_pages.json'):
    os.remove('nlab_pages.json')
if os.path.exists('nlab_scrape.json'):
    os.remove('nlab_scrape.json')

warnings.filterwarnings("ignore", category=scrapy.exceptions.ScrapyDeprecationWarning)

cnt = {"delete": 0, "ignore": 0, "err": 0, "empty": 0, "misc": 0,
    "page": 0, "people": 0, "joke": 0, "svg": 0, "meta": 0}

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
        global cnt

        page_name = urllib.parse.unquote_plus(response.url.rsplit("/",1)[-1])
        if "Sandbox" in page_name or " > history" in page_name:
            page_name = "DELETE"
            source = ""
            cnt["delete"] += 1
        else: 
            try:
                source = response.css("textarea::text").get()
                source = re.sub("\r\n", "\n", source) 
                type_match = re.search(r'category:\s+(people|joke|svg|meta|empty)', source)
                if type_match:
                    type = type_match.group(1)
                    match type:
                        case "people":
                            cnt["people"] += 1
                        case "joke":
                            cnt["joke"] += 1
                        case "svg":
                            cnt["svg"] += 1
                        case "meta":
                            cnt["meta"] += 1
                        case "empty":
                            cnt["empty"] += 1
                        case "people":
                            cnt["people"] += 1
                    page_name = "IGNORE"
                    source = ""    
                    cnt["ignore"] += 1
                else:     
                    cnt["page"] += 1                               
            except Exception as err:
                page_name = "ERR"
                source = ""    
                cnt["err"] += 1             
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

    for key, value in cnt.items():
        print(key, "   ", value)


    os.system('echo \a')

