import pandas as pd

import os
import time
import json
import copy
import logging
import pickle
import threading

import requests

from dotenv import load_dotenv
load_dotenv()

from .grouped_multicall import GroupedMulticall
from .utils import init_logger


class Scheduler:
    def __init__(self, w3, chain, num_threads=2):
        init_logger()

        self.w3 = w3
        self.chain = chain
        self.num_threads = num_threads

        self.halt_event = threading.Event()
        self.lock = threading.Lock()
        self.running_threads = set()
        self.tasks = []

        self.slow_mode = False
        self.tick_delay = 500
        self.good_runs = 0
        self.good_runs_reset = 500

        self.state_path = "/tmp"

    def add_task(self, contract_address, function, input_value, block_identifier=None):
        "Add one task to be executed"
        self.tasks.append((contract_address, function, input_value, block_identifier))
        logging.getLogger("chaino").debug(f"Added {contract_address, function, input_value, block_identifier} to task queue")

    def run_multicall(self, thread, mc):
        logging.getLogger("chaino").debug(f"Started thread {thread.name}.")
        filename = f"{self.state_path}/{self.timestamp}-results.json"

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

        # create timestamp as YYYY-MM-DD-HH-MM-SS
        self.timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")

        gmc = GroupedMulticall(self.w3, self.tasks, margin=0.6)
        for mc in gmc():

            currently_running = 1e99
            while currently_running >= self.num_threads:
                with self.lock:
                    currently_running = len(self.running_threads)

                if self.halt_event.is_set():
                    logging.getLogger("chaino").info("Halt event is set, exiting")

                time.sleep(0.1)
            
            thread = threading.Thread(target=self.run_multicall)
            thread._args = (thread, mc)
            self.running_threads.add(thread)
            thread.start()

        # wait for all threads to finish
        while len(self.running_threads) > 0:
            time.sleep(0.1)

        logging.getLogger("chaino").info("All tasks completed")
