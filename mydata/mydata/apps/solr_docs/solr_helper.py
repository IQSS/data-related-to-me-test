from os.path import dirname, abspath

if __name__=='__main__':
    import os, sys
    DJANGO_ROOT = dirname(dirname(dirname(abspath(__file__))))
    #import os; DJANGO_ROOT = dirname(dirname(dirname(os.getcwd())))
    sys.path.append(DJANGO_ROOT)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mydata.settings.local'


import pysolr
from django.conf import settings

from apps.utils.msg_util import *
from apps.dvobjects.data_related_to_me import DataRelatedToMe

from apps.solr_docs.solr_search_formatter import SolrSearchFormatter
from apps.solr_docs.solr_results_handler import SolrResultsHandler


class SolrHelper(object):

    NUM_DOC_RESULTS_RETURNED = 10


    def __init__(self, page_num=1):

        # Set pages
        self.result_start_offset = (page_num-1) * self.NUM_DOC_RESULTS_RETURNED

        self.num_hits = 0


        self.has_err = False
        self.err_msg = None

    def add_err(self, err_str):
        self.has_err = True
        self.err_msg = err_str


    def make_solr_query(self, qstr):

        solr = pysolr.Solr(settings.SOLR_URL, timeout=10)
        searchFormatter = SolrSearchFormatter(**dict(result_start_offset=self.result_start_offset,
                                                     num_rows=self.NUM_DOC_RESULTS_RETURNED))

        solr_results = solr.search(qstr, **searchFormatter.get_solr_kwargs())

        return solr_results


    def make_q_string_query(self, qstr):

        return self.make_solr_query(qstr, formatted_results=False)



    def make_dataverse_query2(self, search_term, solr_fq_query, page_num=1):

        #solr_fq_query = 'dvobject_types:(dataverses OR datasets OR files)'

        solr = pysolr.Solr(settings.SOLR_URL, timeout=10)

        searchFormatter = SolrSearchFormatter(**dict(fq=solr_fq_query,
                                                     result_start_offset=self.result_start_offset,
                                                     num_rows=self.NUM_DOC_RESULTS_RETURNED)
                                              )

        solr_results = solr.search(search_term, **searchFormatter.get_solr_kwargs())



        return solr_results


if __name__=='__main__':
    d2me = DataRelatedToMe(username='dataverseAdmin')

    solr_helper = SolrHelper(d2me)
    #solr_results = solr_helper.make_dataverse_query()
    r = solr_helper.make_q_string_query('rhinoceros')

"""
from apps.solr_docs.solr_helper import *
solr_helper = SolrHelper()
r = solr_helper.make_q_string_query('rhinoceros')
"""
