import os
import time
import pickle
import logging
import threading

from .scheduler import Scheduler


class BlockScheduler(Scheduler):
    def __init__(self, project_name="chaino", **kwargs):
        self.project_name = project_name
        super().__init__(**kwargs)

    def add_task(self, block_identifier):
        "Add one task to be executed"

        # if file exists, do not add the task
        filename = f"{self.state_path}/{self.project_name}-block-{block_identifier}.pkl"
        if not os.path.exists(filename):
            self.tasks.append((block_identifier))        
            # logging.getLogger("chaino").debug(f"Added block {block_identifier} to task queue")

    def start(self):
        "Start the scheduler"
        logging.getLogger("chaino").info(f"Starting scheduler with {len(self.tasks)} tasks")

        for block_identifier in self.tasks:

            # wait until an RPC is available
            available_rpc = None
            while available_rpc is None:
                available_rpc = self.get_available_rpc()
                if available_rpc is None:
                    time.sleep(0.001)

            # dispatch the task
            available_rpc.dispatch_task(self.get_block, block_identifier)

        logging.getLogger("chaino").info("Waiting for tasks to finish...")
        while self.any_rpc_running():
            time.sleep(0.1)
        logging.getLogger("chaino").info("All tasks completed")

    def get_block(self, w3, block_identifier):
        block = w3.eth.getBlock(block_identifier, True)
        filename = os.path.join(
            self.state_path,
            f"{self.project_name}-block-{block_identifier}.pkl"
        )
        with open(filename, "wb") as f:
            pickle.dump(block, f)
        # logging.getLogger("chaino").debug(f"Saved {filename}")
        return block
