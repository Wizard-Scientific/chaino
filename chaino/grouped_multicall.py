from multicall import Call, Multicall
from web3 import Web3

from .utils import convert_signature_to_abi


class GroupedMulticall:
    """
    GroupedMulticall is a class that groups multiple multicalls together.

    It is used to group multiple multicalls together to reduce the number of RPC calls.
    """

    def __init__(self, w3, inputs, block_number=None, margin=0.1):
        self.w3 = w3
        self.inputs = inputs
        self.margin = margin
        self.block_number = block_number

    def __call__(self):
        "Yield a list of multicalls"
        contract_calls = []
        for contract_address, function, input_value in self.inputs:
            if len(contract_calls) == self.max_length:
                yield Multicall(contract_calls, block_id=self.block_number, _w3=self.w3)
                contract_calls = []

            fn_call = [function]
            fn_call.extend(input_value)

            checksum_address = Web3.toChecksumAddress(contract_address)
            contract_calls.append(
                Call(
                    target=checksum_address,
                    function=fn_call,
                    returns=[(f"[{checksum_address}, {fn_call}]", None)],
                )
            )

        # yield the last one
        if len(contract_calls) > 0:
            yield Multicall(contract_calls, block_id=self.block_number, _w3=self.w3)

    @property
    def max_length(self):
        "Get the maximum number of items that will fit inside a multicall"
        if not hasattr(self, "_max_length"):
            if len(self.inputs) == 0:
                return 0
            # estimate gas used for a single call
            contract_address, function, input_value = list(self.inputs)[0]
            function_abi = convert_signature_to_abi(function)
            contract = self.w3.eth.contract(contract_address, abi=[function_abi])
            fn = contract.functions[function_abi["name"]]
            gas_estimate = fn(*input_value).estimateGas()

            # obtain gas limit from multicall
            fn_call = [function]
            fn_call.extend(input_value)
            gas_limit = Multicall([Call(
                contract_address,
                fn_call,
                [(str(fn_call), None)]
            )], _w3=self.w3).gas_limit

            self._max_length = int(gas_limit / gas_estimate * (1 - self.margin))
        return self._max_length

    @classmethod
    def from_vectors(cls, w3, contract_address_vector, function_vector, input_vector):
        "auto-replicate function_vector if len(1) and len of another one is longer than 1"

        max_length = max([
            len(function_vector),
            len(contract_address_vector),
            len(input_vector),
        ])

        if len(function_vector) == 1:
            function_vector = function_vector * max_length
        if len(contract_address_vector) == 1:
            contract_address_vector = contract_address_vector * max_length
        if len(input_vector) == 1:
            input_vector = input_vector * max_length

        inputs = list(zip(
            contract_address_vector,
            function_vector,
            input_vector,
        ))
        return cls(w3=w3, inputs=inputs)
