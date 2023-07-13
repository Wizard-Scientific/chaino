import os

import pytest

from web3 import Web3, HTTPProvider
from web3.middleware import simple_cache_middleware

from chaino.scheduler import Scheduler
from chaino.call_scheduler import CallScheduler
from chaino.block_scheduler import BlockScheduler
from chaino.rpc import RPC
from chaino.nested_filestore import NestedFilestore


from chaino.utils import init_logger
init_logger(level="INFO")


@pytest.fixture()
def w3():
    _w3 = Web3(HTTPProvider("https://rpc.ankr.com/fantom"))
    _w3.middleware_onion.add(simple_cache_middleware)
    return _w3

@pytest.fixture()
def block_scheduler_multi(rpc_fantom_ankr, rpc_fantom_ftmtools):
    scheduler = BlockScheduler(state_path="/tmp/chaino-test")
    scheduler.add_rpc(rpc_fantom_ankr)
    scheduler.add_rpc(rpc_fantom_ftmtools)
    return scheduler

@pytest.fixture()
def block_scheduler(rpc_fantom_ftmtools):
    scheduler = BlockScheduler(state_path="/tmp/chaino-test")
    scheduler.add_rpc(rpc_fantom_ftmtools)
    return scheduler

@pytest.fixture()
def call_scheduler(rpc_fantom_ftmtools):
    scheduler = CallScheduler(state_path="/tmp/chaino-test")
    scheduler.add_rpc(rpc_fantom_ftmtools)
    return scheduler

@pytest.fixture()
def rpc_fantom_ankr():
    _w3 = Web3(HTTPProvider("https://rpc.ankr.com/fantom"))
    _w3.middleware_onion.add(simple_cache_middleware)
    return RPC(_w3, num_threads=4)

@pytest.fixture()
def rpc_fantom_ftmtools():
    _w3 = Web3(HTTPProvider("https://rpc.ftm.tools"))
    _w3.middleware_onion.add(simple_cache_middleware)
    return RPC(_w3, num_threads=4)


@pytest.fixture()
def filestore():
    return NestedFilestore("/tmp/nested", [4, 3, 2])
