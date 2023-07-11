from chaino.grouped_multicall import GroupedMulticall
from chaino.utils import level_vectors


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
    
    gmc = list(GroupedMulticall(w3, inputs=level_vectors(**inputs))())
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

    gmc = list(GroupedMulticall(w3, inputs=level_vectors(**inputs))())
    
    assert len(gmc) > 0
    assert len(gmc[0].calls) == len(inputs["input_vector"])
    result = gmc[0]()
    assert len(result) == len(inputs["input_vector"])
    for input_value in inputs["input_vector"]:
        assert input_value in result
