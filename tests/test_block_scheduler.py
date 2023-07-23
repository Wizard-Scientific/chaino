import shutil

def test_add_block_task(block_scheduler):
    # clear the path at the start
    shutil.rmtree("/tmp/chaino", ignore_errors=True)
    block_scheduler.add_task(block_number=56889636)
    assert len(block_scheduler.tasks) == 1

def test_add_several_block_tasks(block_scheduler):
    # clear the path at the start
    shutil.rmtree("/tmp/chaino", ignore_errors=True)
    block_num = 56889636
    num_to_get = 10
    for block_number in range(block_num, block_num+num_to_get):
        block_scheduler.add_task(block_number=block_number)
    assert len(block_scheduler.tasks) > 0
    block_scheduler.start()
