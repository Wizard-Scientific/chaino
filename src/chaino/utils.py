import os
import json
import logging

import pandas as pd
from rich.logging import RichHandler
from rich.console import Console
from multicall.signature import parse_signature


def convert_json_to_csv(in_file):
    with open(in_file) as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df.to_csv(in_file.replace('.json', '.csv'), index=False)

def convert_signature_to_abi(signature):
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

def level_vectors(contract_address_vector, function_vector, input_vector, block_id_vector=[]):
    "auto-replicate function_vector if len(1) and len of another one is longer than 1"

    max_length = max([
        len(function_vector),
        len(contract_address_vector),
        len(input_vector),
        len(block_id_vector)
    ])

    if len(function_vector) == 1:
        function_vector = function_vector * max_length
    if len(contract_address_vector) == 1:
        contract_address_vector = contract_address_vector * max_length
    if len(input_vector) == 1:
        input_vector = input_vector * max_length
    if len(block_id_vector) == 1:
        block_id_vector = block_id_vector * max_length
    elif len(block_id_vector) == 0:
        block_id_vector = [None] * max_length

    return list(zip(
        contract_address_vector,
        function_vector,
        input_vector,
        block_id_vector
    ))

def init_logger(level="INFO"):
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
