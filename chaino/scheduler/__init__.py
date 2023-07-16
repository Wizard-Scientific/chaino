import os
import time
import random
import threading


class Scheduler:
    def __init__(self, state_path="/tmp/chaino", project_name="chaino"):
        self.project_name = project_name
        self.set_state_path(state_path)

        self.rpcs = []
        self.tasks = []
        self.results = {}

        self.halt_event = threading.Event()
        self.lock = threading.Lock()

        # create timestamp as YYYY-MM-DD-HH-MM-SS
        self.timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")

    def set_state_path(self, state_path):
        self.state_path = state_path
        if not os.path.exists(self.state_path):
            os.makedirs(self.state_path)

    def add_rpc(self, rpc):
        self.rpcs.append(rpc)

    def get_available_rpc(self):
        # shuffle list of rpcs each time
        rpcs = self.rpcs.copy()
        random.shuffle(rpcs)
        for rpc in rpcs:
            if rpc.any_available_threads():
                return rpc

    def any_rpc_running(self):
        for rpc in self.rpcs:
            if rpc.any_threads_running():
                return True