from django.db import connection
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from apps.utils.msg_util import *
from data_related_to_me import DataRelatedToMe
from permissions_query_helper import PermissionsQueryHelper
from .forms import MyDataFilterForm
from apps.solr_docs.solr_helper import SolrHelper
from apps.dvobjects.pager import PaginationHelper
from apps.dvobjects.role_retriever import RoleRetriever

# Create your views here.
def view_default_query(request, username=None):

    if username is None:
        username = 'dataverseAdmin'

    f = MyDataFilterForm()

    d = dict(username=username, d2me=DataRelatedToMe(username=username),
             filter_form=f)

    return render_to_response('mydata/step1_results.html', d)


def view_solr_results(request, username=None):

    if username is None:
        username = 'dataverseAdmin'

    d = dict(username=username)

    is_valid_form = False

    if 'is_filter_form' in request.GET:
        filter_form = MyDataFilterForm(request.GET)
        if filter_form.is_valid():

            is_valid_form = True

            # Pass forms param to query helper
            #
            pqh = PermissionsQueryHelper(username, filter_form)

            # Check assigned objects in postgres
            #
            pqh.run_queries()
            if pqh.err_found:
                d.update({ 'ERR_FOUND' : True,
                           'ERR_MSG' : pqh.err_msg })

            else:
                search_term = filter_form.get_search_term()

                # Start the SolrHelper
                #
                selected_page = filter_form.get_page_num()
                solr_helper = SolrHelper(selected_page)

                # Make the solr query
                #
                solr_results = solr_helper.make_dataverse_query2(search_term, pqh.get_solr_fq_query())

                if solr_results and solr_results.docs:
                    role_retriever = RoleRetriever(solr_results.docs)
                #solr_results = solr_helper.make_solr_query('*')

                pageHelper = PaginationHelper(solr_results.hits, solr_helper.NUM_DOC_RESULTS_RETURNED, selected_page)
                d.update(pageHelper.get_pagination_dict())

                msgt('docs: ' % solr_results.docs)
                msgt('stats: ' % solr_results.stats)
                d.update({ 'pqh' : pqh,
                           'search_term' : search_term,
                           'solr_results' : solr_results,
                           })
                print d
                #msgt('filter_form: %s' % filter_form.cleaned_data)

    else:
        filter_form = MyDataFilterForm()

    d.update(dict(filter_form=filter_form,
             is_valid_form=is_valid_form))

    return render_to_response('mydata/step2_results.html', d)










