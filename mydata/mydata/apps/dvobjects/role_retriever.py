from __future__ import print_function
from django.db import connection
from apps.utils.msg_util import *
from apps.dvobjects.forms import MyDataFilterForm


SOLR_ENTITY_ID = 'entityId'
SOLR_PARENT_ID = 'parentId'

class RoleRetriever(object):

    def __init__(self, solr_docs_as_dict):

        assert solr_docs_as_dict is not None, "solr_docs_as_dict cannot be None"

        self.solr_docs = solr_docs_as_dict

        self.role_name_lookup = {}  # { role id : role name }

        self.final_doc_role_lookup = {}      # { dvobject ids of retrieved docs : [ role name, role name, role name] }

        self.dv_object_role_lookup = {}     # { dvobject id : [ role name, role name, role name]  }

        self.child_parent_map = {} # { dvobject id : parent dvobject id }

        self.err_found = False
        self.err_msg = None

        #---------------------------
        if self.load_role_names():
            self.retrieve_roles()

    def load_role_names(self):

        msgt('load_role_names')

        qstr = """SELECT id, name FROM dataverserole;"""

        qresults = self.get_query_results(qstr)
        if qresults is None or len(qresults)==0:
            self.add_err_msg('No role names founds in dataverserole table.')
            return False

        for role_info in qresults:
            self.role_name_lookup[role_info['id']] = role_info['name']
        msgt('role_name_lookup: %s' % self.role_name_lookup)

        return True


    def retrieve_roles(self):
        assert self.solr_docs is not None, "self.solr_docs cannot be None"

        # For the retrieved Solr docs, start populating:
        #   (1) role_lookup - just the keys
        #   (2) child_parent_map0.
        #
        for doc in self.solr_docs:
            assert SOLR_ENTITY_ID in doc, "Solr doc MUST haven an %s" % SOLR_ENTITY_ID
            assert SOLR_PARENT_ID in doc, "Solr doc MUST haven an %s" % SOLR_PARENT_ID
            #print('-' * 40)
            #print(doc)
            self.child_parent_map[doc[SOLR_ENTITY_ID]] = int(doc[SOLR_PARENT_ID])
            self.final_doc_role_lookup.setdefault(doc[SOLR_ENTITY_ID], [])


        print ('child_parent_map: %s' % self.child_parent_map)

        self.make_initial_queries()

        ids_without_roles = self.get_doc_ids_without_roles()
        if ids_without_roles and len(ids_without_roles) > 0:
            self.make_secondary_queries(ids_without_roles)


    def get_doc_ids_without_roles(self):

        return [ id for id, roles in self.final_doc_role_lookup.items() if roles is None or len(roles)==0]

    def make_initial_queries(self):
        """
        Retrieve the Roles for retrieved doc Ids and Related parents
        This should retrieve role ids for all Dataverse + Dataset cards
            - May not cover all of the file cards
        """
        msgt('make_initial_queries')

        entity_ids = self.child_parent_map.keys() + self.child_parent_map.values()
        entity_ids = [ str(x) for x in set(entity_ids)]

        # Construct query
        #
        qstr = """SELECT r.definitionpoint_id, r.role_id FROM roleassignment r"""
        qstr += """ WHERE r.definitionpoint_id IN (%s);""" % (','.join(entity_ids))

        # Check for results
        #
        result_rows = self.get_query_results(qstr, no_dict=True)
        if result_rows is None or len(result_rows)==0:
            self.add_err_msg('No direct role assignments found.')
            return False

        # Save results to lookup
        #
        for row in result_rows:
            entity_id = row[0]
            role_name = self.role_name_lookup.get(row[1], 'Role id "%s" has no name' % row[1])

            role_list = self.dv_object_role_lookup.get(entity_id, [])
            if role_name not in role_list:
                self.dv_object_role_lookup.setdefault(entity_id, []).append(role_name)

        msgt('dv_object_role_lookup: %s' % self.dv_object_role_lookup)
        self.load_roles_to_final_dict()

    def make_secondary_queries(self, ids_without_roles):
        """
        These are file ids, get 'grandparent ids' which are dataverses
        """
        assert ids_without_roles is not None and len(ids_without_roles) > 0, "ids_without_roles has no values!"

        pass



    def load_roles_to_final_dict(self):
        """May be called multiple times"""

        updated_role_lookup = {}

        # Iterate through the role list: see if anything is missing
        #
        for entity_id, role_list in self.final_doc_role_lookup.items():
            msg('check final id[%s] roles[%s]' % (entity_id, role_list))
            # Are roles already assigned for this id?
            #
            if role_list is not None and len(role_list) > 0:
                continue    # yes, go to next id

            # No, get them
            #
            role_names = self.dv_object_role_lookup.get(entity_id)
            if role_names and len(role_names) > 0:
                msg('role names for [%s] [%s]' % (entity_id, role_names))
                # Got them!  Make update and move on
                updated_role_lookup[entity_id] = role_names
                continue

            # Didn't have direct roles assigned.  Does the parent have roles?
            #
            parent_id = self.child_parent_map.get(entity_id, None)
            if parent_id is not None:
                role_names = self.dv_object_role_lookup.get(parent_id)
                if role_names and len(role_names) > 0:
                    msg('role names for [%s] [%s]' % (entity_id, role_names))
                    # Got them!  Make update and move on
                    updated_role_lookup[entity_id] = role_names
                    continue


        msg('updated_role_lookup: %s' % updated_role_lookup)
        # Update final_doc_role_lookup with updated_role_lookup
        for entity_id, role_list in updated_role_lookup.items():
            self.final_doc_role_lookup[entity_id] = role_list


        msgt('final_doc_role_lookup: %s' % self.final_doc_role_lookup)
        #self.final_doc_role_lookup = {}      # { dvobject ids of retrieved docs : [ role name, role name, role name] }
        #self.dv_object_role_lookup = {}     # { dvobject id : [ role name, role name, role name]  }
        #self.child_parent_map = {} # { dvobject id : parent dvobject id }




    def add_err_msg(self, m):
        self.err_found = True
        self.err_msg = m


    def get_query_results(self, query_str, no_dict=False):

        cursor = connection.cursor()

        cursor.execute(query_str)

        if no_dict:
            return cursor.fetchall()
        else:
            return self.dictfetchall(cursor)


    def dictfetchall(self, cursor):
        "Returns all rows from a cursor as a dict"
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]