from django.shortcuts import render

from django.db import connection
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from apps.utils.msg_util import *
#from data_related_to_me import DataRelatedToMe
#from permissions_query_helper import PermissionsQueryHelper
#from .forms import MyDataFilterForm
#from apps.solr_docs.solr_helper import SolrHelper
#from apps.dvobjects.pager import PaginationHelper
#from apps.dvobjects.role_retriever import RoleRetriever

class DictInfo(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v


class DatasetVersionInfo(DictInfo):
    pass

class FileMetadataInfo(DictInfo):
    pass

class DataFile(DictInfo):
    pass




# Create your views he
# re.
def view_basic_queries(request, dv_id=None):

    # ----------------------------------------
    # List of dataset versions + file counts
    # ----------------------------------------
    qstr = """select dv.id, dv.dataset_id, count(fm.id) as fcnt
        from datasetversion dv, filemetadata fm
        where dv.id=fm.datasetversion_id
        group by dv.id, dv.dataset_id
        order by dv.id, dv.dataset_id, fcnt desc
        ;"""


    result_rows = get_query_results(qstr)
    if result_rows is None or len(result_rows)==0:
        return HttpResponse('no rows')

    dv_info_list = []
    for row in result_rows:
        dv_info_list.append(DatasetVersionInfo(**row))

    d = dict(dv_info_list=dv_info_list)

    # ----------------------------------------
    # Specific file list
    # ----------------------------------------
    d['filemetadata_list'] = get_file_metadata_list(dv_id)
    d['selected_datasetversion_id'] = int(dv_id) if dv_id is not None else None
    #> 10 else c
    #    int(dv_id)

    return render_to_response('dvfiles/view_basic_queries.html', d)


def get_file_metadata_list(dv_id):
    if dv_id is None:
        return None

    qstr2 = \
"""SELECT fm.*
FROM filemetadata fm
WHERE datasetversion_id = %s;""" % (dv_id)

    result_rows = get_query_results(qstr2)
    if result_rows is None or len(result_rows)==0:
        return None

    # ---------------------------------
    # Use the FileMetadata ids to retrieve Tags
    # ---------------------------------
    file_metadata_ids = [ '%s' % row['id'] for row in result_rows]
    print 'file_metadata_ids', file_metadata_ids
    tag_lookup = get_file_tag_lookup(file_metadata_ids)
    if tag_lookup is None:
        tag_lookup = {}

    # ---------------------------------
    # Use the Data File ids to retrieve ContentType, MD5, Filesize
    # ---------------------------------
    datafile_ids = [ '%s' % row['datafile_id'] for row in result_rows]
    print 'datafile_ids', datafile_ids
    datafile_lookup = get_datafile_lookup(datafile_ids)
    if datafile_lookup is None:
        datafile_lookup = {}

    # ---------------------------------
    filemetadata_list = []
    for row in result_rows:
        fm_info = FileMetadataInfo(**row)
        fm_info.tags = tag_lookup.get(fm_info.id, None)
        fm_info.datafile_info = datafile_lookup.get(fm_info.datafile_id)
        filemetadata_list.append(fm_info)

    return filemetadata_list


"""
SLOW:
 SELECT fm.*, df.*
FROM filemetadata fm,
  datafile df
WHERE fm.datafile_id = df.id
and fm.datasetversion_id =61446;
---------------------------------------
EXPLAIN ANALYZE
SELECT fm.*, df.*
FROM filemetadata fm,
  datafile df
WHERE fm.datasetversion_id =61446
AND fm.datafile_id = df.id;
---------------------------------------
EXPLAIN ANALYZE select fm.*
from filemetadata fm
WHERE fm.datasetversion_id =61446;

---------------------------------------
explain analyze select df.*
from datafile df
where df.id = 2274797;
---------------------------------------
explain analyze select dv.*
from dvobject dv
where dv.id = 2274797;
---------------------------------------
OK - DvObject + DataFile
explain analyze select dv.*, df.*
from datafile df,
dvobject dv
where dv.id=2274797
and dv.id = df.id;




explain ANALYZE SELECT fm.*, df.*, dv.*
FROM filemetadata fm,
  datafile df,
  dvobject dv
WHERE fm.datafile_id = df.id
AND dv.id = df.id
and fm.datasetversion_id =61446;
38001

# dataset versions with the most files
select fm.datasetversion_id, count(fm.id) as cnt
from filemetadata fm
group by fm.datasetversion_id
order by cnt desc
limit 100;

"""

def get_datafile_lookup(datafile_ids):
    if datafile_ids is None or len(datafile_ids) == 0:
        return None

    qstr = \
"""SELECT df.*
FROM datafile df
WHERE df.id IN (%s);"""\
   % (",".join(datafile_ids))

    result_rows = get_query_results(qstr)
    if result_rows is None or len(result_rows)==0:
        return None

    #print 'datafile info', result_rows

    df_lookup = {} # { filemetadata id : [ name, name, name]}
    for row in result_rows:
        df_lookup[row['id']] = DataFile(**row)

    return df_lookup



def get_file_tag_lookup(file_metadata_ids):
    if file_metadata_ids is None or len(file_metadata_ids) == 0:
        return None

    qstr = \
"""SELECT fm_cat.filemetadatas_id, cat.name
FROM filemetadata_datafilecategory fm_cat,
    datafilecategory cat
WHERE fm_cat.filemetadatas_id IN (%s)
AND fm_cat.filecategories_id = cat.id
ORDER BY cat.name;""" \
           % (",".join(file_metadata_ids))

    result_rows = get_query_results(qstr)
    if result_rows is None or len(result_rows)==0:
        return None

    """{'filemetadatas_id': 64L, 'name': u'Data'}, {'filemetadatas_id': 65L, 'name': u'Data'}, etc"""

    name_lookup = {} # { filemetadata id : [ name, name, name]}
    for row in result_rows:
        name_lookup.setdefault(row['filemetadatas_id'], []).append(row['name'])

    print 'name_lookup', name_lookup
    return name_lookup


def add_err_msg(self, m):
    self.err_found = True
    self.err_msg = m



def get_query_results(query_str, no_dict=False):

    cursor = connection.cursor()

    cursor.execute(query_str)

    if no_dict:
        return cursor.fetchall()
    else:
        return dictfetchall(cursor)



def dictfetchall( cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
