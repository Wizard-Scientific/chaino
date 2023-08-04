import os
import time
import pickle
import logging

from nested_filestore import NestedFilestore
from . import Scheduler


class BlockScheduler(Scheduler):
    """
    BlockScheduler downloads blocks from a blockchain.
    Each task for the scheduler to simply download a single block.
    Block results are stored in a NestedFilestore as pickled web3.py objects.
    """

    def __init__(self, filestore_path, hierarchy_order=[3, 3, 3], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filestore = NestedFilestore(
            root_path=filestore_path,
            hierarchy_order=hierarchy_order
        )

    def add_task(self, block_number, check_existing=True):
        "Add one task to be executed"

        # if file exists, do not add the task
        if check_existing and self.filestore.exists(block_number):
            return

        self.tasks.append((block_number))
        logging.getLogger("chaino").debug(f"BlockScheduler task: get block {block_number}")

    def start(self):
        "Start the scheduler"
        logging.getLogger("chaino").info(f"BlockScheduler: start {len(self.tasks)} tasks")

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
        "Get a block from the blockchain and save it to disk"
        block = w3.eth.getBlock(block_number, True)
        with self.filestore.writer(block_number, overwrite=True) as f:
            pickle.dump(block, f, protocol=pickle.HIGHEST_PROTOCOL)

        # we must try to compact the group after writing the block, not during
        group_uri = self.filestore.index.which_group(block_number)
        group = self.filestore.index.get_group(group_uri)
        group.compact()

        logging.getLogger("chaino").debug(f"BlockScheduler saved: block {block_number}")
        return block
