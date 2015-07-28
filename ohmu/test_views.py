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
            /a-------\
            |/b-----\|
            ||      ||
            |\------/|
            \--------/
        """
        )

    def test_two_files(self):
        self.with_nested(12, 5, {
            'a': {'bb': 5, 'c': 5}
        }, r"""
            /a---------\
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
            /a---------------------------------------\
            |/e---------------------\/dd-----\/bb---\|
            ||/k-------\/h\/j---\/i\||/g----\||     ||
            |||/l-----\|| ||    || ||||     |||     ||
            ||||      ||| ||    || ||||     |||     ||
            ||||      ||| ||    || ||||     ||\-----/|
            ||||      ||| ||    || ||||     ||/c----\|
            ||||      ||| ||    || |||\-----/||     ||
            |||\------/|| ||    || |||/f----\||     ||
            ||\--------/\-/\----/\-/||\-----/||     ||
            |\----------------------/\-------/\-----/|
            \----------------------------------------/
        """
        )

    def with_size(self, width, height, str):
        canvas = views.Canvas(width, height)
        canvas.draw(fs.File('a', is_dir=True, path='/'))
        self.assertEqual(canvas.get_string(), coffee_string(str))

    def with_nested(self, width, height, structure, str):
        a = fs.File('a', is_dir=True, path='/')
        a.add_child(fs.File('b', size=5))

        self.assertEqual(len(structure), 1)
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
