#!/usr/bin/env python

from os.path import abspath, basename, join
from stat import S_ISDIR, S_ISREG
from threading import Thread, RLock
import curses
import os
import sys
import time


class File(object):

    def __init__(self, name, is_dir=False, parent=None, size=0, path=None):
        self.name = name
        self.is_dir = is_dir
        self.parent = parent
        self.size = size
        self.path = path
        self.children = []

    def add_child(self, file):
        file.parent = self
        file.path = join(self.path, file.name)
        self.children.append(file)

        parent = self
        while parent:
            parent.size += file.size
            parent = parent.parent

    def sortAll(self):
        self.children.sort(key=lambda x: -x.size)
        for x in self.children:
            x.sortAll()


class Scanner(Thread):

    def __init__(self, root_path):
        super(Scanner, self).__init__()
        self.lock = RLock()
        self.finished = False
        path = abspath(root_path)
        self.root = File(basename(path), is_dir=True, path=path)

    def run(self):
        self.scan(self.root)

    def scan(self, parent):
        dirs = []
        with self.lock:
            for f in os.listdir(parent.path):
                path = join(parent.path, f)
                stat = os.stat(path)
                mode = stat.st_mode
                if S_ISDIR(mode):
                    dir = File(f, is_dir=True)
                    parent.add_child(dir)
                    dirs.append(dir)
                elif S_ISREG(mode):
                    parent.add_child(File(f, size=stat.st_size))
        for dir in dirs:
            self.scan(dir)


class FileView(object):

    def __init__(self, file):
        self.file = file

    def generate(self):
        pass


class Screen(object):

    def __init__(self):
        self.screen = curses.initscr()
        self.height = -1
        self.width = -1

    def start(self):
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(1)
        self.screen.nodelay(1)
        self.update_size()

    def tick(self, tick):
        self.screen.addstr(13, 5, '%.40f' % tick)
        self.screen.refresh()

    def update_size(self):
        self.height, self.width = self.screen.getmaxyx()

    def stop(self):
        self.screen.keypad(0)
        curses.nocbreak()
        curses.echo()
        curses.endwin()


class Ohmu(object):

    refresh_rate = 0.05

    def __init__(self, root_path):
        self.screen = Screen()
        self.scanner = Scanner(root_path)
        self.keep_running = True

    def start(self):
        self.scanner.start()
        self.screen.start()
        self.loop()

    def loop(self):
        start = time.time()
        last_tick = start
        self.screen.tick(start)

        try:
            while self.keep_running:
                self.process_input(self.screen.screen.getch())
                if not self.keep_running:
                    break
                now = time.time()
                passed = now - last_tick
                if passed > self.refresh_rate:
                    last_tick = now
                    self.screen.tick(now)
        except KeyboardInterrupt:
            pass
        except:
            self.screen.stop()
            raise

        self.screen.stop()

    def process_input(self, key):
        if key == ord('q'):
            self.keep_running = False


def main(name, args):
    if name != '__main__':
        return

    root_path = abspath(args[0] if args else '.')
    Ohmu(root_path).start()


main(__name__, sys.argv[1:])
