import re
import spacy
from spacy_conll import init_parser
import subprocess

nlp = spacy.load("en_core_web_sm")
conll_parser = init_parser(
    "en_core_web_sm", 
    "spacy", 
    include_headers=True
)

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

def parse_regex(pattern, xml_string):
    match = re.search(pattern, xml_string)
    if match:
        return int(match.group(1))
    else:
        return None

text = "This is a sample sentence for parsing. This is another sentence."
s = stats(text)

print(parse_regex(r'<dep name="ROOT">(\d+)</dep>', s))
print(parse_regex(r'<sentences>(\d+)</sentences>', s))
