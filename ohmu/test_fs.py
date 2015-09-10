import os
import shutil
from contextlib import contextmanager
from os.path import join
from tempfile import mkdtemp

from mock import Mock, patch

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
            scanner = self.get_scan(join(dir, 'd1'))

        root = scanner.root
        self.equalities(
            root.name, 'd1',
            root.is_dir, True,
            root.parent, None,
            root.size, 19,
        )
        self.equalities(
            [(x.name, x.size) for x in root.children],
            [('a', 10), ('b', 5), ('d2', 4)],
        )

    def test_fobidden_files_are_ignores(self):
        structure = {
            'd1': {
                'a': '-' * 10,
                'd2': {
                    'b': '-' * 5,
                },
            },
        }

        def post_creation(dir):
            os.chmod(join(dir, 'd1', 'd2'), 0)

        def pre_deletion(dir):
            os.chmod(join(dir, 'd1', 'd2'), 0o777)

        with self.file_structure(structure, post_creation, pre_deletion) as d:
            scanner = self.get_scan(join(d, 'd1'))

        self.equalities(
            [x.name for x in scanner.root.children], ['a', 'd2'],
            scanner.root.size, 10,
            scanner.root.children[1].size, 0,
        )

    def test_deleted_files_are_ignored(self):
        structure = {
            'd1': {
                'a': '-' * 10,
                'b': '-' * 10,
            },
        }

        with self.file_structure(structure) as d:
            real_listdir = os.listdir

            with patch.object(fs.os, 'listdir') as listdir:

                def listdir_func(*args, **kwargs):
                    ret = real_listdir(*args, **kwargs)
                    os.remove(join(d, 'd1', 'b'))
                    return ret

                listdir.side_effect = listdir_func

                scanner = self.get_scan(join(d, 'd1'))

        self.equalities(
            [x.name for x in scanner.root.children], ['a'],
            scanner.root.size, 10,
        )

    def test_symlinks_are_ignored(self):
        structure = {'d1': {'a': '-' * 10}}

        def post_creation(dir):
            os.symlink(dir + '/d1/a', dir + '/d1/b')

        with self.file_structure(structure, post_creation) as d:
            scanner = self.get_scan(join(d, 'd1'))

        self.equalities(
            [x.name for x in scanner.root.children], ['a'],
            scanner.root.size, 10,
        )

    def test_scanning_error_is_raised_on_join(self):
        scanner = fs.Scanner('/bad/dir')
        scanner.scan = Mock(side_effect=Exception('The fuck is that'))
        scanner.start()
        with self.assertRaisesRegexp(Exception, 'The fuck is that'):
            scanner.join()

    @contextmanager
    def file_structure(self, structure, post_creation=None, pre_deletion=None):
        dir = mkdtemp()
        self.create_file_structure(structure, dir)
        if post_creation is not None:
            post_creation(dir)
        yield dir
        if pre_deletion is not None:
            pre_deletion(dir)
        shutil.rmtree(dir)

    def get_scan(self, dir):
        scanner = fs.Scanner(dir)
        scanner.start()
        scanner.join()
        scanner.root.sortAll()
        return scanner

    def create_file_structure(self, structure, dir):
        for name, value in structure.items():
            path = join(dir, name)
            if isinstance(value, basestring):
                open(path, 'w').write(value)
            else:
                os.mkdir(path)
                self.create_file_structure(value, path)
