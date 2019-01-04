# sudo permission is required.
# learned from https://github.com/nltk/nltk/wiki/Stanford-CoreNLP-API-in-NLTK
# The following command in bash is needed to start the Stanford NLP server:
'''
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer \
-preload tokenize,ssplit,pos,lemma,ner,parse,depparse \
-status_port 9090 -port 9090 -timeout 15000 &
'''

import pickle
#from stanfordcorenlp import StanfordCoreNLP

#nlp = StanfordCoreNLP(r'./NLP/stanford-corenlp-full-2018-10-05')

from nltk.parse import CoreNLPParser
from nltk.parse.corenlp import CoreNLPDependencyParser

# Tokenizer
parser = CoreNLPParser(url='http://localhost:9091')
# POS Tagger
pos_tagger = CoreNLPParser(url='http://localhost:9091',tagtype='pos')
# NER Tagger
ner_tagger = CoreNLPParser(url='http://localhost:9091',tagtype='ner')
# Neural Dependency Parser
dep_parser = CoreNLPDependencyParser(url='http://localhost:9091')

# Narratives are not simply description of the process - numerical data can do better. They are more for extraction of causations.
narratives = ["Higher tea-cup temperature will accelerate the process.", "Lower room temperature will decelerate the process."]
outputs = []

print("starting...")
for narrative in narratives:
    output = []
    # Narrative itself
    output.append(narrative)
    # Tokenize
    output.append(list(parser.tokenize(narrative)))
    # Part of Speech
    output.append(list(pos_tagger.tag(narrative.split())))
    # Named Entities
    output.append(list(ner_tagger.tag(narrative.split())))
    # Neural dependencies
    parses = dep_parser.parse(narrative.split())
    output.append([[(governor, dep, dependent) for governor, dep, dependent in parse.triples()] for parse in parses][0]) # remove the extra []

    print(output)
    outputs.append(output)

f = open("processed_narratives", "wb+")
pickle.dump(outputs, f)
print("dunped.")
f.close()
