from apps.utils.msg_util import *

from solr_facet_field_list import facet_field_list, facet_field_dict
from solr_highlight_field_list import highlight_field_list
from  pysolr import Results as PySolrResults

CORE_FACET_GROUPS = ('dvObjectType', )

class FacetGroup:
    def __init__(self, name, info):
        self.name = name
        self.display_name = facet_field_dict.get(self.name, self.name)
        self.info = info
    
    def show(self):
        msgt('%s -> %s' % (self.name, self.display_name))
        msg(self.info)
        
class SolrResultsHandler:

    def __init__(self, results):
        if type(results) is not PySolrResults:
           raise TypeError('Expected pysolr.Results object.  Received: [%s]' % type(results))

        self.num_results = 0
        self.docs = []
        self.num_results = 0
        self.facet_groups = {}  # { name : FacetGroup }
        
        self.load_facets(results.facets)
        self.show_facets()
        
    def show_facets(self):
        for fg in self.facet_groups.values():
            fg.show()
        
    def load_facets(self, facets):
        if type(facets) is not dict:
            raise TypeError('expected a dict, not "%s"' % type(facets))
        if facets is None or len(facets) == 0:
            return
        
        for kval, val_dict in facets.items():   
            msg('kval: %s\ndict: %s' % (kval, val_dict))
            if val_dict == {}:
                continue        
            for facet_name, v in val_dict.items():
                # place in tuples (value, count)
                # e.g. [(u'William Shakespeare', 5), (u'Nora Roberts', 3) ...]
                pairs = zip(v[::2], v[1::2])
                # strip out zero counts
                if not facet_name in CORE_FACET_GROUPS:
                    pairs = [p for p in pairs if not p[1] == 0]
                    if len(pairs) == 0:
                        continue
                self.facet_groups[facet_name] = FacetGroup(facet_name, pairs)
                #msg ("\n%s: %s" % (k, v))
        #for fac in self.facets:
        #    msgt(fac)
        #
        #pass

