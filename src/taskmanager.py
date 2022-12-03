""" TaskManager
defines class task manager
"""
from src.transaction import *
from src.variable import *
from copy import deepcopy

class TaskManager:
    instructions = ["read", "write", "begin","beginRO", "end", "r", "w", "dump"]
    def __init__(self, id, sites) -> None:
        self.id = id
        self.tick = 0
        self.transaction_table = {}
        self.sites = sites
        self.wait_for_graph = {}
        self.operations_queue = []

    def parse_instruction(self, instruction, params, tick):
        # if solve deadlock, process queued operations
        while self.solve_deadlock():
            # print("solve deadlock")
            self.execute_cmd_queue()
        
        self.tick = tick
        if instruction == 'beginRO':
            # : check params
            self.beginRO(params.strip())
        elif instruction == 'begin':
            params = [param.strip() for param in params.split(',')]
            # TODO: check params
            self.begin(params[0].strip())
        elif instruction in ['r', 'read']:
            tid, vid = [param.strip() for param in params.split(',')]
            self.operations_queue.append(('R', (tid, vid)))
            # return self.R(tid, vid)
        elif instruction in ['w', 'write']:
            tid, vid, value = [param.strip() for param in params.split(',')]
            self.operations_queue.append(('W', (tid, vid, value)))
            # self.W(tid, vid, value)
        elif instruction == 'end':
            # TODO: params check
            self.end(params.strip())
        elif instruction == 'dump':
            self.dump()
        elif instruction == "fail":
            self.fail(int(params))
        elif instruction == "recover":
            self.recover(int(params))
        else:
            print(f"unrecognized command {instruction}, "
                  f"currently support [{', '.join(instruction)}]")

        self.execute_cmd_queue()
    
    def execute_cmd_queue(self):
        new_queue = []
        # print(self.operations_queue)
        for operation in self.operations_queue:
            type, params = operation[0], operation[1]
            tid, *params = params
            t = self.transaction_table.get(tid)
            if not t:
                continue
            if type == 'R':
                r = self.R(tid, params[0])
                if not r and t.should_abort == False:
                    new_queue.append(operation)
                    print(f"{tid} is waiting because the site is down\n")
                else:
                    print(r)
            elif type == 'W':
                r = self.W(tid, params[0], params[1])
                if not r:
                    new_queue.append(operation)
            else:
                raise "Invalid Command: invalid operation.\n"
        # print(new_queue)
        self.operations_queue = new_queue
        # if r:
        #     self.operations_queue.remove(t)
        # elif not r and t.should_abort == True:
        #     self.operations_queue.remove(t)
        


    def solve_deadlock(self):
        def findCycle(graph):
            cycles = []
            def dfs(path, visited, graph):
                cur = path[-1]
                if len(path) > 2 and path[0] == path[-1]:
                    cycles.append(path)
                    return
                for node in graph.get(cur, []):
                    if node not in visited:
                        visited.append(node)
                        path.append(node)
                        dfs(path, visited, graph)
                return

            for node in graph.keys():
                visited = []
                dfs([node], visited, graph)
            return cycles

        wait_for_graph = self.wait_for_graph
        # print("wait for graph", wait_for_graph)
        # find cycles in wait-for graph
        cycles = findCycle(wait_for_graph)
        # if no cycle found, return False
        if len(cycles) == 0:
            return False
        # find the youngest transaction
        cycle = cycles[0]
        youngest_transaction = max(cycle, key=lambda tid: self.transaction_table[tid].begin_time)
        # print(f"abort transaction {youngest_transaction}")
        self.abort(youngest_transaction)
        return True

    def beginRO(self, tid):
        return self.begin(tid, True)

    def begin(self, tid, readonly=False):
        """ begin a transaction
        """
        if self.transaction_table.get(tid):
            print(f"transaction {tid} already exists")
            return None
        transaction = Transaction(tid, self.tick, readonly)
        if readonly:
            transaction.set_snapshot(deepcopy(self.sites))
        self.transaction_table[tid] = transaction
        return tid

    def update_wait_for(self, tid):
        """ removes tid from wait-for graph
        """
        for t1, ts in list(self.wait_for_graph.items()):
            if tid in ts:
                ts.remove(tid)
            # if wait for no one or t1 is aborted
            if ts == [] or t1 == tid:
                self.wait_for_graph.pop(t1)       

    def abort(self, tid):
        """ commands all sites to abort tid
        """
        print(f"{tid} aborts")
        t: Transaction = self.transaction_table[tid]
        self.update_wait_for(tid)
        # set the transaction.should_abort to True
        t.abort()
        # abort the youngest transaction on each site        
        for site in self.sites.values():
            site.abort(tid)

    def commit(self, tid):
        """ commands all sites to commit (update temp_vars to variables in sites)
        """
        print(f"{tid} commits")
        t = self.transaction_table.get(tid)
        for site in self.sites.values():
            site.commit(t, self.tick)

    def end(self, tid):
        """ the transaction ends
        """
        t: Transaction = self.transaction_table.get(tid)
        if not t:
            print(f"No transaction {tid} is found in transaction table")
            return None
        # abort it t is set should_abort
        if t.should_abort:
            self.abort(tid)
        # commit to all sites
        else:                
            # TODO: some sites could be failed
            self.commit(tid)
        return self.transaction_table.pop(tid)

    def R(self, tid, vid):
        t:Transaction = self.transaction_table.get(tid)
        if not t:
            # print(f"No transaction {tid} is found in transaction table")
            return None
        # it t is not readonly, reads from current sites; otherwise reads from the snapshot
        if t.is_read_only:
            for site in t.snapshot.values():
                if site.is_up and site.data_table.get(vid):
                    result = site.read_only(vid, t.begin_time)
                    if result:
                        return result
            
            variable = self.data_table[vid]
            if variable.is_replicated == True:
                t.abort()
                return None
        else:
            for site in self.sites.values():
                if site.is_up and site.data_table.get(vid):
                    r = site.read(self.transaction_table[tid], vid, self.wait_for_graph)
                    if r:
                        t.site_access_list.append(site.id)
                        return r

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
                can_write = site.can_write(tid, vid, self.wait_for_graph)
                if site.is_up and can_write:
                    site_to_write.append(site)

                # if a site that has variable vid
                # is down or
                # cannot acquire write lock,
                # fail the write command
                else:
                    # fail to write, set list site_to_write to empty
                    site_to_write = []
                    # print(f"{tid} fails to write {vid}")
                    return None
        # ready to write
        for site in site_to_write:
            site.write(t, vid)
            t.site_access_list.append(site.id)
            t.temp_vars[vid] = value
        print(f"{tid} writes {vid}: {value} at {', '.join([f's{site.id}' for site in site_to_write])}")
        return value

    def fail(self, site_id):
        if site_id < 1 or site_id > 10: 
            raise "Invalid Command: invalid site id.\n"
        site = self.sites[site_id]
        site.fail(self.tick)
        print(f"site {site_id} fails at time {self.tick}\n")
        for tid, transaction in self.transaction_table.items():
            if not (transaction.is_read_only or transaction.should_abort):
                if site_id in transaction.site_access_list:
                    transaction.abort()
                    print(f"Abort transaction {tid}\n")

    def recover(self, site_id):
        if site_id < 1 or site_id > 10: 
            raise "Invalid Command: invalid site id.\n"
        site = self.sites[site_id]
        site.recover(self.tick)
        print(f"site {site_id} fails at time {self.tick}\n")

    def dump(self):
        for dm in self.sites.values():
            dm.dump()

