import os
from os.path import abspath, basename, join
from stat import S_ISDIR, S_ISREG
from threading import RLock, Thread

from .utils import format_size


class File(object):

    def __init__(self, name, is_dir=False, parent=None, size=0, path=None):
        self.name = name
        self.is_dir = is_dir
        self.parent = parent
        self.size = size
        self.path = path
        self.children = []

    def add_child(self, file):
        file.parent = self
        file.path = join(self.path, file.name)
        self.children.append(file)

        parent = self
        while parent:
            parent.size += file.size
            parent = parent.parent

    def sortAll(self):
        self.children.sort(key=lambda x: (-x.size, x.name))
        for x in self.children:
            x.sortAll()

    def get_name_size(self, max_size):
        if len(self.name) >= max_size:
            return self.name[:max_size]
        # I'm avoiding complex calculations by just trying two different sizes.
        try1 = '%s %s' % (self.name, format_size(self.size, '%.2f'))
        if len(try1) <= max_size:
            return try1
        try2 = '%s %s' % (self.name, format_size(self.size, '%d'))
        if len(try2) <= max_size:
            return try2
        return self.name

    @property
    def draw_size(self):
        """
        For drawing purposes, all files should have at least a size of 1 so
        that they are visible.
        """
        return self.size if self.size >= 1 else 1


class Scanner(Thread):

    def __init__(self, root_path):
        super(Scanner, self).__init__()
        self.lock = RLock()
        self.daemon = True
        path = abspath(root_path)
        self.root = File(basename(path), is_dir=True, path=path)
        self.exception = None

    def run(self):
        try:
            self.scan(self.root)
        except BaseException as e:
            self.exception = e
            raise

    def join(self):
        super(Scanner, self).join()
        if self.exception is not None:
            raise Exception(self.exception)

    def scan(self, parent):
        dirs = []
        with self.lock:
            try:
                dir_list = os.listdir(parent.path)
            except OSError:
                pass
            else:
                for f in dir_list:
                    path = join(parent.path, f)
                    if os.path.islink(path):
                        continue
                    try:
                        stat = os.stat(path)
                    except OSError:
                        continue
                    mode = stat.st_mode
                    if S_ISDIR(mode):
                        dir = File(f, is_dir=True)
                        parent.add_child(dir)
                        dirs.append(dir)
                    elif S_ISREG(mode):
                        parent.add_child(File(f, size=stat.st_size))
        for dir in dirs:
            self.scan(dir)
