""" TaskManager
defines class task manager
"""
from src.transaction import *

class TaskManager:
    instructions = ["read", "write", "begin", "end", "R", "W"]
    def __init__(self, id) -> None:
        self.id = id
    def begin(self, tid):
        print(f"tm: transaction {tid} begin")
    def end(self, tid):
        print(f"tm: transaction {tid} end")
    def R(self, tid, did):
        print(f"tm: {tid} reads {did}")
    def W(self, tid, did, value):
        print(f"tm: {tid} writes {did} {value}")
