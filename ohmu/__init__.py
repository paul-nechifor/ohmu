#!/usr/bin/env python

import sys
import time
from os.path import abspath

from .views import Screen
from .fs import Scanner


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


def main(name, args):
    if name != '__main__':
        return

    root_path = abspath(args[0] if args else '.')
    Ohmu(root_path).start()


def entry_point():
    main('__main__', sys.argv[1:])


main(__name__, sys.argv[1:])
