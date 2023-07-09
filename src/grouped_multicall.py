from itertools import zip_longest
from multicall import Call, Multicall


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def get_multicall(w3, function, sub_addresses, offset=0):
    contract_calls = []
    contract_idx = offset
    for contract_address in sub_addresses:
        # potentially get out of loop if invoked from grouped multicall
        if contract_address is None:
            continue

        one_call = Call(
            contract_address,
            [function],
            [(contract_idx, None)]
        )
        contract_calls.append(one_call)
        contract_idx += 1
    results = Multicall(contract_calls, _w3=w3)()
    return list(results.values())

def get_multicall_grouped(w3, function, addresses, group_size=500):
    results = []
    for group in grouper(addresses, group_size, fillvalue=None):
        print(".", end="", flush=True)
        multicall_result = get_multicall(w3, function, group, offset=len(results))
        results += multicall_result
    print("", flush=True)
    return(results)
