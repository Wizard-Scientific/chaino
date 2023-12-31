import os
import shutil

import pytest

from web3 import Web3, HTTPProvider
from web3.middleware import simple_cache_middleware, geth_poa_middleware

from chaino.scheduler.call import CallScheduler
from chaino.scheduler.block import BlockScheduler
from chaino.rpc import RPC


from chaino.utils import init_logger
init_logger(level="INFO")


@pytest.fixture()
def w3():
    _w3 = Web3(HTTPProvider("https://rpc.ankr.com/fantom"))
    _w3.middleware_onion.add(simple_cache_middleware)
    return _w3

@pytest.fixture()
def rpc_fantom():
    _w3 = Web3(HTTPProvider("https://rpc.ftm.tools"))
    _w3.middleware_onion.add(simple_cache_middleware)
    return RPC(_w3, num_threads=2)

@pytest.fixture()
def rpc_bsc():
    _w3 = Web3(HTTPProvider("https://bsc-dataseed1.ninicoin.io/"))
    _w3.middleware_onion.add(simple_cache_middleware)
    _w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return RPC(_w3, num_threads=2)

@pytest.fixture()
def block_scheduler():
    scheduler = BlockScheduler(
        chain="fantom",
        filestore_path="/tmp/chaino"
    )
    return scheduler

@pytest.fixture()
def call_scheduler(rpc_fantom):
    scheduler = CallScheduler(state_path="/tmp/chaino")
    scheduler.add_rpc(rpc_fantom)
    return scheduler
