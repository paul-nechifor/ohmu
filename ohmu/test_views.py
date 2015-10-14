import sys

from mock import Mock, patch

from . import fs, views
from .utils import TestCase, coffee_string


class Canvas(TestCase):
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

    def test_one_file(self):
        self.with_nested(10, 5, {
            'a': {'b': 5}
        }, r"""
            /a 5.00B-\
            |/b 5B--\|
            ||      ||
            |\------/|
            \--------/
        """
        )

    def test_small_2_2(self):
        self.with_nested(4, 4, {
            'a': {
                'b': 5,
                'c': 5,
                'd': 5,
                'e': 5,
            }
        }, r"""
            /a-\
            |**|
            |**|
            \--/
        """
        )

    def test_zero_sized_files(self):
        self.with_nested(4, 3, {
            'a': {
                'b': 0,
                'c': 0,
            }
        }, r"""
            /a-\
            |**|
            \--/
        """
        )

    def test_two_files(self):
        self.with_nested(12, 5, {
            'a': {'bb': 5, 'c': 5}
        }, r"""
            /a 10.00B--\
            |/bb-\/c--\|
            ||   ||   ||
            |\---/\---/|
            \----------/
        """
        )

    def test_complex_files(self):
        self.with_nested(42, 12, {
            'a': {
                'bb': 5,
                'c': 5,
                'dd': {
                    'f': 4,
                    'g': 8,
                },
                'e': {
                    'h': 5,
                    'i': 6,
                    'j': 8,
                    'k': {
                        'l': 14,
                    },
                },
            },
        }, r"""
            /a 55.00B--------------------------------\
            |/e 33.00B--------------\/dd 12B-\/bb 5B\|
            ||/k 14.00B\/j--\/i 6B-\||/g 8B-\||     ||
            |||/l 14B-\||   ||     ||||     |||     ||
            ||||      |||   ||     ||||     |||     ||
            ||||      |||   ||     ||||     ||\-----/|
            ||||      |||   |\-----/|||     ||/c 5B-\|
            ||||      |||   |/h 5B-\||\-----/||     ||
            |||\------/||   ||     |||/f 4B-\||     ||
            ||\--------/\---/\-----/||\-----/||     ||
            |\----------------------/\-------/\-----/|
            \----------------------------------------/
        """
        )

    def test_split_in_two_one_element(self):
        with self.assertRaises(AssertionError):
            views.Canvas.split_in_two([1])

    def test_split_in_two_two_elements(self):
        self.check_split(
            [('a', 2), ('b', 2)],
            [['a'], ['b']],
        )

    def test_split_in_two_three_elements(self):
        self.check_split(
            [('a', 3), ('b', 2), ('c', 1)],
            [['a'], ['b', 'c']],
        )

    def test_split_in_two_first_list_is_bigger(self):
        self.check_split(
            [('a', 2), ('b', 2), ('c', 1)],
            [['a', 'b'], ['c']],
        )

    def test_split_in_two_equal_sizes(self):
        self.check_split(
            [('a', 1), ('b', 1), ('c', 1), ('d', 1), ('e', 1)],
            [['a', 'b', 'c'], ['d', 'e']],
        )

    def check_split(self, files, split_names):
        files = [
            fs.File(name, size=size, path='/')
            for name, size in files
        ]
        split = views.Canvas.split_in_two(files)
        real_names = [[x.name for x in list] for list in split[0]]
        self.assertEqual(real_names, split_names)

    def with_size(self, width, height, str):
        canvas = views.Canvas(width, height)
        canvas.draw(fs.File('a', is_dir=True, path='/'))
        self.assertEqual(canvas.get_string(), coffee_string(str))

    def with_nested(self, width, height, structure, str):
        a = fs.File('a', is_dir=True, path='/')
        a.add_child(fs.File('b', size=5))

        self.assertEqual(len(structure), 1)
        if sys.version_info[0] == 3:
            # In Python 3 <dict>.keys() does not return a list but <dict_keys>
            root = fs.File(list(structure.keys())[0], is_dir=True, path='/')
            self.add_recursive(root, list(structure.values())[0])
        else:
            root = fs.File(structure.keys()[0], is_dir=True, path='/')
            self.add_recursive(root, structure.values()[0])

        root.sortAll()

        canvas = views.Canvas(width, height)
        canvas.draw(root)

        self.assertEqual(
            canvas.get_string(),
            coffee_string(str),
        )

    def add_recursive(self, parent, structure):
        for key, value in structure.items():
            if isinstance(value, int):
                parent.add_child(fs.File(key, size=value))
            else:
                dir = fs.File(key, is_dir=True)
                parent.add_child(dir)
                self.add_recursive(dir, value)


class Screen(TestCase):
    @patch('ohmu.views.curses')
    def test_start(self, curses):
        s = views.Screen()
        screen = Mock()
        screen.getmaxyx = Mock(return_value=(20, 10))
        curses.initscr.return_value = screen
        s.start()
        self.assertEqual((s.width, s.height), (10, 20))

    @patch('ohmu.views.curses')
    def test_stop(self, curses):
        s = views.Screen()
        s.started = True
        s.screen = Mock()
        s.stop()
        curses.endwin.assert_called_with()

    @patch('ohmu.views.curses')
    def test_stop_is_no_op_is_not_started(self, curses):
        s = views.Screen()
        s.stop()
        self.assertEqual(0, curses.endwin.call_count)

    def test_escape_returns_escape(self):
        self.assert_screen_returns(
            [views.Screen.ESC_KEY, -1], views.Screen.ESC_KEY,
        )

    def test_alt_t_returns_alt_t(self):
        self.assert_screen_returns(
            [views.Screen.ESC_KEY, ord('t')],
            (views.Screen.ESC_KEY, ord('t')),
        )

    def test_q_returns_q(self):
        self.assert_screen_returns([ord('q')], ord('q'))

    def assert_screen_returns(self, sequence, ret):
        screen = views.Screen()
        screen.screen = Mock()
        screen.screen.getch.side_effect = sequence
        self.assertEqual(ret, screen.get_key_sequence())
