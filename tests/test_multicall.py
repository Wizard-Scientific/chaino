from chaino.grouped_multicall import GroupedMulticall


def test_one(w3):
    inputs = {
        "function_vector": [
            "balanceOf(address)(uint256)",
        ],
        "contract_address_vector": [
            "0x66eEd5FF1701E6ed8470DC391F05e27B1d0657eb",
        ],
        "input_vector": [
            ["0x62dD63009B14e0f0c47D5783db0C51E58d696E65"],
        ]
    }
    
    gmc = list(GroupedMulticall.from_vectors(w3, **inputs)())
    assert len(gmc) > 0

    for mc in gmc:
        assert mc
        assert len(mc.calls) > 0

def test_several(w3):
    inputs = {
        "function_vector": [
            "balanceOf(address)(uint256)",
        ],
        "contract_address_vector": [
            "0x66eEd5FF1701E6ed8470DC391F05e27B1d0657eb",
        ],
        "input_vector": [
            ["0xB1dD2Fdb023cB54b7cc2a0f5D9e8d47a9F7723ce"],
            ["0x62dD63009B14e0f0c47D5783db0C51E58d696E65"],
            ["0xdE26e98d868FE02fFfb6DF26E638995124d3Ca13"],
        ]
    }

    gmc = list(GroupedMulticall.from_vectors(w3, **inputs)())
    
    assert len(gmc) > 0
    assert len(gmc[0].calls) == len(inputs["input_vector"])
    result = gmc[0]()
    assert len(result) == len(inputs["input_vector"])

def test_archive_block(w3):
    total_supply = [ '0xd5c313DE2d33bf36014e6c659F13acE112B80a8E', 'totalSupply()(uint256)', [] ]

    gmc = list(GroupedMulticall(w3, inputs=[total_supply], block_number=59923357)())
    result1 = list(gmc[0]().values())[0]

    gmc = list(GroupedMulticall(w3, inputs=[total_supply], block_number=65923357)())
    result2 = list(gmc[0]().values())[0]

    assert result1 != result2
