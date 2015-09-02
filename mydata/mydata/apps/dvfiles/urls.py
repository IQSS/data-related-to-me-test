from django.conf.urls import patterns, include, url


urlpatterns = patterns('apps.dvfiles.views',

    url(r'^basic-queries/(?P<dv_id>\d{1,10})$', 'view_basic_queries', name='view_basic_queries_by_dv_id'),

    url(r'^basic-queries/$', 'view_basic_queries', name='view_basic_queries'),

#    url(r'^solr/(?P<username>\w{1,50})$', 'view_solr_results', name='view_solr_results_with_name'),

#    url(r'^db-roles/(?P<username>\w{1,50})$', 'view_default_query', name='view_default_query_with_username'),


#    url(r'^db-roles/$', 'view_default_query', name='view_default_query'),


 #   url(r'^send-metadata-to-dataverse/(?P<import_success_id>\d{1,10})/$', 'send_metadata_to_dataverse', name="send_metadata_to_dataverse"),

  #  url(r'^params-for-datavarse/(?P<import_success_id>\d{1,10})/$', 'show_import_success_params', name="show_import_success_params"),

)


