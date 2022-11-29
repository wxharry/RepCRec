""" Variable
defines class Variable
"""

from enum import Enum

class LockType(Enum):
    Read  = 0
    Write = 1

class Lock:
    def __init__(self, variable_id, lock_type: LockType):
        self.variable_id = variable_id
        self.lock_type = lock_type
        self.is_queued = False
    
    def isShared(self):
        return self.lock_type == LockType.Read

    def isExclusive(self):
        return self.lock_type == LockType.Write

class ExclusiveLock(Lock):
    def __init__(self, variable_id, transaction_id) -> None:
        Lock.__init__(variable_id, LockType.Write)
        self.tid = transaction_id

    def acquire(self, tid):
        pass
    
    def release(self, tid):
        pass

class SharedLock(Lock):
    def __init__(self, variable_id, transaction_id):
        super().__init__(variable_id, LockType.Read)
        self.sharing = [transaction_id]
    
    def acquire(self, tid):
        if tid not in self.sharing:
            self.sharing.append(tid)
    
    def release(self, tid):
        if tid in self.sharing:
            self.sharing.remove(tid)
    
    def promote(self):
        return ExclusiveLock(self, self.variable_id)
