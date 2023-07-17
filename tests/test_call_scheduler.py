import os
import json
import random


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

def test_big(call_scheduler):
    with open('tests/data/addresses.json', 'r') as f:
        addresses = json.load(f)
    random.shuffle(addresses)
    for address in addresses:
        call_scheduler.add_task(
            contract_address="0x21Ada0D2aC28C3A5Fa3cD2eE30882dA8812279B6",
            function="balanceOf(address)(uint256)",
            input_value=[address]
        )
    call_scheduler.start()
