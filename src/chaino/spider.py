import pandas as pd

import os
import time
import json
import copy
import pprint
import pickle
import threading

import requests

from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware, simple_cache_middleware, http_retry_request_middleware

from dotenv import load_dotenv
load_dotenv()


class ChainoSpider(object):
    def __init__(self, results_json_filename, chain, tick_delay=0.1, exit_early=False, resume=False):
        self.halt_event = threading.Event()
        self.lock = threading.Lock()
        self.running_threads = set()

        self.chain = chain

        self.slow_mode = False
        self.tick_delay = tick_delay
        self.good_runs = 0
        self.good_runs_reset = 500

        # instantiate a web3 remote provider
        self.w3 = Web3(HTTPProvider(os.environ[f'{chain.upper()}_WEB3_PROVIDER_URI']))

        # remove http retry middleware
        # self.w3.middleware_onion.remove(http_retry_request_middleware)

        # add cache for chain_id
        self.w3.middleware_onion.add(simple_cache_middleware)

        # for BSC, inject the POA compatibility middleware to the innermost layer (0th layer)
        if chain.lower() == "bsc":
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            self.gas_token_name = "BNB"
        elif chain.lower() == "fantom":
            self.gas_token_name = "FTM"
        elif chain.lower() == "ethereum":
            self.gas_token_name = "ETH"

        # seconds between saves, also time to wait at final iteration
        self.save_interval = 10

        # store results to this file
        self.results_json_filename = results_json_filename
        self.state_filename = results_json_filename.replace(".json", "-state.json")

        self.exit_early = exit_early
        if exit_early:
            self.save_interval = 2
            print("Will exit early")

        self.resume = resume

        self.task_state = {}

    def run_slow_if_necessary(self, thread_id):
        # if another thread received a 429, this will be set
        if self.slow_mode is True:
            print(f"Slow mode is active for thread {thread_id}")
            time.sleep(0.1)

        with self.lock:
            self.good_runs += 1
            if self.good_runs == self.good_runs_reset:
                self.good_runs = 0
                self.tick_delay -= 0.005
                if self.tick_delay <= 0:
                    self.tick_delay = 0.01
                print(f"\nLowering tick delay to {self.tick_delay} after {self.good_runs_reset} good runs\n")

        # and always delay by this amount
        time.sleep(self.tick_delay)

    def slow_down(self, thread_id):
        do_pause = False

        with self.lock:
            if self.slow_mode is not True:
                # other threads will enter slow mode
                self.slow_mode = True
                do_pause = True
        
        if do_pause:
            self.tick_delay += 0.01
            self.good_runs = 0
            delay = 0.3
            print(f"\nThread {thread_id} will sleep for {delay} seconds; tick delay is now {self.tick_delay}\n")
            time.sleep(delay)
            with self.lock:
                # release other threads from slow mode
                self.slow_mode = False

    def save_state(self):
        "Write state data to disk"

        results = {}
        with self.lock:
            for task_id in self.task_state.keys():
                results[task_id] = {
                    'results': self.task_state[task_id]['results'],
                    'addresses': self.task_state[task_id]['addresses']
                }

        with open(self.state_filename, "w") as f:
            json.dump(results, f)

        print("Saved state")

    def load_state(self):
        with self.lock:
            try:
                with open(self.state_filename, "r") as f:
                    loaded_state = json.load(f)
            except FileNotFoundError:
                print("No state file found, starting from scratch")
                return

        for task_id in self.task_state.keys():
            self.task_state[task_id]['results'] = loaded_state[task_id]['results']
            self.task_state[task_id]['addresses'] = loaded_state[task_id]['addresses']
            self.task_state[task_id]['total_addresses'] = len(self.task_state[task_id]['addresses'])
            print(f"Loaded task {task_id} with {len(self.task_state[task_id]['results'])} results and {len(self.task_state[task_id]['addresses'])} addresses left")

    def get_results(self, merged=False):
        """
        Obtain results from all tasks.

        When merged is True, the results for all tasks are merged into a single dict.
        """

        results = {}

        with self.lock:
            for task_id in self.task_state.keys():
                if merged:
                    results.update(self.task_state[task_id]['results'])
                else:
                    results[task_id] = self.task_state[task_id]['results']

        return results

    def run(self, *args, **kwargs):
        if self.resume:
            self.load_state()

        try:
            self.spider_event_loop(*args, **kwargs)
            self.halt_event.set()
            self.save_state()
            self.save_parallel_results()
        except KeyboardInterrupt:
            print("Keyboard interrupt, saving state")
            self.halt_event.set()
            time.sleep(0.3)
            self.save_state()

    def get_one_result(self, task_id, address):
        "Get result for address, retrying if necessary"

        result = None
        while result is None:
            # first slow down, if needed
            self.run_slow_if_necessary(task_id)

            try:
                fn = self.task_state[task_id]['contract_method'](address)
                if self.task_state[task_id]['block_identifier'] is None:
                    result = fn.call()
                else:
                    result = fn.call(block_identifier=self.task_state[task_id]['block_identifier'])
            except Exception as e:
                print(f"Thread {task_id} failed call() for address {address} with function {fn}")
                print(f"Error: {e}")
                self.slow_down(task_id)

        return result

    def spider_task(self, task_id):
        "Run a task"

        task_queue = self.task_state[task_id]['addresses']

        while not self.halt_event.is_set() and len(task_queue) > 0:
            with self.lock:
                # obtain first address in queue
                address = task_queue.pop(0)
            
            result = self.get_one_result(task_id, address)
            with self.lock:
                self.task_state[task_id]['results'][address] = result

            print(f"Result for {address} {task_id}: {result}", flush=True)

            if self.exit_early and len(self.task_state[task_id]['results']) > 5:
                break

        print(f"Thread {task_id} finished")
        self.running_threads.remove(task_id)

    def spider_event_loop(self):
        "Provide event loop to run all tasks until completion"

        for task_id in self.task_state.keys():
            print(f"Start task {task_id} for {self.task_state[task_id]['total_addresses']} addresses")
            threading.Thread(target=self.spider_task, args=[task_id]).start()
            self.running_threads.add(task_id)

        print("Started all threads")

        while len(self.running_threads) > 0:
            time.sleep(self.save_interval)
            buf = "\n"
            for task_id in self.task_state.keys():
                with self.lock:
                    buf += f"{task_id}: {(self.task_state[task_id]['total_addresses'] - len(self.task_state[task_id]['addresses'])) / self.task_state[task_id]['total_addresses'] * 100:0.2f}% "
            buf += "\n"
            print(buf, flush=True)
            self.save_state()

    def add_task(self, task_id, method_lambda, addresses, block_identifier=None):
        "Add one task to be executed during the event loop"

        self.task_state[task_id] = {}
        self.task_state[task_id]['addresses'] = copy.copy(addresses)
        self.task_state[task_id]['total_addresses'] = len(addresses)
        self.task_state[task_id]['contract_method'] = copy.copy(method_lambda)
        self.task_state[task_id]['block_identifier'] = block_identifier
        self.task_state[task_id]['results'] = {}

        print(f"added task: {task_id} with {len(addresses)} addresses for method {method_lambda} and block {block_identifier}")

    def add_parallel_tasks(self, num_tasks, method_lambda, addresses, block_identifier=None, task_name_fmt="parallel_task_{}"):
        "Add multiple tasks to be executed in parallel during the event loop"

        address_chunks = [addresses[i::num_tasks] for i in range(num_tasks)]
        print(f"Split into {len(address_chunks)} chunks")

        for chunk_id in range(len(address_chunks)):
            print(f"chunk {chunk_id} has length {len(address_chunks[chunk_id])}")

        for chunk_id in range(len(address_chunks)):
            self.add_task(
                task_id=task_name_fmt.format(chunk_id),
                method_lambda=method_lambda,
                addresses=address_chunks[chunk_id],
                block_identifier=block_identifier,
            )

    def save_parallel_results(self):
        results = self.get_results(merged=True)

        with open(self.results_json_filename, "w") as f:
            json.dump(results, f)

        print("Saved results to", self.results_json_filename)
