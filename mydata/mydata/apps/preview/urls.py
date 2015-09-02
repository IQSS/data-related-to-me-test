from django.conf.urls import patterns, include, url


urlpatterns = patterns('apps.preview.views',


    url(r'^hello/$', 'view_hello', name='view_hello_default'),

    url(r'^hello/(?P<name>\w{1,50})$', 'view_hello', name='view_hello'),



 #   url(r'^send-metadata-to-dataverse/(?P<import_success_id>\d{1,10})/$', 'send_metadata_to_dataverse', name="send_metadata_to_dataverse"),

  #  url(r'^params-for-datavarse/(?P<import_success_id>\d{1,10})/$', 'show_import_success_params', name="show_import_success_params"),

)


