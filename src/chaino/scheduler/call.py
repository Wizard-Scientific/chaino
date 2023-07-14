import os
import time
import json
import logging
import threading

from ..grouped_multicall import GroupedMulticall
from . import Scheduler


class CallScheduler(Scheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = f"{self.state_path}/{self.project_name}-{self.timestamp}-results.json"

    def add_task(self, contract_address, function, input_value, block_number=None):
        "Add one call to the task queue"
        self.tasks.append((contract_address, function, input_value, block_number))
        logging.getLogger("chaino").debug(f"Added call {contract_address, function, input_value, block_number} to task queue")

    def start(self):
        "Start the scheduler"
        logging.getLogger("chaino").info(f"Starting scheduler with {len(self.tasks)} tasks")

        rpc = self.get_available_rpc()
        gmc = GroupedMulticall(rpc._w3, self.tasks, margin=0.6)
        for mc in gmc():
            # wait for a thread to become available
            while not rpc.any_available_threads():
                time.sleep(0.01)

            # dispatch the task
            rpc.dispatch_task(self.get_result, mc)

        logging.getLogger("chaino").info("Waiting for tasks to finish...")
        while self.any_rpc_running():
            time.sleep(0.1)
        logging.getLogger("chaino").info("All tasks completed")

        return self.results.copy()

    def get_result(self, w3, mc):
        # must take w3 as the first option, even though we ignore it

        result = mc()
        with self.lock:
            self.results.update(result)
            with open (self.filename, "w") as f:
                json.dump(self.results, f)
        return result
    