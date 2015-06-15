from apps.utils.msg_util import *
import pysolr
from solr_search_formatter import SolrSearchFormatter
from solr_results_handler import SolrResultsHandler
from django.conf import settings

"""def build_id_query(num_ids):
    
    qparts = []
    id_cnt = 0
    group_count = 1000   # 1024
    for current_group_num in range(0, num_ids/group_count):
        msg('add each part %s' % current_group_num)
        entity_list = [ str(x) for x in range(id_cnt, group_count * (current_group_num+1))]
        id_cnt += len(entity_list)
        qpart = 'entityId:(%s)' % ' OR '.join(entity_list)
        msg(qpart)
        qparts.append(qpart)

    msg('id_cnt: %s' % id_cnt)
    # extra ids
    extra_ids = num_ids % group_count
    msg('extra_ids: %s' % extra_ids)
    if extra_ids > 0:        
        entity_list = [ str(x) for x in range(id_cnt, id_cnt + extra_ids)]
        qpart = 'entityId:(%s)' % ' OR '.join(entity_list)
        qparts.append(qpart)
    
    qparts_fmt = [ '(%s)' % x for x in qparts]
    
    return ' OR '.join(qparts_fmt)
"""
def run_solor_check():
    # Setup a Solr instance. The timeout is optional.
    solr = pysolr.Solr(settings.SOLR_URL, timeout=10)

    #qstr = 'title:dreamcatcher'
    #qstr = 'authorName:Stephen King AND title:dream*'
    #qstr = 'authorName:"shining"'
    qstr = '(Stephen King) AND (dream*)'
    qstr = 'education'
    qstr = "entityId:78"
    qstr = "entityId:(21 OR 78 OR 85)"
    qstr = "(dvObjectType:datasets) AND (entityId:(21 OR 78 OR 85))"


    qstr = build_id_query(1220)  # + ' AND ("siddons")'
    #msgx(qstr)
    #qstr = 'siddons'
    #msgx(qstr)
    #qstr = 'Lewis'
    searchFormatter = SolrSearchFormatter()

    results = solr.search(qstr, **searchFormatter.get_solr_kwargs())

    solr_results = SolrResultsHandler(results)

    msg(type(results))
    #msg(qstr)
    msg('query string len: %s' % len(qstr))
    ##  BREAK!!! BREAK !!!

if __name__=='__main__':
    t0 = time.time()
    run_solor_check()
    t1 = time.time()

    total = t1-t0
    print ('total: %s' % total)
    #timeit.Timer("run_solor_check()", "from __main__ import run_solor_check", number=1)
    #msg(t)
    
    #msg(t.timeit())
    #msg(t.repeat(3, 2000000))
    ##print(timeit.timeit("run_solor_check()", setup="from __main__ import run_solor_check"))

"""
print ('docs', results.docs)
print ('-' * 60)
msgt('facets')#, results.facets)
if len(results.facets) > 0:
    for kval, val_dict in results.facets.items():
        for k, v in val_dict.items():
            msg ("\n%s: %s" % (k, v))
dashes()
print ('grouped', results.grouped)
print ('-' * 60)
print ('hits', results.hits)
print ('-' * 60)
print ('stats', results.stats)
print ('-' * 60)
print ('spellcheck', results.spellcheck)
print ('-' * 60)
print ('qtime', results.qtime)
print ('-' * 60)
#print (dir(results))
print ('-' * 60)
print ('docs', len(results.docs))
msgt('highlighting')
if len(results.highlighting) > 0:
    for kval, val_dict in results.highlighting.items():
        for k, v in val_dict.items():
            print ("%s: %s" % (k, v))
#msg(results.highlighting)
dashes()

cnt = 0
for doc in results.docs:
    cnt +=1
    #info_str = '%s, %s' % (doc['title'], doc['authorName_ss'])
    info_str = doc.get('publicationCitation', 'not found')
    if type(info_str) is list:
        info_str = info_str[0]
    print ('(%s) %s' % (cnt, info_str))
print ('-'*40)
#keys = doc.keys()
#keys.sort()
#for k in keys:
#   print ("%s: %s" % (k,doc[k]))
dashes()
#msg(dir(results))
dashes()
#msg(results.highlighting)
print (doc)

#print ('docs', results.docs)

"""