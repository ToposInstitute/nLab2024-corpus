import os 
import re
from tqdm import tqdm
import spacy
from spacy_conll import init_parser

os.chdir('/NetMath/nLab2024/2024')
if os.path.exists('nlab_new.json'):
    os.remove('nlab_new.json')

nlp = spacy.load("en_core_web_lg")

conll_parser = init_parser(
    "en_core_web_sm", 
    "spacy", 
    #include_headers=True,
    #ext_names={"conll_pd": "pandas"},
)

nlp.max_length = 15000000

page = ""

# New output portion to generate CoNLL-U-like format
def get_conllu_format(doc):
    clines = []
    for sent_id, sent in enumerate(doc.sents, start=1):
        clines.append(f"# sent_id = {sent_id}")
        clines.append(f"# text = {sent.text}")
        for token_id, token in enumerate(sent, start=1):
            line = [
                token_id,  # ID
                token.text,  # FORM
                token.lemma_,  # LEMMA
                token.pos_,  # UPOS
                token.tag_,  # XPOS
                "_",  # FEATS (can be replaced with actual features)
                token.head.i - token.sent[0].i + 1 if token.head != token else 0,  # HEAD
                token.dep_,  # DEPREL
                "_",  # DEPS
                "_" if token.whitespace_ else "SpaceAfter=No"  # MISC
            ]
            clines.append("\t".join(map(str, line)))
        clines.append("")
    return "\n".join(clines)

with open('nlab_clean.json', 'r', encoding="utf-8") as input, open('nlab2024.conll', 'w', encoding="utf-8") as output:
    lines = []   
    halt = True
    items = list(range(56000))
    cnt = 0
    for item in tqdm(items):
        rec = input.readline()
        if "{" in rec:
            data = ''.join(lines)
            data = re.sub(' - ', ' ', data)
            data = re.sub('\n', ' ', data)            
            data = re.sub(r'\s+', ' ', data)
            data = re.sub(r'{', '\n', data)            
            doc = conll_parser(data)
            conllu_output = get_conllu_format(doc)
            output.write(conllu_output)
            lines = []
            cnt += 1
        elif "}" in rec:
            rec = ""
        elif rec == "":
            break           
        lines.append(rec)
