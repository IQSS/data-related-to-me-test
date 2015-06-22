from django.db import connection
from apps.utils.msg_util import *

class PermissionsQueryHelper(object):

    SOLR_ID_GROUP_SIZE = 1000 # To not overwhelm the solr query OR statements

    def __init__(self, username, filter_form, page_num=1):
        assert filter_form is not None, "filter_form cannot be None"
        assert filter_form.cleaned_data is not None, "Only use for valid filter_form!"

        self.username = username
        self.filter_form = filter_form
        self.page_num = page_num

        self.dvobject_direct_ids = []
        self.step1_query = None
        self.step2_query = None
        self.step3_query = None
        self.step4_query = None

        # -----------------------
        # error messages
        # -----------------------
        self.err_found = False
        self.err_msg = None

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
        self.all_file_ids = []
        self.secondary_file_ids = []

        # -----------------------
        # count of Ids used in solr query
        # -----------------------
        self.solr_query_id_list_count = 0

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
        self.step_load4_indirect_file_info()


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
        assert self.filter_form is not None and self.filter_form.cleaned_data is not None, "filter_form cannot be None (or invalid)"


        if self.dvobject_direct_ids is None or len(self.dvobject_direct_ids) ==0:
            self.add_err_msg('No direct dv objects found')
            return False


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
        self.all_dataset_ids = self.initial_dataset_ids

        # Parse out File information (incomplete)
        #
        self.file_info = [ x for x in qresults if x['dtype'] == 'DataFile']
        self.initial_file_ids = [ x['id'] for x in self.file_info]
        self.all_file_ids = self.initial_file_ids

        print 'initial_file_ids', len(self.initial_file_ids)
        return True





    def step3_load_indirect_dataset_info(self):
        """If the user has Dataverse assignments, look for underlying Datasets"""

        if self.all_dataverse_ids is None or len(self.all_dataverse_ids) == 0:
            return False

        dataverse_ids_as_str = [ str(x) for x in self.all_dataverse_ids]

        self.step3_query = self.filter_form.get_sql03_indirect_datasets(','.join(dataverse_ids_as_str))
        if self.step3_query == None:
            #self.add_err_msg('No query needed for secondary datasets')
            return False

        qresults = self.get_query_results(self.step3_query)
        if qresults is None or len(qresults)==0:
            return True

        # May overlap with initial dataset_ids and info
        self.secondary_dataset_ids = [ x['id'] for x in qresults]
        self.all_dataset_ids = set(self.initial_dataset_ids + self.secondary_dataset_ids)
        self.dataset_info.append(qresults)

        return True


    def step_load4_indirect_file_info(self):

        if len(self.all_dataset_ids) == 0:
            return False

        dataset_ids_as_str = [ str(x) for x in self.all_dataset_ids]

        self.step4_query = self.filter_form.get_sql04_indirect_files(','.join(dataset_ids_as_str))
        if self.step4_query == None:
            #self.add_err_msg('No query needed for secondary files')
            return False

        qresults = self.get_query_results(self.step4_query)
        if qresults is None or len(qresults)==0:
            return True

        # May overlap with initial datafile_ids and info
        self.secondary_file_ids = [ x['id'] for x in qresults]
        self.all_file_ids = set(self.initial_file_ids + self.secondary_file_ids)

        #self.file_info.append(qresults)
        return True

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


    def get_solr_fq_query(self):
        assert self.filter_form is not None and self.filter_form.cleaned_data is not None, "filter_form cannot be None (or invalid)"

        dvobject_id_query = self.get_solr_dvobject_fq_query_fragment()

        return self.filter_form.get_solr_facet_query(dvobject_id_query)


    def get_solr_dvobject_fq_query_fragment(self):
        assert self.filter_form is not None and self.filter_form.cleaned_data is not None, "filter_form cannot be None (or invalid)"

        entity_ids = []
        parent_ids = []
        if self.filter_form.are_dataverses_included():
            entity_ids += self.all_dataverse_ids

        if self.filter_form.are_datasets_included():
            entity_ids += self.initial_dataset_ids
            parent_ids += self.all_dataverse_ids

        if self.filter_form.are_files_included():
            entity_ids += self.initial_file_ids
            parent_ids += self.all_dataset_ids


        entity_ids = set(entity_ids)
        parent_ids = set(parent_ids)

        self.solr_query_id_list_count = len(entity_ids) + len(parent_ids)

        # e.g.  (entityId:(20 11 592 7 17 24 14 15 21 18 25 19 22 23 12 2 8 3 16 4 9 5 13 6 10))
        entity_id_clause = None
        if len(entity_ids) > 0:
            #entity_id_clause = """(entityId:(%s))""" % ' '.join(['%s' % x for x in entity_ids])
            entity_id_clause = self.build_id_query(entity_ids, 'entityId')

        parent_id_clause = None
        if len(parent_ids) > 0:
            #parent_id_clause = """(parentId:(%s))""" % ' '.join(['%s' % x for x in parent_ids])
            parent_id_clause = self.build_id_query(parent_ids, 'parentId')

        if entity_id_clause and parent_id_clause:
            return """(%s OR %s)""" % (entity_id_clause, parent_id_clause)

        if entity_id_clause:
            return entity_id_clause

        if parent_id_clause:
            return parent_id_clause

        #self.are_files_included() or self.are_datasets_included() or self.are_dataverses_included(),


    def format_ids_for_solr_clause(self, slice_of_ids, param_name='entityId'):

        assert isinstance(slice_of_ids, list), 'id_list must be a list object'
        assert param_name is not None, 'param_name cannot be None'

        entity_list = [ str(x) for x in slice_of_ids]

        # join them in a solr OR clause (space is separator)
        or_clause = ' '.join(entity_list)

        # wrap the Ids into an fq
        qpart = '%s:(%s)' % (param_name, or_clause)

        return qpart

    def build_id_query(self, id_list, param_name='entityId'):
        """
        SOLR cannot parse over 1024 items in a boolean clause
        Group IDs in batches of 1000
        """
        if id_list is None or len(id_list) == 0:
            return None

        # If this is a set, convert it to a list
        if isinstance(id_list, set):
            id_list = list(id_list)

        num_ids = len(id_list)

        qparts = []     # query clauses
        id_cnt = 0
        #-------------------------------------------
        # Loop occurs if number of ids
        #  exceeds SOLR_ID_GROUP_SIZE
        #-------------------------------------------
        for current_group_num in range(0, num_ids/self.SOLR_ID_GROUP_SIZE):
            # slice group of ids off
            #
            slice_of_ids = id_list[id_cnt : self.SOLR_ID_GROUP_SIZE * (current_group_num+1)]

            # add them to the count
            #
            id_cnt += len(slice_of_ids)

            # format ids into solr OR clause
            #
            qparts.append(self.format_ids_for_solr_clause(slice_of_ids, param_name))


        #-------------------------------------------
        # Extra ids not evenly divisible by SOLR_ID_GROUP_SIZE
        #-------------------------------------------
        extra_id_count = num_ids % self.SOLR_ID_GROUP_SIZE

        if extra_id_count > 0:
            # slice group of ids off
            slice_of_ids = id_list[id_cnt : (id_cnt + extra_id_count)]

            # format ids into solr OR clause
            #
            qparts.append(self.format_ids_for_solr_clause(slice_of_ids, param_name))

        qparts_fmt = [ '(%s)' % x for x in qparts]

        return ' OR '.join(qparts_fmt)
        #return '(%s)' % (' OR '.join(qparts_fmt))


