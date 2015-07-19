from unittest import TestCase

import ohmu


class TestFile(TestCase):
    def test_dirs_have_the_size_of_their_children(self):
        a = ohmu.File('a', is_dir=True)
        b = ohmu.File('b', is_dir=True)
        c = ohmu.File('c', is_dir=True)
        a.add_child(b)
        b.add_child(c)

        c.add_child(ohmu.File('d', size=1))
        c.add_child(ohmu.File('e', size=1))
        b.add_child(ohmu.File('f', size=2))
        a.add_child(ohmu.File('e', size=3))

        self.assertEqual(c.size, 2)
        self.assertEqual(b.size, 4)
        self.assertEqual(a.size, 7)

    def test_files_are_in_order(self):
        root = ohmu.File('p', is_dir=True)
        root.add_child(ohmu.File('a', size=2))
        root.add_child(ohmu.File('b', size=1))
        root.add_child(ohmu.File('c', size=3))
        self.assertEqual([x.name for x in root], ['c', 'a', 'b'])
