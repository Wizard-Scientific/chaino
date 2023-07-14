import os
import time
import json
import logging
import threading

from ..grouped_multicall import GroupedMulticall
from . import Scheduler


class CallScheduler(Scheduler):
    def add_task(self, contract_address, function, input_value, block_identifier=None):
        "Add one call to the task queue"
        self.tasks.append((contract_address, function, input_value, block_identifier))
        # logging.getLogger("chaino").debug(f"Added call {contract_address, function, input_value, block_identifier} to task queue")

    def run_task(self, thread, mc):
        logging.getLogger("chaino").debug(f"Started thread {thread.name}.")
        filename = f"{self.state_path}/{self.timestamp}-results.json"

        # loop until successful; errors out after 10 tries
        try:
            result = mc()
        except Exception as e:
            logging.getLogger("chaino").error(f"Multicall failed: {e}")

        # obtain lock
        with self.lock:
            # get current state
            try:
                with open (filename, "r") as f:
                    current_state = json.load(f)
            except:
                current_state = {}

            # update current state
            current_state.update(result)

            # write results as json
            with open (filename, "w") as f:
                json.dump(current_state, f)

        logging.getLogger("chaino").info(f"Thread finished: {thread.name}; updated state: {filename}")
        self.running_threads.remove(thread)

    def start(self):
        "Start the scheduler"
        logging.getLogger("chaino").info(f"Starting scheduler with {len(self.tasks)} tasks")

        gmc = GroupedMulticall(self.w3, self.tasks, margin=0.6)
        for mc in gmc():

            currently_running = 1e99
            while currently_running >= self.num_threads:
                with self.lock:
                    currently_running = len(self.running_threads)

                if self.halt_event.is_set():
                    logging.getLogger("chaino").info("Halt event is set, exiting")

                time.sleep(0.1)
            
            thread = threading.Thread(target=self.run_task)
            thread._args = (thread, mc)
            self.running_threads.add(thread)
            thread.start()

        # wait for all threads to finish
        while len(self.running_threads) > 0:
            time.sleep(0.1)

        logging.getLogger("chaino").info("All tasks completed")

    def get_call_result(self, w3, contract_address, function, input_value, block_identifier=None):
        pass
