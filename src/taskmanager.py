""" TaskManager
defines class task manager
"""
from src.transaction import *
from src.variable import *

class TaskManager:
    instructions = ["read", "write", "begin","beginRO", "end", "R", "W", "dump"]
    def __init__(self, id, sites) -> None:
        self.id = id
        self.tick = 0
        self.transaction_table = {}
        self.sites = sites

    def parse_instruction(self, instruction, params, tick):
        self.tick = tick
        if instruction == 'beginRO':
            # TODO: check params
            self.beginRO(params.strip())
        elif instruction == 'begin':
            params = [param.strip() for param in params.split(',')]
            # TODO: check params
            self.begin(params[0].strip())
        elif instruction in ['R', 'read']:
            tid, vid = [param.strip() for param in params.split(',')]
            return self.R(tid, vid)
        elif instruction in ['W', 'write']:
            tid, vid, value = [param.strip() for param in params.split(',')]
            self.W(tid, vid, value)
        elif instruction == 'end':
            # TODO: params check
            self.end(params.strip())
        elif instruction == 'dump':
            self.dump()
        else:
            print(f"unrecognized command {instruction}, "
                  f"currently support [{', '.join(instruction)}]")

    def beginRO(self, tid):
        return self.begin(tid, True)

    def begin(self, tid, readonly=False):
        """ Return the transaction begins
        """
        if self.transaction_table.get(tid):
            print(f"transaction {tid} already exists")
            return None
        transaction = Transaction(tid, self.tick, readonly)
        if readonly:
            transaction.set_snapshot(self.sites)
        self.transaction_table[tid] = transaction
        return tid

    def end(self, tid):
        """ Return the transaction ends
        """
        # TBD: to abort
        t: Transaction = self.transaction_table.get(tid)
        if not t:
            print(f"No transaction {tid} is found in transaction table")
            return None
        for vid, val in t.temp_vars.items():
            for site in self.sites.values():
                site.commit(tid, vid, val, self.tick)
        return self.transaction_table.pop(tid)

    def R(self, tid, vid):
        t:Transaction = self.transaction_table.get(tid)
        if not t:
            print(f"No transaction {tid} is found in transaction table")
            return None
        # it t is not readonly, reads from current sites; otherwise reads from the snapshot
        if t.is_read_only:
            for site in t.snapshot.values():
                if site.is_up and site.data_table.get(vid):
                    return site.data_table.get(vid)
        else:
            for site in self.sites.values():
                if site.is_up and site.data_table.get(vid):
                    return site.read(self.transaction_table[tid], vid)

        return None # format only, no meaning

    def W(self, tid, vid, value):
        t:Transaction = self.transaction_table.get(tid)
        if not t:
            print(f"No transaction {tid} is found in transaction table")
            return None

        # a transaction can only write to a variable if and only if 
        # it acquires all the lock on the variable from all the sites
        # if not, it should not acquire any locks on variable
        site_to_write = []
        for site in self.sites.values():
            if site.data_table.get(vid):
                can_write = site.can_write(tid, vid)
                if site.is_up and can_write:
                    site_to_write.append(site)

                # if a site that has variable vid
                # is down or
                # cannot acquire write lock,
                # fail the write command
                else:
                    # fail to write
                    site_to_write = []
                    break
        
        # ready to write
        for site in site_to_write:
            site.write(t, vid)
            t.temp_vars[vid] = value
        return
    
    def dump(self):
        for dm in self.sites.values():
            dm.dump()

