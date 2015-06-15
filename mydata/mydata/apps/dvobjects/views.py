from django.db import connection
from django.shortcuts import render, render_to_response
from django.http import HttpResponse

from data_related_to_me import DataRelatedToMe
from .forms import FilterForm

# Create your views here.
def view_default_query(request, username=None):

    if username is None:
        username = 'dataverseAdmin'

    f = FilterForm()

    d = dict(username=username, d2me=DataRelatedToMe(username=username),
             filter_form=f)

    return render_to_response('mydata/test_query.html', d)

