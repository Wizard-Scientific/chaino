import os
import time
import pickle
import logging
import threading

from .scheduler import Scheduler


class BlockScheduler(Scheduler):
    def add_task(self, block_identifier):
        "Add one task to be executed"

        # if file exists, do not add the task
        filename = f"{self.state_path}/{self.chain}-block-{block_identifier}.pkl"
        if not os.path.exists(filename):
            self.tasks.append((block_identifier))        
            logging.getLogger("chaino").debug(f"Added block {block_identifier} to task queue")

    def run_task(self, thread, block_identifier):
        logging.getLogger("chaino").debug(f"Started thread {thread.name}.")

        block = None
        while block is None:
            self.run_slow_if_necessary()

            try:
                block = self.w3.eth.getBlock(block_identifier, True)
            except:
                logging.getLogger("chaino").warning(f"Thread {thread} failed to get block {block_identifier}")
                self.slow_down()

        filename = f"{self.state_path}/{self.chain}-block-{block_identifier}.pkl"
        with open(filename, "wb") as f:
            pickle.dump(block, f)

        logging.getLogger("chaino").info(f"Wrote: {filename}")
        self.running_threads.remove(thread)

    def start(self):
        "Start the scheduler"
        logging.getLogger("chaino").info(f"Starting scheduler with {len(self.tasks)} tasks")

        for block_identifier in self.tasks:

            currently_running = 1e99
            # wait until there are fewer than num_threads running
            while currently_running >= self.num_threads:
                with self.lock:
                    currently_running = len(self.running_threads)

                if self.halt_event.is_set():
                    logging.getLogger("chaino").info("Halt event is set, exiting")

                time.sleep(0.001)

            # start a new thread
            thread = threading.Thread(target=self.run_task)
            thread._args = (thread, block_identifier)
            self.running_threads.add(thread)
            thread.start()

            self.tick()

        # wait for all threads to finish
        while len(self.running_threads) > 0:
            time.sleep(0.1)

        logging.getLogger("chaino").info("All tasks completed")
