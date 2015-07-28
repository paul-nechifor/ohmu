from contextlib import contextmanager
from os.path import join
from tempfile import mkdtemp
import os
import shutil

from . import fs
from .utils import TestCase


class File(TestCase):

    def test_dirs_have_the_size_of_their_children(self):
        a = fs.File('a', is_dir=True, path='/')
        b = fs.File('b', is_dir=True, path='/')
        c = fs.File('c', is_dir=True, path='/')
        a.add_child(b)
        b.add_child(c)

        c.add_child(fs.File('d', size=1))
        c.add_child(fs.File('e', size=1))
        b.add_child(fs.File('f', size=2))
        a.add_child(fs.File('e', size=3))

        a.sortAll()
        self.assertEqual(c.size, 2)
        self.assertEqual(b.size, 4)
        self.assertEqual(a.size, 7)

    def test_files_are_in_order(self):
        root = fs.File('p', is_dir=True, path='/')
        root.add_child(fs.File('a', size=2))
        root.add_child(fs.File('b', size=1))
        root.add_child(fs.File('c', size=3))
        root.sortAll()
        self.assertEqual([x.name for x in root.children], ['c', 'a', 'b'])


class Scanner(TestCase):

    def test_read_file_sizes(self):
        structure = {
            'd1': {
                'a': '-' * 10,
                'b': '-' * 5,
                'd2': {
                    'c': '-' * 1,
                    'd': '-' * 3,
                },
            },
        }
        with self.file_structure(structure) as dir:
            scanner = fs.Scanner(join(dir, 'd1'))
            scanner.start()
            scanner.join()

        root = scanner.root
        self.equalities(
            root.name, 'd1',
            root.is_dir, True,
            root.parent, None,
            root.size, 19,
        )
        root.sortAll()
        self.equalities(
            [(x.name, x.size) for x in root.children],
            [('a', 10), ('b', 5), ('d2', 4)],
        )

    @contextmanager
    def file_structure(self, structure):
        dir = mkdtemp()
        self.create_file_structure(structure, dir)
        yield dir
        shutil.rmtree(dir)

    def create_file_structure(self, structure, dir):
        for name, value in structure.items():
            path = join(dir, name)
            if isinstance(value, basestring):
                open(path, 'w').write(value)
            else:
                os.mkdir(path)
                self.create_file_structure(value, path)
