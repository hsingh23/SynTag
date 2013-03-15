from re import sub, split
from nltk import word_tokenize
from nltk.corpus import wordnet as wn
from itertools import chain
from random import choice
nouns = ['nn', 'nns', 'nnp', 'nnps', 'nr', 'nr$', 'nrs', 'n']
verbs = ['vb', 'vbd', 'vbg', 'vbn', 'vbp', 'vbz', 'v']
adj = ['jj', 'jjr', 'jjs', 'jjt', 'a']
adverb = ['rb', 'rbr', 'rbs', 'r']
simple_tags = {}
for a in nouns:
    simple_tags[a] = 'n'
for a in verbs:
    simple_tags[a] = 'v'
for a in adj:
    simple_tags[a] = 'a'
for a in adverb:
    simple_tags[a] = 'r'
from cPickle import load


inp = open("syn/syn.pkl")
syn = load(inp)
inp.close()

inp = open("syn/syn-pos-tagger.pkl")
tagger = load(inp)
inp.close()


def tagged(search):
    normalized = sub(r'[^A-z0-9; ,.\?!]', '', search.lower())
    normalized_sents = split(r'[.!\?]', normalized)
    tokenized_sents = filter(lambda a: len(a) != 0, [word_tokenize(a) for a in normalized_sents])
    tagged_sents = tagger.batch_tag(tokenized_sents)
    return tagged_sents


def filtered_for_syn(sents):
    my_sents = []
    for i, sent in enumerate(sents):
        my_sent = []
        for j, word_pair in enumerate(sent):
            word = word_pair[0]
            pos = word_pair[1].lower()
            if pos in simple_tags:
                try:
                    my_sent.append(syn[word + "." + simple_tags[pos]])
                except KeyError:
                    w = list(set(chain.from_iterable(
                        [s.lemma_names for s in wn.synsets(word, simple_tags[pos])]
                    )))
                    my_sent.append(w if len(w) > 0 else [word])
            else:
                my_sent.append([word])
        my_sents.append(my_sent)
    return my_sents

fed = filtered_for_syn


def make_sentence(syn_sents):
    mystr = []
    for sent in syn_sents:
        for i, a in enumerate(sent):
            mystr.append(choice(a).title() if i == 0 else choice(a))
        mystr.append(".")
    return " ".join(mystr).replace("_", " ")


def do_it_all(s):
    a = make_sentence(filtered_for_syn(tagged(s)))
    return sub(r' (?=[\.\?,])', '', a)
