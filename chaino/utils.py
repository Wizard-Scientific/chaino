import os
import json
import pickle
import logging

import pandas as pd
from rich.logging import RichHandler
from rich.console import Console
from multicall.signature import parse_signature


def convert_json_to_csv(in_file):
    "Convert a JSON file to a CSV file"
    with open(in_file) as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df.to_csv(in_file.replace('.json', '.csv'), index=False)

def convert_signature_to_abi(signature):
    "Convert a function signature to an ABI"

    def get_next_input():
        counter = 0
        while True:
            counter += 1
            yield f"_i{counter:03d}"

    def get_next_output():
        counter = 0
        while True:
            counter += 1
            yield f"_o{counter:03d}"

    function, input_types, output_types = parse_signature(signature)
    function_abi = {
        "name": function.split("(")[0],
        "type": "function",
        "inputs": [{"type": input_type, "name": next_name} for input_type, next_name in zip(input_types, get_next_input())],
        "outputs": [{"type": output_type, "name": next_name} for output_type, next_name in zip(output_types, get_next_output())],
    }
    return function_abi

def init_logger(level="INFO"):
    "Initialize the logger"

    logger = logging.getLogger("chaino")

    # only the first invocation will configure this
    if not logger.handlers:

        level = logging.getLevelName(level)
        logger.setLevel(level)
        logger.propagate = False

        filename = os.path.join("/tmp", f"{logger.name.lower()}.log")
        logfile = open(filename, 'a', encoding="utf-8") # pylint: disable=consider-using-with

        stderr = Console(
            file=logfile,
            tab_size=2,
            width=100,
            force_terminal=True
        )

        handler = RichHandler(
            markup=True,
            console=stderr,
            show_path=True,
            show_time=True,
            show_level=True,
            rich_tracebacks=True
        )

        monitor_format = logging.Formatter('%(message)s')
        handler.setFormatter(monitor_format)
        logger.addHandler(handler)

        logger.info(
            "Process %d (parent %d) logging to %s at level %s",
            os.getpid(),
            os.getppid(),
            filename,
            level
        )

def blocks_to_txs_csv(filestore, block_start, block_end):
    "Stream blocks from filestore and print transactions as CSV"

    fields = [
        "block_number",
        "tx_hash",
        "method",
        "from",
        "to",
        "quantity",
    ]
    print(",".join(fields))

    for index in range(block_start, block_end):
        block = pickle.load(filestore.get(index))
        for tx in block.transactions:
            tx_dict = {
                "block_number": tx["blockNumber"],
                "tx_hash": tx["hash"].hex(),
                "method": tx["input"][:10],
                "from": tx["from"],
                "to": tx["to"],
                "quantity": tx["value"],
            }
            print(",".join([str(tx_dict[field]) for field in fields]))
