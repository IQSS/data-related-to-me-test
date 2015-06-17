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

    def __init__(self, d2me=None):

        self.d2me = d2me

        self.solr_fq_query = None

        self.has_err = False
        self.err_msg = None

    def add_err(self, err_str):
        self.has_err = True
        self.err_msg = err_str


    def make_solr_query(self, qstr, formatted_results=True):

        solr = pysolr.Solr(settings.SOLR_URL, timeout=10)
        searchFormatter = SolrSearchFormatter()

        solr_results = solr.search(qstr, **searchFormatter.get_solr_kwargs())

        if formatted_results:
            return SolrResultsHandler(solr_results)

        return solr_results


    def make_q_string_query(self, qstr):

        return self.make_solr_query(qstr, formatted_results=False)



    def make_dataverse_query2(self, solr_fq_query):

        #solr_fq_query = 'dvobject_types:(dataverses OR datasets OR files)'

        search_term = '*'

        solr = pysolr.Solr(settings.SOLR_URL, timeout=10)

        solr_results = solr.search(search_term, fq=solr_fq_query, rows=10)

        return solr_results

    def make_dataverse_query(self):

        self.solr_fq_query = self.get_dataverse_facet_query()

        searchFormatter = SolrSearchFormatter(**dict(fq=self.solr_fq_query))

        search_term = '*'

        solr = pysolr.Solr(settings.SOLR_URL, timeout=10)

        solr_kwargs =  searchFormatter.get_solr_kwargs()
        solr_results = solr.search(search_term, **solr_kwargs)

        return solr_results

    def get_dataverse_facet_query(self):
        """
        If there are dataverse ids, format the solr query string
        """
        assert isinstance(self.d2me, DataRelatedToMe), 'd2me must be a DataRelatedToMe object'

        if self.d2me.all_dataverse_ids is None or len(self.d2me.all_dataverse_ids) == 0:
            return None

        self.d2me.all_dataverse_ids.remove(1)

        fmt_list = [ str(x) for x in self.d2me.all_dataverse_ids]   # + self.d2me.initial_dataset_ids]

        id_list = ' '.join(fmt_list)
        #Columbian white-tailed deer
        return '(entityId:(%s)) AND (publicationStatus:Unpublished) AND (dvObjectType:(dataverses OR datasets))' % (id_list) # AND (dvObjectType:datasets)' % (id_list, id_list)

        return '(entityId:(%s)) OR (parentId:(%s))' % (id_list, id_list) # AND (dvObjectType:datasets)' % (id_list, id_list)

        return '"Classical"'# AND (entityId:(%s)) OR (parentId:(%s)) AND (dvObjectType:datasets)' % (id_list, id_list)

        #return '(dvObjectType:dataverses) AND (entityId:(%s))' % (' OR '.join(fmt_list))


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
