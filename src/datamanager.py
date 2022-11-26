""" datamanager
defines class data manager
"""
from src.transaction import *
from src.variable import *
from src.lock import *

class DataManager:
    instructions = ["fail", "recover"]
    def __init__(self, id) -> None:
        self.is_up = True
        self.id = id
        self.data_table = {}
        self.lock_table = {}
        self.wait_for = {}
        self.fail_time_list = []
        self.recover_time_list = []

    def set_variable(self, var):
        self.data_table[var.id] = var

    def read(self, tid, vid):
        lock:Lock = self.lock_table.get(vid, None)
        # if a lock exists
        if lock:
            if lock.lock_type == LockType.Read:
                lock.sharing.append(tid)
            elif lock.lock_type == LockType.Write:
                self.wait_for[tid] = vid
        # if no lock on variable vid
        else:
            shared_lock = SharedLock(vid)
            shared_lock.acquire(tid)
            self.lock_table[vid] = shared_lock
        return self.data_table[vid]

    def fail(self, site):
        pass

    def recover(self, site):
        pass

    def commit(self, t):
        pass
    
    def dump(self):
        print(f"site {self.id}",
              f"-",
              ", ".join([str(v) for v in self.data_table.values()]))
        
