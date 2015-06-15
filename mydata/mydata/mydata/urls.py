from django.conf.urls import include, url
from django.contrib import admin

admin.site.site_header = 'Dataverse DB'

urlpatterns = [
    # Examples:
    # url(r'^$', 'mydata.views.home', name='home'),
     url(r'^step1/', include('apps.dvobjects.urls')),

    url(r'^mydata-admin/', include(admin.site.urls)),
]
