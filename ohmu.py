#!/usr/bin/env python

from os.path import abspath, basename, join
from stat import S_ISDIR, S_ISREG
from threading import Thread, RLock
import curses
import os
import re
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


class Canvas(object):

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.table = [
            [[' ', 0] for y in xrange(width)]
            for i in xrange(height)
        ]

    def draw(self, file):
        self.draw_object(file, 0, self.width - 1, 0, self.height - 1)

    def fill_vertical(self, t, sx, sy, ny):
        for i in xrange(ny):
            t[sy + i][sx] = '|'

    def fill_horizontal(self, t, sx, sy, nx):
        for i in xrange(nx):
            t[sy][sx + i] = '-'

    def fill_horizontal_name(self, name, t, sx, sy, nx):
        if nx <= 0:
            return
        name = name[:nx]
        left = nx - len(name)
        if left > 0:
            name += '-' * left
        for i, c in enumerate(name):
            t[sy][sx + i] = c

    def draw_object(self, object, sx, tx, sy, ty):  # noqa
        dx = tx - sx + 1
        dy = ty - sy + 1
        t = self.table
        name = object.name

        if dx == 1 and dy == 1:
            t[sy][sx][0] = '*'
            return
        elif dx == 1:
            t[sy][sx][0] = '^'
            t[ty][sx][0] = 'v'
            if dy > 2:
                t[sy + 1][sx][0] = name[0]
                self.fill_vertical(t, sx, sy + 2, dy - 3)
            return
        elif dy == 1:
            t[sy][sx][0] = '<'
            t[sy][tx][0] = '>'
            self.fill_horizontal_name(name, t, sx + 1, sy, dx - 2)
            return

        t[sy][sx][0] = '/'
        t[sy][tx][0] = '\\'
        t[ty][sx][0] = '\\'
        t[ty][tx][0] = '/'

        if dx == 2 and dy > 2:
            t[sy + 1][sx][0] = name[0]
            self.fill_horizontal(t, sx + 1, sy, dx - 2)
            self.fill_vertical(t, sx, sy + 2, dy - 3)
        else:
            self.fill_horizontal_name(name, t, sx + 1, sy, dx - 2)
            self.fill_vertical(t, sx, sy + 1, dy - 2)

        self.fill_horizontal(t, sx + 1, ty, dx - 2)
        self.fill_vertical(t, tx, sy + 1, dy - 2)

    def get_string(self):
        return '\n'.join(''.join(y[0] for y in x) for x in self.table)


class Screen(object):

    def __init__(self):
        self.screen = curses.initscr()
        curses.start_color()
        self.height = -1
        self.width = -1

    def start(self):
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(1)
        self.screen.nodelay(1)
        self.update_size()

    def tick(self, tick, scanner):
        canvas = Canvas(self.width, self.height)
        with scanner.lock:
            scanner.root.sortAll()
            canvas.draw(scanner.root)

        for i, line in enumerate(canvas.table[:-1]):
            for j, [char, color] in enumerate(line):
                self.screen.addstr(i, j, char)

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
        try:
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
            self.process_input(self.screen.screen.getch())
            if not self.keep_running:
                break
            now = time.time()
            passed = now - last_tick
            if passed > self.refresh_rate:
                last_tick = now
                self.screen.tick(now, self.scanner)

    def process_input(self, key):
        if key == ord('q'):
            self.keep_running = False


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


def main(name, args):
    if name != '__main__':
        return

    root_path = abspath(args[0] if args else '.')
    Ohmu(root_path).start()


main(__name__, sys.argv[1:])
