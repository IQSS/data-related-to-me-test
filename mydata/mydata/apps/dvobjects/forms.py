from django import forms


class MyDataFilterForm(forms.Form):
    """
    Filtering for DvObjects related to the user
    """

    # ------------------------------------------------------
    # Publication statuses
    # ------------------------------------------------------
    PUBLICATION_STATUSES = ('Published', 'Unpublished', 'Draft')
    PUBLICATION_STATUS_CHOICES = [(x, x) for x in PUBLICATION_STATUSES]

    # ------------------------------------------------------
    # DvObjects
    # ------------------------------------------------------
    DVOBJECT_TYPE_CHOICES = (("dataverses", "Dataverses"),
                            ("datasets", "Datasets"),
                            ("files", "DataFiles"))

    # ------------------------------------------------------
    # Roles
    # ------------------------------------------------------
    ROLES = ['Admin', 'File Downloader', 'Dataverse + Dataset Creator',
             'Dataverse Creator', 'Dataset Creator', 'Contributor',
             'Curator', 'Member']
    ROLE_CHOICES = [ (id_num, x) for id_num, x in enumerate(ROLES, 1)]
    # ------------------------------------------------------

    search_term = forms.CharField(required=False)

    is_filter_form = forms.CharField(widget=forms.HiddenInput, initial=1)

    dvobject_types = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                             choices=DVOBJECT_TYPE_CHOICES,
                                             initial=[x for x, y in DVOBJECT_TYPE_CHOICES[:2]])

    publication_statuses = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                             choices=PUBLICATION_STATUS_CHOICES,
                                             initial=PUBLICATION_STATUSES)

    roles = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                     choices=ROLE_CHOICES,
                                      initial=[x for x, y in ROLE_CHOICES])




    def get_solr_facet_query(self):
        assert self.cleaned_data is not None, "Only use this for valid forms!"

        query_parts = []

        query_parts.append(self.get_solr_query_clause_for_param('dvobject_types'))
        query_parts.append(self.get_solr_query_clause_for_param('publication_statuses'))

        return ' AND '.join(query_parts)

    #(publicationStatus:Unpublished)

    def get_solr_query_clause_for_param(self, param_name):
        """
        Example of formatted solr query clause:         (dvObjectType:(dataverses OR datasets))
        """
        assert self.cleaned_data is not None, "Only use this for valid forms!"
        assert param_name in self.cleaned_data, "There must be '%s' in the form" % (param_name)

        value_list = self.cleaned_data[param_name]

        value_str = ' OR '.join(value_list)
        if len(value_list) > 1:
            value_str = '(%s)' % value_str

        return  """(%s:%s)""" % (param_name, value_str)


    def get_sql_role_query_fragment(self):
        """
        Example of formatted sql query clause:   (dvObjectType:(dataverses OR datasets))
        """
        assert self.cleaned_data is not None, "Only use this for valid forms!"
        assert 'roles' in self.cleaned_data, "There must be 'roles' parameters in the form"

        value_list = self.cleaned_data['roles']

        value_str = ','.join([str(x) for x in value_list])

        return """r.role_id in (%s)""" % value_str

