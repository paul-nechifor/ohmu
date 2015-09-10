from .utils import TestCase, coffee_string


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
