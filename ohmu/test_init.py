from mock import Mock, patch
import curses

from . import Ohmu, entry_point, main, sys
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


class OhmuTest(TestCase):
    def test_exits_when_loop_exits(self):
        o = self.get_mocked_ohmu_instance()
        o.loop = Mock()
        o.start()
        o.screen.stop.assert_called_with()

    def test_exits_when_ctrl_c_is_pressed(self):
        o = self.get_mocked_ohmu_instance()
        o.loop = Mock(side_effect=KeyboardInterrupt)
        o.start()
        o.screen.stop.assert_called_with()

    def test_stop_on_exceptions_and_rethrow(self):
        o = self.get_mocked_ohmu_instance()
        o.loop = Mock(side_effect=Exception('Nucular Exception'))
        with self.assertRaisesRegexp(Exception, 'Nucular Exception'):
            o.start()
        o.screen.stop.assert_called_with()

    def test_loop_stops_on_q(self):
        o = self.get_mocked_ohmu_instance()
        o.process_input(ord('q'))
        self.assertFalse(o.keep_running)

    def test_loop_can_be_stopped_by_process_input(self):
        o = self.get_mocked_ohmu_instance()
        o.screen.get_key_sequence = Mock(return_value=ord('q'))
        o.loop()
        self.assertFalse(o.keep_running)
        self.assertEqual(o.screen.tick.call_count, 1)

    def test_changing_the_screen_size_triggers_update(self):
        o = self.get_mocked_ohmu_instance()
        o.process_input(curses.KEY_RESIZE)
        o.screen.update_size.assert_called_with()

    def get_mocked_ohmu_instance(self):
        o = Ohmu('/tmp')
        o.scanner = Mock()
        o.screen = Mock()
        return o
