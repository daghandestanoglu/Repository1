import curses
import random
import time

COLS, ROWS = 10, 20

SHAPES = [
    [[1,1,1,1]],
    [[1,0,0],[1,1,1]],
    [[0,0,1],[1,1,1]],
    [[1,1],[1,1]],
    [[0,1,1],[1,1,0]],
    [[0,1,0],[1,1,1]],
    [[1,1,0],[0,1,1]],
]

COLORS = [1, 2, 3, 4, 5, 6, 7]


def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]


class Piece:
    def __init__(self, kind=None):
        self.kind = kind if kind is not None else random.randint(0, 6)
        self.shape = [row[:] for row in SHAPES[self.kind]]
        self.color = COLORS[self.kind]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def cells(self, ox=0, oy=0, shape=None):
        s = shape or self.shape
        return [(self.x + c + ox, self.y + r + oy)
                for r, row in enumerate(s)
                for c, v in enumerate(row) if v]


class Tetris:
    def __init__(self):
        self.board = [[0] * COLS for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.piece = Piece()
        self.next = Piece()
        self.game_over = False

    def valid(self, piece, ox=0, oy=0, shape=None):
        for x, y in piece.cells(ox, oy, shape):
            if x < 0 or x >= COLS or y >= ROWS:
                return False
            if y >= 0 and self.board[y][x]:
                return False
        return True

    def ghost_y(self):
        dy = 0
        while self.valid(self.piece, oy=dy + 1):
            dy += 1
        return self.piece.y + dy

    def lock(self):
        for x, y in self.piece.cells():
            if y < 0:
                self.game_over = True
                return
            self.board[y][x] = self.piece.color

        cleared = [r for r in range(ROWS) if all(self.board[r])]
        for r in cleared:
            self.board.pop(r)
            self.board.insert(0, [0] * COLS)

        pts = [0, 100, 300, 500, 800]
        self.score += pts[len(cleared)] * self.level
        self.lines += len(cleared)
        self.level = self.lines // 10 + 1

        self.piece = self.next
        self.next = Piece()

    def move(self, dx):
        if self.valid(self.piece, ox=dx):
            self.piece.x += dx

    def rotate(self):
        s = rotate(self.piece.shape)
        for k in [0, -1, 1, -2, 2]:
            if self.valid(self.piece, ox=k, shape=s):
                self.piece.shape = s
                self.piece.x += k
                break

    def drop(self):
        if self.valid(self.piece, oy=1):
            self.piece.y += 1
        else:
            self.lock()

    def hard_drop(self):
        self.piece.y = self.ghost_y()
        self.lock()


def draw(stdscr, game):
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    board_w = COLS * 2 + 2
    ox = max(0, (w - board_w - 20) // 2)
    oy = max(0, (h - ROWS - 2) // 2)

    try:
        stdscr.addstr(oy, ox, "+" + "-" * (COLS * 2) + "+")
        stdscr.addstr(oy + ROWS + 1, ox, "+" + "-" * (COLS * 2) + "+")
    except curses.error:
        pass
    for r in range(ROWS):
        try:
            stdscr.addstr(oy + 1 + r, ox, "|")
            stdscr.addstr(oy + 1 + r, ox + COLS * 2 + 1, "|")
        except curses.error:
            pass

    for r in range(ROWS):
        for c in range(COLS):
            val = game.board[r][c]
            if val:
                try:
                    stdscr.addstr(oy + 1 + r, ox + 1 + c * 2, "[]",
                                  curses.color_pair(val) | curses.A_BOLD)
                except curses.error:
                    pass

    gy = game.ghost_y()
    for x, y in game.piece.cells(oy=gy - game.piece.y):
        if 0 <= y < ROWS and 0 <= x < COLS:
            try:
                stdscr.addstr(oy + 1 + y, ox + 1 + x * 2, "::",
                              curses.color_pair(game.piece.color) | curses.A_DIM)
            except curses.error:
                pass

    for x, y in game.piece.cells():
        if 0 <= y < ROWS and 0 <= x < COLS:
            try:
                stdscr.addstr(oy + 1 + y, ox + 1 + x * 2, "[]",
                              curses.color_pair(game.piece.color) | curses.A_BOLD)
            except curses.error:
                pass

    sx = ox + COLS * 2 + 4
    sy = oy

    def put(row, text, attr=0):
        try:
            stdscr.addstr(sy + row, sx, text, attr)
        except curses.error:
            pass

    put(0,  "TETRIS",         curses.A_BOLD)
    put(2,  f"Score: {game.score}")
    put(3,  f"Lines: {game.lines}")
    put(4,  f"Level: {game.level}")
    put(6,  "NEXT:",          curses.A_BOLD)
    for r, row in enumerate(game.next.shape):
        line = "".join("[]" if v else "  " for v in row)
        try:
            stdscr.addstr(sy + 7 + r, sx, line,
                          curses.color_pair(game.next.color) | curses.A_BOLD)
        except curses.error:
            pass

    put(11, "Controls:",      curses.A_BOLD)
    put(12, "A/D : move")
    put(13, "W   : rotate")
    put(14, "S   : soft drop")
    put(15, "SPC : hard drop")
    put(16, "Q to quit")
    put(17, "R to restart")

    if game.game_over:
        msg  = " GAME OVER "
        sub  = " press R "
        my = oy + ROWS // 2
        mx  = ox + (COLS * 2 + 2 - len(msg)) // 2 + 1
        mx2 = ox + (COLS * 2 + 2 - len(sub)) // 2 + 1
        try:
            stdscr.addstr(my,     mx,  msg, curses.A_BOLD | curses.A_REVERSE)
            stdscr.addstr(my + 1, mx2, sub, curses.A_REVERSE)
        except curses.error:
            pass

    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN,    curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE,    curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW,  curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN,   curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_RED,     curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_WHITE,   curses.COLOR_BLACK)

    game = Tetris()
    last_drop = time.time()

    while True:
        speed = max(0.1, 0.8 - (game.level - 1) * 0.07)
        key = stdscr.getch()

        if key == ord('q') or key == ord('Q'):
            break

        if key == ord('r') or key == ord('R'):
            game = Tetris()
            last_drop = time.time()

        if not game.game_over:
            if key in (ord('a'), ord('A')):
                game.move(-1)
            elif key in (ord('d'), ord('D')):
                game.move(1)
            elif key in (ord('w'), ord('W')):
                game.rotate()
            elif key in (ord('s'), ord('S')):
                game.drop()
                last_drop = time.time()
            elif key == ord(' '):
                game.hard_drop()
                last_drop = time.time()

            now = time.time()
            if now - last_drop >= speed:
                game.drop()
                last_drop = now

        draw(stdscr, game)
        time.sleep(0.03)


curses.wrapper(main)