import os
import time
import pickle
import logging

from ..nested_filestore import NestedFilestore
from . import Scheduler


class BlockScheduler(Scheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filestore = NestedFilestore(self.state_path, [4, 3, 2])

    def add_task(self, block_number, check_existing=True):
        "Add one task to be executed"

        # if file exists, do not add the task
        if check_existing and self.filestore.exists(block_number):
            return

        self.tasks.append((block_number))
        # logging.getLogger("chaino").debug(f"Added block {block_number} to task queue")

    def start(self):
        "Start the scheduler"
        logging.getLogger("chaino").info(f"Starting scheduler with {len(self.tasks)} tasks")

        for block_number in self.tasks:
            # wait until an RPC is available
            available_rpc = None
            while available_rpc is None:
                available_rpc = self.get_available_rpc()
                if available_rpc is None:
                    time.sleep(0.001)

            # dispatch the task
            available_rpc.dispatch_task(self.get_block, block_number)

        logging.getLogger("chaino").info("Waiting for tasks to finish...")
        while self.any_rpc_running():
            time.sleep(0.1)
        logging.getLogger("chaino").info("All tasks completed")

    def get_block(self, w3, block_number):
        block = w3.eth.getBlock(block_number, True)
        filename = os.path.join(
            self.state_path,
            f"{self.project_name}-block-{block_number}.pkl"
        )
        with self.filestore.writer(block_number, overwrite=True) as f:
            pickle.dump(block, f)
        # logging.getLogger("chaino").debug(f"Saved {filename}")
        return block