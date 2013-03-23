from re import sub, split
from nltk import word_tokenize
from nltk.corpus import wordnet as wn
from itertools import chain
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
    normalized = sub(r'[^A-z0-9; ,.\?!]', '', search.lower())
    normalized_sents = split(r'[.!\?]', normalized)
    tokenized_sents = filter(lambda a: len(a) != 0, [word_tokenize(a) for a in normalized_sents])
    tagged_sents = tagger.batch_tag(tokenized_sents)
    return tagged_sents


def filtered_for_syn(sents):
    my_sents = []
    for sent in sents:
        my_sent = []
        for word_pair in sent:
            word = word_pair[0]
            pos = word_pair[1].lower()
            if pos in simple_tags:
                try:
                    my_sent.append(tensify(syn[word + "." + simple_tags[pos]], pos))
                except KeyError:
                    pass
                    # Makes the data more unreliable - but may be a feature to enable later
                    # w = tensify(list(set(chain.from_iterable(
                    #     [s.lemma_names for s in wn.synsets(word, simple_tags[pos])]
                    # ))), pos)
                    # my_sent.append(w if len(w) > 0 else [word])
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
