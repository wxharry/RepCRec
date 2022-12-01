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
        self.fail_time_list = []
        self.recover_time_list = []

    def parse_instruction(self, instruction, tick):
        if instruction == 'fail':
            self.fail(tick)
        if instruction == 'recover':
            self.recover(tick)

    def set_variable(self, var):
        self.data_table[var.id] = var
    
    def read(self, transaction:Transaction, vid, wait_for):
        tid = transaction.id
        lock: Lock = self.lock_table.get(vid, None)
        # variable: Variable = self.data_table.get(vid, None)
        # if no lock on variable vid
        if not lock:
            shared_lock = SharedLock(vid, tid)
            self.lock_table[vid] = shared_lock
            return self.data_table[vid]
        # if exists a shared lock
        elif lock.isShared():
            lock.acquire(tid)
            return self.data_table[vid]
            # return variable.commit_values[-1][0]
            # check if this variable has write lock
            # if w_lock_queue
        # if exists an exclusive lock and t has access
        elif lock.isExclusive() and lock.hasAccess(tid):
            return transaction.temp_vars.get(vid)
        # if exists an exclusive lock and t has no access
        elif lock.isExclusive() and not lock.hasAccess(tid):
            wait_for[tid] = wait_for.get(tid, []) + [lock.tid]
            return None

        # for completion only
        return None

    def can_write(self, tid, vid, wait_for):
        lock:Lock = self.lock_table.get(vid)
        if not lock:
            return True
        # if a write lock and t has access
        # or a read lock and t is the only one sharing (can promote)
        if (lock.isExclusive() and lock.hasAccess(tid)) or (lock.isShared() and lock.canPromote(tid)):
            return True
        wait_for[tid] = list(set(wait_for.get(tid, []) + ([lock.tid] if lock.isExclusive() else lock.sharing)))
        return False

    def write(self, transaction, vid):
        tid = transaction.id
        lock: Lock = self.lock_table.get(vid, None)
        # variable: Variable = self.data_table.get(vid, None)
        # if no lock on variable vid
        if not lock:
            shared_lock = ExclusiveLock(vid, tid)
            self.lock_table[vid] = shared_lock
            return self.data_table[vid]
        # if exists a shared lock
        elif lock.isShared():
            if lock.canPromote(tid):
                self.lock_table[vid] = lock.promote(tid)
                return self.data_table[vid]
            # return variable.commit_values[-1][0]
            # check if this variable has write lock
            # if w_lock_queue
        # if exists an exclusive lock and t has access
        elif lock.isExclusive() and lock.hasAccess(tid):
            return transaction.temp_vars.get(vid)
        # if exists an exclusive lock and t has no access
        elif lock.isExclusive() and not lock.hasAccess(tid):
            return None

        # for completion only
        return None


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

    def abort(self, tid):
        """ release all locks acquired by tid
        """

        # release lock
        for vid, lock in list(self.lock_table.items()):
            if lock:
                self.lock_table[vid] = lock.release(tid)
            if not self.lock_table[vid]:
                self.lock_table.pop(vid)
        # self.update_lock_table()

    def commit(self, tid, vid, value, commit_time):
        # release current lock for this transaction
        lock = self.lock_table.get(vid)
        if lock:
            self.lock_table[vid] = lock.release(tid)
        # update commit queue
        var:Variable = self.data_table.get(vid)
        if var:
            var.add_commit_value(value, commit_time)

    def dump(self):
        print(f"site {self.id}",
              f"-",
              ", ".join([str(v) for v in self.data_table.values()]))

