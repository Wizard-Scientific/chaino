#!/usr/bin/env python3

import os
import json
import random
import logging

import click

from chaino.utils import init_logger, blocks_to_txs_csv
from chaino.scheduler.block import BlockScheduler
from nested_filestore.tarball import GzipTarballNestedFilestore


@click.group()
def cli():
    pass

@cli.command()
@click.argument('chain', type=str)
@click.argument('block_start', type=int)
@click.argument('block_end', type=int)
@click.argument('filestore', type=str)
@click.option('no_check_existing', '--no-check-existing', is_flag=True, default=True)
def download(chain, block_start, block_end, filestore, no_check_existing):
    "Write blocks from blockchain to disk"

    block_scheduler = BlockScheduler(
        chain=chain,
        filestore_path=filestore,
        hierarchy_order=[3, 3, 3],
    )

    logging.getLogger("chaino").info(f"Scan blocks from {block_start} to {block_end}")
    for block_number in range(block_start, block_end):
        block_scheduler.add_task(
            block_number=block_number,
            check_existing=no_check_existing
        )

    block_scheduler.start()

@cli.command()
@click.argument('block_start', type=int)
@click.argument('block_end', type=int)
@click.argument('filestore', type=str)
def transactions_csv(block_start, block_end, filestore):
    "Print transactions as CSV"
    filestore = GzipTarballNestedFilestore(
        root_path=os.path.expanduser(filestore),
        hierarchy_order=[3, 3, 3],
    )
    blocks_to_txs_csv(filestore, block_start, block_end)


if __name__ == "__main__":
    init_logger(level=os.getenv("LOG_LEVEL", "INFO"))
    cli()
