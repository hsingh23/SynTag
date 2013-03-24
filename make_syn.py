from nltk.corpus import wordnet as wn
import json
import redis
import urlparse

syn = {}
json_syn = {}
compiled_syn = {}

for synset in wn.all_synsets():
    lemmas = synset.lemma_names
    dname = synset.name.rpartition('.')[0]
    name = dname.rpartition('.')[0]
    syn[dname] = set(lemmas) if dname not in syn else syn[dname].union(set(lemmas))

for k, v in syn.iteritems():
    if len(v) > 0 and k.partition(".")[0] not in v:
        compiled_syn[k] = list(v)
        json_syn[k] = json.dumps(list(v))

# url = urlparse.urlparse("redis://rediscloud:CG9cBFC10pZORJVL@pub-redis-19126.us-east-1-2.3.ec2.garantiadata.com:19126")
# r = redis.Redis(host=url.hostname, port=url.port, password=url.password)
# r.mset(json_syn)

from cPickle import dump
output = open('syn.pkl', 'wb')
dump(compiled_syn, output, -1)
output.close()

output = open('syn_json.pkl', 'wb')
dump(json_syn, output, -1)
output.close()