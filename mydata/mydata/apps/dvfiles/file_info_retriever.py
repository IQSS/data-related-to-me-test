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



"""
Inputs:
---------------------------------
    (1) datasetversion id

    (2) Tags (optional)
    (3) File Type (optional)
    (4) Access (optional)
    (5) Search Term (optional)
---------------------------------
Initial Retrieval
    (1) query 1: Filemetadata by DatasetVersion
    (2) query 2: DvObject + DataFile Info
    (3) query 3: Tags

Secondary Retrieval
    (1) query 1: Filemetadata by DatasetVersion
        - if unpublished, filter Access facet if needed

    (2) query 2: Retrieve matching DvObject + DataFile Info
        - filter by FileType
        - if published, filter Access facet on DataFile if needed

    (3) query 3: Retrieve tags
        - filter by tags

    - Gather dataset ids
        - dataset ids, file types

    - Gather dataset ids filemetadata ids,
        - LIMIT by tags

    - Gather filemetadata ids, tags

    - Narrow

"""
class FileInfoRetriever(object):

    def __init__(self, dataset_version_id, **kwargs):

        self.dataset_version_id = dataset_version_id

        self.all_tags = []
        self.selected_tags = kwargs.get('selected_tags', [])

        self.all_file_types = []
        self.selected_file_types = kwargs.get('selected_file_types', [])

        self.datafile_ids = []
        self.metafile_ids = []


    def