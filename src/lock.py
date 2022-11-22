""" Variable
defines class Variable
"""

from enum import Enum

class LockType(Enum):
    Read : 0
    Write: 1

class Lock:
    def __init__(self, variable_id: int, lock_type: LockType):
        self.variable_id = variable_id
        self.lock_type = lock_type
        self.is_queued = False

