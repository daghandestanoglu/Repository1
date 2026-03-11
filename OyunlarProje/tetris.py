import sys
import os
import random
import time
import threading

# Windows / Unix keyboard input
if os.name == 'nt':
    import msvcrt
else:
    import tty
    import termios

# ─────────────────────────────────────────
#  SABITLER
# ─────────────────────────────────────────
W, H = 10, 20

SHAPES = [
    [[1,1,1,1]],
    [[1,1],[1,1]],
    [[1,1,1],[0,1,0]],
    [[1,1,1],[1,0,0]],
    [[1,1,1],[0,0,1]],
    [[1,1,0],[0,1,1]],
    [[0,1,1],[1,1,0]],
]

COLORS = [
    '\033[96m',  # cyan
    '\033[93m',  # yellow
    '\033[95m',  # magenta
    '\033[97m',  # white
    '\033[94m',  # blue
    '\033[92m',  # green
    '\033[91m',  # red
]
RESET = '\033[0m'
CLEAR = '\033[2J\033[H'
HIDE_CURSOR = '\033[?25l'
SHOW_CURSOR = '\033[?25h'

# ─────────────────────────────────────────
#  GLOBAL OYUN DURUMU
# ─────────────────────────────────────────
board     = [[0]*W for _ in range(H)]
score     = 0
level     = 1
game_over = False
key_buf   = None
key_lock  = threading.Lock()


# ─────────────────────────────────────────
#  YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────
def new_piece():
    idx   = random.randint(0, len(SHAPES)-1)
    shape = [row[:] for row in SHAPES[idx]]
    return {'shape': shape, 'color': idx+1,
            'x': W//2 - len(shape[0])//2, 'y': 0}

def rotate_shape(shape):
    return [list(row) for row in zip(*shape[::-1])]

def is_valid(piece, ox=0, oy=0, shape=None):
    s = shape if shape else piece['shape']
    for y, row in enumerate(s):
        for x, cell in enumerate(row):
            if cell:
                nx, ny = piece['x']+x+ox, piece['y']+y+oy
                if nx < 0 or nx >= W or ny >= H:
                    return False
                if ny >= 0 and board[ny][nx]:
                    return False
    return True

def place_piece(piece):
    for y, row in enumerate(piece['shape']):
        for x, cell in enumerate(row):
            if cell:
                board[piece['y']+y][piece['x']+x] = piece['color']

def clear_lines():
    global board, score, level
    full   = [i for i, row in enumerate(board) if all(row)]
    pts    = [0, 100, 300, 500, 800]
    score += pts[min(len(full), 4)] * level
    for i in full:
        board.pop(i)
        board.insert(0, [0]*W)
    level = score // 1000 + 1


# ─────────────────────────────────────────
#  EKRAN ÇİZİMİ
# ─────────────────────────────────────────
def render(piece, next_p):
    display = [row[:] for row in board]
    for y, row in enumerate(piece['shape']):
        for x, cell in enumerate(row):
            if cell:
                ny, nx = piece['y']+y, piece['x']+x
                if 0 <= ny < H and 0 <= nx < W:
                    display[ny][nx] = piece['color']

    lines = []
    lines.append('┌' + '──'*W + '┐')

    for ri, row in enumerate(display):
        line = '│'
        for cell in row:
            if cell:
                line += COLORS[cell-1] + '██' + RESET
            else:
                line += '  '
        line += '│'

        if   ri == 0:  line += '   TETRIS'
        elif ri == 2:  line += f'   Skor : {score}'
        elif ri == 3:  line += f'   Level: {level}'
        elif ri == 5:  line += '   Sonraki:'
        elif ri in (6, 7, 8):
            ni  = ri - 6
            ns  = next_p['shape']
            seg = ''
            if ni < len(ns):
                for cell in ns[ni]:
                    seg += COLORS[next_p['color']-1]+'██'+RESET if cell else '  '
            line += '   ' + seg
        elif ri == 11: line += '   A D  hareket'
        elif ri == 12: line += '   W   döndür'
        elif ri == 13: line += '   S   hızlı düş'
        elif ri == 14: line += '   Q   çıkış'

        lines.append(line)

    lines.append('└' + '──'*W + '┘')

    sys.stdout.write(CLEAR + '\n'.join(lines) + '\n')
    sys.stdout.flush()


# ─────────────────────────────────────────
#  KLAVYE OKUMA (ayrı thread)
# ─────────────────────────────────────────
def read_keys():
    global key_buf, game_over

    if os.name == 'nt':
        while not game_over:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ('\x00', '\xe0'):
                    ch2 = msvcrt.getwch()
                    mapping = {'H':'UP','P':'DOWN','K':'LEFT','M':'RIGHT'}
                    k = mapping.get(ch2)
                else:
                    k = ch.lower()
                with key_lock:
                    key_buf = k
            time.sleep(0.02)
    else:
        fd  = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while not game_over:
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    ch2 = sys.stdin.read(1)
                    ch3 = sys.stdin.read(1)
                    mapping = {'A':'UP','B':'DOWN','C':'RIGHT','D':'LEFT'}
                    k = mapping.get(ch3)
                else:
                    k = ch.lower()
                with key_lock:
                    key_buf = k
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


def get_key():
    global key_buf
    with key_lock:
        k, key_buf = key_buf, None
    return k


# ─────────────────────────────────────────
#  ANA OYUN DÖNGÜSÜ
# ─────────────────────────────────────────
def run_game():
    global board, score, level, game_over

    board     = [[0]*W for _ in range(H)]
    score     = 0
    level     = 1
    game_over = False

    piece  = new_piece()
    next_p = new_piece()

    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()

    kt = threading.Thread(target=read_keys, daemon=True)
    kt.start()

    last_fall = time.time()

    while not game_over:
        fall_interval = max(0.1, 0.5 - (level-1)*0.04)

        k = get_key()

        if k == 'q':
            break
        elif k == 'a':
            if is_valid(piece, ox=-1): piece['x'] -= 1
        elif k == 'd':
            if is_valid(piece, ox=1):  piece['x'] += 1
        elif k == 'w':
            rot = rotate_shape(piece['shape'])
            if is_valid(piece, shape=rot): piece['shape'] = rot
        elif k == 's':
            if is_valid(piece, oy=1): piece['y'] += 1

        if time.time() - last_fall >= fall_interval:
            if is_valid(piece, oy=1):
                piece['y'] += 1
            else:
                place_piece(piece)
                clear_lines()
                piece  = next_p
                next_p = new_piece()
                if not is_valid(piece):
                    game_over = True
                    break
            last_fall = time.time()

        render(piece, next_p)
        time.sleep(0.03)

    sys.stdout.write(CLEAR)
    sys.stdout.write(f'\n  ★ GAME OVER ★\n  Skor: {score}   Level: {level}\n\n')
    sys.stdout.write(SHOW_CURSOR)
    sys.stdout.flush()


# ─────────────────────────────────────────
#  BAŞLAT
# ─────────────────────────────────────────
if __name__ == '__main__':
    run_game()