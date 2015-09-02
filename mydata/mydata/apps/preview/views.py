from django.shortcuts import render, render_to_response
from django.http import HttpResponse

# Create your views here.
def view_hello(request, name='cathy'):

    return HttpResponse('hello: ' + name)
    if username is None:
        username = 'dataverseAdmin'

    f = MyDataFilterForm()

    d = dict(username=username, d2me=DataRelatedToMe(username=username),
             filter_form=f)

    return render_to_response('mydata/step1_results.html', d)
