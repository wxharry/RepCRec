""" Variable
defines class Variable
"""
class Variable:
    def __init__(self, vid, commit_value, commit_time, is_replicated=False):
        # assert id <= 20 and id >= 1
        self.id = vid
        # self.value = value
        self.is_replicated = is_replicated
        self.commit_values = [(commit_value, commit_time)]
        self.temp_value = None # format (value, tid)
        self.access = True

    def get_recent_value(self):
        return self.commit_values[-1][0]
    
    def get_temp_value(self):
        return self.temp_value
    
    def add_commit_value(self, value: int, ts):
        self.commit_values.append((value, ts))

    def __str__(self) -> str:
        return f"{self.id}: {self.commit_values[-1][0]}"

    def __repr__(self) -> str:
        return self.__str__()
