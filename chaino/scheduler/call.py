import os
import time
import json
import logging
import threading

from ..grouped_multicall import GroupedMulticall
from . import Scheduler


class CallScheduler(Scheduler):
    """
    Call Scheduler class for Chaino.

    This scheduler is used to call functions on contracts.
    """

    def __init__(self, state_path, project_name="chaino", block_number=None, *args, **kwargs):
        "Initialize the scheduler."
        super().__init__(*args, **kwargs)

        self.state_path = state_path
        if not os.path.exists(self.state_path):
            os.makedirs(self.state_path)

        self.results = {}
        self.block_number = block_number
        self.filename = f"{self.state_path}/{project_name}-{self.timestamp}-results.json"

    def add_task(self, contract_address, function, input_value):
        "Add one call to the task queue"
        self.tasks.append((contract_address, function, input_value))
        logging.getLogger("chaino").debug(f"Added call {contract_address, function, input_value} to task queue")

    def start(self):
        "Start the scheduler"
        logging.getLogger("chaino").info(f"Starting scheduler with {len(self.tasks)} tasks")

        rpc = self.get_available_rpc()
        gmc = GroupedMulticall(rpc._w3, self.tasks, block_number=self.block_number, margin=0.6)
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
        "Get the result of a multicall"
        # must take w3 as the first option, even though we ignore it
        result = mc()
        with self.lock:
            self.results.update(result)
            with open (self.filename, "w") as f:
                json.dump(self.results, f)
        return result
    
    @classmethod
    def map_call(cls, rpc, contract_address, function_signature, inputs, block_number=None, state_path="/tmp/chaino"):
        """
        Call one function on one contract for a list of inputs.
        This is a common pattern when a function is invoked on a list of addresses.
        """

        call_scheduler = cls(
            block_number=block_number,
            state_path=state_path,
        )
        call_scheduler.add_rpc(rpc)

        for input_vector in inputs:
            call_scheduler.add_task(
                contract_address=contract_address,
                function=function_signature,
                input_value=input_vector,
            )

        return call_scheduler.start()


def parse_address(item):
    """
    Convenience function to parse an address in the special case that the function was called with a single parameter, which was an address.
    """
    return item.split(",")[2].split("'")[1]
