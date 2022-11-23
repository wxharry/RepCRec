""" datamanager
defines class data manager
"""
from src.transaction import *
from src.variable import *

class DataManager:
    instructions = ["fail", "recover"]
    def __init__(self, id) -> None:
        self.is_up = True
        self.id = id
        self.data_table = {}
        self.lock_table = {}
        self.fail_time_list = []
        self.recover_time_list = []

    def set_variable(self, var):
        self.data_table[var.id] = var

    def dump(self):
        print(f"site {self.id}",
              f"-",
              ", ".join([str(v) for v in self.data_table.values()]))
        
