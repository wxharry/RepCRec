""" Variable
defines class Variable
"""

from enum import Enum

class LockType(Enum):
    Read  = 0
    Write = 1

class Lock:
    def __init__(self, variable_id, lock_type: LockType):
        """ 
            Description: initialize Lock Object
            Input: variable id, lock type
            Output: None
            Date: 11/28/2022
            Author: Yulin Hu
        """
        self.variable_id = variable_id
        self.lock_type = lock_type
    
    def isShared(self):
        return self.lock_type == LockType.Read

    def isExclusive(self):
        return self.lock_type == LockType.Write

class ExclusiveLock(Lock):
    def __init__(self, variable_id, transaction_id) -> None:
        """ 
            Description: initialize ExclusiveLock Object
            Input: variable id, transaction id
            Output: None
            Date: 11/28/2022
            Author: Yulin Hu
        """
        Lock.__init__(self, variable_id, LockType.Write)
        self.tids = [transaction_id]

    def acquire(self, tid):
        self.tids = [tid]
    
    def release(self, tid):
        if self.tids == [tid]:
            self.tids = []
        return None

    def hasAccess(self, tid):
        return [tid] == self.tids

class SharedLock(Lock):
    def __init__(self, variable_id, transaction_id):
        """ 
            Description: initialize SharedLock Object
            Input: variable id, transaction id
            Output: None
            Date: 11/28/2022
            Author: Yulin Hu
        """
        super().__init__(variable_id, LockType.Read)
        self.tids = [transaction_id]

    def acquire(self, tid):
        if tid not in self.tids:
            self.tids.append(tid)

    def release(self, tid):
        if tid in list(self.tids):
            self.tids.remove(tid)
        if len(self.tids) == 0:
            return None
        return self

    def hasAccess(self, tid):
        return tid in self.tids


    def promote(self, tid):
        return ExclusiveLock(self.variable_id, tid)
