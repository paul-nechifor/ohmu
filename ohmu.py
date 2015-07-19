#!/usr/bin/env python

import curses
import heapq


class File(object):
    def __init__(self, name, is_dir=False, parent=None, size=0):
        self.name = name
        self.is_dir = is_dir
        self.parent = parent
        self.size = size
        self.children = []

    def add_child(self, file):
        file.parent = self
        heapq.heappush(self.children, (file.size, file))
        parent = self
        while parent:
            parent.size += file.size
            parent = parent.parent

    def __iter__(self):
        return (x[1] for x in reversed(self.children))


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
        self.update_size()

    def update_size(self):
        self.height, self.width = self.screen.getmaxyx()

    def stop(self):
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()


def main():
    screen = Screen()
    screen.start()
    screen.screen.getch()
    screen.stop()


if __name__ == '__main__':
    main()
