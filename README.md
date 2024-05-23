# NetMath
Network mathematics software

## nLab corpus 
The development environment for a NLP pipeline to create a nLab corpus requires Python, Perl, Julia and Jupyter notebooks, Pandoc and Microsoft Visual C++ Redistributable. Julia requires the IJulia, Pandoc and JSON packages. 

Run the following to install a language model for spaCy.
`pip install -U pip setuptools wheel
pip install -U spacy
python -m spacy download en_core_web_sm`

`pip install` the following Python packages:
* request
* scrapy
* urllib
* urllib.parse
* spacy_conll[all]
* jupyterlab

To run:

The Perl program conllu-stats.pl needs cpan packages JSON and JSON::Parse and udlib.pm needs to to be included from https://github.com/UniversalDependencies/tools/blob/master/udlib.pm .

### software pipeline

Note: nLabclean.ipynb is a Jupyter lab notebook running Julia

The pipeline is,
nlab_scrapy.py -> nlab_pages.json -> nlab_clean.ipynb -> nlab_clean.json -> nlab_conll.py -> nlab_new.json -> conllu-stats.pl

