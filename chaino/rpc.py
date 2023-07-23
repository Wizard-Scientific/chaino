import time
import logging
import threading

from web3 import Web3, HTTPProvider
from web3.middleware import simple_cache_middleware, geth_poa_middleware

from .utils import convert_signature_to_abi


class RPC:
    """
    RPC class for Chaino.
    """

    def __init__(self, w3=None, url=None, chain=None, poa=False, tick_delay=0.1, slow_timeout=30, num_threads=2):
        # provide some defaults for a few chains
        if not w3 and not url and chain:
            if chain in rpc_defaults.keys():
                url = rpc_defaults[chain]
            else:
                raise Exception(f"Unknown chain {chain}")

        if w3:
            self._w3 = w3
        elif url:
            self._w3 = Web3(HTTPProvider(url))
            self._w3.middleware_onion.add(simple_cache_middleware)

            if 'bsc' in url or 'binance' in url or 'avax' in url or 'avalanche' in url:
                poa = True
            if poa is True:
                self._w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        else:
            raise Exception("Either w3 or url must be provided")

        self.halt_event = threading.Event()
        self.lock = threading.Lock()
        self.running_threads = set()

        self.tick_delay = tick_delay
        self.num_threads = num_threads
        self.slow_mode = False
        self.slow_timeout = slow_timeout
        self.good_runs = 0
        self.good_runs_reset = 200
        self.too_fast = []

        self.task_counter = 0

    @property
    def w3(self):
        "Get the web3 instance."
        # enforce a delay by calling tick before returning w3
        self.tick()
        return self._w3

    def any_available_threads(self):
        "Check if any threads are available."
        with self.lock:
            return len(self.running_threads) < self.num_threads

    def any_threads_running(self):
        "Check if any threads are running."
        with self.lock:
            return len(self.running_threads) > 0

    def run_slow_if_necessary(self):
        "Run slowly if necessary."
        # if another thread received a 429, this will be set
        while self.slow_mode is True:
            time.sleep(0.01)

    def slow_down(self):
        "Slow down the RPC."
        with self.lock:
            check_slow_mode = self.slow_mode

        if check_slow_mode is False:
            # other threads on this RPC need to stop
            self.slow_mode = True

            logging.getLogger("chaino").warning(f"{self} too fast: {self.tick_delay}")

            self.too_fast.append(self.tick_delay)
            self.tick_delay += 0.005

            time.sleep(self.slow_timeout)
            self.slow_mode = False
        
    def consider_speedup(self):
        "Consider speeding up the RPC."
        with self.lock:
            self.good_runs += 1
            if self.good_runs >= self.good_runs_reset:
                self.good_runs = 0
                self.good_runs_reset = int(self.good_runs_reset * 1.1)
                self.tick_delay -= 0.001
                if self.tick_delay <= 0:
                    self.tick_delay = 0.001
                logging.getLogger("chaino").info(f"{self} faster: {self.tick_delay}")

    def tick(self):
        "Advance in time by one tick."
        self.run_slow_if_necessary()
        self.consider_speedup()
        time.sleep(self.tick_delay)

    def fetch_result(self, task_id, task_fn, *args):
        "Fetch the result of a task."
        result = None
        while result is None:
            self.run_slow_if_necessary()
            try:
                # this implements the tick delay implicitly
                result = task_fn(self.w3, *args)
            except Exception as e:
                logging.getLogger("chaino").warning(f"{self} failed {task_id}: {e}")
                self.slow_down()
        self.running_threads.remove(task_id)

    def dispatch_task(self, task_fn, *args):
        "Dispatch a task to the RPC."
        task_id = f"{task_fn.__name__}-{self.task_counter}"
        self.task_counter += 1
        logging.getLogger("chaino").debug(f"{self} {task_id}")

        # # for debugging, launch the task in the current thread
        # self.fetch_result(task_id, task_fn, *args)

        thread = threading.Thread(target=self.fetch_result, args=(task_id, task_fn, *args))
        self.running_threads.add(task_id)
        thread.start()
        return thread

    def __repr__(self):
        rpc_name = self._w3.provider.endpoint_uri.replace("https://", "")
        return f"<RPC {rpc_name[:25]}>"

    def eth_contract_function(self, address, function_signature):
        "Get a contract function for an address."
        checksum_address = Web3.toChecksumAddress(address)
        function_abi = convert_signature_to_abi(function_signature)
        contract = self._w3.eth.contract(address, abi=[function_abi])
        return contract.functions[function_abi["name"]]

    def eth_call(self, address, function_signature, block_number=None, *vargs):
        "Call a function on a contract."
        fn = self.eth_contract_function(address, function_signature)
        if block_number is None:
            return fn(*args).call()
        else:
            return fn(*args).call(block_identifier=block_number)

rpc_defaults = {
    "fantom": "https://rpc.ftm.tools",
    "binance": "https://bsc-dataseed1.binance.org/",
    "arbitrum": "https://arb1.arbitrum.io/rpc",
    "avalanche": "https://api.avax.network/ext/bc/C/rpc",
    "ethereum": "https://eth.llamarpc.com",
}

synonyms = {
    "bsc": "binance",
    "eth": "ethereum",
    "ftm": "fantom",
    "arb": "arbitrum",
    "avax": "avalanche",
}

for synonym in synonyms:
    rpc_defaults[synonym] = rpc_defaults[synonyms[synonym]]
