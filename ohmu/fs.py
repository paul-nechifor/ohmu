from os.path import abspath, basename, join
from stat import S_ISDIR, S_ISREG
from threading import Thread, RLock
import os


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


class Scanner(Thread):

    def __init__(self, root_path):
        super(Scanner, self).__init__()
        self.lock = RLock()
        self.daemon = True
        path = abspath(root_path)
        self.root = File(basename(path), is_dir=True, path=path)

    def run(self):
        self.scan(self.root)

    def scan(self, parent):
        dirs = []
        with self.lock:
            for f in os.listdir(parent.path):
                path = join(parent.path, f)
                stat = os.stat(path)
                mode = stat.st_mode
                if S_ISDIR(mode):
                    dir = File(f, is_dir=True)
                    parent.add_child(dir)
                    dirs.append(dir)
                elif S_ISREG(mode):
                    parent.add_child(File(f, size=stat.st_size))
        for dir in dirs:
            self.scan(dir)
