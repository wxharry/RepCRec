""" TaskManager
defines class task manager
"""
from src.transaction import *

class TaskManager:
    instructions = ["read", "write", "begin","beginRO", "end", "R", "W"]
    def __init__(self, id, sites) -> None:
        self.id = id
        self.tick = 0
        self.transaction_table = {}
        self.sites = sites

    def beginRO(self, tid):
        return self.begin(tid, True)

    def begin(self, tid, readonly=False):
        """ Return the transaction begins
        """
        if self.transaction_table.get(tid):
            print(f"transaction {tid} already exists")
            return None
        transaction = Transaction(tid, self.tick, readonly)
        if readonly:
            transaction.set_snapshot(self.sites)
        self.transaction_table[tid] = transaction
        return tid
        
    def end(self, tid):
        """ Return the transaction ends
        """
        # TBD: to abort
        for site in self.sites.values():
            site.commit(self.transaction_table[tid])
        return self.transaction_table.pop(tid)
        
    def R(self, tid, vid):
        t:Transaction = self.transaction_table.get(tid)
        if not t:
            print(f"No transaction {tid} is found in transaction table")
            return None
        # it t is not readonly, reads from current sites; otherwise reads from the snapshot
        sites = self.sites if not t.is_read_only else t.snapshot
        for site in sites.values():
            if site.is_up and vid in site.data_table.keys():
                print(site.read(tid, vid))
                return site.read(tid, vid)
        
    def W(self, tid, did, value):
        print(f"tm: {tid} writes {did} {value}")
