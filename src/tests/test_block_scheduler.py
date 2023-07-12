def test_add_block_task(block_scheduler):
    block_scheduler.add_task(block_identifier=56889636)
    assert len(block_scheduler.tasks) == 1

def test_add_several_block_tasks(block_scheduler):
    block_num = 56889636
    num_to_get = 500
    for block_identifier in range(block_num, block_num+num_to_get):
        block_scheduler.add_task(block_identifier=block_identifier)
    assert len(block_scheduler.tasks) == num_to_get

    block_scheduler.start()
