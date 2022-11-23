""" Variable
defines class Variable
"""
class Variable:
    def __init__(self, id, value, is_replicated=False):
        # assert id <= 20 and id >= 1
        self.id = id
        self.value = value
        self.is_replicated = is_replicated
        self.commit_values = [self.value]
        self.temp_value = None

    def get_recent_value(self):
        return self.commit_values[-1]
    
    def get_temp_value(self):
        return self.temp_value
    
    def add_commit_value(self, value: int):
        self.commit_values.append(value)

    def __str__(self) -> str:
        return f"{self.id}: {self.value}"

    def __repr__(self) -> str:
        return self.__str__()