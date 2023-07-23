import pytest


def test_filestore_resolve(filestore):
    assert filestore.resolve(12) == "/tmp/chaino/000/000/12.bin"
    assert filestore.resolve(123) == "/tmp/chaino/000/000/123.bin"
    assert filestore.resolve(1234) == "/tmp/chaino/000/001/1234.bin"
    assert filestore.resolve(12345) == "/tmp/chaino/000/012/12345.bin"
    assert filestore.resolve(123456) == "/tmp/chaino/000/123/123456.bin"
    assert filestore.resolve(1234567) == "/tmp/chaino/001/234/1234567.bin"
    assert filestore.resolve(12345678) == "/tmp/chaino/012/345/12345678.bin"
    assert filestore.resolve(123456789) == "/tmp/chaino/123/456/123456789.bin"

def test_filestore_workflow(filestore):
    # ensure the test file does not exist before we start
    assert not filestore.exists(12345678)

    filestore.put(12345678, "tests/data/12345678.bin")
    assert filestore.exists(12345678)
    with filestore.get(12345678) as f:
        assert f.read() == b"hi"

def test_does_not_exist(filestore):
    # ensure the test file does not exist before we start
    assert not filestore.exists(12345678)

    # try to get the file and ensure it raises ValueError
    with pytest.raises(ValueError):
        filestore.get(12345678)

def test_filestore_min_max(filestore):
    filestore.put(12, "tests/data/12345678.bin")
    filestore.put(1234, "tests/data/12345678.bin")
    filestore.put(12345678, "tests/data/12345678.bin")
    assert filestore.smallest_id == "12"
    assert filestore.largest_id == "12345678"
