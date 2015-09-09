from mock import patch

from . import entry_point, main, sys
from .utils import TestCase


class Main(TestCase):
    @patch('ohmu.Ohmu')
    def test_main_takes_a_dir_path(self, Ohmu):
        main('__main__', ['/dir1/2'])
        Ohmu.assert_called_with('/dir1/2')

    @patch('ohmu.Ohmu')
    @patch('ohmu.abspath')
    def test_main_uses_the_current_dir(self, abspath, Ohmu):
        abspath.return_value = '/the/abs/path'
        main('__main__', [])
        abspath.assert_called_with('.')
        Ohmu.assert_called_with('/the/abs/path')

    @patch('ohmu.main')
    def test_entry_point_works(self, main):
        with patch.object(sys, 'argv', ['-', '/some/dir']):
            entry_point()
        main.assert_called_with('__main__', ['/some/dir'])
