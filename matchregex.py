import os 
import re
import subprocess
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

def stats(data):
    doc = conll_parser(data)
    conll = doc._.conll_str
    perl_command = ['perl', 'conllu-stats.pl']
    process = subprocess.Popen(perl_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate(input=conll)

    if process.returncode != 0:
        print("Error occurred during the Perl script execution:")
        print(stderr)
    return stdout

def match_regex(pattern, xml_string):
    match = re.search(pattern, xml_string)
    if match:
        return int(match.group(1))
    else:
        return None

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

with open('nlab_2024clean.json', 'r', encoding="utf-8") as input, \
     open('nlab2024.conll', 'w', encoding="utf-8") as output, \
     open('nlab2024report.txt', 'w', encoding="utf-8") as report:
    lines = []   
    halt = True
    items = list(range(41000))
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
            #report.write(str(len(list(doc.sents)))+"\n")

            num_sentences = 0

            # Iterate over sentences to count them and print their root tokens
            for sentence in doc.sents:
                num_sentences += 1
                report.write(f"Sentence {num_sentences} root: {sentence.root.text}\n")
                if sentence.root.text == " \n ":
                    report.write(f"  Sentence text: {sentence.text} \n")

            conllu_output = get_conllu_format(doc)
            output.write(conllu_output)
            lines = []
            cnt += 1
        elif "}" in rec:
            rec = ""
        elif rec == "":
            output.write("]\n")
            break           
        lines.append(rec)
