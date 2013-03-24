from re import sub, split
from nltk import word_tokenize
# from nltk.corpus import wordnet as wn
# from itertools import chain
from random import choice
nouns = ['nn', 'nns', 'n', 'uh']
verbs = ['vb', 'vbd', 'vbg', 'vbn', 'vbp', 'vbz', 'v']
adj = ['jj', 'jjr', 'jjs', 'jjt', 'a']
# adverb = ['rb', 'rbr', 'rbs', 'r']
simple_tags = {}
for a in nouns:
    simple_tags[a] = 'n'
for a in verbs:
    simple_tags[a] = 'v'
for a in adj:
    simple_tags[a] = 'a'
# for a in adverb:
#     simple_tags[a] = 'r'
from cPickle import load


inp = open("syn.pkl")
syn = load(inp)
inp.close()

inp = open("syn-pos-tagger.pkl")
tagger = load(inp)
inp.close()


def tagged(search):
    cleaned = sub(r'[^A-z0-9; ,.\?!]', '', search.lower())
    normalized_sents = split(r'[.!\?]', cleaned)
    tokenized_sents = filter(lambda a: len(a) != 0, (word_tokenize(a) for a in normalized_sents))
    tagged_sents = tagger.batch_tag(tokenized_sents)
    return tagged_sents


def filtered_for_syn(sents, p=1):
    return [[get_syn_for_word_pair(word, pos) for word, pos in ((word_pair[0], word_pair[1].lower()) for word_pair in sent)] for sent in sents]


def make_sentence(syn_sents):
    mystr = []
    for sent in syn_sents:
        mystr.append(choice(sent[0]).title())
        for a in sent[1:]:
            try:
                mystr.append(choice(a))
            except Exception:
                pass
        mystr.append(".")
    # sub out the bad stuff when making sentence
    return sub(r' (?=[\.\?,;])', '', " ".join(mystr).replace("_", " "))

# Helper functions


def tensify(syn_list, pos):
    # for verb congugation
    s_list = []
    # past tense, past participle
    if pos in ["vbd", "vbn"]:
        for word, tag in ((a, tagger.tag[a]) for a in s_list):
            if tag == pos:
                s_list.append(word)
            elif tag == 'vbg' and len(word) > 3 and word[-3:] == "ing":
                s_list.append(word[:-3] + "ed")
            elif tag == 'vbz' and len(word) > 2 and word[-1:] == "s":
                s_list.append(word[:-2] + "ed" if word[-2] == 'e' else word[:-1] + "ed")
            elif tag == 'vb':
                if True or real_word(word + "ed"):
                    s_list.append(word + "ed")

    # present participle or gerund
    elif pos == "vbg":
        for word, tag in ((a, tagger.tag[a]) for a in s_list):
            if tag == pos:
                s_list.append(word)
            elif tag in ["vbd", "vbn"] and len(word) > 2 and word[-2:] == "ed":
                s_list.append(word[:-2] + "ing")
            elif tag == 'vbz' and len(word) > 2 and word[-1:] == "s":
                s_list.append(word[:-2] + "ing" if word[-2] == 'e' else word[:-1] + "ing")
            elif tag == 'vb':
                if True or real_word(word + "ing"):
                    s_list.append(word + "ing")
    # present tense, 3rd person singular
    elif pos == "vbz":
        for word, tag in ((a, tagger.tag[a]) for a in s_list):
            if tag == pos:
                s_list.append(word)
            elif tag in ["vbd", "vbn"] and len(word) > 2 and word[-2:] == "ed":
                s_list.append(word[:-1] + "s")
            elif tag == 'vbz' and len(word) > 2 and word[-1:] == "s":
                s_list.append(word[:-1] + "d" if word[-2:] == "es" else word[:-1] + "ed")
            elif tag == 'vb':
                s_list.append(word + "es")
    else:
        return syn_list
    return s_list


def get_syn_for_word_pair(word, pos):
    if pos in simple_tags:
        if word[:-1] + "." + simple_tags[pos] in syn:
            return tensify(syn[word[:-1] + "." + simple_tags[pos]], pos)
        elif word + "." + simple_tags[pos] in syn:
            return tensify(syn[word + "." + simple_tags[pos]], pos)
        else:
            return [word]
    else:
        return [word]
