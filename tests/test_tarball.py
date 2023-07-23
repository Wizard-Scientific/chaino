import os
import shutil

import pytest

from nested_filestore.tarball import TarballNestedFilestore


def test_init_tarball():
    filestore = TarballNestedFilestore(
        root_path="/tmp/chaino",
        hierarchy_order=[3, 3, 3],
        base=10,
    )
    assert filestore.root_path == "/tmp/chaino"
    assert filestore.hierarchy_order == [3, 3, 3]
    assert filestore.base == 10
    assert filestore.pad_character == "0"
    assert filestore.container_size == 1000

def test_tarball_workflow(tarball_filestore):
    # ensure the test file does not exist before we start
    assert not tarball_filestore.exists(12345678)
    tarball_filestore.put(12345678, "tests/data/12345678.bin")
    assert tarball_filestore.exists(12345678)
    with tarball_filestore.get(12345678) as f:
        assert f.read() == b"hi"

def test_little_tarball(tarball_little_filestore):
    assert tarball_little_filestore.container_size == 10

def test_tarball_create(tarball_little_filestore):
    assert not tarball_little_filestore.container_full(0)

    for i in range(0, 10):
        tarball_little_filestore.put(i, "tests/data/12345678.bin")
        assert not tarball_little_filestore.container_full(i)

    assert os.path.exists("/tmp/chaino/0/0.tar")

    for i in range(10, 20):
        tarball_little_filestore.put(i, "tests/data/12345678.bin")
        assert not tarball_little_filestore.container_full(i)

    assert os.path.exists("/tmp/chaino/0/1.tar")

    tarball_little_filestore.put(20, "tests/data/12345678.bin")
    assert os.path.exists("/tmp/chaino/0/2/20.bin")

def test_tarball_get(tarball_little_filestore):
    for i in range(0, 9):
        tarball_little_filestore.put(i, "tests/data/12345678.bin")
        assert not tarball_little_filestore.container_full(i)
    tarball_little_filestore.put(9, "tests/data/12345679.bin")
    tarball_little_filestore.put(10, "tests/data/12345679.bin")
    tarball_little_filestore.put(11, "tests/data/12345678.bin")

    assert os.path.exists("/tmp/chaino/0/0.tar")

    # get an index that is in the tarball
    with tarball_little_filestore.get(1) as f:
        assert f.read() == b"hi"

    # this is in the tarball with different content
    with tarball_little_filestore.get(9) as f:
        assert f.read() == b"bye"

    # this one is not inside a tarball
    with tarball_little_filestore.get(10) as f:
        assert f.read() == b"bye"

def test_tarball_tiny_get():
    shutil.rmtree("/tmp/chaino", ignore_errors=True)
    return TarballNestedFilestore("/tmp/chaino", [1, 1])

    for i in range(0, 10):
        tarball_tiny_filestore.put(i, "tests/data/12345678.bin")
        assert not tarball_tiny_filestore.container_full(i)

    assert os.path.exists("/tmp/chaino/0.tar")

    # get an index that is in the tarball
    for i in range(0, 10):
        with tarball_tiny_filestore.get(i) as f:
            assert f.read() == b"hi"
