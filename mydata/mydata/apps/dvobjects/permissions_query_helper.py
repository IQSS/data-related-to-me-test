

class PermissionsQueryHelper(object):

    def __init__(self, username, filter_form):
        assert filter_form is not None, "filter_form cannot be None"
        assert filter_form.cleaned_data is not None, "Only use for valid filter_form!"

        self.username = username
        self.filter_form = filter_form
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

        # -----------------------
        # datafiles
        # -----------------------
        self.file_info = []
        self.initial_file_ids = []
        self.secondary_file_ids = []

    def build_queries(self):

        # Step 1: Roles


        # Step 2: Direct Permissions

        # Step 3: Indirect Datasets

        # Step 4: Indirect Files

        pass

    def build_step1_query(self):
        assert self.filter_form is not None and self.filter_form.cleaned_data is not None, "filter_form cannot be None (or invalid)"
        """
        Can we limit this by role?  Not sure--should be able to.
        Can we limit this by dvobject?
            - Files: Need Dataverses and Datasets
            - Datasets: Need Dataverses, Don't need files
            - Dataverses: Only need Dataverses
        """
        return

