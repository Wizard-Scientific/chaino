import os
import re
import glob
import shutil


class NestedFilestore:
    """
    NestedFilestore is a filestore that stores files in a nested directory structure.
    """

    def __init__(self, root_path, hierarchy_order, pad_character="0", base=10):
        "args are root filesystem path, and order of hierarchy starting from leaf back to the root"
        self.root_path = root_path
        self.hierarchy_order = hierarchy_order
        self.base = 10 # only base 10 is supported for now
        self.pad_character = pad_character
        self.created_dirs = set()
        self.index_cache = []

    def exists(self, index):
        "does the specified index exist as a file? If it exists, return True"
        return os.path.exists(self.resolve(index))
    
    def put(self, index, filename=None, filehandle=False, move=False, overwrite=False):
        "given the path to an existing file, and given an index, copy the file to the file store and put it in the right place, creating directories as needed."
        dst_filename = self.resolve(index)

        if not overwrite and self.exists(index):
            raise ValueError(f"{index} ({dst_filename}) already exists.")

        dst_path = os.path.dirname(dst_filename)
        if dst_path not in self.created_dirs:
            os.makedirs(dst_path, exist_ok=True)
            self.created_dirs.add(dst_path)

        if filehandle:
            return open(dst_filename, "wb")
        elif filename:
            if move:
                shutil.move(filename, dst_filename)
            else:
                shutil.copy(filename, dst_filename)
            return dst_filename
        else:
            raise ValueError("either filename or filehandle must be specified.")

    def writer(self, index, overwrite=False):
        "given an index, return a writable file handle pointing to the file UNLESS it exists"
        return self.put(index, filehandle=True, overwrite=overwrite)
    
    def get(self, index):
        "given an index, return a file handle pointing to the file if it exists"
        try:
            return open(self.resolve(index), "rb")
        except FileNotFoundError:
            raise ValueError(f"{index} ({self.resolve(index)}) does not exist.")
    
    def resolve(self, index):
        "convert an index to a fully qualified filesystem path"

        node_path = self.decompose(index)
        filename = os.path.join(self.root_path, *node_path)
        return filename

    def decompose(self, index):
        "based on the hierarchy order, return a tuple of the path components for the given index"
        index_str = str(index)
        # get the leaf id, which is the last N digits of the index
        leaf_order = self.hierarchy_order[0]
        # leaf_id = index_str[-leaf_order:]
        leaf_filename = f"{index_str}.bin"
        # remove the right-most leaf_order digits from the string
        index_str = index_str[:-leaf_order]

        subdirs = []
        for level in self.hierarchy_order[1:]:
            # get the subdir id, which is the last N digits of the index
            subdir_id = index_str[-level:]

            # pad the subdir id with the pad character if it is too short
            if len(subdir_id) < level:
                subdir_id = subdir_id.rjust(level, self.pad_character)
            subdirs.insert(0, subdir_id)

            # remove right-most level digits from the string
            index_str = index_str[:-level]

        return *subdirs, leaf_filename

    def get_container_path(self, index):
        "given an index, return the path to the container directory"
        node_path = self.decompose(index)
        return os.path.join(*node_path[:-1])

    def _cache_file_list(self):
        if len(self.index_cache) == 0:
            file_list = glob.glob(os.path.join(self.root_path, "**/*.bin"), recursive=True)
            for filename in sorted(file_list):
                match = re.search(r'([^/]+).bin', filename)
                if match:
                    self.index_cache.append(match.group(1))

    @property
    def smallest_id(self):
        self._cache_file_list()
        return self.index_cache[0]

    @property
    def largest_id(self):
        self._cache_file_list()
        return self.index_cache[-1]
