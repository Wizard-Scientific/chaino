import os

import pytest

from web3 import Web3, HTTPProvider
from web3.middleware import simple_cache_middleware


@pytest.fixture()
def w3():
    _w3 = Web3(HTTPProvider("https://rpc.ankr.com/fantom"))
    _w3.middleware_onion.add(simple_cache_middleware)
    return _w3
