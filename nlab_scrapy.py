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

cnt = {"concept": 0, "people": 0, "err": 0, "empty": 0,
       "joke": 0, "svg": 0, "meta": 0, "reference": 0, 
       "sandbox": 0, "history": 0, "symbol": 0, "survey": 0, 
       "first_idea": 0}
info = {}
page_name = ""
source = ""
cat = ""

def remove_page(category):
    global page_name
    global source
    global cnt
    global info
    global cat
    #page_name = "DELETE"
    source = ""
    cat = category
    cnt[category] += 1
    if category in info:
        info[category].append(page_name)
    else:
        info[category] = [page_name]


class nLabPagesSpider(scrapy.Spider):
    name = "nlab_pages"    
    start_urls = [
        #"https://ncatlab.org/nlab/list/analysis"
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
        #global info
        page_names = response.css("ul li a::text").getall()
        with open("nlab_page_names.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(page_names))

        #with open("nlab_page_names_concepts.txt", "r", encoding="utf-8") as f:
            #page_names = f.read().split()    

        page_links = response.css("ul li a::attr(href)").getall()

        # with open("debug.txt", "w", encoding="utf-8") as debug:
        #     pages = len(page_names)
        #     for index in range(pages):
        #         debug.write(page_names[index] + "   " + page_links[index] + "\n")
        #exit()


        source_links = [ url.replace("/show/", "/source/")
                         for url in page_links ]
        yield from response.follow_all(source_links, self.parse_page_source)

    def parse_page_source(self, response):
        global cnt
        global info
        global page_name
        global source
        global cat

        page_name = urllib.parse.unquote_plus(response.url.rsplit("/",1)[-1])
        page_name = page_name.lower()
        if "sandbox" in page_name:
            remove_page("sandbox")
        elif "> history" in page_name:            
            remove_page("history")
        elif re.search(r'^\W', page_name):            
            remove_page("symbol")
        elif "survey" in page_name:
            remove_page("survey")
        elif re.search(r'^\d', page_name):            
            pass #remove_page("number")
        elif "first idea" in page_name:    
            remove_page("first_idea")
        else: 
            try:
                source = response.css("textarea::text").get()
                source = re.sub("\r\n", "\n", source) 
                categories = r'category:\s+(people|joke|svg|meta|empty|reference|survey)'
                type_match = re.search(categories, source)
                if type_match:
                    type = type_match.group(1)
                    remove_page(type)                                                      
                else:     
                    cnt["concept"] += 1  
                    cat = "concept"
                    if "concept" in info:
                        info["concept"].append(page_name)
                    else:
                        info["concept"] = [page_name]
                
            except Exception as err:
                page_name = "DELETE"
                source = ""    
                cnt["err"] += 1    
                remove_page("err")  
        if cat == "concept":       
            yield {
                "name": page_name,
                "url": response.url,
                "source": source,
            }
        else:
            yield

if __name__ == "__main__":
    process = CrawlerProcess(settings={
        "FEEDS": {
            "nlab_scrape.json": {"format": "json"},
        },
    })
    process.crawl(nLabPagesSpider)
    process.start()

    with open("nlab_report.txt", "w", encoding="utf-8") as report:      
        for name, data in info.items():
            report.write(name + "\n")
            for page_name in sorted(data):
                report.write("   " + page_name + "\n")  

    cnt = dict(sorted(cnt.items()))
    for key, value in cnt.items():
        print(key, "   ", value)

    os.system('echo \a')