import os
import json

from web3 import Web3
from chaino.scheduler import Scheduler


a_task = {
    "contract_address": "0xd5c313DE2d33bf36014e6c659F13acE112B80a8E",
    "function": "balanceOf(address)(uint256)",
    "input_value": ["0xB1dD2Fdb023cB54b7cc2a0f5D9e8d47a9F7723ce"],
}


def test_add_task(scheduler):
    scheduler.add_task(**a_task)
    assert len(scheduler.tasks) == 1

def test_start(scheduler):
    scheduler.add_task(**a_task)
    scheduler.start()
    assert False

def test_mlqdr(scheduler):
    with open(os.path.expanduser("~/Work/mpx-snapshots/data/mlqdr-addresses.json"), 'r') as f:
        addresses = json.load(f)

    for address in addresses:
        scheduler.add_task(
            contract_address="0xCa3C69622E22524fF2b6cC24Ee7e654bbF91578a",
            function="balanceOf(address)(uint256)",
            input_value=[address]
        )
    scheduler.start()

def test_mpx(scheduler):
    with open(os.path.expanduser("~/Work/mpx-api/usr/vesting/migration-addresses.json"), 'r') as f:
        address_dict = json.load(f)
    addresses = list(address_dict.values())

    for address in addresses:
        scheduler.add_task(
            contract_address=Web3.to_checksum_address(address),
            function="unclaimed()(uint256)",
            input_value=[]
        )
    scheduler.start()
    assert False
