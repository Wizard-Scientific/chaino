from chaino.grouped_multicall import GroupedMulticall


def test_one(w3):
    function_vector = ["balanceOf(address)(uint256)"]
    contract_address_vector = ["0xd5c313DE2d33bf36014e6c659F13acE112B80a8E"]
    input_vector = ["0xB1dD2Fdb023cB54b7cc2a0f5D9e8d47a9F7723ce"]
    
    gmc = list(GroupedMulticall(w3)(function_vector, contract_address_vector, input_vector))
    assert len(gmc) > 0

    for mc in gmc:
        assert mc
        assert len(mc.calls) > 0

def test_several(w3):
    function_vector = ["balanceOf(address)(uint256)"]
    contract_address_vector = ["0x66eEd5FF1701E6ed8470DC391F05e27B1d0657eb"]
    input_vector = [
        "0xB1dD2Fdb023cB54b7cc2a0f5D9e8d47a9F7723ce",
        "0x62dd63009b14e0f0c47d5783db0c51e58d696e65",
        "0xde26e98d868fe02fffb6df26e638995124d3ca13",
    ]

    gmc = list(GroupedMulticall(w3)(function_vector, contract_address_vector, input_vector))
    assert len(gmc) > 0
    assert len(gmc[0].calls) == len(input_vector)
    result = gmc[0]()
    assert len(result) == len(input_vector)
    for input_value in input_vector:
        assert input_value in result
