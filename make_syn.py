from nltk.corpus import wordnet as wn
import json
import redis
import urlparse

syn = {}
retsyn = {}

for synset in wn.all_synsets():
    lemmas = synset.lemma_names
    dname = synset.name.rpartition('.')[0]
    name = dname.rpartition('.')[0]
    syn[dname] = set(lemmas) if dname not in syn else syn[dname].union(set(lemmas))

for k, v in syn.iteritems():
    if len(v) > 0:
        syn[k] = list(v)
        retsyn[k] = json.dumps(list(v))
    else:
        del syn[k]

url = urlparse.urlparse("redis://rediscloud:CG9cBFC10pZORJVL@pub-redis-19126.us-east-1-2.3.ec2.garantiadata.com:19126")
r = redis.Redis(host=url.hostname, port=url.port, password=url.password)
r.mset(retsyn)

from cPickle import dump
output = open('syn.pkl', 'wb')
dump(syn, output, -1)
output.close()

output = open('syn.json', 'wb')
output.write(json.dumps(syn))
output.close()