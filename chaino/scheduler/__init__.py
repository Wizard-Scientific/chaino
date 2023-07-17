import os
import time
import json
import random
import logging
import threading

from ..rpc import RPC


class Scheduler:
    """
    Scheduler class for Chaino.    
    """

    def __init__(self, chain=None):
        self.rpcs = []
        self.tasks = []

        self.halt_event = threading.Event()
        self.lock = threading.Lock()

        # create timestamp as YYYY-MM-DD-HH-MM-SS
        self.timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")

        if chain:
            self.add_rpcs(chain)

    def add_rpc(self, rpc):
        "Add an RPC to the scheduler."
        self.rpcs.append(rpc)

    def add_rpcs(self, chain):
        "Add a quick RPC to the scheduler."
        if not self.add_rpc_config(chain):
            self.add_rpc_default(chain)

    def add_rpc_config(self, chain, config_filename="~/.config/chaino/rpc.json"):
        config_filename = os.path.expanduser(config_filename)
        if os.path.exists(config_filename):
            with open(config_filename, "r") as f:
                rpc_list = json.load(f)
            if chain in rpc_list:
                rpcs = rpc_list[chain]
                random.shuffle(rpcs)
                for rpc_config in rpcs[:8]:
                    self.add_rpc(RPC(**rpc_config))
                    logging.getLogger("chaino").info(f"Added RPC {rpc_config['url']} to scheduler")
                return True
            else:
                logging.getLogger("chaino").warning(f"Chain {chain} not found in ~/.config/chaino/rpc.json")

    def add_rpc_default(self, chain, tick_delay=0.15, slow_timeout=120, num_threads=2):
        "Add a default RPC to the scheduler."
        self.add_rpc(RPC(chain=chain, tick_delay=tick_delay, slow_timeout=slow_timeout, num_threads=num_threads))

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
