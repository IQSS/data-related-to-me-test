from django.db import connection
from apps.utils.msg_util import *

class PermissionsQueryHelper(object):

    def __init__(self, username, filter_form):
        assert filter_form is not None, "filter_form cannot be None"
        assert filter_form.cleaned_data is not None, "Only use for valid filter_form!"

        self.username = username
        self.filter_form = filter_form

        self.dvobject_direct_ids = []
        self.step1_query = None
        self.step2_query = None
        self.step3_query = None

        # -----------------------
        # dataverses
        # -----------------------
        self.dataverse_info = []
        self.all_dataverse_ids = []

        # -----------------------
        # datasets
        # -----------------------
        self.dataset_info = []
        self.initial_dataset_ids = []
        self.secondary_dataset_ids = []
        self.all_dataset_ids = []

        # -----------------------
        # datafiles
        # -----------------------
        self.file_info = []
        self.initial_file_ids = []
        self.secondary_file_ids = []

    def run_queries(self):

        # Step 1: Roles
        if not self.run_step1_query():
            return

        # Step 2: Direct Permissions
        if not self.step2_load_direct_dv_objects():
            return

        # Step 3: Indirect Datasets
        if not self.step3_load_indirect_dataset_info():
            return

        # Step 4: Indirect Files

        pass

    def run_step1_query(self):
        assert self.filter_form is not None and self.filter_form.cleaned_data is not None, "filter_form cannot be None (or invalid)"
        """
        Can we limit this by role?  Not sure--should be able to.
        Can we limit this by dvobject?
            - Files: Need Dataverses and Datasets
            - Datasets: Need Dataverses, Don't need files
            - Dataverses: Only need Dataverses
        """
        self.step1_query = self.filter_form.get_sql_01_role_assignment_query(self.username)

        msg('step1_query: %s' % self.step1_query)

        qresults = self.get_query_results(self.step1_query)
        if qresults is None or len(qresults)==0:
            self.add_err_msg('No direct role assignments found.')
            return False

        #self.direct_role_assignments = qresults
        self.dvobject_direct_ids =  [ x['definitionpoint_id'] for x in qresults]

        return True


    def step2_load_direct_dv_objects(self):
        assert self.dvobject_direct_ids is not None and len(self.dvobject_direct_ids) > 0, 'You must have dv_object_ids'
        assert self.filter_form is not None and self.filter_form.cleaned_data is not None, "filter_form cannot be None (or invalid)"

        dv_ids_as_strings = [ str(x) for x in self.dvobject_direct_ids]

        self.step2_query = self.filter_form.get_sql02_direct_assignments(','.join(dv_ids_as_strings))

        #self.dvobject_query = q

        qresults = self.get_query_results(self.step2_query)
        if qresults is None or len(qresults)==0:
            self.add_err_msg('No direct dv objects found.')
            return False

        #self.direct_dvobject_assignments = qresults

        # Parse out Dataverse information (complete)
        #
        self.dataverse_info = [ x for x in qresults if x['dtype'] == 'Dataverse']
        self.all_dataverse_ids = [ x['id'] for x in self.dataverse_info]

        # Parse out Dataset information (incomplete)
        #
        self.dataset_info = [ x for x in qresults if x['dtype'] == 'Dataset']
        self.initial_dataset_ids = [ x['id'] for x in self.dataset_info]

        # Parse out File information (incomplete)
        #
        self.file_info = [ x for x in qresults if x['dtype'] == 'DataFile']
        self.initial_file_ids = [ x['id'] for x in self.file_info]
        print 'initial_file_ids', len(self.initial_file_ids)
        return True





    def step3_load_indirect_dataset_info(self):
        """If the user has Dataverse assignments, look for underlying Datasets"""

        if self.all_dataverse_ids is None or len(self.all_dataverse_ids) == 0:
            return

        dataverse_ids_as_str = [ str(x) for x in self.all_dataverse_ids]

        self.step3_query = self.filter_form.get_sql03_indirect_datasets(','.join(dataverse_ids_as_str))
        if self.step3_query == None:
            self.add_err_msg('No query needed for secondary datasets')
            return

        qresults = self.get_query_results(self.step3_query)
        if qresults is None or len(qresults)==0:
            return

        # May overlap with initial dataset_ids and info
        self.secondary_dataset_ids = [ x['id'] for x in qresults]
        self.all_dataset_ids = set(self.initial_dataset_ids + self.secondary_dataset_ids)
        self.dataset_info.append(qresults)


    def add_err_msg(self, m):
        self.err_found = True
        self.err_msg = m


    def get_query_results(self, query_str):

        cursor = connection.cursor()

        cursor.execute(query_str)

        return self.dictfetchall(cursor)


    def dictfetchall(self, cursor):
        "Returns all rows from a cursor as a dict"
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]
