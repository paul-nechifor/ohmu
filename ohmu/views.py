from itertools import chain, repeat
import curses
import math
import os
import sys

xrange = range if sys.version_info[0] == 3 else xrange


class Canvas(object):

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.table = [
            [[' ', 2] for y in xrange(width)]
            for i in xrange(height)
        ]

    def draw(self, file):
        self.draw_object(file, 0, 0, self.width - 1, 0, self.height - 1)

    def draw_object(self, object, l, sx, tx, sy, ty):  # noqa
        dx = tx - sx + 1
        dy = ty - sy + 1
        t = self.table
        name = object.name

        color = 1 + l % 6 if object.is_dir else 0
        for x in xrange(dx):
            for y in xrange(dy):
                t[sy + y][sx + x][1] = color

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
            self.fill_horizontal_name(
                object.get_name_size(dx - 2), t, sx + 1, sy, dx - 2
            )
            return

        t[sy][sx][0] = curses.ACS_ULCORNER
        t[sy][tx][0] = curses.ACS_URCORNER
        t[ty][sx][0] = curses.ACS_LLCORNER
        t[ty][tx][0] = curses.ACS_LRCORNER

        if dx == 2 and dy > 2:
            t[sy + 1][sx][0] = name[0]
            self.fill_horizontal(t, sx + 1, sy, dx - 2)
            self.fill_vertical(t, sx, sy + 2, dy - 3)
        else:
            self.fill_horizontal_name(
                object.get_name_size(dx - 2), t, sx + 1, sy, dx - 2
            )
            self.fill_vertical(t, sx, sy + 1, dy - 2)

        self.fill_horizontal(t, sx + 1, ty, dx - 2)
        self.fill_vertical(t, tx, sy + 1, dy - 2)

        if dx > 2 and dy > 2 and object.children:
            self.draw_children(
                object.children, l + 1,
                sx + 1, tx - 1,
                sy + 1, ty - 1,
            )

    def fill_vertical(self, t, sx, sy, ny):
        for i in xrange(ny):
            t[sy + i][sx][0] = curses.ACS_VLINE

    def fill_horizontal(self, t, sx, sy, nx):
        for i in xrange(nx):
            t[sy][sx + i][0] = curses.ACS_HLINE

    def fill_horizontal_name(self, name, t, sx, sy, nx):
        if nx <= 0:
            return
        left = nx - len(name)
        for i, c in enumerate(chain(name, repeat(curses.ACS_HLINE, left))):
            t[sy][sx + i][0] = c

    def draw_children(self, children, l, sx, tx, sy, ty):  # noqa
        if len(children) == 1:
            self.draw_object(children[0], l, sx, tx, sy, ty)
            return

        lists, sizes = self.split_in_two(children)

        dx = tx - sx + 1
        dy = ty - sy + 1
        ratio = sizes[0] / float(sizes[0] + sizes[1])
        if dx > dy:
            dx2 = int(math.ceil(dx * ratio))
            self.draw_children(
                lists[0], l,
                sx, sx + dx2 - 1,
                sy, ty,
            )
            if dx2 < dx:
                self.draw_children(
                    lists[1], l,
                    sx + dx2, tx,
                    sy, ty,
                )
        else:
            dy2 = int(math.ceil(dy * ratio))
            self.draw_children(
                lists[0], l,
                sx, tx,
                sy, sy + dy2 - 1,
            )
            if dy2 < dy:
                self.draw_children(
                    lists[1], l,
                    sx, tx,
                    sy + dy2, ty,
                )

    def get_string(self):
        return '\n'.join(''.join(y[0] for y in x) for x in self.table)

    @classmethod
    def split_in_two(cls, files):
        assert len(files) >= 2

        list_l, list_r = [files[0]], [files[-1]]
        size_l, size_r = files[0].draw_size, files[-1].draw_size
        index_l, index_r = 1, len(files) - 2

        while index_l <= index_r:
            if size_l < size_r:
                list_l.append(files[index_l])
                size_l += files[index_l].draw_size
                index_l += 1
            else:
                list_r.append(files[index_r])
                size_r += files[index_r].draw_size
                index_r -= 1

        # Make sure the first list is always the largest.
        if size_l < size_r:
            # Move one element.
            file = list_r.pop()
            size_r -= file.draw_size
            list_l.append(file)
            size_l += file.draw_size

        # Reverse since it's in the wrong order.
        list_r = list(reversed(list_r))

        return [list_l, list_r], [size_l, size_r]


class Screen(object):

    ESC_KEY = 27

    def __init__(self):
        self.height = -1
        self.width = -1
        self.started = False
        self.screen = None

        # Use a short delay for sending the Escape key (but don't override it
        # if it's set).
        os.environ.setdefault('ESCDELAY', '10')

    def start(self):
        self.screen = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        for i, color in enumerate([0, 1, 2, 3, 6, 4, 5]):
            curses.init_pair(i + 1, curses.COLOR_WHITE, color)

        self.started = True
        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)
        self.screen.keypad(True)
        self.screen.nodelay(True)
        self.update_size()

    def tick(self, tick, scanner):
        canvas = Canvas(self.width, self.height)
        with scanner.lock:
            scanner.root.sortAll()
            canvas.draw(scanner.root)

        for i, line in enumerate(canvas.table):
            for j, [char, color] in enumerate(line):
                self.screen.insch(
                    i, j, char, curses.color_pair(1 + color) | curses.A_BOLD
                )

        self.screen.refresh()

    def update_size(self):
        self.height, self.width = self.screen.getmaxyx()

    def get_key_sequence(self):
        """Returns a key, or key sequence."""
        key = self.screen.getch()
        if key == self.ESC_KEY:  # Escape or Alt.
            self.screen.nodelay(True)
            key2 = self.screen.getch()
            if key2 == -1:
                return key  # Escape.
            return (key, key2)  # Alt.
        return key

    def stop(self):
        if not self.started:
            return
        self.screen.keypad(0)
        curses.curs_set(True)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
