import sys
import os
import random
import time
import threading

if os.name == 'nt':
    import msvcrt
else:
    import tty
    import termios

# ─────────────────────────────────────────
#  SABİTLER
# ─────────────────────────────────────────
SW, SH = 30, 20  # oyun alanı genişlik / yükseklik

RESET       = '\033[0m'
CLEAR       = '\033[2J\033[H'
HIDE_CURSOR = '\033[?25l'
SHOW_CURSOR = '\033[?25h'

GREEN  = '\033[92m'
YELLOW = '\033[93m'
RED    = '\033[91m'
CYAN   = '\033[96m'
WHITE  = '\033[97m'

# ─────────────────────────────────────────
#  GLOBAL OYUN DURUMU
# ─────────────────────────────────────────
snake      = []
direction  = (1, 0)
food       = (0, 0)
sn_score   = 0
sn_over    = False
sn_key_buf = None
sn_lock    = threading.Lock()


# ─────────────────────────────────────────
#  YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────
def spawn_food():
    while True:
        pos = (random.randint(0, SW-1), random.randint(0, SH-1))
        if pos not in snake:
            return pos

def sn_get_key():
    global sn_key_buf
    with sn_lock:
        k, sn_key_buf = sn_key_buf, None
    return k


# ─────────────────────────────────────────
#  EKRAN ÇİZİMİ
# ─────────────────────────────────────────
def draw_snake():
    lines = []
    lines.append('┌' + '─'*SW + '┐')

    for y in range(SH):
        row = '│'
        for x in range(SW):
            pos = (x, y)
            if pos == snake[0]:
                row += GREEN + '◉' + RESET
            elif pos in snake[1:]:
                row += GREEN + '█' + RESET
            elif pos == food:
                row += YELLOW + '●' + RESET
            else:
                row += ' '
        row += '│'

        if   y == 0:  row += f'   SNAKE'
        elif y == 2:  row += f'   Skor : {sn_score}'
        elif y == 4:  row += '   W  yukarı'
        elif y == 5:  row += '   S  aşağı'
        elif y == 6:  row += '   A  sola'
        elif y == 7:  row += '   D  sağa'
        elif y == 8:  row += '   Q  çıkış'

        lines.append(row)

    lines.append('└' + '─'*SW + '┘')
    sys.stdout.write(CLEAR + '\n'.join(lines) + '\n')
    sys.stdout.flush()


# ─────────────────────────────────────────
#  KLAVYE OKUMA (ayrı thread)
# ─────────────────────────────────────────
def sn_read_keys():
    global sn_key_buf, sn_over

    if os.name == 'nt':
        while not sn_over:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ('\x00', '\xe0'):
                    ch2 = msvcrt.getwch()
                    mapping = {'H':'w','P':'s','K':'a','M':'d'}
                    k = mapping.get(ch2)
                else:
                    k = ch.lower()
                with sn_lock:
                    sn_key_buf = k
            time.sleep(0.02)
    else:
        fd  = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while not sn_over:
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    ch2 = sys.stdin.read(1)
                    ch3 = sys.stdin.read(1)
                    mapping = {'A':'w','B':'s','D':'a','C':'d'}
                    k = mapping.get(ch3)
                else:
                    k = ch.lower()
                with sn_lock:
                    sn_key_buf = k
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


# ─────────────────────────────────────────
#  ANA OYUN DÖNGÜSÜ
# ─────────────────────────────────────────
def run_snake():
    global snake, direction, food, sn_score, sn_over

    snake     = [(SW//2, SH//2), (SW//2-1, SH//2), (SW//2-2, SH//2)]
    direction = (1, 0)
    sn_score  = 0
    sn_over   = False
    food      = spawn_food()

    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()

    kt = threading.Thread(target=sn_read_keys, daemon=True)
    kt.start()

    speed     = 0.15
    last_move = time.time()

    while not sn_over:
        k = sn_get_key()

        if k == 'q':
            break
        elif k == 'w' and direction != (0, 1):
            direction = (0, -1)
        elif k == 's' and direction != (0, -1):
            direction = (0, 1)
        elif k == 'a' and direction != (1, 0):
            direction = (-1, 0)
        elif k == 'd' and direction != (-1, 0):
            direction = (1, 0)

        if time.time() - last_move >= speed:
            hx, hy = snake[0]
            dx, dy = direction
            new_head = (hx+dx, hy+dy)

            # Duvara çarpma
            if not (0 <= new_head[0] < SW and 0 <= new_head[1] < SH):
                sn_over = True
                break

            # Kendine çarpma
            if new_head in snake:
                sn_over = True
                break

            snake.insert(0, new_head)

            if new_head == food:
                sn_score += 10
                food  = spawn_food()
                speed = max(0.05, speed - 0.002)
            else:
                snake.pop()

            last_move = time.time()

        draw_snake()
        time.sleep(0.02)

    sys.stdout.write(CLEAR)
    sys.stdout.write(f'\n  ★ GAME OVER ★\n  Skor: {sn_score}   Uzunluk: {len(snake)}\n\n')
    sys.stdout.write(SHOW_CURSOR)
    sys.stdout.flush()


# ─────────────────────────────────────────
#  BAŞLAT
# ─────────────────────────────────────────
if __name__ == '__main__':
    run_snake()