""" datamanager
defines class data manager
"""
from src.transaction import *

class DataManager:
    instructions = ["fail", "recover"]
    def __init__(self, id) -> None:
        self.id = id
    def fail(self):
        print(f"dm: fail site {self.id}")
    def recover(self):
        print(f"dm: recover site {self.id}")
        
