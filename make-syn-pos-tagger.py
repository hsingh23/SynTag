import nltk

patterns = [
    (r'.*ing$', 'vbg'),               # gerunds
    (r'.*ed$', 'vbd'),               # gerunds
    (r'.*s$', ''),                 # plural nouns
    (r'.*es$', 'vbz'),                 # present tense, 3rd person singular
    (r'^-?[0-9]+(.[0-9]+)?$', 'CD'),   # cardinal numbers
    (r'(The|the|A|a|An|an)$', 'AT'),   # articles
    (r'.*able$', 'JJ'),                # adjectives
    (r'.*ness$', 'NN'),                # nouns formed from adjectives
    (r'.*ly$', 'RB'),                  # adverbs
    (r'.*', 'NN')                      # nouns (default)
]

lookup = nltk.defaultdict(list)
brown_tags = nltk.corpus.brown.tagged_words()
treebank_tags = nltk.corpus.treebank.tagged_words()

brown_sent_tags = nltk.corpus.brown.tagged_sents()
treebank_sent_tags = nltk.corpus.treebank.tagged_sents()

brown_bigram_tagger = nltk.BigramTagger(brown_sent_tags)
treebank_bigram_tagger = nltk.BigramTagger(treebank_sent_tags)

for k, v in brown_tags:
    lookup[k.lower()] = v.lower()
for k, v in treebank_tags:
    if k not in lookup:
        lookup[k.lower()] = v.lower()

t0 = nltk.RegexpTagger(patterns, backoff=nltk.DefaultTagger('n'))
t1 = nltk.UnigramTagger(model=lookup, backoff=t0)
t2 = nltk.BigramTagger(brown_sent_tags, backoff=t1)
t3 = nltk.BigramTagger(treebank_sent_tags, backoff=t2)

from cPickle import dump
output = open('syn-pos-tagger.pkl', 'wb')
dump(t3, output, -1)
output.close()
output = open('syn-pos-tagger-bak.pkl', 'wb')
dump(t3, output, -1)
output.close()
