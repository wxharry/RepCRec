""" Transaction
defines class transactions
"""
class Transaction:
    def __init__(self, id) -> None:
        self.id = id
    def __str__(self) -> str:
        return f"transaction_{self.id}"
