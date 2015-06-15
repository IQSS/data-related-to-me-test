from django.conf.urls import patterns, include, url


urlpatterns = patterns('apps.dvobjects.views',


    url(r'^solr/$', 'view_search_results', name='view_search_results'),


    url(r'^db-roles/(?P<username>\w{1,50})$', 'view_default_query', name='view_default_query_with_username'),


    url(r'^db-roles/$', 'view_default_query', name='view_default_query'),


 #   url(r'^send-metadata-to-dataverse/(?P<import_success_id>\d{1,10})/$', 'send_metadata_to_dataverse', name="send_metadata_to_dataverse"),

  #  url(r'^params-for-datavarse/(?P<import_success_id>\d{1,10})/$', 'show_import_success_params', name="show_import_success_params"),

)


