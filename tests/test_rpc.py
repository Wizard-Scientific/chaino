def test_dispatch_task(block_scheduler):
    block_identifier = 10000000
    rpc = block_scheduler.get_available_rpc()
    thread = rpc.dispatch_task(block_scheduler.get_block, block_identifier)
