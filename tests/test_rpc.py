def test_get_block(block_scheduler):
    block_number = 10000000
    rpc = block_scheduler.get_available_rpc()
    thread = rpc.dispatch_task(block_scheduler.get_block, block_number)

def test_eth_call(rpc_fantom):
    fn = rpc_fantom.eth_contract_function(
        address='0xd5c313DE2d33bf36014e6c659F13acE112B80a8E',
        function_signature='totalSupply()(uint256)',
    )
    result_latest = fn().call()
    result_snapshot = fn().call(block_identifier=59923357)
    assert result_latest != result_snapshot

def test_eth_call_bsc(rpc_bsc):
    fn = rpc_bsc.eth_contract_function(
        address='0x51BfC6e47c96d2b8c564B0DdD2C44fC03707cdc7',
        function_signature='totalSupply()(uint256)',
    )
    result_latest = fn().call()
    result_snapshot = fn().call(block_identifier=29541500)
    assert result_latest != result_snapshot
