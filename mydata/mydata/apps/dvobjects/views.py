from django.db import connection
from django.shortcuts import render, render_to_response
from django.http import HttpResponse

from data_related_to_me import DataRelatedToMe
from .forms import FilterForm
from apps.solr_docs.solr_helper import SolrHelper

# Create your views here.
def view_default_query(request, username=None):

    if username is None:
        username = 'dataverseAdmin'

    f = FilterForm()

    d = dict(username=username, d2me=DataRelatedToMe(username=username),
             filter_form=f)

    return render_to_response('mydata/step1_results.html', d)


def view_search_results(request, username=None):

    if username is None:
        username = 'dataverseAdmin'

    d2me = DataRelatedToMe(username=username)

    solr_helper = SolrHelper(d2me)
    solr_results = solr_helper.make_dataverse_query()


    #f = FilterForm()

    d = dict(username=username,
             d2me=d2me,
             solr_helper=solr_helper,
             solr_results=solr_results,
             )

    return render_to_response('mydata/step2_results.html', d)










