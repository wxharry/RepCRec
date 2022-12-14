""" Transaction
defines class transactions
"""
class Transaction:
    def __init__(self, id: str, begin_time: int, is_read_only: bool) :
        """ 
            Description: initialize Transaction Object
            Input: transaction id, begin timestamp, read only flag
            Output: None
            Date: 11/29/2022
            Author: Yulin Hu, Xiaohan Wu
        """
        self.id = id
        self.begin_time = begin_time
        self.is_read_only = is_read_only
        self.should_abort = False
        self.site_access_list = []
        self.temp_vars = {}
    
    def set_snapshot(self, snapshot):
        self.snapshot = snapshot

    def __repr__(self):
        if self.is_read_only:
            return self.id + " begin at " + self.begin_time + " read_only\n"
        else:
            return self.id + " begin at " + self.begin_time + " not read_only"
    
    def abort(self):
        self.should_abort = True
