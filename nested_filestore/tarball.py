import os
import shutil
import tarfile
import logging
import threading

import ratarmountcore as rmc

from . import NestedFilestore


class TarballHelper:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tarball_cache = {}
        self.tarball_exists_cache = {}
        self.container_size = self.base ** self.hierarchy_order[0]
        self.tar_lock = threading.Lock()

    def container_full(self, index):
        "is the container that contains this index full?"

        # if there is a tarball for this index, then the container is full
        if self.tarball_exists(index):
            return True

        # if the container path does not exist, then it is not full
        container_path = os.path.dirname(self.resolve(index))
        if not os.path.exists(container_path):
            return False

        # if the container path has the right number of files, then it is full
        if len(os.listdir(container_path)) == self.container_size:
            return True
        elif len(os.listdir(container_path)) > self.container_size:
            raise ValueError(f"container {container_path} has {len(os.listdir(container_path))} files, but should have {self.container_size}")

    def tarball_for_index(self, index):
        "get the tarball filename for the container that contains this index"
        container_tree = self.decompose(index)
        container_id = container_tree[-2]

        filename = super().resolve(index)
        container_path = os.path.dirname(filename)
        container_container = os.path.dirname(container_path)

        tarball_filename = os.path.join(container_container, f"{container_id}.tar")
        return tarball_filename

    def tarball_exists(self, index):
        "does a tarball exist for the container that contains this index?"
        tarball_filename = self.tarball_for_index(index)

        # save results for later to avoid unnecessary filesystem calls
        if tarball_filename not in self.tarball_exists_cache:
            self.tarball_exists_cache[tarball_filename] = os.path.exists(tarball_filename)

        return self.tarball_exists_cache[tarball_filename]

    def tarball_create(self, index):
        "create a tarball for the container path that contains this index"
        tarball_filename = self.tarball_for_index(index)
        # container_path = os.path.dirname(self.resolve(index))
        container_path = self.get_container_path(index)
        full_container_path = os.path.join(self.root_path, container_path)

        filenames_to_remove = []
        # iterate files in the container path and add them to the tarball
        with tarfile.open(tarball_filename, mode="w") as tarball:
            for filename in sorted(os.listdir(full_container_path)):
                full_filename = os.path.join(self.root_path, container_path, filename)
                tarball.add(
                    full_filename,
                    arcname=os.path.join(container_path, filename),
                    recursive=False
                )
                filenames_to_remove.append(full_filename)

            # ensure the right number of files are now in the tarball
            if len(tarball.getmembers()) != len(os.listdir(full_container_path)):
                raise ValueError(f"tarball {tarball_filename} contains different number of files than container path")

        # iterate files again and delete them
        for full_filename in filenames_to_remove:
            os.remove(full_filename)
        os.rmdir(full_container_path)

    def tarball_open(self, index):
        "open the tarball for the container that contains this index"
        tarball_filename = self.tarball_for_index(index)
        if tarball_filename not in self.tarball_cache:
            if not os.path.exists(tarball_filename):
                return None
            tarball = rmc.open(tarball_filename, recursive=True)
            self.tarball_cache[tarball_filename] = tarball
        else:
            tarball = self.tarball_cache[tarball_filename]
        return tarball

    def tarball_create_if_full(self, index):
        with self.tar_lock:
            if self.container_full(index):
                logging.getLogger("chaino").info(f"Tarballing {index}")
                self.tarball_create(index)

class TarballNestedFilestore(TarballHelper, NestedFilestore):
    """
    NestedFilestore is a filestore that stores files in a nested directory structure.
    """
    def exists(self, index):
        "does the specified index exist as a file? If it exists, return True"

        # first check if there is a tarball for this index
        if self.tarball_exists(index):
            return True

        # otherwise, pass along to the superclass
        return super().exists(index)

    def put(self, index, *args, **kwargs):
        "given the path to an existing file, and given an index, copy the file to the file store and put it in the right place, creating directories as needed."

        # do not proceed if the index already exists inside a tarball and overwrite is False
        if self.tarball_exists(index):
            raise ValueError(f"{index} already exists inside tarball.")

        # put the file as usual
        return super().put(index=index, *args, **kwargs)

    def get(self, index):
        "given an index, return a file handle pointing to the file if it exists"

        # if the file exists as a tarball, then open the tarball and return the file handle
        tarball = self.tarball_open(index)
        container_path = self.get_container_path(index)
        if tarball:
            index_filename = os.path.join(container_path, f"{index}.bin")
            info = tarball.getFileInfo(index_filename)
            return tarball.open(info)

        # otherwise, pass to the superclass to handle as a normal file
        return super().get(index)
    
    def resolve(self, index):
        "convert an index to a fully qualified filesystem path"

        # check if the tarball exists
        tarball_filename = self.tarball_for_index(index)
        if os.path.exists(tarball_filename):
            return tarball_filename

        # otherwise, pass to the superclass to handle as a normal file
        return super().resolve(index)
