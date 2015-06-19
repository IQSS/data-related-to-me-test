from django.db import connection
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from apps.utils.msg_util import *
from data_related_to_me import DataRelatedToMe
from permissions_query_helper import PermissionsQueryHelper
from .forms import MyDataFilterForm
from apps.solr_docs.solr_helper import SolrHelper

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
                #solr_results = solr_helper.make_dataverse_query2(search_term, pqh.get_solr_fq_query())
                solr_results = solr_helper.make_solr_query('*')


                page_count = solr_results.hits / solr_helper.NUM_DOC_RESULTS_RETURNED
                page_count += solr_results.hits % solr_helper.NUM_DOC_RESULTS_RETURNED
                page_numbers = range(1, page_count+1)

                card_start_num = (solr_helper.NUM_DOC_RESULTS_RETURNED * (selected_page - 1)) +1
                #if selected_page > page_count:
                #    selected_page = 1

                #msgt(dir(solr_results))
                msgt(solr_results.stats)
                d.update({ 'pqh' : pqh,
                            'search_term' : search_term,
                           'solr_results' : solr_results,
                           'page_count' : page_count,
                           'page_numbers' : page_numbers,
                            'last_page' : page_numbers[-1],
                           'selected_page' : selected_page,
                           'prev_page' : max([selected_page-1, 1]),
                           'next_page' : min([selected_page+1, page_numbers[-1]]),
                           'card_start_num' : card_start_num,
                           'card_end_num' : min([card_start_num + 19, solr_results.hits])
                           })

                #msgt('filter_form: %s' % filter_form.cleaned_data)

    else:
        filter_form = MyDataFilterForm()

    d.update(dict(filter_form=filter_form,
             is_valid_form=is_valid_form))

    return render_to_response('mydata/step2_results.html', d)










