import shutil

import pytest


def test_filestore_resolve(filestore):
    assert filestore.resolve(12) == "/tmp/nested/00/000/12.bin"
    assert filestore.resolve(123) == "/tmp/nested/00/000/123.bin"
    assert filestore.resolve(1234) == "/tmp/nested/00/000/1234.bin"
    assert filestore.resolve(12345) == "/tmp/nested/00/001/12345.bin"
    assert filestore.resolve(123456) == "/tmp/nested/00/012/123456.bin"
    assert filestore.resolve(1234567) == "/tmp/nested/00/123/1234567.bin"
    assert filestore.resolve(12345678) == "/tmp/nested/01/234/12345678.bin"
    assert filestore.resolve(123456789) == "/tmp/nested/12/345/123456789.bin"

    assert filestore.resolve(12345678, path_only=True) == "/tmp/nested/01/234"

def test_filestore_workflow(filestore):
    # ensure the test file does not exist before we start
    shutil.rmtree("/tmp/nested", ignore_errors=True)
    assert not filestore.exists(12345678)
    filestore.put("src/tests/data/12345678.bin", 12345678)
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
