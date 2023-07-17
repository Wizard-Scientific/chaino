import os
import time
import random
import threading


class Scheduler:
    """
    Scheduler class for Chaino.    
    """

    def __init__(self):
        self.rpcs = []
        self.tasks = []

        self.halt_event = threading.Event()
        self.lock = threading.Lock()

        # create timestamp as YYYY-MM-DD-HH-MM-SS
        self.timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")

    def add_rpc(self, rpc):
        "Add an RPC to the scheduler."
        self.rpcs.append(rpc)

    def get_available_rpc(self):
        "Get an RPC that has available threads."

        # shuffle list of rpcs each time
        rpcs = self.rpcs.copy()
        random.shuffle(rpcs)
        for rpc in rpcs:
            if rpc.any_available_threads():
                return rpc

    def any_rpc_running(self):
        "Check if any RPC is running."
        for rpc in self.rpcs:
            if rpc.any_threads_running():
                return True

    def add_task(self):
        "Add one task to be executed"
        raise NotImplementedError
    
    def start(self):
        "Start the scheduler"
        raise NotImplementedError
    
    def get_result(self):
        "Get the result of a task"
        raise NotImplementedError
