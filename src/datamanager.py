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

        for n in range(1,21):
            if n % 2 == 0:
                self.data_table[n] =  Variable(n)
            elif n % 10 + 1 == self.id:
                self.data_table[n] = Variable(n)

        
