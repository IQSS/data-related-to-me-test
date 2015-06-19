
class PaginationHelper(object):

    def __init__(self, num_results, docs_per_page, selected_page_num=1):
        """
        Input:
            num_results - Total objects returned
            docs_per_page - Number of cards per page
            selected_page_num - current page

        Output:
            page_count - total number of pages
            page_number_list - array of page numbers
            prev_page_num - previous page
            next_page_num - next page
            card_start_num - start card number e.g. 21
            end_card_num - end card number, e.g. 30
        """
        assert isinstance(num_results, int) and num_results >= 0, 'num_results must be 0 or higher'
        assert isinstance(docs_per_page, int) and docs_per_page > 0, 'docs_per_page must be greater than 0'
        assert isinstance(selected_page_num, int) and selected_page_num > 0, 'page_nume must be greater than 0'

        self.num_results = num_results
        self.docs_per_page = docs_per_page
        self.selected_page_num = selected_page_num

        # -------------------
        # Make page stats
        # -------------------

        # page count
        self.page_count = num_results / docs_per_page
        if (self.num_results % self.docs_per_page) > 0:
            self.page_count += 1

        # Sanity check for the selected page
        if self.selected_page_num > self.page_count:
            self.selected_page_num = 1

        # page number list
        self.page_number_list = range(1, self.page_count+1)

        # prev/next page numbers
        self.prev_page_num =  max([self.selected_page_num-1, 1]) # must be at least 1
        self.next_page_num =  min([self.selected_page_num+1, self.page_count]) # must be at least 1

        # start/end card numbers
        self.card_start_num =  (self.docs_per_page * (self.selected_page_num - 1)) +1
        self.card_end_num = min([self.card_start_num + (self.docs_per_page-1), self.num_results ])

    def get_pagination_dict(self):
        return self.__dict__
