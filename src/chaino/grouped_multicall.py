import random
import string

from multicall import Call, Multicall
from web3 import Web3

from .utils import convert_signature_to_abi


class GroupedMulticall:
    def __init__(self, w3):
        self.w3 = w3
        self.margin = 0.1

    def get_max_items(self, function, contract_address, input_value):
        # estimate gas used for a single call
        function_abi = convert_signature_to_abi(function)
        contract = self.w3.eth.contract(contract_address, abi=[function_abi])
        fn = contract.functions[function_abi["name"]]
        gas_estimate = fn(input_value).estimate_gas()

        # obtain gas limit from multicall
        gas_limit = Multicall([Call(
            contract_address,
            [function, input_value],
            [('result', None)]
        )], _w3=self.w3).gas_limit

        return int(gas_limit / gas_estimate * (1 - self.margin))

    def __call__(self, function_vector, contract_address_vector, input_vector):
        max_items = self.get_max_items(
            function_vector[0],
            contract_address_vector[0],
            input_vector[0],
        )

        # auto-replicate function_vector if len(1) and len of another one is longer than 1
        max_length = max([
            len(function_vector),
            len(contract_address_vector),
            len(input_vector)
        ])
        if len(function_vector) == 1 and max_length > 1:
            function_vector = function_vector * max_length
        if len(contract_address_vector) == 1 and max_length > 1:
            contract_address_vector = contract_address_vector * max_length
        if len(input_vector) == 1 and max_length > 1:
            input_vector = input_vector * max_length

        contract_calls = []
        inputs = zip(function_vector, contract_address_vector, input_vector)
        for function, contract_address, input_value in inputs:
            if len(contract_calls) == max_items or input_value is None:
                yield Multicall(contract_calls, _w3=self.w3)
                contract_calls = []

            if input_value:
                contract_calls.append(
                    Call(
                        contract_address,
                        [function, input_value],
                        [(input_value, None)]
                    )
                )

        # yield the last one
        if len(contract_calls) > 0:
            yield Multicall(contract_calls, _w3=self.w3)
