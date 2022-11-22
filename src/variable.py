""" Variable
defines class Variable
"""
class Variable:
    def __init__(self, id: int):
        assert id <= 20 and id >= 1
        self.id = id
        self.value = id * 10
        self.is_replicated = id % 2 == 0
        self.commit_values = [self.value]
        self.temp_value = None

    def get_recent_value(self):
        return self.commit_values[-1]
    
    def get_temp_value(self):
        return self.temp_value
    
    def add_commit_value(self, value: int):
        self.commit_values.append(value)

