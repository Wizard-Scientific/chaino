import pandas as pd

import os
import time
import logging
import threading

from .utils import init_logger


class Scheduler:
    def __init__(self, w3, chain, state_path="/tmp/chaino", tick_delay=0.1, num_threads=4):
        init_logger()

        self.w3 = w3
        self.chain = chain
        self.num_threads = num_threads

        self.halt_event = threading.Event()
        self.lock = threading.Lock()
        self.running_threads = set()
        self.tasks = []

        self.slow_mode = False
        self.tick_delay = tick_delay
        self.good_runs = 0
        self.good_runs_reset = 500

        self.set_state_path(state_path)

        # create timestamp as YYYY-MM-DD-HH-MM-SS
        self.timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")

    def set_state_path(self, state_path):
        self.state_path = state_path
        if not os.path.exists(self.state_path):
            os.makedirs(self.state_path)

    def run_slow_if_necessary(self):
        # if another thread received a 429, this will be set
        if self.slow_mode is True:
            time.sleep(self.num_threads)

    def slow_down(self):
        if self.slow_mode is False:
            self.slow_mode = True
            if self.good_runs >= 0:
                self.tick_delay += 0.005
                self.good_runs = -1
            delay = 60
            logging.getLogger("chaino").info(f"sleep for {delay} seconds; tick delay is now {self.tick_delay}")
            time.sleep(delay)
            self.slow_mode = False
        

    def consider_speedup(self):
        if self.good_runs < 0:
            return

        with self.lock:
            self.good_runs += 1
            if self.good_runs == self.good_runs_reset:
                self.good_runs = 0
                self.tick_delay -= 0.005
                if self.tick_delay <= 0:
                    self.tick_delay = 0.01
                logging.getLogger("chaino").info(f"Lowering tick delay to {self.tick_delay} after {self.good_runs_reset} good runs")

    def tick(self):
        self.run_slow_if_necessary()
        self.consider_speedup()
        time.sleep(self.tick_delay)
