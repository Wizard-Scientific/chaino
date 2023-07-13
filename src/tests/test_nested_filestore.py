import shutil

from chaino.nested_filestore import NestedFilestore


def test_filestore_resolve():
    filestore = NestedFilestore("/tmp/nested", [4, 3])
    assert filestore.resolve(123456789) == "/tmp/nested/12/345/123456789.bin"
    assert filestore.resolve(123456789, path_only=True) == "/tmp/nested/12/345"

def test_filestore_workflow():
    # ensure the test file does not exist before we start
    shutil.rmtree("/tmp/nested", ignore_errors=True)
    filestore = NestedFilestore("/tmp/nested", [4, 3])
    assert not filestore.exists(123456789)
    filestore.put("src/tests/data/123456789.bin", 123456789)
    assert filestore.exists(123456789)
    with filestore.get(123456789) as f:
        assert f.read() == b"hi"
