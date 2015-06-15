from solr_facet_field_list import facet_field_list
from solr_highlight_field_list import highlight_field_list

class SolrSearchFormatter:
    """
    Testing out solr.  Learning search structure, etc
    """
    def __init__(self, **kwargs):
        self.search_str = ''
        self.stats_on = kwargs.get('stats', 'true')
        self.debug = kwargs.get('debug', 'true')
        self.result_start_offset = kwargs.get('result_start_offset', 0)
        self.num_rows = kwargs.get('num_rows', 20)

        self.highlight_start_tag = kwargs.get('highlight_start_tag', '<em>')
        self.highlight_end_tag = kwargs.get('highlight_end_tag', '</em>')

    def get_solr_kwargs(self):
        solr_kw = {
            'start': self.result_start_offset,     # result offset
            'rows': self.num_rows,      # num results
            'facet' : 'on',
            'facet.field' : facet_field_list,
            'hl': 'true',
            'hl.fragsize': 500,
            'hl.fl' : highlight_field_list,
            #, 'hl.fl' :  ['title','authorName', 'dsDescription', 'publicationCitation', 'authorName_ss']\
            'hl.simple.pre' : self.highlight_start_tag,
            'hl.simple.post' : self.highlight_end_tag,
            'fq' : [ 'dvObjectType:(dataverses OR datasets OR files)'],
            'debug' : self.debug,
            'sort' : ['release_or_create_date_dt desc'],
        }
        
        if self.stats_on:
            solr_kw.update({
                        'stats' : 'true',
                        'stats.field' : ['dvObjectType', 'subject_ss']
                    })
                    
        return solr_kw
            #'stats')
        
    