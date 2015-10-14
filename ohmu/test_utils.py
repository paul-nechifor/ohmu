from .utils import TestCase, coffee_string, format_size


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

    def test_assert_equal(self):
        string = '\n'.join([
            'Strings are different:',
            '===================================================',
            'good',
            '---------------------------------------------------',
            'bad',
            '===================================================',
        ])
        with self.assertRaisesRegexp(AssertionError, string):
            self.assertEqual('good', 'bad')

    def test_format_size(self):
        self.assertEqual(format_size(10, '%d'), '10B')
        self.assertEqual(format_size(1024, '%.2f'), '1.00K')
        self.assertEqual(format_size(1025, '%d'), '1K')
        self.assertEqual(format_size(1024 * 1024, '%d'), '1M')
        self.assertEqual(format_size(3 * 1024 ** 4, '%d'), '3T')
