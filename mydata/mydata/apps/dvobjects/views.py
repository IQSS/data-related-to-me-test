from django.db import connection
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from apps.utils.msg_util import *
from data_related_to_me import DataRelatedToMe
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

    is_valid_form = False

    if 'is_filter_form' in request.GET:
        filter_form = MyDataFilterForm(request.GET)
        if filter_form.is_valid():
            is_valid_form = True#= filter_form.get_solr_facet_query()
            msgt('filter_form: %s' % filter_form.cleaned_data)
    else:
        filter_form = MyDataFilterForm()

    d2me = DataRelatedToMe(username=username)

    solr_helper = SolrHelper(d2me)
    solr_results = solr_helper.make_dataverse_query()



    d = dict(username=username,
             d2me=d2me,
             solr_helper=solr_helper,
             solr_results=solr_results,
             filter_form=filter_form,
             is_valid_form=is_valid_form
             )

    return render_to_response('mydata/step2_results.html', d)










