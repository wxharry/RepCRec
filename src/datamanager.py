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
        self.lock_table = {} # value should be a list of shared read lock or write lock or both
        self.wait_for_graph = {}
        self.fail_time_list = []
        self.recover_time_list = []

    def set_variable(self, var):
        self.data_table[var.id] = var

    # def read(self, tid, vid):
    #     lock: Lock = self.lock_table.get(vid, None)
    #     variable: Variable = self.data_table.get(vid, None)
    #     # if a lock exists
    #     if lock:
    #         if lock.lock_type == LockType.Read:
    #             # check if this read lock is belonged to this transaction
    #             if tid in lock.sharing:
    #                 return variable.commit_values[-1][0]
                
    #             # check if this variable has write lock
    #             if w_lock_queue

    #             # lock.sharing.append(tid)
    #         elif lock.lock_type == LockType.Write:
    #             self.wait_for[tid] = vid
    #     # if no lock on variable vid
    #     else:
    #         shared_lock = SharedLock(vid)
    #         shared_lock.acquire(tid)
    #         self.lock_table[vid] = shared_lock
    #     return self.data_table[vid]


    def fail(self, fail_time):
        if not self.is_up:
            return "Invalid Command: trying to fail a down site."
        self.is_up = False
        self.fail_time_list.append(fail_time)
        self.lock_table.clear()


    def recover(self, recover_time):
        if self.is_up:
            return "Invalid Command: trying to recover a up site."
        self.is_up = True
        self.recover_time_list.append(recover_time)
        for vid, variable in self.data_table.items():
            # replicated variables are not readable when site recovers
            if variable.is_replicated:
                self.data_table[vid].access = False

    def commit(self, tid, commit_time):
        # release current lock for this transaction
        for vid, locks in self.lock_table.items():
            new_locks = []
            for l in locks:
                if l.lock_type == LockType.R:
                    l.sharing.remove(tid)
                    new_locks.append(l)
                else:
                    if l.tid != tid:
                        new_locks.append(l)
            
            self.lock_table[vid] = new_locks
        
        # update commit queue
        for vid, variable in self.data_table.items():
            if variable.temp_value != None and variable.temp_value[1] == tid:
                self.data_table[vid].commit_values.append((variable.temp_value[0], commit_time))
                self.data_table[vid].access = True


                

    
    def dump(self):
        print(f"site {self.id}",
              f"-",
              ", ".join([str(v) for v in self.data_table.values()]))
        
