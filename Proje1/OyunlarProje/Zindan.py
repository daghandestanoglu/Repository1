#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║        KARANLIK ZINDAN  - Python Roguelike v3.0          ║
║              Modüler / Fonksiyon Tabanlı                  ║
╚══════════════════════════════════════════════════════════╝

KULLANIM (başka dosyadan):
    from dungeon_crawler import start_game
    start_game()

    # veya ayarlarla:
    from dungeon_crawler import start_game
    start_game(skip_menu=True, player_name="Ali", player_class="warrior")

    # veya direkt çalıştır:
    python dungeon_crawler.py
"""

import os, sys, random, math, heapq
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
from collections import deque

# ════════════════════════════════════════════════════════════
#  BÖLÜM 1 — TERMINAL ARAÇLARI
# ════════════════════════════════════════════════════════════

def terminal_clear():
    """Ekranı temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

def terminal_getch() -> str:
    """Enter gerektirmeden tek tuş okur (Windows + Unix)."""
    try:
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ('\x00', '\xe0'):          # ok tuşları
            ch2 = msvcrt.getwch()
            return {'H': 'w', 'P': 's', 'K': 'a', 'M': 'd'}.get(ch2, '')
        return ch
    except ImportError:
        import tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

# ANSI renk kodları
_ANSI = {
    'reset': '\033[0m', 'bold': '\033[1m', 'dim': '\033[2m',
    'red': '\033[91m',  'green': '\033[92m', 'yellow': '\033[93m',
    'blue': '\033[94m', 'magenta': '\033[95m', 'cyan': '\033[96m',
    'white': '\033[97m','gray': '\033[90m',
}

def colorize(text: str, *colors: str) -> str:
    """Metne ANSI renk uygular."""
    prefix = ''.join(_ANSI.get(c, '') for c in colors)
    return f"{prefix}{text}{_ANSI['reset']}"

def progress_bar(val: int, mx: int, length: int, color: str) -> str:
    """Renkli [████░░] çubuğu üretir."""
    pct    = val / max(1, mx)
    filled = int(pct * length)
    body   = colorize('█' * filled, color) + colorize('░' * (length - filled), 'gray')
    return colorize('[', 'white') + body + colorize(']', 'white')

# ════════════════════════════════════════════════════════════
#  BÖLÜM 2 — SABITLER
# ════════════════════════════════════════════════════════════

MAP_W, MAP_H       = 60, 22
VIEW_W, VIEW_H     = 60, 22
MIN_ROOM, MAX_ROOM = 5, 11
MAX_DEPTH          = 10        # bu kattan sonra zafer ekranı

TILE_CHARS = {
    'wall': '#', 'floor': '.', 'corridor': ',',
    'door_closed': '+', 'door_open': "'",
    'stairs_down': '>', 'stairs_up': '<',
    'trap': '^', 'chest': '$', 'altar': '&',
}
TILE_COLORS = {
    'wall': 'gray',   'floor': 'white',  'corridor': 'gray',
    'door_closed': 'yellow', 'door_open': 'yellow',
    'stairs_down': 'cyan',   'stairs_up': 'cyan',
    'trap': 'red',    'chest': 'yellow', 'altar': 'magenta',
}

# ════════════════════════════════════════════════════════════
#  BÖLÜM 3 — VERİ YAPILARI
# ════════════════════════════════════════════════════════════

@dataclass
class Vec2:
    x: int
    y: int
    def __add__(self, o):       return Vec2(self.x + o.x, self.y + o.y)
    def __eq__(self, o):        return isinstance(o, Vec2) and self.x == o.x and self.y == o.y
    def __hash__(self):         return hash((self.x, self.y))
    def dist(self, o):          return math.sqrt((self.x-o.x)**2 + (self.y-o.y)**2)
    def manhattan(self, o):     return abs(self.x-o.x) + abs(self.y-o.y)
    def copy(self):             return Vec2(self.x, self.y)


@dataclass
class Tile:
    ttype:    str  = 'wall'
    explored: bool = False
    visible:  bool = False
    blocked:  bool = True
    opaque:   bool = True
    trap_id:  str  = ''

    @staticmethod
    def make_floor():    return Tile('floor',    blocked=False, opaque=False)
    @staticmethod
    def make_wall():     return Tile('wall',     blocked=True,  opaque=True)
    @staticmethod
    def make_corridor(): return Tile('corridor', blocked=False, opaque=False)


@dataclass
class Item:
    name:     str
    char:     str
    color:    str
    itype:    str          # weapon / armor / ring / amulet / potion / scroll / gold
    value:    int   = 10
    weight:   float = 1.0
    atk:      int   = 0
    defs:     int   = 0
    hp_b:     int   = 0
    mp_b:     int   = 0
    heal:     int   = 0
    mana:     int   = 0
    effect:   str   = ''
    desc:     str   = ''
    quantity: int   = 1
    cursed:   bool  = False
    enchant:  int   = 0

    def display(self) -> str:
        enchant_str = f'+{self.enchant}' if self.enchant > 0 else ''
        text = colorize(f'{self.char} {self.name}{enchant_str}', self.color)
        if self.cursed:
            text += colorize(' [Lanetli]', 'red')
        return text


@dataclass
class Monster:
    name:        str
    char:        str
    color:       str
    hp:          int
    max_hp:      int
    atk:         int
    defense:     int
    xp:          int
    gold_drop:   tuple = (0, 5)
    drop_table:  list  = field(default_factory=list)
    special:     str   = ''
    flee_pct:    float = 0.0
    resistances: list  = field(default_factory=list)
    pos:         Vec2  = field(default_factory=lambda: Vec2(0, 0))
    awake:       bool  = False
    visible:     bool  = False
    status:      dict  = field(default_factory=dict)   # effect -> turns_remaining
    special_cd:  int   = 0


@dataclass
class Room:
    x: int; y: int; w: int; h: int
    def center(self):     return Vec2(self.x + self.w//2, self.y + self.h//2)
    def random_pos(self): return Vec2(random.randint(self.x+1, self.x+self.w-2),
                                      random.randint(self.y+1, self.y+self.h-2))

# ════════════════════════════════════════════════════════════
#  BÖLÜM 4 — OYUN VERİTABANLARI (eşyalar, canavarlar, büyüler)
# ════════════════════════════════════════════════════════════

def _item(name, char, color, itype, **kw) -> Item:
    return Item(name=name, char=char, color=color, itype=itype, **kw)

ITEM_DB: Dict[str, Item] = {
    # ── Silahlar ──────────────────────────────────────────
    'dagger':       _item('Hançer',            ')', 'white',   'weapon', atk=3,  value=15,  weight=0.5),
    'short_sword':  _item('Kısa Kılıç',        ')', 'white',   'weapon', atk=5,  value=30),
    'long_sword':   _item('Uzun Kılıç',        ')', 'yellow',  'weapon', atk=8,  value=60,  weight=2.0),
    'great_sword':  _item('Büyük Kılıç',       ')', 'red',     'weapon', atk=14, value=120, weight=4.0, desc='Ağır ama güçlü'),
    'staff':        _item('Büyücü Asası',      '/', 'cyan',    'weapon', atk=2,  mp_b=20,  value=80),
    'fire_staff':   _item('Ateş Asası',        '/', 'red',     'weapon', atk=4,  mp_b=30,  value=150, effect='cast_fire'),
    'bow':          _item('Yay',               '}', 'yellow',  'weapon', atk=7,  value=80),
    # ── Zırhlar ───────────────────────────────────────────
    'leather':      _item('Deri Zırh',         '[', 'yellow',  'armor',  defs=2, value=20,  weight=2.0),
    'chain_mail':   _item('Zincir Zırh',       '[', 'white',   'armor',  defs=5, value=60,  weight=4.0),
    'plate_mail':   _item('Plaka Zırh',        '[', 'cyan',    'armor',  defs=9, value=150, weight=7.0),
    'robe':         _item('Büyücü Cübbesi',    '[', 'magenta', 'armor',  defs=1, mp_b=15,  value=50),
    'shadow_cloak': _item('Gölge Pelerini',    '[', 'blue',    'armor',  defs=3, value=90,  weight=0.5),
    'dragon_scale': _item('Ejder Pulu Zırhı',  '[', 'red',     'armor',  defs=14, value=500, desc='Efsanevi'),
    # ── İksirler ──────────────────────────────────────────
    'hp_potion':    _item('Sağlık İksiri',     '!', 'red',     'potion', heal=25, value=20, weight=0.2),
    'big_hp_pot':   _item('Büyük Sağlık İksiri','!','red',     'potion', heal=60, value=50),
    'mp_potion':    _item('Mana İksiri',       '!', 'blue',    'potion', mana=20, value=20, weight=0.2),
    'antidote':     _item('Panzehir',          '!', 'green',   'potion', effect='cure_poison', value=25),
    'str_pot':      _item('Güç İksiri',        '!', 'yellow',  'potion', effect='strength',    value=40),
    'invis_pot':    _item('Görünmezlik İksiri', '!','white',   'potion', effect='invisible',   value=60),
    # ── Tomarlar ──────────────────────────────────────────
    'scroll_tp':    _item('Işınlanma Tomarı',  '?', 'white',   'scroll', effect='teleport',    value=30),
    'scroll_map':   _item('Harita Tomarı',     '?', 'cyan',    'scroll', effect='reveal_map',  value=40),
    'scroll_fire':  _item('Ateş Tomarı',       '?', 'red',     'scroll', effect='mass_fire',   value=50),
    # ── Yüzük & Kolye ─────────────────────────────────────
    'ring_regen':   _item('Yenilenme Yüzüğü',  '=', 'green',   'ring',   effect='regen', hp_b=5, value=120),
    'ring_protect': _item('Koruma Yüzüğü',     '=', 'blue',    'ring',   defs=3, value=100),
    'amulet_mana':  _item('Mana Kolyesi',      '"', 'cyan',    'amulet', mp_b=25, value=150),
    'amulet_life':  _item('Hayat Kolyesi',     '"', 'red',     'amulet', hp_b=20, value=180),
    # ── Altın ─────────────────────────────────────────────
    'gold':         _item('Altın',             '$', 'yellow',  'gold',   value=1, weight=0.01),
}

def item_copy(key: str) -> Item:
    """ITEM_DB'den derin kopya döndürür."""
    import copy
    return copy.deepcopy(ITEM_DB[key])


def _mon(name, char, color, hp, atk, df, xp, **kw) -> Monster:
    return Monster(name=name, char=char, color=color,
                   hp=hp, max_hp=hp, atk=atk, defense=df, xp=xp, **kw)

MONSTER_DB: Dict[str, Monster] = {
    'rat':       _mon('Sıçan',         'r', 'yellow',  8,  3,  0,   5,  gold_drop=(0,3)),
    'kobold':    _mon('Kobold',         'k', 'green',  12,  5,  1,  10,  drop_table=['dagger']),
    'goblin':    _mon('Goblin',         'g', 'green',  18,  7,  2,  15,  gold_drop=(2,8),  drop_table=['dagger','hp_potion']),
    'skeleton':  _mon('İskelet',        's', 'white',  22,  8,  3,  20,  resistances=['poison']),
    'zombie':    _mon('Zombi',          'z', 'green',  30,  9,  2,  25,  drop_table=['hp_potion'], special='infect'),
    'orc':       _mon('Ork',            'o', 'red',    35, 12,  4,  35,  gold_drop=(3,12), drop_table=['short_sword','leather']),
    'troll':     _mon('Trol',           'T', 'green',  55, 15,  6,  60,  gold_drop=(5,20), special='regen', flee_pct=0.15),
    'dark_elf':  _mon('Karanlık Elf',   'e', 'magenta',40, 16,  5,  70,  drop_table=['shadow_cloak'], special='backstab'),
    'mage_npc':  _mon('Kötü Büyücü',   'm', 'cyan',   35, 18,  3,  80,  drop_table=['mp_potion'], special='fireball'),
    'vampire':   _mon('Vampir',         'V', 'red',    65, 20,  7, 120,  gold_drop=(10,30), special='drain', resistances=['poison']),
    'spider':    _mon('Dev Örümcek',    'S', 'yellow', 25, 10,  2,  40,  drop_table=['antidote'], special='poison_bite'),
    'golem':     _mon('Taş Golem',      'G', 'white',  80, 22, 15, 200,  resistances=['poison','ice','fire']),
    'dragon':    _mon('Ejderha',        'D', 'red',   120, 28, 12, 300,  gold_drop=(30,80), drop_table=['dragon_scale'], special='fire_breath', resistances=['fire']),
    'lich':      _mon('Lich',           'L', 'magenta',100, 25, 10, 400, gold_drop=(20,60), drop_table=['amulet_mana'], special='life_drain',  resistances=['poison','ice']),
}

SPELL_DB: Dict[str, tuple] = {
    # id: (görünen_ad, mana_maliyeti, hasar, tür, alan_yarıçapı, açıklama)
    'fireball':    ('Ateş Topu',      8,  20, 'fire',   2, 'Alan ateş hasarı'),
    'ice_bolt':    ('Buz Oku',        5,  14, 'ice',    0, 'Tek hedef, dondurur'),
    'blizzard':    ('Blizzard',      12,  30, 'ice',    4, 'Geniş alan buz'),
    'chain_light': ('Zincir Şimşek', 10,  22, 'fire',   1, 'Zincirleme şimşek'),
    'holy_smite':  ('Kutsal Darbe',   6,  18, 'holy',   0, 'Kutsal hasar'),
    'backstab':    ('Sırttan Vur',    3,  25, 'phys',   0, 'Kritik hasar'),
    'poison_dart': ('Zehir Oku',      4,   8, 'poison', 0, 'Zehirler'),
    'shadow_step': ('Gölge Adım',     5,   0, 'none',   0, 'Görünmez 8 tur'),
}

# ════════════════════════════════════════════════════════════
#  BÖLÜM 5 — OYUNCU
# ════════════════════════════════════════════════════════════

class Player:
    """Oyuncu durumunu ve hesaplanan özelliklerini tutar."""

    CLASS_STATS = {
        'warrior': (80, 20, 12, 6, 8,  ['holy_smite']),
        'mage':    (45, 80,  5, 2, 10, ['fireball', 'ice_bolt', 'blizzard', 'chain_light']),
        'rogue':   (60, 35, 10, 4, 9,  ['backstab', 'poison_dart', 'shadow_step']),
    }
    CLASS_NAMES = {'warrior': 'Savaşçı', 'mage': 'Büyücü', 'rogue': 'Haydut'}
    CLASS_STARTERS = {
        'warrior': ('short_sword', 'leather'),
        'mage':    ('staff',       'robe'),
        'rogue':   ('dagger',      'shadow_cloak'),
    }
    LEVEL_GAINS = {
        'warrior': (12, 3, 2, 1),
        'mage':    (6, 12, 1, 0),
        'rogue':   (9,  5, 2, 1),
    }

    def __init__(self, name: str, cls: str):
        self.name = name
        self.cls  = cls
        mhp, mmp, batk, bdef, fov, spells = self.CLASS_STATS[cls]
        self.max_hp   = mhp;  self.max_mp  = mmp
        self.base_atk = batk; self.base_def = bdef
        self.fov_r    = fov
        self.hp = mhp; self.mp = mmp
        self.level   = 1;  self.xp = 0; self.xp_next = 100
        self.gold    = 0;  self.turns = 0; self.depth = 1; self.kills = 0
        self.pos     = Vec2(0, 0)
        self.hunger  = 800; self.hunger_max = 800
        self.equipment: Dict[str, Optional[Item]] = {
            'weapon': None, 'armor': None, 'ring': None, 'amulet': None
        }
        self.inventory: List[Item] = []
        self.max_carry = 26
        self.status: Dict[str, int] = {}   # effect_name -> turns_remaining
        self.spells: List[str] = list(spells)
        self._give_starters()

    def _give_starters(self):
        for key in self.CLASS_STARTERS[self.cls]:
            self._force_equip(item_copy(key))
        self.inventory += [item_copy('hp_potion'), item_copy('mp_potion')]

    def _force_equip(self, item: Item):
        """Envantere bakmadan direkt giydirir (başlangıç için)."""
        slot = {'weapon': 'weapon', 'armor': 'armor',
                'ring': 'ring', 'amulet': 'amulet'}.get(item.itype)
        if slot:
            if self.equipment[slot]:
                self.inventory.append(self.equipment[slot])
            self.equipment[slot] = item
        else:
            self.inventory.append(item)

    # ── Hesaplanan özellikler ─────────────────────────────
    @property
    def atk(self) -> int:
        w = self.equipment['weapon']
        return self.base_atk + self.level + (w.atk + w.enchant if w else 0)

    @property
    def defense(self) -> int:
        a = self.equipment['armor']
        r = self.equipment['ring']
        return self.base_def + (a.defs + a.enchant if a else 0) + (r.defs if r else 0)

    @property
    def total_max_hp(self) -> int:
        am = self.equipment['amulet']
        r  = self.equipment['ring']
        return self.max_hp + (am.hp_b if am else 0) + (r.hp_b if r else 0)

    @property
    def total_max_mp(self) -> int:
        w  = self.equipment['weapon']
        am = self.equipment['amulet']
        return self.max_mp + (w.mp_b if w else 0) + (am.mp_b if am else 0)

    # ── Durum efektleri ───────────────────────────────────
    def has_status(self, effect: str) -> bool:
        return self.status.get(effect, 0) > 0

    def add_status(self, effect: str, duration: int):
        self.status[effect] = max(self.status.get(effect, 0), duration)

    # ── Seviye atlama ─────────────────────────────────────
    def gain_xp(self, amount: int) -> List[str]:
        messages = []
        self.xp += amount
        while self.xp >= self.xp_next:
            self.xp      -= self.xp_next
            self.level   += 1
            self.xp_next  = int(self.xp_next * 1.5)
            dh, dm, da, dd = self.LEVEL_GAINS[self.cls]
            self.max_hp  += dh; self.max_mp  += dm
            self.base_atk += da; self.base_def += dd
            self.hp = self.total_max_hp
            self.mp = self.total_max_mp
            messages.append(colorize(f'★ SEVİYE ATLADIN! Seviye {self.level}! ★', 'yellow', 'bold'))
        return messages

# ════════════════════════════════════════════════════════════
#  BÖLÜM 6 — ZINDAN ÜRETİMİ (BSP)
# ════════════════════════════════════════════════════════════

class _BSPNode:
    def __init__(self, x, y, w, h):
        self.rect = (x, y, w, h)
        self.left = self.right = self.room = None

    def split(self, min_size=10):
        x, y, w, h = self.rect
        if w < min_size*2 and h < min_size*2:
            return
        horiz = (random.random() < h/(w+h)) if w != h else (random.random() < 0.5)
        if horiz:
            if h < min_size*2: return
            sp = random.randint(min_size, h - min_size)
            self.left  = _BSPNode(x, y,    w, sp)
            self.right = _BSPNode(x, y+sp, w, h-sp)
        else:
            if w < min_size*2: return
            sp = random.randint(min_size, w - min_size)
            self.left  = _BSPNode(x,    y, sp, h)
            self.right = _BSPNode(x+sp, y, w-sp, h)
        self.left.split(min_size)
        self.right.split(min_size)

    def create_rooms(self, rooms: list):
        if self.left or self.right:
            if self.left:  self.left.create_rooms(rooms)
            if self.right: self.right.create_rooms(rooms)
        else:
            x, y, w, h = self.rect
            rw = random.randint(MIN_ROOM, min(MAX_ROOM, w-2))
            rh = random.randint(MIN_ROOM, min(MAX_ROOM, h-2))
            rx = random.randint(x+1, x+w-rw-1)
            ry = random.randint(y+1, y+h-rh-1)
            self.room = Room(rx, ry, rw, rh)
            rooms.append(self.room)

    def get_room(self) -> Optional[Room]:
        if self.room: return self.room
        lr = self.left.get_room()  if self.left  else None
        rr = self.right.get_room() if self.right else None
        if not lr: return rr
        if not rr: return lr
        return lr if random.random() < 0.5 else rr

    def connect_corridors(self, tiles):
        if self.left and self.right:
            self.left.connect_corridors(tiles)
            self.right.connect_corridors(tiles)
            lr = self.left.get_room()
            rr = self.right.get_room()
            if lr and rr:
                _carve_corridor(lr.center(), rr.center(), tiles)


def _carve_corridor(a: Vec2, b: Vec2, tiles):
    x, y = a.x, a.y
    while x != b.x:
        _set_corridor_tile(x, y, tiles)
        x += 1 if b.x > x else -1
    while y != b.y:
        _set_corridor_tile(x, y, tiles)
        y += 1 if b.y > y else -1
    _set_corridor_tile(x, y, tiles)


def _set_corridor_tile(x, y, tiles):
    if 0 < x < MAP_W-1 and 0 < y < MAP_H-1 and tiles[y][x].ttype == 'wall':
        tiles[y][x] = Tile.make_corridor()


class DungeonLevel:
    """Tek bir zindan katını üretir ve yönetir."""

    def __init__(self, depth: int):
        self.depth  = depth
        self.tiles: List[List[Tile]] = [[Tile() for _ in range(MAP_W)] for _ in range(MAP_H)]
        self.rooms:           List[Room]            = []
        self.monsters:        List[Monster]         = []
        self.items_on_floor:  List[Tuple[Vec2,Item]]= []
        self.stairs_up   = Vec2(0, 0)
        self.stairs_down = Vec2(0, 0)
        self._generate()

    # ── Üretim ────────────────────────────────────────────
    def _generate(self):
        root = _BSPNode(0, 0, MAP_W, MAP_H)
        root.split(10)
        root.create_rooms(self.rooms)
        root.connect_corridors(self.tiles)
        for room in self.rooms:
            for y in range(room.y, room.y + room.h):
                for x in range(room.x, room.x + room.w):
                    if 0 <= x < MAP_W and 0 <= y < MAP_H:
                        self.tiles[y][x] = Tile.make_floor()
        # Merdivenler
        su = self.rooms[0].center()
        sd = self.rooms[-1].center()
        self.stairs_up   = su; self.stairs_down = sd
        self.tiles[su.y][su.x].ttype = 'stairs_up'
        self.tiles[sd.y][sd.x].ttype = 'stairs_down'
        self._place_doors()
        self._place_traps()
        self._place_items()
        self._place_monsters()
        self._place_specials()

    def _place_doors(self):
        for y in range(1, MAP_H-1):
            for x in range(1, MAP_W-1):
                t = self.tiles[y][x]
                if t.ttype != 'corridor' or random.random() >= 0.07:
                    continue
                walls = sum(1 for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]
                            if self.tiles[y+dy][x+dx].ttype == 'wall')
                if walls >= 2:
                    t.ttype = 'door_closed'; t.blocked = True; t.opaque = True

    def _place_traps(self):
        for room in self.rooms[1:]:
            if random.random() < 0.3:
                pos = room.random_pos()
                self.tiles[pos.y][pos.x].ttype   = 'trap'
                self.tiles[pos.y][pos.x].trap_id = random.choice(['pit','poison','fire','teleport'])

    def _place_items(self):
        d = self.depth
        for room in self.rooms[1:]:
            for _ in range(random.randint(0, 2)):
                pos = room.random_pos()
                if self._monster_at(pos): continue
                key = self._random_item_key(d)
                it  = item_copy(key)
                if it.itype == 'gold':
                    it.quantity = random.randint(1, int(10*(1+d*0.15)))
                    it.value    = it.quantity
                self.items_on_floor.append((pos, it))

    def _random_item_key(self, d: int) -> str:
        pool = {
            'hp_potion':4, 'mp_potion':2, 'antidote':1, 'gold':4,
            'dagger':1, 'short_sword':0.8, 'leather':0.8, 'bow':0.5,
            'scroll_tp':1, 'scroll_map':0.5, 'scroll_fire':0.5,
            'long_sword':   0.4 if d > 3 else 0,
            'chain_mail':   0.4 if d > 2 else 0,
            'great_sword':  0.2 if d > 5 else 0,
            'plate_mail':   0.2 if d > 4 else 0,
            'ring_regen':   0.3 if d > 2 else 0,
            'ring_protect': 0.3 if d > 2 else 0,
            'amulet_mana':  0.2 if d > 3 else 0,
            'amulet_life':  0.2 if d > 3 else 0,
            'big_hp_pot':   0.5 if d > 2 else 0,
            'fire_staff':   0.15 if d > 4 else 0,
            'dragon_scale': 0.05 if d > 8 else 0,
            'invis_pot': 0.3, 'str_pot': 0.3,
        }
        keys    = [k for k, v in pool.items() if v > 0]
        weights = [pool[k] for k in keys]
        return random.choices(keys, weights=weights)[0]

    def _place_monsters(self):
        import copy
        pool = self._monster_pool()
        for room in self.rooms[1:]:
            for _ in range(random.randint(0, 1 + self.depth//2)):
                pos = room.random_pos()
                if self._monster_at(pos): continue
                key = random.choice(pool)
                m   = copy.deepcopy(MONSTER_DB[key])
                m.pos = pos
                scale  = 1 + (self.depth - 1) * 0.12
                m.hp   = m.max_hp = max(1, int(m.max_hp * scale))
                m.atk  = max(1, int(m.atk * scale))
                m.xp   = int(m.xp * scale)
                self.monsters.append(m)

    def _monster_pool(self) -> List[str]:
        d = self.depth
        pool = ['rat', 'kobold', 'goblin']
        if d >= 2: pool += ['skeleton', 'zombie']
        if d >= 3: pool += ['orc', 'spider']
        if d >= 5: pool += ['troll', 'dark_elf', 'mage_npc']
        if d >= 7: pool += ['vampire', 'golem']
        if d >= 9: pool += ['dragon', 'lich']
        return pool

    def _place_specials(self):
        if len(self.rooms) > 3 and random.random() < 0.4:
            pos = random.choice(self.rooms[2:]).center()
            self.tiles[pos.y][pos.x].ttype = 'chest'
        if len(self.rooms) > 4 and random.random() < 0.3:
            pos = random.choice(self.rooms[2:]).center()
            self.tiles[pos.y][pos.x].ttype = 'altar'

    # ── Sorgular ──────────────────────────────────────────
    def _monster_at(self, pos: Vec2) -> bool:
        return any(m.pos == pos for m in self.monsters)

    def get_monster_at(self, pos: Vec2) -> Optional[Monster]:
        return next((m for m in self.monsters if m.pos == pos), None)

    def get_item_at(self, pos: Vec2) -> Optional[Tuple[int, Item]]:
        for i, (p, it) in enumerate(self.items_on_floor):
            if p == pos: return i, it
        return None

# ════════════════════════════════════════════════════════════
#  BÖLÜM 7 — FOV & PATHFINDING
# ════════════════════════════════════════════════════════════

def compute_fov(tiles: List[List[Tile]], origin: Vec2, radius: int):
    """Basit açısal ışın atma ile görüş alanını hesaplar."""
    for row in tiles:
        for t in row:
            t.visible = False
    tiles[origin.y][origin.x].visible  = True
    tiles[origin.y][origin.x].explored = True
    for angle in range(360):
        rad = math.radians(angle)
        dx, dy = math.cos(rad), math.sin(rad)
        x, y = float(origin.x), float(origin.y)
        for _ in range(radius):
            ix, iy = int(round(x)), int(round(y))
            if not (0 <= ix < MAP_W and 0 <= iy < MAP_H): break
            tiles[iy][ix].visible  = True
            tiles[iy][ix].explored = True
            if tiles[iy][ix].opaque and (ix != origin.x or iy != origin.y): break
            x += dx; y += dy


def pathfind(tiles: List[List[Tile]], start: Vec2, goal: Vec2, max_dist=18) -> List[Vec2]:
    """A* yol bulma. Engel olmayan karelerden geçen en kısa yolu döndürür."""
    if start == goal: return []
    open_set = [(0, (start.x, start.y))]
    came: Dict[tuple, tuple] = {}
    g: Dict[tuple, int] = {(start.x, start.y): 0}
    while open_set:
        _, cur = heapq.heappop(open_set)
        if cur == (goal.x, goal.y):
            path = []
            while cur in came:
                path.append(Vec2(*cur)); cur = came[cur]
            return list(reversed(path))
        cx, cy = cur
        for ddx, ddy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = cx+ddx, cy+ddy
            if not (0 <= nx < MAP_W and 0 <= ny < MAP_H): continue
            if tiles[ny][nx].blocked: continue
            ng = g[cur] + 1
            if ng > max_dist: continue
            nk = (nx, ny)
            if ng < g.get(nk, 99999):
                g[nk] = ng
                f = ng + abs(nx-goal.x) + abs(ny-goal.y)
                heapq.heappush(open_set, (f, nk))
                came[nk] = cur
    return []

# ════════════════════════════════════════════════════════════
#  BÖLÜM 8 — RENDERER (ekrana çizim)
# ════════════════════════════════════════════════════════════

def render_game(player: Player, dungeon: DungeonLevel, messages: deque):
    """Oyun ekranını baştan sona çizer."""
    terminal_clear()
    cn = Player.CLASS_NAMES
    hp_color = 'green' if player.hp / player.total_max_hp > 0.5 else 'red'
    hun_pct  = player.hunger / player.hunger_max
    hun_col  = 'green' if hun_pct > 0.6 else ('yellow' if hun_pct > 0.3 else 'red')
    hun_str  = 'Tok' if hun_pct > 0.6 else ('Aç' if hun_pct > 0.3 else 'ACIKTI!')
    w_item   = player.equipment['weapon']
    a_item   = player.equipment['armor']

    border = colorize('═' * 70, 'cyan')
    print(colorize('╔' + '═'*70 + '╗', 'cyan', 'bold'))

    # Satır 1: karakter bilgisi
    line1 = (colorize('║', 'cyan') +
             colorize(f' {player.name} [{cn[player.cls]}] Sv.{player.level}  ', 'bold', 'yellow') +
             progress_bar(player.hp, player.total_max_hp, 10, hp_color) +
             colorize(f' {player.hp}/{player.total_max_hp}HP  ', 'white') +
             progress_bar(player.mp, player.total_max_mp, 8, 'blue') +
             colorize(f' {player.mp}/{player.total_max_mp}MP  ', 'white') +
             colorize(hun_str, hun_col) +
             colorize(f'  ATK:{player.atk} DEF:{player.defense}  XP:{player.xp}/{player.xp_next}  ', 'white') +
             colorize(f'{player.gold}g  Kat:{player.depth}  Öl:{player.kills}', 'yellow') +
             colorize('  ║', 'cyan'))
    print(line1)

    # Satır 2: ekipman + durum efektleri
    wn  = colorize(w_item.name, 'yellow') if w_item else colorize('─', 'gray')
    an  = colorize(a_item.name, 'cyan')   if a_item else colorize('─', 'gray')
    sfx = colorize(' '.join(f'[{e}:{t}t]' for e, t in player.status.items() if t > 0), 'yellow') if player.status else ''
    print(colorize('║', 'cyan') +
          colorize(' Silah:', 'white') + wn +
          colorize('  Zırh:', 'white') + an +
          (colorize('  '+sfx, 'yellow') if sfx else '') +
          colorize('                                              ║', 'cyan'))

    print(colorize('╠' + '═'*70 + '╣', 'cyan'))

    # ── Harita ────────────────────────────────────────────
    vx = max(0, min(MAP_W - VIEW_W, player.pos.x - VIEW_W // 2))
    vy = max(0, min(MAP_H - VIEW_H, player.pos.y - VIEW_H // 2))
    for sy in range(VIEW_H):
        my = vy + sy
        if my >= MAP_H: break
        row = colorize('║', 'cyan')
        for sx in range(VIEW_W):
            mx = vx + sx
            if mx >= MAP_W: row += ' '; continue
            tile = dungeon.tiles[my][mx]
            pos  = Vec2(mx, my)
            if pos == player.pos:
                row += colorize('@', 'yellow', 'bold')
            elif not tile.explored:
                row += ' '
            else:
                mon = dungeon.get_monster_at(pos) if tile.visible else None
                if mon:
                    row += colorize(mon.char, mon.color, 'bold')
                else:
                    it = dungeon.get_item_at(pos)
                    if it and tile.visible:
                        _, item = it
                        row += colorize(item.char, item.color)
                    else:
                        ch = TILE_CHARS.get(tile.ttype, '?')
                        ck = TILE_COLORS.get(tile.ttype, 'white')
                        extras = ['dim'] if not tile.visible else []
                        row += colorize(ch, ck, *extras)
        row += colorize('║', 'cyan')
        print(row)

    # ── Mesajlar ──────────────────────────────────────────
    print(colorize('╠' + '═'*70 + '╣', 'cyan'))
    recent = list(messages)[-3:]
    while len(recent) < 3: recent.insert(0, ('', 'white'))
    for txt, ck in recent:
        print(colorize('║ ', 'cyan') +
              colorize(txt[:68].ljust(68), ck) +
              colorize(' ║', 'cyan'))
    print(colorize('╠' + '═'*70 + '╣', 'cyan'))
    print(colorize('║', 'cyan') +
          colorize(' w/a/s/d:Hareket  >:İn  <:Çık  i:Envanter  z:Büyüler  g:Topla  r:Dinlen  ?:Yardım  q:Çıkış', 'white') +
          colorize('   ║', 'cyan'))
    print(colorize('╚' + '═'*70 + '╝', 'cyan'))

# ════════════════════════════════════════════════════════════
#  BÖLÜM 9 — OYUN MANTIĞI (savaş, büyüler, AI, tuzaklar…)
# ════════════════════════════════════════════════════════════

def attack_monster(player: Player, monster: Monster,
                   dungeon: DungeonLevel, add_msg) -> bool:
    """
    Oyuncu canavarı vurur. Canavar ölürse True döner.
    add_msg(text, color) oyun mesaj kuyruğuna ekler.
    """
    dmg  = max(0, player.atk - monster.defense + random.randint(-2, 2))
    crit = random.random() < (0.15 if player.cls == 'rogue' else 0.05)
    if crit:
        dmg = int(dmg * 2)
        add_msg(colorize('KRİTİK!', 'yellow', 'bold'), 'yellow')
    if player.has_status('invisible'):
        dmg = int(dmg * 1.5)
        player.status.pop('invisible', None)
    monster.hp -= max(0, dmg)
    add_msg(f'{colorize(monster.name, monster.color)} → {dmg} hasar (HP:{monster.hp}/{monster.max_hp})', 'white')
    if monster.hp <= 0:
        kill_monster(player, monster, dungeon, add_msg)
        return True
    return False


def kill_monster(player: Player, monster: Monster,
                 dungeon: DungeonLevel, add_msg):
    """Canavarı öldürür, XP/altın/drop hesaplar."""
    dungeon.monsters.remove(monster)
    for msg in player.gain_xp(monster.xp):
        add_msg(msg, 'yellow')
    player.kills += 1
    lo, hi = monster.gold_drop
    gold = random.randint(lo, hi)
    if gold: player.gold += gold
    add_msg(f'{colorize(monster.name, monster.color)} öldürüldü!'
            f' +{monster.xp}XP' + (f' +{gold}g' if gold else ''), 'yellow')
    if monster.drop_table and random.random() < 0.35:
        it = item_copy(random.choice(monster.drop_table))
        dungeon.items_on_floor.append((monster.pos.copy(), it))
        add_msg(f'{colorize(monster.name, monster.color)} '
                f'{colorize(it.name, it.color)} bıraktı!', 'cyan')


def trigger_trap(player: Player, tile: Tile, pos: Vec2,
                 dungeon: DungeonLevel, add_msg,
                 teleport_fn):
    """Tuzağı tetikler."""
    tid = tile.trap_id
    tile.ttype   = 'floor'       # tuzak görünür hale gelsin
    tile.trap_id = ''
    add_msg(colorize(f'TUZAK! ({tid})', 'red', 'bold'), 'red')
    if tid == 'pit':
        d = random.randint(5, 15); player.hp -= d
        add_msg(f'Çukur! -{d} HP', 'red')
    elif tid == 'poison':
        player.add_status('poison', 8)
        add_msg('Zehirlendiniz!', 'green')
    elif tid == 'fire':
        d = random.randint(8, 20); player.hp -= d
        player.add_status('burn', 3)
        add_msg(f'Alev tuzağı! -{d} HP', 'red')
    elif tid == 'teleport':
        teleport_fn()


def teleport_random(player: Player, dungeon: DungeonLevel, add_msg):
    """Oyuncuyu rastgele boş bir kareye ışınlar."""
    for _ in range(300):
        rx = random.randint(1, MAP_W - 2)
        ry = random.randint(1, MAP_H - 2)
        if not dungeon.tiles[ry][rx].blocked and not dungeon.get_monster_at(Vec2(rx, ry)):
            player.pos = Vec2(rx, ry)
            add_msg('Işınlandınız!', 'cyan')
            return


def use_item(player: Player, item: Item, inv_slot,
             dungeon: DungeonLevel, add_msg, teleport_fn):
    """Bir eşyayı kullanır (iksir, tomar) veya giydirir (silah vb.)."""
    if item.itype in ('weapon', 'armor', 'ring', 'amulet'):
        equip_item(player, item, inv_slot, add_msg)
    elif item.itype == 'potion':
        use_potion(player, item, add_msg)
        _remove_from_inv(player, item)
    elif item.itype == 'scroll':
        use_scroll(player, item, dungeon, add_msg, teleport_fn)
        _remove_from_inv(player, item)


def equip_item(player: Player, item: Item, current_slot, add_msg):
    """Eşyayı giydirir ya da çıkarır."""
    slot_map = {'weapon': 'weapon', 'armor': 'armor',
                'ring':   'ring',   'amulet': 'amulet'}
    if current_slot:            # zaten giyili → çıkar
        if item.cursed:
            add_msg(colorize('Lanetli eşyayı çıkaramazsınız!', 'red'), 'red'); return
        player.equipment[current_slot] = None
        player.inventory.append(item)
        add_msg(f'{item.name} çıkarıldı.', 'white')
    else:                       # envanterden → giy
        sl = slot_map.get(item.itype)
        if not sl: return
        old = player.equipment[sl]
        if old: player.inventory.append(old)
        _remove_from_inv(player, item)
        player.equipment[sl] = item
        add_msg(f'{colorize(item.name, item.color)} giyildi.', 'cyan')
        if item.cursed:
            add_msg(colorize('LANETLİ! Çıkaramazsınız!', 'red', 'bold'), 'red')


def use_potion(player: Player, item: Item, add_msg):
    if item.heal:
        healed = min(item.heal, player.total_max_hp - player.hp)
        player.hp = min(player.total_max_hp, player.hp + item.heal)
        add_msg(f'{item.name} içildi. +{healed} HP', 'green')
    if item.mana:
        player.mp = min(player.total_max_mp, player.mp + item.mana)
        add_msg(f'{item.name} içildi. +{item.mana} MP', 'blue')
    eff = item.effect
    if   eff == 'cure_poison': player.status.pop('poison', None); add_msg('Zehir temizlendi!', 'green')
    elif eff == 'strength':    player.base_atk += 2;              add_msg('ATK+2!', 'yellow')
    elif eff == 'invisible':   player.add_status('invisible', 12); add_msg('Görünmez oldunuz!', 'white')
    player.hunger = min(player.hunger_max, player.hunger + 50)


def use_scroll(player: Player, item: Item, dungeon: DungeonLevel,
               add_msg, teleport_fn):
    eff = item.effect
    if eff == 'teleport':
        teleport_fn()
    elif eff == 'reveal_map':
        for row in dungeon.tiles:
            for t in row: t.explored = True
        add_msg('Harita açıldı!', 'cyan')
    elif eff == 'mass_fire':
        for mon in list(dungeon.monsters):
            if dungeon.tiles[mon.pos.y][mon.pos.x].visible:
                d = random.randint(15, 30); mon.hp -= d
                add_msg(f'Ateş! {mon.name} -{d} HP', 'red')
                if mon.hp <= 0:
                    kill_monster(player, mon, dungeon, add_msg)


def cast_spell(player: Player, spell_id: str,
               dungeon: DungeonLevel, add_msg):
    """Büyü döker."""
    if spell_id not in SPELL_DB: return
    name, mc, dmg, dtype, radius, _ = SPELL_DB[spell_id]
    if player.mp < mc:
        add_msg(f'Yeterli mana yok! ({mc} MP gerekli)', 'red'); return
    player.mp -= mc
    if spell_id == 'shadow_step':
        player.add_status('invisible', 8)
        add_msg('Gölgelere karıştınız! (8 tur)', 'white'); return
    targets = [m for m in dungeon.monsters
               if dungeon.tiles[m.pos.y][m.pos.x].visible]
    if not targets:
        add_msg('Görünürde düşman yok!', 'yellow'); return
    if radius > 0:
        hits = [m for m in targets if player.pos.dist(m.pos) <= radius + 8]
    else:
        hits = [min(targets, key=lambda m: player.pos.dist(m.pos))]
    for mon in hits:
        if dtype in mon.resistances:
            add_msg(f'{mon.name} {dtype} hasarına dirençli!', 'cyan'); continue
        d2 = max(0, dmg + random.randint(-3, 3) + player.level)
        mon.hp -= d2
        add_msg(f'{colorize(name,"cyan")} → {colorize(mon.name,mon.color)} -{d2} HP', 'cyan')
        if dtype == 'ice':    mon.status['freeze'] = max(mon.status.get('freeze', 0), 2)
        elif dtype == 'poison': mon.status['poison'] = max(mon.status.get('poison', 0), 5)
        elif dtype == 'fire':   mon.status['burn']   = max(mon.status.get('burn',   0), 3)
        if mon.hp <= 0:
            kill_monster(player, mon, dungeon, add_msg)


def tick_player_effects(player: Player, add_msg):
    """Oyuncunun durum efektlerini bir tur ilerletir."""
    for effect, dur in list(player.status.items()):
        if effect == 'poison': player.hp -= 1;  add_msg('Zehir! -1 HP', 'green')
        elif effect == 'burn': player.hp -= 3;  add_msg('Yanıyor! -3 HP', 'red')
        player.status[effect] = dur - 1
        if player.status[effect] <= 0:
            del player.status[effect]
            add_msg(f'{effect} etkisi bitti.', 'white')
    ring = player.equipment.get('ring')
    if ring and ring.effect == 'regen':
        player.hp = min(player.total_max_hp, player.hp + 1)


def run_monster_ai(player: Player, dungeon: DungeonLevel, add_msg):
    """Tüm canavarların AI turunu işler."""
    for mon in list(dungeon.monsters):
        if mon.hp <= 0: continue
        _tick_monster_status(mon, dungeon, add_msg)
        if mon.hp <= 0: continue
        if mon.status.get('freeze', 0) > 0: continue
        if mon.special == 'regen' and mon.hp < mon.max_hp:
            mon.hp = min(mon.max_hp, mon.hp + 2)
        if mon.pos.dist(player.pos) <= 10 or mon.awake:
            mon.awake = True
        if not mon.awake: continue
        # kaçış modu
        if mon.flee_pct > 0 and mon.hp / mon.max_hp < mon.flee_pct:
            _ai_flee(mon, player, dungeon); continue
        # bitişik → saldır
        if mon.pos.manhattan(player.pos) == 1:
            _monster_attack(mon, player, add_msg)
        else:
            # özel yetenek
            if mon.special and mon.special_cd == 0 and mon.pos.dist(player.pos) <= 7:
                if _monster_special(mon, player, add_msg):
                    mon.special_cd = 5; continue
            if mon.special_cd > 0: mon.special_cd -= 1
            # hareket
            path = pathfind(dungeon.tiles, mon.pos, player.pos, 20)
            if path:
                nxt = path[0]
                if not dungeon.get_monster_at(nxt) and nxt != player.pos:
                    mon.pos = nxt


def _tick_monster_status(mon: Monster, dungeon: DungeonLevel, add_msg):
    for effect, dur in list(mon.status.items()):
        if effect == 'poison': mon.hp -= 1
        elif effect == 'burn': mon.hp -= 3
        mon.status[effect] = dur - 1
        if mon.status[effect] <= 0:
            del mon.status[effect]
    if mon.hp <= 0 and mon in dungeon.monsters:
        dungeon.monsters.remove(mon)
        add_msg(f'{colorize(mon.name, mon.color)} durumdan öldü!', 'green')


def _ai_flee(mon: Monster, player: Player, dungeon: DungeonLevel):
    best = None; bd = mon.pos.dist(player.pos)
    for ddx, ddy in [(0,1),(0,-1),(1,0),(-1,0)]:
        nx, ny = mon.pos.x+ddx, mon.pos.y+ddy
        if not (0 <= nx < MAP_W and 0 <= ny < MAP_H): continue
        if dungeon.tiles[ny][nx].blocked: continue
        nd = Vec2(nx, ny).dist(player.pos)
        if nd > bd and not dungeon.get_monster_at(Vec2(nx, ny)):
            bd = nd; best = Vec2(nx, ny)
    if best: mon.pos = best


def _monster_attack(mon: Monster, player: Player, add_msg):
    if player.has_status('invisible'): return
    dmg = max(0, mon.atk - player.defense + random.randint(-2, 2))
    player.hp -= dmg
    add_msg(f'{colorize(mon.name, mon.color)} -{dmg} HP '
            f'(HP:{player.hp}/{player.total_max_hp})', 'red')


def _monster_special(mon: Monster, player: Player, add_msg) -> bool:
    s = mon.special
    if s == 'fireball':
        d = random.randint(12, 20); player.hp -= max(0, d - player.defense//2)
        add_msg(f'{colorize(mon.name,mon.color)} Ateş Topu! -{max(0,d-player.defense//2)} HP', 'red')
        return True
    if s == 'poison_bite':
        d = random.randint(5, 10); player.hp -= max(0, d - player.defense)
        player.add_status('poison', 6)
        add_msg(f'{colorize(mon.name,mon.color)} zehirli ısırdı!', 'green')
        return True
    if s == 'drain':
        dr = random.randint(8, 15); player.hp -= max(0, dr)
        mon.hp = min(mon.max_hp, mon.hp + dr//2)
        add_msg(f'{colorize(mon.name,mon.color)} can çekti! -{dr} HP', 'red')
        return True
    if s == 'fire_breath':
        d = random.randint(20, 35); player.hp -= max(0, d - player.defense)
        player.add_status('burn', 3)
        add_msg(colorize(f'{mon.name} ATEŞ NEFES! -{max(0,d-player.defense)} HP', 'red', 'bold'), 'red')
        return True
    if s == 'life_drain':
        player.max_hp = max(10, player.max_hp - 2)
        player.hp     = min(player.hp, player.max_hp)
        add_msg(f'{colorize(mon.name,mon.color)} max HP azalttı!', 'red')
        return True
    if s == 'infect' and random.random() < 0.25:
        player.add_status('poison', 4)
        add_msg(f'{colorize(mon.name,mon.color)} enfekte etti!', 'green')
        return True
    return False


def _remove_from_inv(player: Player, item: Item):
    if item in player.inventory:
        player.inventory.remove(item)

# ════════════════════════════════════════════════════════════
#  BÖLÜM 10 — UI EKRANLARI (menü, envanter, büyü, yardım)
# ════════════════════════════════════════════════════════════

def screen_main_menu() -> str:
    """Ana menüyü gösterir. 'new' veya 'quit' döner."""
    while True:
        terminal_clear()
        print(colorize('\n\n  ╔══════════════════════════════════════════╗', 'yellow', 'bold'))
        print(colorize(  '  ║        KARANLIK ZINDAN  v3.0             ║', 'yellow', 'bold'))
        print(colorize(  '  ║     Python Terminal Roguelike            ║', 'yellow', 'bold'))
        print(colorize(  '  ╚══════════════════════════════════════════╝\n', 'yellow', 'bold'))
        print(colorize(  '  [1] Yeni Oyun', 'cyan'))
        print(colorize(  '  [q] Çıkış\n', 'red'))
        k = terminal_getch()
        if k == '1':   return 'new'
        if k in 'qQ':  return 'quit'


def screen_char_select() -> Optional[Tuple[str, str]]:
    """
    Karakter seçim ekranı.
    Seçim yapılırsa (player_name, class_id) döner; iptal edilirse None.
    """
    classes = [
        ('warrior', 'Savaşçı', 'red',     'HP:80 MP:20 ATK:12 DEF:6', 'Kutsal Darbe, güçlü ve dayanıklı'),
        ('mage',    'Büyücü',  'cyan',    'HP:45 MP:80 ATK:5  DEF:2', 'Ateş Topu, Blizzard, Zincir Şimşek'),
        ('rogue',   'Haydut',  'green',   'HP:60 MP:35 ATK:10 DEF:4', 'Sırttan Vur, Gölge Adım, Zehir'),
    ]
    sel = 0
    while True:
        terminal_clear()
        print(colorize('\n  ── KARAKTERİNİZİ SEÇİN ──\n', 'yellow', 'bold'))
        for i, (cid, cname, ck, stats, desc) in enumerate(classes):
            marker = colorize('▶ ', 'yellow') if i == sel else '  '
            bold   = 'bold' if i == sel else ''
            print(colorize(f'{marker}[{i+1}] {cname}', ck, bold))
            print(colorize(f'       {stats}', 'white'))
            print(colorize(f'       {desc}\n', 'gray'))
        print(colorize('  1/2/3 seç   ENTER onayla   ESC geri\n', 'white'))
        k = terminal_getch()
        if k in ('1','2','3'):      sel = int(k) - 1
        if k in ('\r', '\n'):
            name = _prompt_name()
            if name: return name, classes[sel][0]
        if k == '\x1b':             return None


def _prompt_name() -> str:
    terminal_clear()
    print(colorize('\n  Karakter adını gir:\n', 'yellow', 'bold'))
    try:
        n = input(colorize('  > ', 'cyan')).strip()
        return n or random.choice(['Kahraman', 'Yiğit', 'Cesur'])
    except:
        return 'Kahraman'


def screen_inventory(player: Player, dungeon: DungeonLevel, add_msg):
    """
    Envanter ekranı.  Harf → kullan/giy,  d+harf → bırak,  ESC/i → kapat.
    """
    while True:
        terminal_clear()
        # Tüm eşyaları listele (giyili olanlar başta)
        inv_entries: List[Tuple[Item, Optional[str], bool]] = []
        for slot, it in player.equipment.items():
            if it: inv_entries.append((it, slot, True))
        for it in player.inventory:
            inv_entries.append((it, None, False))

        print(colorize('\n  ╔══ ENVANTER ══════════════════════════════════════════╗', 'yellow', 'bold'))
        for i, (it, slot, equipped) in enumerate(inv_entries):
            tag  = colorize(f'[{slot}]', 'cyan') if equipped else ''
            stat = ''
            if it.itype == 'weapon': stat = colorize(f' ATK+{it.atk}', 'white')
            elif it.itype == 'armor':  stat = colorize(f' DEF+{it.defs}', 'white')
            elif it.itype == 'potion':
                if it.heal: stat = colorize(f' +{it.heal}HP', 'green')
                elif it.mana: stat = colorize(f' +{it.mana}MP', 'blue')
            elif it.itype == 'gold': stat = colorize(f' x{it.quantity}', 'yellow')
            print(f'  {colorize(chr(ord("a")+i), "cyan")}) {it.display()}{stat} {tag} '
                  f'{colorize(str(it.value)+"g", "gray")}')
        tw = sum(it.weight for it in player.inventory)
        print(colorize(f'  ╠══ Altın:{player.gold}g  Ağırlık:{tw:.1f} ══════════════════════════╣', 'yellow'))
        print(colorize('  ║ Harf:kullan/giy  d+harf:bırak  ESC/i:kapat              ║', 'white'))
        print(colorize('  ╚═══════════════════════════════════════════════════════════╝', 'yellow'))

        k = terminal_getch()
        if k in ('\x1b', 'i'): break

        if k == 'd':
            k2  = terminal_getch()
            idx = ord(k2) - ord('a')
            if 0 <= idx < len(inv_entries):
                it, slot, equipped = inv_entries[idx]
                if equipped: player.equipment[slot] = None
                elif it in player.inventory: player.inventory.remove(it)
                dungeon.items_on_floor.append((player.pos.copy(), it))
                add_msg(f'{it.name} bırakıldı.', 'white')
            continue

        if 97 <= ord(k) <= 122:
            idx = ord(k) - 97
            if 0 <= idx < len(inv_entries):
                it, slot, equipped = inv_entries[idx]
                tp = lambda: teleport_random(player, dungeon, add_msg)
                use_item(player, it, slot if equipped else None, dungeon, add_msg, tp)


def screen_spell_menu(player: Player, dungeon: DungeonLevel, add_msg) -> bool:
    """
    Büyü menüsü.  Harf → dökmek.
    Büyü döküldüyse True, iptal edildiyse False döner.
    """
    terminal_clear()
    print(colorize('\n  ╔══ BÜYÜLER ═══════════════════════════════════════════╗', 'cyan', 'bold'))
    for i, sid in enumerate(player.spells):
        if sid not in SPELL_DB: continue
        name, mc, dmg, dtype, rad, desc = SPELL_DB[sid]
        ok = player.mp >= mc
        ck = 'cyan' if ok else 'red'
        print(colorize(f'  {chr(ord("a")+i)}) {name:<18} MP:{mc:<3} '
                       f'Hasar:{dmg:<4} {dtype:<8} {desc}', ck))
    print(colorize(f'\n  Mana: {player.mp}/{player.total_max_mp}   '
                   f'Harf:seç  ESC:iptal\n', 'blue'))
    print(colorize('  ╚═══════════════════════════════════════════════════════╝', 'cyan'))
    k = terminal_getch()
    if k == '\x1b': return False
    if 97 <= ord(k) <= 122:
        idx = ord(k) - 97
        if 0 <= idx < len(player.spells):
            cast_spell(player, player.spells[idx], dungeon, add_msg)
            return True
    return False


def screen_help():
    """Yardım ekranını gösterir."""
    terminal_clear()
    helps = [
        ('w/a/s/d', 'Hareket'),  ('.', 'Bekle (1 tur)'),
        ('>',       'Aşağı merdiven'), ('<', 'Yukarı merdiven'),
        ('g',       'Eşyayı topla'),   ('i', 'Envanter'),
        ('z',       'Büyü menüsü'),    ('r', 'Dinlen (HP/MP +1)'),
        ('q/x',     'Oyundan çık'),
    ]
    print(colorize('\n  ╔══ YARDIM ══════════════════════════════╗', 'yellow', 'bold'))
    for key, desc in helps:
        print(f'  {colorize(key.ljust(10), "cyan")} {colorize(desc, "white")}')
    print(colorize('  ╚════════════════════════════════════════╝\n', 'yellow'))
    print(colorize('  [Herhangi bir tuş] devam', 'gray'))
    terminal_getch()


def screen_game_over(player: Player):
    """Ölüm ekranı."""
    terminal_clear()
    print(colorize('\n\n  ╔══════════════════════════════╗', 'red', 'bold'))
    print(colorize(  '  ║          ÖLDÜN!              ║', 'red', 'bold'))
    print(colorize(  '  ╚══════════════════════════════╝\n', 'red', 'bold'))
    print(f'  {colorize(player.name, "white", "bold")} - '
          f'{colorize(player.cls.capitalize(), "cyan")} Seviye {player.level}')
    print(f'  Kat {player.depth}\'de hayatını kaybetti.')
    print(f'  {player.kills} düşman öldürüldü  •  {player.gold} altın  •  {player.turns} tur\n')
    print(colorize('  [Herhangi bir tuş] devam', 'white'))
    terminal_getch()


def screen_victory(player: Player):
    """Zafer ekranı."""
    terminal_clear()
    print(colorize('\n\n  ★═══════════════════════════★', 'yellow', 'bold'))
    print(colorize(  '  ★       KAZANDIN!           ★', 'yellow', 'bold'))
    print(colorize(  '  ★   Zindanı fethettın!      ★', 'yellow', 'bold'))
    print(colorize(  '  ★═══════════════════════════★\n', 'yellow', 'bold'))
    print(f'  Seviye:{player.level}  Öldürme:{player.kills}  '
          f'Altın:{player.gold}g  Tur:{player.turns}\n')
    print(colorize('  [Herhangi bir tuş] devam', 'white'))
    terminal_getch()

# ════════════════════════════════════════════════════════════
#  BÖLÜM 11 — ANA OYUN DÖNGÜSÜ
# ════════════════════════════════════════════════════════════

def _init_dungeon_level(player: Player, depth: int, cache: dict) -> DungeonLevel:
    """Önbellekten veya yeni oluşturarak zindan katını döndürür."""
    if depth not in cache:
        cache[depth] = DungeonLevel(depth)
    return cache[depth]


def _handle_move(player: Player, dx: int, dy: int,
                 dungeon: DungeonLevel, add_msg, teleport_fn) -> bool:
    """Hareket girişimi. Gerçekten hareket ettiyse True döner."""
    nx, ny = player.pos.x + dx, player.pos.y + dy
    if not (0 <= nx < MAP_W and 0 <= ny < MAP_H):
        return False
    tile = dungeon.tiles[ny][nx]
    # Kapı açma
    if tile.ttype == 'door_closed':
        tile.ttype = 'door_open'; tile.blocked = False; tile.opaque = False
        add_msg('Kapı açıldı.', 'yellow'); return True
    # Canavar saldırısı
    mon = dungeon.get_monster_at(Vec2(nx, ny))
    if mon:
        attack_monster(player, mon, dungeon, add_msg); return True
    # Duvar
    if tile.blocked: return False
    # Hareket
    player.pos = Vec2(nx, ny)
    # Tuzak kontrolü
    if tile.ttype == 'trap':
        trigger_trap(player, tile, player.pos, dungeon, add_msg, teleport_fn)
    # Eşya bildirimi
    it = dungeon.get_item_at(player.pos)
    if it:
        _, item = it
        if item.itype == 'gold':
            player.gold += item.quantity
            dungeon.items_on_floor.remove((player.pos, item))
            add_msg(f'{item.quantity} altın toplandı!', 'yellow')
        else:
            add_msg(f'Yerde: {colorize(item.name, item.color)} [g: topla]', 'white')
    return True


def _do_pickup(player: Player, dungeon: DungeonLevel, add_msg):
    it = dungeon.get_item_at(player.pos)
    if not it:
        add_msg('Burada bir şey yok.', 'white'); return
    idx, item = it
    if item.itype == 'gold':
        player.gold += item.quantity
        dungeon.items_on_floor.pop(idx)
        add_msg(f'{item.quantity} altın!', 'yellow'); return
    if len(player.inventory) >= player.max_carry:
        add_msg('Envanter dolu!', 'red'); return
    dungeon.items_on_floor.pop(idx)
    player.inventory.append(item)
    add_msg(f'{colorize(item.name, item.color)} toplandı.', 'white')


def _use_stairs(player: Player, dungeon_cache: dict,
                current_dungeon: DungeonLevel, going_down: bool,
                add_msg) -> Tuple[Optional[DungeonLevel], bool]:
    """
    Merdiven kullanır.
    Döner: (yeni_dungeon_ya_da_None, zafer_mi)
    """
    target = current_dungeon.stairs_down if going_down else current_dungeon.stairs_up
    if player.pos != target:
        add_msg('Merdivenin üzerinde değilsiniz!', 'red')
        return current_dungeon, False
    if going_down:
        player.depth += 1
        if player.depth > MAX_DEPTH:
            return None, True          # zafer!
        lvl = _init_dungeon_level(player, player.depth, dungeon_cache)
        player.pos = lvl.stairs_up.copy()
        add_msg(colorize(f'Kat {player.depth}\'e indинiz!', 'cyan'), 'cyan')
        return lvl, False
    else:
        if player.depth <= 1:
            add_msg('En üst kattasınız.', 'yellow')
            return current_dungeon, False
        player.depth -= 1
        lvl = _init_dungeon_level(player, player.depth, dungeon_cache)
        player.pos = lvl.stairs_down.copy()
        add_msg(f'Kat {player.depth}\'e çıktınız.', 'white')
        return lvl, False


def game_loop(player: Player) -> str:
    """
    Asıl oyun döngüsü.
    'dead', 'victory' veya 'quit' döner.
    """
    dungeon_cache: Dict[int, DungeonLevel] = {}
    dungeon = _init_dungeon_level(player, 1, dungeon_cache)
    player.pos = dungeon.stairs_up.copy()
    compute_fov(dungeon.tiles, player.pos, player.fov_r)

    messages: deque = deque(maxlen=200)

    def add_msg(text, color='white'):
        messages.append((text, color))

    def do_teleport():
        teleport_random(player, dungeon, add_msg)

    add_msg(f'Hoş geldin {player.name}! Zindana giriş.', 'yellow')
    add_msg('w/a/s/d hareket, ? yardım', 'cyan')

    direction_keys = {
        'w': (0,-1), 's': (0,1), 'a': (-1,0), 'd': (1,0),
    }

    while True:
        render_game(player, dungeon, messages)
        key = terminal_getch().lower()
        moved = False

        if key in direction_keys:
            dx, dy = direction_keys[key]
            moved = _handle_move(player, dx, dy, dungeon, add_msg, do_teleport)

        elif key == '.':
            add_msg('Bekliyorsunuz...', 'white'); moved = True

        elif key == '>':
            dungeon, victory = _use_stairs(player, dungeon_cache, dungeon, True, add_msg)
            if victory:
                screen_victory(player); return 'victory'
            compute_fov(dungeon.tiles, player.pos, player.fov_r)
            moved = True

        elif key == '<':
            dungeon, _ = _use_stairs(player, dungeon_cache, dungeon, False, add_msg)
            compute_fov(dungeon.tiles, player.pos, player.fov_r)
            moved = True

        elif key == 'g':
            _do_pickup(player, dungeon, add_msg); moved = True

        elif key == 'i':
            screen_inventory(player, dungeon, add_msg)

        elif key == 'z':
            used = screen_spell_menu(player, dungeon, add_msg)
            if used: moved = True

        elif key == 'r':
            if not player.has_status('poison') and not player.has_status('burn'):
                player.hp = min(player.total_max_hp, player.hp + 1)
            player.mp = min(player.total_max_mp, player.mp + 1)
            add_msg('Dinleniyorsunuz...', 'white'); moved = True

        elif key == '?':
            screen_help()

        elif key in ('q', 'x'):
            return 'quit'

        if moved:
            player.turns += 1
            player.hunger -= 1
            tick_player_effects(player, add_msg)
            run_monster_ai(player, dungeon, add_msg)
            compute_fov(dungeon.tiles, player.pos, player.fov_r)
            for mon in dungeon.monsters:
                mon.visible = dungeon.tiles[mon.pos.y][mon.pos.x].visible
            if player.hunger <= 0:
                player.hp -= 1; add_msg('Açlıktan ölüyorsunuz!', 'red')
            elif player.hunger % 100 == 0 and player.hunger < 300:
                add_msg('Çok acıktınız!', 'yellow')
            if player.hp <= 0:
                screen_game_over(player); return 'dead'

# ════════════════════════════════════════════════════════════
#  BÖLÜM 12 — GENEL GİRİŞ NOKTASI
# ════════════════════════════════════════════════════════════

def start_game(skip_menu: bool = False,
               player_name: str = '',
               player_class: str = '') -> str:
    """
    ╔═══════════════════════════════════════════════════════╗
    ║              GENEL GİRİŞ NOKTASI                      ║
    ╠═══════════════════════════════════════════════════════╣
    ║  Parametreler:                                        ║
    ║    skip_menu   – True ise ana menüyü atlar            ║
    ║    player_name – Boşsa oyuncudan alınır               ║
    ║    player_class– 'warrior' / 'mage' / 'rogue'        ║
    ║                  Boşsa seçim ekranı gösterilir        ║
    ╠═══════════════════════════════════════════════════════╣
    ║  Dönüş: 'dead' | 'victory' | 'quit'                  ║
    ╚═══════════════════════════════════════════════════════╝

    KULLANIM ÖRNEKLERİ
    ------------------
    # 1) Tam oyun (menülerle):
    from dungeon_crawler import start_game
    start_game()

    # 2) Menüsüz, hazır karakter:
    from dungeon_crawler import start_game
    result = start_game(skip_menu=True,
                        player_name='Arda',
                        player_class='mage')
    print(f'Oyun sonu: {result}')

    # 3) Menüsüz ama karakter seçimi isteniyor:
    from dungeon_crawler import start_game
    start_game(skip_menu=True)
    """
    while True:
        if not skip_menu:
            action = screen_main_menu()
            if action == 'quit':
                print(colorize('\nGörüşürüz, kahraman!', 'yellow')); return 'quit'

        # Karakter oluştur
        if player_name and player_class:
            name = player_name
            cls  = player_class
        else:
            result = screen_char_select()
            if not result:
                if skip_menu:
                    return 'quit'
                continue
            name, cls = result

        player = Player(name, cls)
        outcome = game_loop(player)

        if skip_menu:
            return outcome
        # Tam modda döngü devam eder (tekrar oyna)
        if outcome == 'quit':
            print(colorize('\nGörüşürüz, kahraman!', 'yellow')); return 'quit'
        # dead / victory → ana menüye dön


# ════════════════════════════════════════════════════════════
#  Direkt çalıştırma
# ════════════════════════════════════════════════════════════
if __name__ == '__main__':
    try:
        start_game()
    except KeyboardInterrupt:
        print(colorize('\n\nÇıkıldı.', 'yellow'))