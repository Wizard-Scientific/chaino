import os

import pytest

from web3 import Web3, HTTPProvider
from web3.middleware import simple_cache_middleware

from chaino.scheduler import Scheduler
from chaino.call_scheduler import CallScheduler
from chaino.block_scheduler import BlockScheduler


@pytest.fixture()
def w3():
    _w3 = Web3(HTTPProvider("https://rpc.ankr.com/fantom"))
    _w3.middleware_onion.add(simple_cache_middleware)
    return _w3

@pytest.fixture()
def scheduler(w3):
    return Scheduler(w3, chain="fantom")

@pytest.fixture()
def block_scheduler(w3):
    return BlockScheduler(w3, chain="fantom")

@pytest.fixture()
def call_scheduler(w3):
    return CallScheduler(w3, chain="fantom")
