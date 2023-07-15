import os
import shutil


class NestedFilestore:
    """
    NestedFilestore is a filestore that stores files in a nested directory structure.
    """

    def __init__(self, root_path, hierarchy_order, pad_character="0"):
        "args are root filesystem path, and order of hierarchy starting from leaf back to the root"
        self.root_path = root_path
        self.hierarchy_order = hierarchy_order
        self.pad_character = pad_character
        self.created_dirs = set()

    def exists(self, index):
        "does the specified index exist as a file? If it exists, return True"
        return os.path.exists(self.resolve(index))
    
    def put(self, filename, index, move=False):
        "given the path to an existing file, and given an index, copy the file to the file store and put it in the right place, creating directories as needed."
        dst_filename = self.resolve(index)
        if not self.exists(index):
            dst_path = self.resolve(index, path_only=True)
            os.makedirs(dst_path, exist_ok=True)
            if move:
                shutil.move(filename, dst_filename)
            else:
                shutil.copy(filename, dst_filename)
        return dst_filename

    def writer(self, index, overwrite=False):
        "given an index, return a writable file handle pointing to the file UNLESS it exists"
        dst_filename = self.resolve(index)

        if not overwrite and self.exists(index):
            raise ValueError(f"{index} ({dst_filename}) already exists.")
        else:
            dst_path = os.path.dirname(dst_filename)
            # ensure we only create each directory once per instance
            if dst_path not in self.created_dirs:
                os.makedirs(dst_path, exist_ok=True)
                self.created_dirs.add(dst_path)
            return open(dst_filename, "wb")
    
    def get(self, index):
        "given an index, return a file handle pointing to the file if it exists"
        try:
            return open(self.resolve(index), "rb")
        except FileNotFoundError:
            raise ValueError(f"{index} ({self.resolve(index)}) does not exist.")
    
    def resolve(self, index, path_only=False):
        "convert an index to a fully qualified filesystem path"

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

        filename = os.path.join(self.root_path, *subdirs, leaf_filename)

        if path_only:
            return os.path.dirname(filename)
        return filename
