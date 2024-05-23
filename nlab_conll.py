import os 
import re
from tqdm import tqdm
import spacy
from spacy_conll import init_parser

os.chdir('/NetMath/nlab/data')
if os.path.exists('nlab_new.json'):
    os.remove('nlab_new.json')

nlp = spacy.load("en_core_web_lg")

conll_parser = init_parser(
    "en_core_web_sm", 
    "spacy", 
    #include_headers=True,
    ext_names={"conll_pd": "pandas"},
)
#nlp.add_pipe("conll_formatter", last=True)
nlp.max_length = 15000000

page = ""
with open('nlab_clean.json', 'r', encoding="utf-8") as input, open('nlab_new.json', 'w', encoding="utf-8") as output:
    lines = []   
    items = list(range(1800000))
    cnt = 0
    for item in tqdm(items):
        rec = input.readline()
        if "PAGINATE" in rec:
            data = ''.join(lines)    
            data = re.sub(' - ', ' ', data)
            data = re.sub(r'\s+', ' ', data)
            data = re.sub('PAGINATE', ' ', data)            
            doc = conll_parser(data)
            conll = doc._.conll_str
            #conll = doc._.pandas
            if cnt > 0:
                output.write("PAGINATE\n")
            article = "# page = " + page + "\n"
            output.write(article)
            output.write(conll)
            lines = []
            cnt += 1
        elif "page = " in rec:
            match = re.search("page = (.*)", rec)
            if match:
                page = match.group(1)
            rec = re.sub(r'page = .*', '', rec)
        elif rec == "":
            break           
        lines.append(rec) 


