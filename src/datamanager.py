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
        self.lock_queue = {}
        self.temp_vars = {}

    def parse_instruction(self, instruction, tick):
        if instruction == 'fail':
            self.fail(tick)
        if instruction == 'recover':
            self.recover(tick)

    def set_variable(self, var):
        self.data_table[var.id] = var

    # def has_write_lock_in_queue()
    
    def read(self, transaction:Transaction, vid, wait_for):
        tid = transaction.id
        lock: Lock = self.lock_table.get(vid, None)
        # variable: Variable = self.data_table.get(vid, None)
        # if no lock on variable vid
        variable = self.data_table[vid]
        if variable.access == False:
            return None
        if not lock:
            shared_lock = SharedLock(vid, tid)
            self.lock_table[vid] = shared_lock
            return self.data_table[vid]
        # if exists a shared lock
        elif lock.isShared():
            # check if this variable has write lock in the queue
            # if there is a write lock waiting for the current shared lock, wait til that write finishes
            if len(self.lock_queue.get(vid, [])) > 0:
                prev_ts = self.lock_queue[vid]
                if tid not in prev_ts:
                    wait_for[tid] = wait_for.get(tid, []) + [prev_ts[-1]]
                    return None
            lock.acquire(tid)
            return self.data_table[vid]
        # if exists an exclusive lock and t has access
        elif lock.isExclusive() and lock.hasAccess(tid):
            return transaction.temp_vars.get(vid)
        # if exists an exclusive lock and t has no access
        elif lock.isExclusive() and not lock.hasAccess(tid):
            print(f"{tid} waits")
            wait_for[tid] = wait_for.get(tid, []) + lock.tids
            return None

        # for completion only
        return None
    
    def read_only(self, vid, begin_time):
        variable = self.data_table[vid]
        if variable.access:
            for commit_pair in variable.commit_values[::-1]:
                commit_value = commit_pair[0]
                commit_time = commit_pair[1]
                if commit_time <= begin_time:
                    # Upon recovery of a site s, the site makes replicated variables available for writing, but not reading.
                    if variable.is_replicated:
                        for fail_time in self.fail_time_list:
                            if fail_time > commit_time:
                                return None
                    # make a new variable for output only
                    # add an arbitrary tick 
                    return Variable(vid, commit_value, -1)
        
        return None



    def can_promote(self, tid, lock, wait_for):
        """ returns if tid can promote on a shared lock
        """
        waiters = [waiter for waiter, occupants in wait_for.items() if tid in occupants]
        if lock.isShared() and lock.hasAccess(tid) and len(lock.tids) == 1 \
            and len(waiters) == 0:
            return True
        wait_for[tid] = list(set(wait_for.get(tid, []) + ([id for id in waiters if not id == tid])))
        return False

    def add_lock_to_queue(self, lock, vid):
        locks = self.lock_queue.get(vid, [])
        for l in locks:
            if l.lock_type == lock.lock_type and l.tids == lock.tids:
                return
        locks.append(lock)
                

    def can_write(self, tid, vid, wait_for):
        """ returns if tid can acquire write lock on vid
        if not, it will add wait-for edges to the wait-for graph
        """
        lock:Lock = self.lock_table.get(vid)
        if not lock:
            return True
        # if a write lock and t has access
        # or a read lock and t is the only one sharing (can promote)
        # if t cannot promote a shared lock, it will update wait-for graph, 
        # make sure t has access to the lock before checking if the lock can be promoted
        # print("can promote", self.can_promote(tid, lock, wait_for))
        if (lock.isExclusive() and lock.hasAccess(tid)) or (lock.isShared() and lock.hasAccess(tid) and self.can_promote(tid, lock, wait_for)):
            return True
        print(f"{tid} waits")
        # add the tid to the lock queue to wait if tid has not been added to the queue
        # self.lock_queue[vid] =  self.lock_queue.get(vid, []) + ([lock] if lock.tid not in self.lock_queue.get(vid, []) else [])
        self.add_lock_to_queue(lock, vid)
        wait_for[tid] = list(set(wait_for.get(tid, []) + (lock.tids if lock.isExclusive() else [id for id in lock.tids if not id == tid])))
        return False

    def write(self, tid, vid, value):
        lock: Lock = self.lock_table.get(vid, None)
        # variable: Variable = self.data_table.get(vid, None)
        # if no lock on variable vid
        if not lock:
            w_lock = ExclusiveLock(vid, tid)
            self.lock_table[vid] = w_lock
            self.temp_vars[tid] = self.temp_vars.get(tid, {})
            self.temp_vars[tid][vid] = value
            return value
        # if exists a shared lock
        elif lock.isShared():
            self.lock_table[vid] = lock.promote(tid)
            self.temp_vars[tid] = self.temp_vars.get(tid, {})
            self.temp_vars[tid][vid] = value
            return value
            # return variable.commit_values[-1][0]
            # check if this variable has write lock
            # if w_lock_queue
        # if exists an exclusive lock and t has access
        elif lock.isExclusive() and lock.hasAccess(tid):
            self.temp_vars[tid] = self.temp_vars.get(tid, {})
            self.temp_vars[tid][vid] = value
            return value
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
        self.lock_queue.clear()


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
        """ release all locks acquired by tid, and remove from lock queue
        """

        # release lock
        for vid, lock in list(self.lock_table.items()):
            if lock:
                self.lock_table[vid] = lock.release(tid)
            if not self.lock_table[vid]:
                self.lock_table.pop(vid)

        # remove from lock queue
        for queue in self.lock_queue.values():
            if tid in queue:
                queue.remove(tid)
        if tid in self.temp_vars:
            self.temp_vars.pop(tid)

    def commit(self, tid, commit_time):
        # release current lock for tid
        for id, lock in list(self.lock_table.items()):
            if lock and lock.hasAccess(tid):
                self.lock_table[id] = lock.release(tid)
        
        # remove from lock queue
        for queue in self.lock_queue.values():
            if tid in queue:
                queue.remove(tid)

        # update new values to the variables in data_table
        if self.temp_vars.get(tid):
            for vid, val in self.temp_vars[tid].items():
                var:Variable = self.data_table.get(vid)
                if var:
                    var.add_commit_value(val, commit_time)

    def dump(self):
        print(f"site {self.id}",
              f"-",
              ", ".join([str(v) for v in self.data_table.values()]))

