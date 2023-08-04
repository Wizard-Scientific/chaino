#!/usr/bin/env python3

import os
import json
import random
import logging

import click

from chaino.utils import init_logger, blocks_to_txs_csv, group_to_txs_csv
from chaino.scheduler.block import BlockScheduler
from nested_filestore import NestedFilestore


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
@click.argument('filestore', type=str)
@click.argument('block_start', type=int, default=-1)
@click.argument('block_end', type=int, default=-1)
def transactions_csv(block_start, block_end, filestore):
    "Print transactions as CSV"
    filestore = NestedFilestore(
        root_path=os.path.expanduser(filestore),
        hierarchy_order=[3, 3, 3],
    )

    if block_start == -1:
        block_start = int(filestore.index.min)
    if block_end == -1:
        block_end = int(filestore.index.max)

    blocks_to_txs_csv(
        filestore,
        block_start,
        block_end,
    )


@cli.command()
@click.argument('blocks_filestore', type=str)
@click.argument('txs_filestore', type=str)
@click.argument('dimensions', type=str, default="3,3")
def extract_txs(blocks_filestore, txs_filestore):
    "Print transactions as CSV. Dimensions refer to Txs filestore."

    print("loading blocks filestore")
    blocks_filestore_obj = NestedFilestore(
        root_path=os.path.expanduser(blocks_filestore),
        hierarchy_order=[3, 3, 3],
    )

    txs_filestore_obj = NestedFilestore(
        root_path=os.path.expanduser(txs_filestore),
        hierarchy_order=[int(d) for d in dimensions.split(",")],
    )

    print("extracting transactions")
    for block_group_uri in blocks_filestore_obj.index.groups:

        print(f"extracting {block_group_uri}")
        block_group = blocks_filestore_obj.index.get_group(block_group_uri)
        block_group_id = block_group.uri.replace("/", "").lstrip("0")
        if len(block_group_id) == 0:
            block_group_id = "0"

        if not txs_filestore_obj.index.exists(block_group_id):
            buf = group_to_txs_csv(block_group)
            with txs_filestore_obj.writer(block_group_id) as f:
                f.write(bytes(buf, "utf-8"))
            txs_item = txs_filestore_obj.index.get(block_group_id)
            txs_item.group.compact()
        else:
            print(f"skipping {block_group_uri}")


if __name__ == "__main__":
    init_logger(level=os.getenv("LOG_LEVEL", "INFO"))
    cli()
