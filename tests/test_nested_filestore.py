import shutil

import pytest


def test_filestore_resolve(filestore):
    assert filestore.resolve(12) == "/tmp/nested/000/000/12.bin"
    assert filestore.resolve(123) == "/tmp/nested/000/000/123.bin"
    assert filestore.resolve(1234) == "/tmp/nested/000/001/1234.bin"
    assert filestore.resolve(12345) == "/tmp/nested/000/012/12345.bin"
    assert filestore.resolve(123456) == "/tmp/nested/000/123/123456.bin"
    assert filestore.resolve(1234567) == "/tmp/nested/001/234/1234567.bin"
    assert filestore.resolve(12345678) == "/tmp/nested/012/345/12345678.bin"
    assert filestore.resolve(123456789) == "/tmp/nested/123/456/123456789.bin"

    assert filestore.resolve(12345678, path_only=True) == "/tmp/nested/012/345"

def test_filestore_workflow(filestore):
    # ensure the test file does not exist before we start
    shutil.rmtree("/tmp/nested", ignore_errors=True)
    assert not filestore.exists(12345678)
    filestore.put(12345678, "tests/data/12345678.bin")
    assert filestore.exists(12345678)
    with filestore.get(12345678) as f:
        assert f.read() == b"hi"

def test_does_not_exist(filestore):
    # ensure the test file does not exist before we start
    shutil.rmtree("/tmp/nested", ignore_errors=True)
    
    assert not filestore.exists(12345678)
    # try to get the file and ensure it raises ValueError
    with pytest.raises(ValueError):
        filestore.get(12345678)
