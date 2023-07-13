import shutil

from chaino.nested_filestore import NestedFilestore


def test_filestore_resolve():
    filestore = NestedFilestore("/tmp/nested", [4, 3, 2])

    assert filestore.resolve(12) == "/tmp/nested/00/000/12.bin"
    assert filestore.resolve(123) == "/tmp/nested/00/000/123.bin"
    assert filestore.resolve(1234) == "/tmp/nested/00/000/1234.bin"
    assert filestore.resolve(12345) == "/tmp/nested/00/001/12345.bin"
    assert filestore.resolve(123456) == "/tmp/nested/00/012/123456.bin"
    assert filestore.resolve(1234567) == "/tmp/nested/00/123/1234567.bin"
    assert filestore.resolve(12345678) == "/tmp/nested/01/234/12345678.bin"
    assert filestore.resolve(123456789) == "/tmp/nested/12/345/123456789.bin"

    assert filestore.resolve(12345678, path_only=True) == "/tmp/nested/01/234"

def test_filestore_workflow():
    # ensure the test file does not exist before we start
    shutil.rmtree("/tmp/nested", ignore_errors=True)
    filestore = NestedFilestore("/tmp/nested", [4, 3])
    assert not filestore.exists(12345678)
    filestore.put("src/tests/data/12345678.bin", 12345678)
    assert filestore.exists(12345678)
    with filestore.get(12345678) as f:
        assert f.read() == b"hi"
