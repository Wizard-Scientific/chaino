import os
import shutil
import tarfile

import ratarmountcore as rmc

from . import NestedFilestore


class TarballHelper:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tarball_cache = {}
        self.container_size = self.base ** self.hierarchy_order[0]

    def container_full(self, index):
        "is the container that contains this index full?"
        container_path = os.path.dirname(self.resolve(index))
        if len(os.listdir(container_path)) >= self.container_size:
            return True

    def tarball_for_index(self, index):
        "get the tarball filename for the container that contains this index"
        filename = super().resolve(index)
        container_path = os.path.dirname(filename)
        tarball_filename = os.path.join(container_path, f"{index}.tar")
        return tarball_filename

    def tarball_exists(self, index):
        "does a tarball exist for the container that contains this index?"
        tarball_filename = self.tarball_for_index(index)
        return os.path.exists(tarball_filename)

    def tarball_create(self, index, move=False):
        "create a tarball for the container path that contains this index"
        tarball_filename = self.tarball_for_index(index)
        container_path = os.path.dirname(self.resolve(index))

        with tarfile.open(tarball_filename, "w") as tarball:
            # iterate files in the container path and add them to the tarball
            for filename in os.listdir(container_path):
                full_filename = os.path.join(container_path, filename)
                tarball.add(full_filename)
                if move:
                    os.remove(full_filename)

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

    def put(self, index, filename=None, filehandle=False, move=False, overwrite=False):
        "given the path to an existing file, and given an index, copy the file to the file store and put it in the right place, creating directories as needed."

        # do not proceed if the index already exists inside a tarball and overwrite is False
        if not overwrite and self.tarball_exists(index):
            raise ValueError(f"{index} already exists inside tarball.")

        # put the file as usual
        super().put(index, filename=filename, filehandle=filehandle, move=move, overwrite=overwrite)

        # if the previous put() filled the entire nested directory, then tar it up
        if self.container_full(index):
            self.tarball_create(index, move=move)

    def get(self, index):
        "given an index, return a file handle pointing to the file if it exists"

        # if the file exists as a tarball, then open the tarball and return the file handle
        tarball = self.tarball_open(index)
        if tarball:
            info = tarball.getFileInfo(f"/{index}.bin")
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
