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
    SOLR_DATAVERSES_LABEL = "dataverses"
    SOLR_DATASETS_LABEL = "datasets"
    SOLR_FILES_LABEL = "files"
    DVOBJECTS_SOLR = (SOLR_DATAVERSES_LABEL, SOLR_DATASETS_LABEL, SOLR_FILES_LABEL)
    DVOBJECTS_POSTGRES = ("Dataverse", "Dataset", "DataFile")
    DVOBJECTS_LABEL = ("Dataverses", "Datasets", "Files")

    DVOBJECT_TYPE_CHOICES = zip(DVOBJECTS_SOLR, DVOBJECTS_LABEL)
    SOLR_TO_SQL_MAP = dict(zip(DVOBJECTS_SOLR, DVOBJECTS_POSTGRES))

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
                                             initial=[x[0] for x in DVOBJECT_TYPE_CHOICES[:2]])

    publication_statuses = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                             choices=PUBLICATION_STATUS_CHOICES,
                                             initial=PUBLICATION_STATUSES)

    roles = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                     choices=ROLE_CHOICES,
                                      initial=[x[0] for x in ROLE_CHOICES])

    def are_files_included(self):
        assert self.cleaned_data is not None, "Only use this for valid forms!"
        return self.SOLR_FILES_LABEL in self.cleaned_data['dvobject_types']

    def are_datasets_included(self):
        assert self.cleaned_data is not None, "Only use this for valid forms!"
        return self.SOLR_DATASETS_LABEL in self.cleaned_data['dvobject_types']

    def are_dataverses_included(self):
        assert self.cleaned_data is not None, "Only use this for valid forms!"
        return self.SOLR_DATAVERSES_LABEL in self.cleaned_data['dvobject_types']

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

        return """ AND r.role_id in (%s)""" % value_str

    def get_sql_dvobject_query_fragment(self):
        """
        Example of formatted sql query clause:   (dvObjectType:(dataverses OR datasets))
        """
        assert self.cleaned_data is not None, "Only use this for valid forms!"
        assert 'dvobject_types' in self.cleaned_data, "There must be 'dvobject_types' parameters in the form"

        value_list = self.cleaned_data['dvobject_types']

        value_str = ','.join([ "'%s'" % (self.SOLR_TO_SQL_MAP.get(x)) for x in value_list])

        return """ AND dv.dtype in (%s)""" % value_str


    def get_sql_01_role_assignment_query(self, username):

        return """SELECT r.id, r.assigneeidentifier, r.definitionpoint_id, r.role_id
FROM roleassignment r
WHERE substr(r.assigneeidentifier, 2)= '%s'%s;""" % (username,
                                                     self.get_sql_role_query_fragment(),
                                                     )

    def get_sql02_direct_assignments(self, id_list_str="--- IDs from QUERY 1 ----"):

        dvobject_type_fragment = ''
        if self.are_files_included():
            # No restriction
            # Datasets needed for indirect File permissions
            # also: Dataverses needed for indirect Dataset permissions
            pass

        elif self.are_datasets_included():
            # Exclude files
            # Dataverses needed for indirect Dataset permissions
            dvobject_type_fragment = """ AND dv.dtype in ('Dataverse','Dataset')"""

        elif self.are_dataverses_included():
            # exclude datasets and files
            dvobject_type_fragment = """ AND dv.dtype ='Dataverse'"""

        sql_str = """SELECT dv.id, dv.dtype, dv.modificationtime, dv.owner_id"""
        sql_str += """ FROM dvobject dv"""
        sql_str += """ WHERE dv.id IN (%s)%s""" % (id_list_str, dvobject_type_fragment)
        sql_str += """ ORDER BY dv.dtype;"""

        return sql_str

    def get_sql03_indirect_datasets(self, id_list_str="--- IDs from QUERY 2 ----"):
        if (not self.are_datasets_included()) and (not self.are_files_included()):
            return ('No query needed. Not looking for datasets or files')

        sql_str = """SELECT dv.id, dv.dtype, dv.modificationtime, dv.owner_id"""
        sql_str += """ FROM dvobject dv"""
        sql_str += """ WHERE dv.owner_id IN (%s)""" % (id_list_str)
        sql_str += """ AND dv.dtype IN ('Dataset');"""

        return sql_str

    def get_sql04_indirect_files(self, id_list_str="--- IDs from Queries 2 and 3 ---"):
        if not self.are_files_included():
            return 'No query needed. Not looking for files'

        sql_str = """SELECT dv.id, dv.dtype, dv.modificationtime, dv.owner_id"""
        sql_str += """ FROM dvobject dv"""
        sql_str += """ WHERE dv.owner_id IN (%s)""" % (id_list_str)
        sql_str += """ AND dv.dtype IN ('DataFile');"""

        return sql_str

    def get_direct_indirect_grid(self):

        direct_row = [ self.are_files_included() or self.are_datasets_included() or self.are_dataverses_included(),
                       self.are_files_included() or self.are_datasets_included(),
                       self.are_files_included()
                       ]
        indirect_row = [ False,
                        self.are_files_included() or self.are_datasets_included(),
                        self.are_files_included()
                         ]
        return [direct_row, indirect_row]