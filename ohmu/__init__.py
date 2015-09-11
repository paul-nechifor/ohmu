#!/usr/bin/env python

from os.path import abspath
import curses
import sys
import time

from .fs import Scanner
from .views import Screen


class Ohmu(object):

    refresh_rate = 0.05

    def __init__(self, root_path):
        self.screen = Screen()
        self.scanner = Scanner(root_path)
        self.keep_running = True

    def start(self):
        try:
            self.scanner.start()
            self.screen.start()
            self.loop()
        except KeyboardInterrupt:
            pass
        except:
            self.screen.stop()
            raise
        self.screen.stop()

    def loop(self):
        start = time.time()
        last_tick = start
        self.screen.tick(start, self.scanner)
        while self.keep_running:
            self.process_input(self.screen.get_key_sequence())
            if not self.keep_running:
                break
            now = time.time()
            passed = now - last_tick
            if passed > self.refresh_rate:
                last_tick = now
                self.screen.tick(now, self.scanner)

    def process_input(self, key_sequence):
        if key_sequence in (ord('q'), Screen.ESC_KEY):
            self.keep_running = False
        elif key_sequence == curses.KEY_RESIZE:
            self.screen.update_size()


def main(name, args):
    if name != '__main__':
        return
    root_path = abspath(args[0] if args else '.')
    Ohmu(root_path).start()


def entry_point():
    main('__main__', sys.argv[1:])


main(__name__, sys.argv[1:])
