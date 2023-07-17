#!/usr/bin/env python3

import os

import click
from dotenv import load_dotenv
from web3 import Web3, HTTPProvider
from web3.middleware import simple_cache_middleware, geth_poa_middleware

from chaino.utils import init_logger, blocks_to_txs_csv
from chaino.scheduler.block import BlockScheduler
from chaino.nested_filestore import NestedFilestore
from chaino.rpc import RPC


@click.group()
def cli():
    pass

@cli.command()
@click.argument('chain', type=str)
@click.argument('block_start', type=int)
@click.argument('block_end', type=int)
@click.argument('filestore', type=str)
def download(chain, block_start, block_end, filestore):
    "Write blocks from blockchain to disk"
    if chain == 'fantom':
        _w3 = Web3(HTTPProvider("https://rpc.ftm.tools"))
        _w3.middleware_onion.add(simple_cache_middleware)
    elif chain == 'bsc':
        _w3 = Web3(HTTPProvider("https://bsc-dataseed1.binance.org/"))
        _w3.middleware_onion.add(simple_cache_middleware)
        _w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    else:
        raise Exception('Unknown chain')

    block_scheduler = BlockScheduler(state_path=filestore)
    block_scheduler.add_rpc(RPC(_w3, tick_delay=0.15, slow_timeout=120, num_threads=2))
    for block_number in range(block_start, block_end):
        block_scheduler.add_task(block_number=block_number)
    block_scheduler.start()

@cli.command()
@click.argument('block_start', type=int)
@click.argument('block_end', type=int)
@click.argument('filestore', type=str)
def transactions_csv(block_start, block_end, filestore):
    "Print transactions as CSV"
    filestore = NestedFilestore(
        root_path=os.path.expanduser(filestore),
        hierarchy_order=[4, 3, 2],
    )
    blocks_to_txs_csv(filestore, block_start, block_end)


if __name__ == "__main__":
    init_logger(level="INFO")
    cli()
