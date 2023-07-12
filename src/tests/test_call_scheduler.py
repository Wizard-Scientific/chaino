import os
import json
import random

from web3 import Web3
import pandas as pd


a_task = {
    "contract_address": "0xd5c313DE2d33bf36014e6c659F13acE112B80a8E",
    "function": "balanceOf(address)(uint256)",
    "input_value": ["0xB1dD2Fdb023cB54b7cc2a0f5D9e8d47a9F7723ce"],
}


def test_add_task(call_scheduler):
    call_scheduler.add_task(**a_task)
    assert len(call_scheduler.tasks) == 1

def test_start(call_scheduler):
    call_scheduler.add_task(**a_task)
    call_scheduler.start()

def test_mlqdr(call_scheduler):
    with open(os.path.expanduser("~/Work/mpx-snapshots/data/mlqdr-addresses.json"), 'r') as f:
        addresses = json.load(f)

    for address in addresses:
        call_scheduler.add_task(
            contract_address="0xCa3C69622E22524fF2b6cC24Ee7e654bbF91578a",
            function="balanceOf(address)(uint256)",
            input_value=[address]
        )
    call_scheduler.start()

def test_mpx(call_scheduler):
    with open(os.path.expanduser("~/Work/mpx-api/usr/vesting/migration-addresses.json"), 'r') as f:
        address_dict = json.load(f)
    addresses = list(address_dict.values())

    for address in addresses:
        call_scheduler.add_task(
            contract_address=Web3.toChecksumAddress(address),
            function="unclaimed()(uint256)",
            input_value=[]
        )
    call_scheduler.start()

def test_oath(call_scheduler):
    df = pd.read_csv(os.path.expanduser('~/Work/savvy-fairlaunch/oath/data/2022-10-25/lge_participants.csv'))
    addresses = list(df['address'])
    addresses = [Web3.toChecksumAddress(address) for address in addresses]
    random.shuffle(addresses)
    for address in addresses:
        call_scheduler.add_task(
            contract_address="0x21Ada0D2aC28C3A5Fa3cD2eE30882dA8812279B6",
            function="balanceOf(address)(uint256)",
            input_value=[address]
        )
    call_scheduler.start()

def test_pills(call_scheduler):
    with open(os.path.expanduser('~/Work/morpheus-swap/analysis/data/pills-addresses.json')) as f:
        addresses = json.load(f)
    random.shuffle(addresses)

    for address in addresses:
        call_scheduler.add_task(
            contract_address="0x66eEd5FF1701E6ed8470DC391F05e27B1d0657eb",
            function="balanceOf(address)(uint256)",
            input_value=[address]
        )
    call_scheduler.start()

