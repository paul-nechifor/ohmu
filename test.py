from contextlib import contextmanager
from os.path import join
from tempfile import mkdtemp
from unittest import TestCase as BaseTestCase
import os
import shutil

import ohmu
from ohmu import coffee_string


class TestCase(BaseTestCase):

    def equalities(self, *args):
        for a, b in zip(*(iter(args),) * 2):
            self.assertEqual(a, b)


class File(TestCase):

    def test_dirs_have_the_size_of_their_children(self):
        a = ohmu.File('a', is_dir=True, path='/')
        b = ohmu.File('b', is_dir=True, path='/')
        c = ohmu.File('c', is_dir=True, path='/')
        a.add_child(b)
        b.add_child(c)

        c.add_child(ohmu.File('d', size=1))
        c.add_child(ohmu.File('e', size=1))
        b.add_child(ohmu.File('f', size=2))
        a.add_child(ohmu.File('e', size=3))

        a.sortAll()
        self.assertEqual(c.size, 2)
        self.assertEqual(b.size, 4)
        self.assertEqual(a.size, 7)

    def test_files_are_in_order(self):
        root = ohmu.File('p', is_dir=True, path='/')
        root.add_child(ohmu.File('a', size=2))
        root.add_child(ohmu.File('b', size=1))
        root.add_child(ohmu.File('c', size=3))
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
            scanner = ohmu.Scanner(join(dir, 'd1'))
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


class Canvas(TestCase):
    def _test_one_dir(self):
        a = ohmu.File('a', is_dir=True, path='/')
        a.add_child(ohmu.File('b', size=5))
        canvas = ohmu.Canvas(10, 7)
        canvas.draw(a)

        self.assertEqual(
            canvas.get_string(),
            coffee_string(r"""
                /a-------\
                |/b-----\|
                ||      ||
                |\------/|
                \--------/
            """)
        )

    def test_limits_1_1(self):
        self.with_size(1, 1, """
            *
        """)

    def test_limits_2_1(self):
        self.with_size(2, 1, """
            <>
        """)

    def test_limits_3_1(self):
        self.with_size(3, 1, """
            <a>
        """)

    def test_limits_4_1(self):
        self.with_size(4, 1, """
            <a->
        """)

    def test_limits_5_1(self):
        self.with_size(5, 1, """
            <a-->
        """)

    def test_limits_1_2(self):
        self.with_size(1, 2, """
            ^
            v
        """)

    def test_limits_1_3(self):
        self.with_size(1, 3, """
            ^
            a
            v
        """)

    def test_limits_1_4(self):
        self.with_size(1, 4, """
            ^
            a
            |
            v
        """)

    def test_limits_1_5(self):
        self.with_size(1, 5, """
            ^
            a
            |
            |
            v
        """)

    def test_limits_2_2(self):
        self.with_size(2, 2, r"""
            /\
            \/
        """)

    def test_limits_3_2(self):
        self.with_size(3, 2, r"""
            /a\
            \-/
        """)

    def test_limits_2_3(self):
        self.with_size(2, 3, r"""
            /\
            a|
            \/
        """)

    def with_size(self, width, height, str):
        canvas = ohmu.Canvas(width, height)
        canvas.draw(ohmu.File('a', is_dir=True, path='/'))
        self.assertEqual(canvas.get_string(), coffee_string(str))


class Utils(TestCase):
    def test_coffee_string(self):
        list = [
            (
                """
                    a
                """,
                'a',
            ),
            (
                """
                    aa
                    bbb
                """,
                'aa\nbbb',
            ),
            (
                """
                    xx
                        yyyy
                        zzzz
                    nn
                """,
                'xx\n    yyyy\n    zzzz\nnn',
            ),
        ]

        for coffee, normal in list:
            self.assertEqual(coffee_string(coffee), normal)
