import json

import pandas as pd
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
