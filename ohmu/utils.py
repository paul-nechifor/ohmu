from unittest import TestCase as BaseTestCase
import re
import curses
import sys

if sys.version_info.major == 3:
    basestring = str

class TestCase(BaseTestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        curses.ACS_ULCORNER = '/'
        curses.ACS_URCORNER = '\\'
        curses.ACS_LLCORNER = '\\'
        curses.ACS_LRCORNER = '/'
        curses.ACS_HLINE = '-'
        curses.ACS_VLINE = '|'

    def equalities(self, *args):
        for a, b in zip(*(iter(args),) * 2):
            self.assertEqual(a, b)

    def assertEqual(self, a, b):
        if not (isinstance(a, basestring) or isinstance(b, basestring)):
            return super(TestCase, self).assertEqual(a, b)
        if a != b:
            raise AssertionError(coffee_string("""
                Strings are different:
                ===================================================
                %s
                ---------------------------------------------------
                %s
                ===================================================
            """) % (a, b))


def coffee_string(string):
    """
    Cuts the useless whitespaces out of a Python multiline string.

    That means this::

        print coffee_string('''
            def x(a):
                pass
        ''')

    ... is equivalent to this::

        print "def x(a):\\n    pass"
    """

    lines = string.split('\n')[1:-1]

    def start_spaces(x):
        return len(re.match(r'^ *', x).group(0))

    # Don't count empty lines.
    count_lines = (x for x in lines if len(x) > 0)
    min_spaces = min(map(start_spaces, count_lines))

    regex = re.compile(r'^ {,%s}' % min_spaces)
    return '\n'.join(map(lambda x: regex.sub('', x), lines))
