#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║        KARANLIK ZINDAN  - Python Roguelike v2.0          ║
║   Sıfır bağımlılık  •  Her Python sürümünde çalışır      ║
╚══════════════════════════════════════════════════════════╝
Çalıştır:  python dungeon_crawler.py
Kontroller: w/a/s/d hareket, ? yardım
"""

import os, sys, random, math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
from collections import deque
import heapq

# ─── TERMINAL HELPERS ────────────────────────────────────
def clear():
    os.system('cls' if os.name=='nt' else 'clear')

def getch() -> str:
    try:
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ('\x00', '\xe0'):
            ch2 = msvcrt.getwch()
            return {'H':'w','P':'s','K':'a','M':'d'}.get(ch2, '')
        return ch
    except ImportError:
        import tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch

C = {
    'reset':'\033[0m','bold':'\033[1m','dim':'\033[2m',
    'red':'\033[91m','green':'\033[92m','yellow':'\033[93m',
    'blue':'\033[94m','magenta':'\033[95m','cyan':'\033[96m',
    'white':'\033[97m','gray':'\033[90m',
}

def col(text, *colors) -> str:
    prefix = ''.join(C.get(c,'') for c in colors)
    return f"{prefix}{text}{C['reset']}"

def bar(val, mx, length, color):
    pct = val / max(1, mx)
    filled = int(pct * length)
    b = col('█'*filled, color) + col('░'*(length-filled), 'gray')
    return col('[','white') + b + col(']','white')

# ─── CONSTANTS ───────────────────────────────────────────
MAP_W, MAP_H     = 60, 22
VIEW_W, VIEW_H   = 60, 22
MIN_ROOM, MAX_ROOM = 5, 11
MAX_DEPTH        = 10

# ─── VEC2 ────────────────────────────────────────────────
@dataclass
class Vec2:
    x: int; y: int
    def __add__(self,o): return Vec2(self.x+o.x,self.y+o.y)
    def __eq__(self,o):  return isinstance(o,Vec2) and self.x==o.x and self.y==o.y
    def __hash__(self):  return hash((self.x,self.y))
    def dist(self,o):    return math.sqrt((self.x-o.x)**2+(self.y-o.y)**2)
    def manhattan(self,o): return abs(self.x-o.x)+abs(self.y-o.y)
    def copy(self):      return Vec2(self.x,self.y)

# ─── TILE ────────────────────────────────────────────────
TILE_CH  = {'wall':'#','floor':'.','corridor':',','door_closed':'+','door_open':"'",
            'stairs_down':'>','stairs_up':'<','trap':'^','chest':'$','altar':'&'}
TILE_COL = {'wall':'gray','floor':'white','corridor':'gray','door_closed':'yellow',
            'door_open':'yellow','stairs_down':'cyan','stairs_up':'cyan',
            'trap':'red','chest':'yellow','altar':'magenta'}

@dataclass
class Tile:
    ttype:    str  = 'wall'
    explored: bool = False
    visible:  bool = False
    blocked:  bool = True
    opaque:   bool = True
    trap_id:  str  = ''

    @staticmethod
    def floor():   return Tile('floor',   blocked=False, opaque=False)
    @staticmethod
    def wall():    return Tile('wall',    blocked=True,  opaque=True)
    @staticmethod
    def corridor():return Tile('corridor',blocked=False, opaque=False)

# ─── BSP ─────────────────────────────────────────────────
@dataclass
class Room:
    x:int; y:int; w:int; h:int
    def center(self): return Vec2(self.x+self.w//2, self.y+self.h//2)
    def random_pos(self):
        return Vec2(random.randint(self.x+1,self.x+self.w-2),
                    random.randint(self.y+1,self.y+self.h-2))

class BSPNode:
    def __init__(self,x,y,w,h):
        self.rect=(x,y,w,h); self.left=self.right=None; self.room=None
    def split(self,ms=10):
        x,y,w,h=self.rect
        if w<ms*2 and h<ms*2: return
        horiz=random.random()<(h/(w+h)) if w!=h else random.random()<0.5
        if horiz:
            if h<ms*2: return
            sp=random.randint(ms,h-ms)
            self.left=BSPNode(x,y,w,sp); self.right=BSPNode(x,y+sp,w,h-sp)
        else:
            if w<ms*2: return
            sp=random.randint(ms,w-ms)
            self.left=BSPNode(x,y,sp,h); self.right=BSPNode(x+sp,y,w-sp,h)
        self.left.split(ms); self.right.split(ms)
    def create_rooms(self,rooms):
        if self.left or self.right:
            if self.left:  self.left.create_rooms(rooms)
            if self.right: self.right.create_rooms(rooms)
        else:
            x,y,w,h=self.rect
            rw=random.randint(MIN_ROOM,min(MAX_ROOM,w-2))
            rh=random.randint(MIN_ROOM,min(MAX_ROOM,h-2))
            rx=random.randint(x+1,x+w-rw-1)
            ry=random.randint(y+1,y+h-rh-1)
            self.room=Room(rx,ry,rw,rh); rooms.append(self.room)
    def get_room(self):
        if self.room: return self.room
        lr=self.left.get_room()  if self.left  else None
        rr=self.right.get_room() if self.right else None
        return (lr if rr is None else (rr if lr is None else (lr if random.random()<0.5 else rr)))
    def connect(self,tiles):
        if self.left and self.right:
            self.left.connect(tiles); self.right.connect(tiles)
            lr=self.left.get_room(); rr=self.right.get_room()
            if lr and rr: _carve(lr.center(),rr.center(),tiles)

def _carve(a,b,tiles):
    x,y=a.x,a.y
    while x!=b.x:
        _sc(x,y,tiles); x+=1 if b.x>x else -1
    while y!=b.y:
        _sc(x,y,tiles); y+=1 if b.y>y else -1
    _sc(x,y,tiles)

def _sc(x,y,tiles):
    if 0<x<MAP_W-1 and 0<y<MAP_H-1 and tiles[y][x].ttype=='wall':
        tiles[y][x]=Tile.corridor()

# ─── FOV ─────────────────────────────────────────────────
def compute_fov(tiles,origin,radius):
    for row in tiles:
        for t in row: t.visible=False
    tiles[origin.y][origin.x].visible=True
    tiles[origin.y][origin.x].explored=True
    for angle in range(360):
        rad=math.radians(angle)
        dx,dy=math.cos(rad),math.sin(rad)
        x,y=float(origin.x),float(origin.y)
        for _ in range(radius):
            ix,iy=int(round(x)),int(round(y))
            if not(0<=ix<MAP_W and 0<=iy<MAP_H): break
            tiles[iy][ix].visible=True; tiles[iy][ix].explored=True
            if tiles[iy][ix].opaque and (ix!=origin.x or iy!=origin.y): break
            x+=dx; y+=dy

# ─── A* ──────────────────────────────────────────────────
def astar(tiles,start,goal,max_d=18):
    if start==goal: return []
    open_set=[(0,(start.x,start.y))]; came={}; g={(start.x,start.y):0}
    while open_set:
        _,cur=heapq.heappop(open_set)
        if cur==(goal.x,goal.y):
            path=[]
            while cur in came: path.append(Vec2(*cur)); cur=came[cur]
            return list(reversed(path))
        cx,cy=cur
        for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx,ny=cx+dx,cy+dy
            if not(0<=nx<MAP_W and 0<=ny<MAP_H) or tiles[ny][nx].blocked: continue
            ng=g[cur]+1
            if ng>max_d: continue
            nk=(nx,ny)
            if ng<g.get(nk,9999):
                g[nk]=ng; f=ng+abs(nx-goal.x)+abs(ny-goal.y)
                heapq.heappush(open_set,(f,nk)); came[nk]=cur
    return []

# ─── ITEMS ───────────────────────────────────────────────
@dataclass
class Item:
    name:str; char:str; color:str; itype:str
    value:int=10; weight:float=1.0
    atk:int=0; defs:int=0; hp_b:int=0; mp_b:int=0
    heal:int=0; mana:int=0; effect:str=''
    desc:str=''; quantity:int=1; cursed:bool=False; enchant:int=0
    def display(self):
        e=f'+{self.enchant}' if self.enchant>0 else ''
        c=col(f'{self.char} {self.name}{e}',self.color)
        if self.cursed: c+=col(' [Lanetli]','red')
        return c

def _mi(name,char,color,itype,**kw): return Item(name=name,char=char,color=color,itype=itype,**kw)

ITEMS={
    'dagger':      _mi('Hançer',           ')','white', 'weapon',atk=3, value=15,weight=0.5,desc='Hafif'),
    'short_sword': _mi('Kısa Kılıç',       ')','white', 'weapon',atk=5, value=30),
    'long_sword':  _mi('Uzun Kılıç',       ')','yellow','weapon',atk=8, value=60,weight=2.0),
    'great_sword': _mi('Büyük Kılıç',      ')','red',   'weapon',atk=14,value=120,weight=4.0),
    'staff':       _mi('Büyücü Asası',     '/','cyan',  'weapon',atk=2, mp_b=20,value=80),
    'fire_staff':  _mi('Ateş Asası',       '/','red',   'weapon',atk=4, mp_b=30,value=150,effect='cast_fire'),
    'bow':         _mi('Yay',              '}','yellow','weapon',atk=7, value=80),
    'leather':     _mi('Deri Zırh',        '[','yellow','armor', defs=2,value=20,weight=2.0),
    'chain_mail':  _mi('Zincir Zırh',      '[','white', 'armor', defs=5,value=60,weight=4.0),
    'plate_mail':  _mi('Plaka Zırh',       '[','cyan',  'armor', defs=9,value=150,weight=7.0),
    'robe':        _mi('Büyücü Cübbesi',   '[','magenta','armor',defs=1,mp_b=15,value=50),
    'shadow_cloak':_mi('Gölge Pelerini',   '[','blue',  'armor', defs=3,value=90,weight=0.5),
    'dragon_scale':_mi('Ejder Pulu Zırhı', '[','red',   'armor', defs=14,value=500,desc='Efsanevi'),
    'hp_potion':   _mi('Sağlık İksiri',    '!','red',   'potion',heal=25,value=20,weight=0.2),
    'big_hp_pot':  _mi('Büyük Sağlık İksiri','!','red', 'potion',heal=60,value=50),
    'mp_potion':   _mi('Mana İksiri',      '!','blue',  'potion',mana=20,value=20,weight=0.2),
    'antidote':    _mi('Panzehir',          '!','green', 'potion',effect='cure_poison',value=25),
    'str_pot':     _mi('Güç İksiri',        '!','yellow','potion',effect='strength',value=40),
    'invis_pot':   _mi('Görünmezlik İksiri','!','white', 'potion',effect='invisible',value=60),
    'scroll_tp':   _mi('Işınlanma Tomarı',  '?','white', 'scroll',effect='teleport',value=30),
    'scroll_map':  _mi('Harita Tomarı',     '?','cyan',  'scroll',effect='reveal_map',value=40),
    'scroll_fire': _mi('Ateş Tomarı',       '?','red',   'scroll',effect='mass_fire',value=50),
    'ring_regen':  _mi('Yenilenme Yüzüğü',  '=','green', 'ring',  effect='regen',hp_b=5,value=120),
    'ring_protect':_mi('Koruma Yüzüğü',     '=','blue',  'ring',  defs=3,value=100),
    'amulet_mana': _mi('Mana Kolyesi',       '"','cyan',  'amulet',mp_b=25,value=150),
    'amulet_life': _mi('Hayat Kolyesi',      '"','red',   'amulet',hp_b=20,value=180),
    'gold':        _mi('Altın',              '$','yellow','gold',  value=1,weight=0.01),
}

def icp(key):
    import copy; return copy.deepcopy(ITEMS[key])

# ─── MONSTERS ────────────────────────────────────────────
@dataclass
class Monster:
    name:str; char:str; color:str
    hp:int; max_hp:int; atk:int; defense:int; xp:int
    gold_drop:tuple=(0,5); drop_table:list=field(default_factory=list)
    special:str=''; flee_pct:float=0.0; resistances:list=field(default_factory=list)
    pos:Vec2=field(default_factory=lambda:Vec2(0,0))
    awake:bool=False; visible:bool=False
    status:dict=field(default_factory=dict)
    special_cd:int=0

def _mm(name,char,color,hp,atk,df,xp,**kw):
    return Monster(name=name,char=char,color=color,hp=hp,max_hp=hp,atk=atk,defense=df,xp=xp,**kw)

MONSTERS={
    'rat':      _mm('Sıçan',      'r','yellow', 8, 3,0,5,  gold_drop=(0,3)),
    'kobold':   _mm('Kobold',     'k','green',  12,5,1,10, drop_table=['dagger']),
    'goblin':   _mm('Goblin',     'g','green',  18,7,2,15, gold_drop=(2,8),drop_table=['dagger','hp_potion']),
    'skeleton': _mm('İskelet',    's','white',  22,8,3,20, resistances=['poison']),
    'zombie':   _mm('Zombi',      'z','green',  30,9,2,25, drop_table=['hp_potion'],special='infect'),
    'orc':      _mm('Ork',        'o','red',    35,12,4,35,gold_drop=(3,12),drop_table=['short_sword','leather']),
    'troll':    _mm('Trol',       'T','green',  55,15,6,60,gold_drop=(5,20),special='regen',flee_pct=0.15),
    'dark_elf': _mm('Karanlık Elf','e','magenta',40,16,5,70,drop_table=['shadow_cloak'],special='backstab'),
    'mage_npc': _mm('Kötü Büyücü','m','cyan',   35,18,3,80,drop_table=['mp_potion'],special='fireball'),
    'vampire':  _mm('Vampir',     'V','red',    65,20,7,120,gold_drop=(10,30),special='drain',resistances=['poison']),
    'spider':   _mm('Dev Örümcek','S','yellow', 25,10,2,40, drop_table=['antidote'],special='poison_bite'),
    'golem':    _mm('Taş Golem',  'G','white',  80,22,15,200,resistances=['poison','ice','fire']),
    'dragon':   _mm('Ejderha',    'D','red',    120,28,12,300,gold_drop=(30,80),drop_table=['dragon_scale'],special='fire_breath',resistances=['fire']),
    'lich':     _mm('Lich',       'L','magenta',100,25,10,400,gold_drop=(20,60),drop_table=['amulet_mana'],special='life_drain',resistances=['poison','ice']),
}

SPELLS={
    'fireball':    ('Ateş Topu',    8,20,'fire',  2,'Alan ateş hasarı'),
    'ice_bolt':    ('Buz Oku',      5,14,'ice',   0,'Dondurur'),
    'blizzard':    ('Blizzard',    12,30,'ice',   4,'Geniş alan'),
    'chain_light': ('Zincir Şimşek',10,22,'fire', 1,'Zincirleme'),
    'holy_smite':  ('Kutsal Darbe', 6,18,'holy',  0,'Kutsal hasar'),
    'backstab':    ('Sırttan Vur',  3,25,'phys',  0,'Dev hasar'),
    'poison_dart': ('Zehir Oku',    4, 8,'poison',0,'Zehirler'),
    'shadow_step': ('Gölge Adım',   5, 0,'none',  0,'Görünmez 8 tur'),
}

# ─── PLAYER ──────────────────────────────────────────────
class Player:
    def __init__(self,name,cls):
        self.name=name; self.cls=cls
        self.level=1; self.xp=0; self.xp_next=100
        self.gold=0; self.turns=0; self.depth=1; self.kills=0
        self.pos=Vec2(0,0); self.hunger=800; self.hunger_max=800
        s={'warrior':(80,20,12,6,8),'mage':(45,80,5,2,10),'rogue':(60,35,10,4,9)}
        self.max_hp,self.max_mp,self.base_atk,self.base_def,self.fov_r=s[cls]
        self.hp=self.max_hp; self.mp=self.max_mp
        self.equipment={'weapon':None,'armor':None,'ring':None,'amulet':None}
        self.inventory:List[Item]=[]; self.max_carry=26
        self.status:dict={}
        sp={'warrior':['holy_smite'],'mage':['fireball','ice_bolt','blizzard','chain_light'],'rogue':['backstab','poison_dart','shadow_step']}
        self.spells=sp[cls]; self._give_starter()

    def _give_starter(self):
        s={'warrior':('short_sword','leather'),'mage':('staff','robe'),'rogue':('dagger','shadow_cloak')}
        for k in s[self.cls]: self._equip(icp(k))
        self.inventory+=[icp('hp_potion'),icp('mp_potion')]

    def _equip(self,item):
        sl={'weapon':'weapon','armor':'armor','ring':'ring','amulet':'amulet'}.get(item.itype)
        if sl:
            if self.equipment[sl]: self.inventory.append(self.equipment[sl])
            self.equipment[sl]=item
        else: self.inventory.append(item)

    @property
    def atk(self):
        b=self.base_atk+self.level; w=self.equipment['weapon']
        return b+(w.atk+w.enchant if w else 0)
    @property
    def defense(self):
        b=self.base_def; a=self.equipment['armor']; r=self.equipment['ring']
        return b+(a.defs+a.enchant if a else 0)+(r.defs if r else 0)
    @property
    def total_max_hp(self):
        b=self.max_hp; am=self.equipment['amulet']; r=self.equipment['ring']
        return b+(am.hp_b if am else 0)+(r.hp_b if r else 0)
    @property
    def total_max_mp(self):
        b=self.max_mp; w=self.equipment['weapon']; am=self.equipment['amulet']
        return b+(w.mp_b if w else 0)+(am.mp_b if am else 0)

    def has_status(self,e): return self.status.get(e,0)>0
    def add_status(self,e,d): self.status[e]=max(self.status.get(e,0),d)

    def gain_xp(self,amt):
        msgs=[]; self.xp+=amt
        while self.xp>=self.xp_next:
            self.xp-=self.xp_next; self.level+=1; self.xp_next=int(self.xp_next*1.5)
            g={'warrior':(12,3,2,1),'mage':(6,12,1,0),'rogue':(9,5,2,1)}
            dh,dm,da,dd=g[self.cls]
            self.max_hp+=dh; self.max_mp+=dm; self.base_atk+=da; self.base_def+=dd
            self.hp=self.total_max_hp; self.mp=self.total_max_mp
            msgs.append(col(f'★ SEVİYE ATLADIN! Seviye {self.level}! ★','yellow','bold'))
        return msgs

# ─── DUNGEON ─────────────────────────────────────────────
class DungeonLevel:
    def __init__(self,depth):
        self.depth=depth
        self.tiles=[[Tile() for _ in range(MAP_W)] for _ in range(MAP_H)]
        self.rooms:List[Room]=[]; self.monsters:List[Monster]=[]
        self.items_on_floor:List[Tuple[Vec2,Item]]=[]
        self.stairs_down=Vec2(0,0); self.stairs_up=Vec2(0,0)
        self._gen()

    def _gen(self):
        root=BSPNode(0,0,MAP_W,MAP_H); root.split(10)
        root.create_rooms(self.rooms); root.connect(self.tiles)
        for room in self.rooms:
            for y in range(room.y,room.y+room.h):
                for x in range(room.x,room.x+room.w):
                    if 0<=x<MAP_W and 0<=y<MAP_H: self.tiles[y][x]=Tile.floor()
        r0,rN=self.rooms[0],self.rooms[-1]
        su=r0.center(); sd=rN.center()
        self.stairs_up=su; self.stairs_down=sd
        self.tiles[su.y][su.x].ttype='stairs_up'
        self.tiles[sd.y][sd.x].ttype='stairs_down'
        self._doors(); self._traps(); self._items(); self._mons(); self._specials()

    def _doors(self):
        for y in range(1,MAP_H-1):
            for x in range(1,MAP_W-1):
                t=self.tiles[y][x]
                if t.ttype=='corridor' and random.random()<0.07:
                    walls=sum(1 for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)] if self.tiles[y+dy][x+dx].ttype=='wall')
                    if walls>=2: t.ttype='door_closed'; t.blocked=True; t.opaque=True

    def _traps(self):
        for room in self.rooms[1:]:
            if random.random()<0.3:
                pos=room.random_pos(); self.tiles[pos.y][pos.x].ttype='trap'
                self.tiles[pos.y][pos.x].trap_id=random.choice(['pit','poison','fire','teleport'])

    def _items(self):
        d=self.depth
        for room in self.rooms[1:]:
            for _ in range(random.randint(0,2)):
                pos=room.random_pos()
                if self._mat(pos): continue
                key=self._ri(d); it=icp(key)
                if it.itype=='gold': it.quantity=random.randint(1,int(10*(1+d*0.15))); it.value=it.quantity
                self.items_on_floor.append((pos,it))

    def _ri(self,d):
        pool={'hp_potion':4,'mp_potion':2,'antidote':1,'gold':4,'dagger':1,'short_sword':0.8,
              'leather':0.8,'bow':0.5,'scroll_tp':1,'scroll_map':0.5,'scroll_fire':0.5,
              'long_sword':0.4 if d>3 else 0,'chain_mail':0.4 if d>2 else 0,
              'great_sword':0.2 if d>5 else 0,'plate_mail':0.2 if d>4 else 0,
              'ring_regen':0.3 if d>2 else 0,'ring_protect':0.3 if d>2 else 0,
              'amulet_mana':0.2 if d>3 else 0,'amulet_life':0.2 if d>3 else 0,
              'big_hp_pot':0.5 if d>2 else 0,'fire_staff':0.15 if d>4 else 0,
              'dragon_scale':0.05 if d>8 else 0,'invis_pot':0.3,'str_pot':0.3}
        keys=[k for k,v in pool.items() if v>0]
        return random.choices(keys,weights=[pool[k] for k in keys])[0]

    def _mons(self):
        import copy; pool=self._mpool()
        for room in self.rooms[1:]:
            for _ in range(random.randint(0,1+self.depth//2)):
                pos=room.random_pos()
                if self._mat(pos): continue
                key=random.choice(pool); m=copy.deepcopy(MONSTERS[key]); m.pos=pos
                sc=1+(self.depth-1)*0.12
                m.hp=m.max_hp=max(1,int(m.max_hp*sc)); m.atk=max(1,int(m.atk*sc)); m.xp=int(m.xp*sc)
                self.monsters.append(m)

    def _mpool(self):
        d=self.depth; p=['rat','kobold','goblin']
        if d>=2: p+=['skeleton','zombie']
        if d>=3: p+=['orc','spider']
        if d>=5: p+=['troll','dark_elf','mage_npc']
        if d>=7: p+=['vampire','golem']
        if d>=9: p+=['dragon','lich']
        return p

    def _specials(self):
        if len(self.rooms)>3 and random.random()<0.4:
            pos=random.choice(self.rooms[2:]).center(); self.tiles[pos.y][pos.x].ttype='chest'
        if len(self.rooms)>4 and random.random()<0.3:
            pos=random.choice(self.rooms[2:]).center(); self.tiles[pos.y][pos.x].ttype='altar'

    def _mat(self,pos): return any(m.pos==pos for m in self.monsters)
    def get_monster_at(self,pos): return next((m for m in self.monsters if m.pos==pos),None)
    def get_item_at(self,pos):
        for i,(p,it) in enumerate(self.items_on_floor):
            if p==pos: return i,it
        return None

# ─── RENDERER ────────────────────────────────────────────
def render(p, d, messages):
    clear()
    cn={'warrior':'Savaşçı','mage':'Büyücü','rogue':'Haydut'}
    hp_c='green' if p.hp/p.total_max_hp>0.5 else 'red'
    hun_pct=p.hunger/p.hunger_max
    hun_c='green' if hun_pct>0.6 else ('yellow' if hun_pct>0.3 else 'red')
    hun_s='Tok' if hun_pct>0.6 else ('Aç' if hun_pct>0.3 else 'ACIKTI!')
    w=p.equipment['weapon']; a=p.equipment['armor']

    print(col('╔'+'═'*70+'╗','cyan','bold'))
    print(col('║','cyan') +
          col(f' {p.name} [{cn[p.cls]}] Sv.{p.level}  ','bold','yellow') +
          bar(p.hp,p.total_max_hp,10,hp_c) +
          col(f' {p.hp}/{p.total_max_hp}HP  ','white') +
          bar(p.mp,p.total_max_mp,8,'blue') +
          col(f' {p.mp}/{p.total_max_mp}MP  ','white') +
          col(f'{hun_s}  ',hun_c) +
          col(f'ATK:{p.atk} DEF:{p.defense}  XP:{p.xp}/{p.xp_next}  ','white') +
          col(f'{p.gold}g  Kat:{p.depth}','yellow') +
          col('  ║','cyan'))
    wn=col(w.name,'yellow') if w else col('─','gray')
    an=col(a.name,'cyan')   if a else col('─','gray')
    sfx=col(' '.join(f'[{e}:{t}t]' for e,t in p.status.items() if t>0),'yellow') if p.status else ''
    print(col('║','cyan') + col(f' Silah:','white') + wn + col('  Zırh:','white') + an +
          (col('  '+sfx,'yellow') if sfx else '') + col('                                          ║','cyan'))
    print(col('╠'+'═'*70+'╣','cyan'))

    # MAP
    vx=max(0,min(MAP_W-VIEW_W,p.pos.x-VIEW_W//2))
    vy=max(0,min(MAP_H-VIEW_H,p.pos.y-VIEW_H//2))
    for sy in range(VIEW_H):
        my=vy+sy
        if my>=MAP_H: break
        row=col('║','cyan')
        for sx in range(VIEW_W):
            mx=vx+sx
            if mx>=MAP_W: row+=' '; continue
            tile=d.tiles[my][mx]
            if Vec2(mx,my)==p.pos:
                row+=col('@','yellow','bold')
            elif not tile.explored:
                row+=' '
            else:
                mon=d.get_monster_at(Vec2(mx,my)) if tile.visible else None
                if mon and tile.visible:
                    row+=col(mon.char,mon.color,'bold')
                else:
                    it=d.get_item_at(Vec2(mx,my))
                    if it and tile.visible:
                        _,item=it; row+=col(item.char,item.color)
                    else:
                        ch=TILE_CH.get(tile.ttype,'?')
                        ck=TILE_COL.get(tile.ttype,'white')
                        row+=col(ch,ck,*(['dim'] if not tile.visible else []))
        row+=col('║','cyan')
        print(row)

    print(col('╠'+'═'*70+'╣','cyan'))
    recent=list(messages)[-3:]
    while len(recent)<3: recent.insert(0,('','white'))
    for txt,ck in recent:
        print(col('║ ','cyan') + col(txt[:68].ljust(68),ck) + col(' ║','cyan'))
    print(col('╠'+'═'*70+'╣','cyan'))
    print(col('║','cyan') + col(' w/a/s/d:Hareket  >:İn  <:Çık  i:Envanter  z:Büyüler  g:Topla  r:Dinlen  ?:Yardım  q:Çıkış','white') + col('  ║','cyan'))
    print(col('╚'+'═'*70+'╝','cyan'))

# ─── GAME ────────────────────────────────────────────────
class Game:
    def __init__(self):
        self.player=None; self.dungeon=None
        self.dungeon_cache={}; self.messages=deque(maxlen=200); self.running=True

    def msg(self,t,c='white'): self.messages.append((t,c))

    def run(self):
        self._main_menu()
        if not self.running: return
        while self.running:
            render(self.player,self.dungeon,self.messages)
            key=getch().lower()
            self._handle_key(key)
            if self.player and self.player.hp<=0: self._game_over(); return

    def _main_menu(self):
        while True:
            clear()
            print(col('\n\n  ╔══════════════════════════════════════════╗','yellow','bold'))
            print(col(  '  ║        KARANLIK ZINDAN  v2.0             ║','yellow','bold'))
            print(col(  '  ║     Python Terminal Roguelike            ║','yellow','bold'))
            print(col(  '  ╚══════════════════════════════════════════╝\n','yellow','bold'))
            print(col(  '  [1] Yeni Oyun','cyan'))
            print(col(  '  [q] Çıkış\n','red'))
            k=getch()
            if k=='1':
                p=self._char_select()
                if p: self.player=p; break
            elif k in ('q','Q'): self.running=False; return

    def _char_select(self):
        classes=[('warrior','Savaşçı','red',  'HP:80 MP:20 ATK:12 DEF:6','Kutsal Darbe, güçlü ve dayanıklı'),
                 ('mage',  'Büyücü', 'cyan',  'HP:45 MP:80 ATK:5  DEF:2','Ateş Topu, Blizzard, Zincir Şimşek'),
                 ('rogue', 'Haydut', 'green', 'HP:60 MP:35 ATK:10 DEF:4','Sırttan Vur, Gölge Adım, Zehir')]
        sel=0
        while True:
            clear()
            print(col('\n  ── KARAKTERİNİZİ SEÇİN ──\n','yellow','bold'))
            for i,(cid,cname,ck,stats,desc) in enumerate(classes):
                m=col('▶ ','yellow') if i==sel else '  '
                print(col(f'{m}[{i+1}] {cname}',ck,'bold' if i==sel else ''))
                print(col(f'       {stats}','white'))
                print(col(f'       {desc}\n','gray'))
            print(col('  1/2/3 seç   ENTER onayla   ESC geri\n','white'))
            k=getch()
            if k in ('1','2','3'): sel=int(k)-1
            if k in ('\r','\n'):
                name=self._get_name()
                if name:
                    p=Player(name,classes[sel][0]); self._init_dungeon(p); return p
            if k=='\x1b': return None

    def _get_name(self):
        clear(); print(col('\n  Karakter adını gir:\n','yellow','bold'))
        try:
            n=input(col('  > ','cyan')).strip()
            return n or random.choice(['Kahraman','Yiğit','Cesur'])
        except: return 'Kahraman'

    def _init_dungeon(self,p):
        lvl=DungeonLevel(1); self.dungeon_cache[1]=lvl; self.dungeon=lvl
        p.pos=lvl.stairs_up.copy(); compute_fov(lvl.tiles,p.pos,p.fov_r)
        self.msg(f'Hoş geldin {p.name}! Zindana giriş.','yellow')
        self.msg('w/a/s/d hareket, ? yardım','cyan')

    def _handle_key(self,key):
        p=self.player; moved=False
        dm={'w':(0,-1),'s':(0,1),'a':(-1,0),'d':(1,0)}
        if key in dm: self._try_move(*dm[key]); moved=True
        elif key=='.': self.msg('Bekliyorsunuz...'); moved=True
        elif key=='>': self._stairs(True); moved=True
        elif key=='<': self._stairs(False); moved=True
        elif key=='g': self._pick_up(); moved=True
        elif key=='i': self._inventory()
        elif key=='z': self._spell_menu(); moved=True
        elif key=='r': self._rest(); moved=True
        elif key=='?': self._help()
        elif key in ('x','q'): self.running=False; return
        if moved:
            p.turns+=1; p.hunger-=1
            self._tick()
            self._mons_turn()
            compute_fov(self.dungeon.tiles,p.pos,p.fov_r)
            for m in self.dungeon.monsters: m.visible=self.dungeon.tiles[m.pos.y][m.pos.x].visible
            if p.hunger<=0: p.hp-=1; self.msg('Açlıktan ölüyorsunuz!','red')
            elif p.hunger%100==0 and p.hunger<300: self.msg('Çok acıktınız!','yellow')

    def _try_move(self,dx,dy):
        p=self.player; d=self.dungeon
        nx,ny=p.pos.x+dx,p.pos.y+dy
        if not(0<=nx<MAP_W and 0<=ny<MAP_H): return
        tile=d.tiles[ny][nx]
        if tile.ttype=='door_closed':
            tile.ttype='door_open'; tile.blocked=False; tile.opaque=False
            self.msg('Kapı açıldı.','yellow'); return
        mon=d.get_monster_at(Vec2(nx,ny))
        if mon: self._attack(mon); return
        if tile.blocked: return
        p.pos=Vec2(nx,ny)
        if tile.ttype=='trap': self._trap(tile,Vec2(nx,ny))
        it=d.get_item_at(Vec2(nx,ny))
        if it:
            idx,item=it
            if item.itype=='gold':
                p.gold+=item.quantity; d.items_on_floor.pop(idx)
                self.msg(f'{item.quantity} altın toplandı!','yellow')
            else: self.msg(f'Yerde: {col(item.name,item.color)} [g: topla]')

    def _attack(self,mon):
        p=self.player
        dmg=max(0,p.atk-mon.defense+random.randint(-2,2))
        crit=random.random()<(0.15 if p.cls=='rogue' else 0.05)
        if crit: dmg=int(dmg*2); self.msg(col('KRİTİK!','yellow','bold'),'yellow')
        if p.has_status('invisible'): dmg=int(dmg*1.5); p.status.pop('invisible',None)
        mon.hp-=max(0,dmg)
        self.msg(f'{col(mon.name,mon.color)} → {dmg} hasar (HP:{mon.hp}/{mon.max_hp})')
        if mon.hp<=0: self._kill(mon)

    def _kill(self,mon):
        p=self.player; d=self.dungeon; d.monsters.remove(mon)
        [self.msg(m,'yellow') for m in p.gain_xp(mon.xp)]
        p.kills+=1
        lo,hi=mon.gold_drop; g=random.randint(lo,hi)
        if g: p.gold+=g
        self.msg(f'{col(mon.name,mon.color)} öldürüldü! +{mon.xp}XP'+(f' +{g}g' if g else ''),'yellow')
        if mon.drop_table and random.random()<0.35:
            item=icp(random.choice(mon.drop_table)); d.items_on_floor.append((mon.pos.copy(),item))
            self.msg(f'{col(mon.name,mon.color)} {col(item.name,item.color)} bıraktı!','cyan')

    def _trap(self,tile,pos):
        p=self.player; tid=tile.trap_id; tile.ttype='floor'
        self.msg(col(f'TUZAK! ({tid})','red','bold'),'red')
        if tid=='pit': d=random.randint(5,15); p.hp-=d; self.msg(f'Çukur! -{d}HP','red')
        elif tid=='poison': p.add_status('poison',8); self.msg('Zehirlendiniz!','green')
        elif tid=='fire': d=random.randint(8,20); p.hp-=d; p.add_status('burn',3); self.msg(f'Alev! -{d}HP','red')
        elif tid=='teleport': self._tp()

    def _tp(self):
        p=self.player; d=self.dungeon
        for _ in range(200):
            rx,ry=random.randint(1,MAP_W-2),random.randint(1,MAP_H-2)
            if not d.tiles[ry][rx].blocked and not d.get_monster_at(Vec2(rx,ry)):
                p.pos=Vec2(rx,ry); self.msg('Işınlandınız!','cyan'); return

    def _stairs(self,down):
        p=self.player; d=self.dungeon
        tgt=d.stairs_down if down else d.stairs_up
        if p.pos!=tgt: self.msg('Merdivenin üzerinde değilsiniz!','red'); return
        if down:
            p.depth+=1
            if p.depth>MAX_DEPTH: self._victory(); return
            if p.depth not in self.dungeon_cache: self.dungeon_cache[p.depth]=DungeonLevel(p.depth)
            self.dungeon=self.dungeon_cache[p.depth]; p.pos=self.dungeon.stairs_up.copy()
            self.msg(col(f'Kat {p.depth}\'e indинiz!','cyan'),'cyan')
        else:
            if p.depth<=1: self.msg('En üst kattasınız.','yellow'); return
            p.depth-=1
            if p.depth not in self.dungeon_cache: self.dungeon_cache[p.depth]=DungeonLevel(p.depth)
            self.dungeon=self.dungeon_cache[p.depth]; p.pos=self.dungeon.stairs_down.copy()
            self.msg(f'Kat {p.depth}\'e çıktınız.')
        compute_fov(self.dungeon.tiles,p.pos,p.fov_r)

    def _pick_up(self):
        p=self.player; d=self.dungeon; it=d.get_item_at(p.pos)
        if not it: self.msg('Burada bir şey yok.'); return
        idx,item=it
        if item.itype=='gold': p.gold+=item.quantity; d.items_on_floor.pop(idx); self.msg(f'{item.quantity} altın!','yellow'); return
        if len(p.inventory)>=p.max_carry: self.msg('Envanter dolu!','red'); return
        d.items_on_floor.pop(idx); p.inventory.append(item)
        self.msg(f'{col(item.name,item.color)} toplandı.')

    def _rest(self):
        p=self.player
        if not p.has_status('poison') and not p.has_status('burn'):
            p.hp=min(p.total_max_hp,p.hp+1)
        p.mp=min(p.total_max_mp,p.mp+1); self.msg('Dinleniyorsunuz...')

    def _inventory(self):
        p=self.player
        while True:
            clear()
            inv=[]
            for sl,item in p.equipment.items():
                if item: inv.append((item,sl,True))
            for item in p.inventory: inv.append((item,None,False))
            print(col('\n  ╔══ ENVANTER ════════════════════════════════════════╗','yellow','bold'))
            for i,(item,sl,eq) in enumerate(inv):
                tag=col(f'[{sl}]','cyan') if eq else ''
                st=''
                if item.itype=='weapon': st=col(f' ATK+{item.atk}','white')
                elif item.itype=='armor': st=col(f' DEF+{item.defs}','white')
                elif item.itype=='potion':
                    st=(col(f' +{item.heal}HP','green') if item.heal else '') or (col(f' +{item.mana}MP','blue') if item.mana else '')
                elif item.itype=='gold': st=col(f' x{item.quantity}','yellow')
                print(f'  {col(chr(ord("a")+i),"cyan")}) {item.display()}{st} {tag} {col(str(item.value)+"g","gray")}')
            tw=sum(i.weight for i in p.inventory)
            print(col(f'  ╠══ Altın:{p.gold}g  Ağırlık:{tw:.1f} ═══════════════════════╣','yellow'))
            print(col('  ║ Harf:kullan/giy  d+harf:bırak  ESC/i:kapat           ║','white'))
            print(col('  ╚═══════════════════════════════════════════════════════╝','yellow'))
            k=getch()
            if k in ('\x1b','i'): break
            if k=='d':
                k2=getch(); idx=ord(k2)-ord('a')
                if 0<=idx<len(inv):
                    item,sl,eq=inv[idx]
                    if eq: p.equipment[sl]=None
                    elif item in p.inventory: p.inventory.remove(item)
                    self.dungeon.items_on_floor.append((p.pos.copy(),item))
                    self.msg(f'{item.name} bırakıldı.')
                continue
            if 97<=ord(k)<=122:
                idx=ord(k)-97
                if 0<=idx<len(inv): self._use_equip(inv[idx])

    def _use_equip(self,entry):
        item,sl,eq=entry; p=self.player
        if item.itype in ('weapon','armor','ring','amulet'):
            if eq:
                if item.cursed: self.msg(col('Lanetli çıkaramazsınız!','red'),'red'); return
                p.equipment[sl]=None; p.inventory.append(item); self.msg(f'{item.name} çıkarıldı.')
            else:
                sm={'weapon':'weapon','armor':'armor','ring':'ring','amulet':'amulet'}
                sl2=sm.get(item.itype)
                if sl2:
                    old=p.equipment[sl2]
                    if old: p.inventory.append(old)
                    if item in p.inventory: p.inventory.remove(item)
                    p.equipment[sl2]=item; self.msg(f'{col(item.name,item.color)} giyildi.','cyan')
                    if item.cursed: self.msg(col('LANETLİ!','red','bold'),'red')
        elif item.itype=='potion':
            if item.heal: p.hp=min(p.total_max_hp,p.hp+item.heal); self.msg(f'+{item.heal}HP','green')
            if item.mana: p.mp=min(p.total_max_mp,p.mp+item.mana); self.msg(f'+{item.mana}MP','blue')
            e=item.effect
            if e=='cure_poison': p.status.pop('poison',None); self.msg('Zehir temizlendi!','green')
            elif e=='strength': p.base_atk+=2; self.msg('ATK+2!','yellow')
            elif e=='invisible': p.add_status('invisible',12); self.msg('Görünmez oldunuz!','white')
            if item in p.inventory: p.inventory.remove(item)
            p.hunger=min(p.hunger_max,p.hunger+50)
        elif item.itype=='scroll':
            e=item.effect
            if e=='teleport': self._tp()
            elif e=='reveal_map':
                for row in self.dungeon.tiles:
                    for t in row: t.explored=True
                self.msg('Harita açıldı!','cyan')
            elif e=='mass_fire':
                for m in list(self.dungeon.monsters):
                    if self.dungeon.tiles[m.pos.y][m.pos.x].visible:
                        d=random.randint(15,30); m.hp-=d; self.msg(f'Ateş! {m.name} -{d}HP','red')
                        if m.hp<=0: self._kill(m)
            if item in p.inventory: p.inventory.remove(item)

    def _spell_menu(self):
        p=self.player; clear()
        print(col('\n  ╔══ BÜYÜLER ═══════════════════════════════════════════╗','cyan','bold'))
        for i,sid in enumerate(p.spells):
            if sid not in SPELLS: continue
            name,mc,dmg,dtype,rad,desc=SPELLS[sid]
            ok=p.mp>=mc; ck='cyan' if ok else 'red'
            print(col(f'  {chr(ord("a")+i)}) {name:<18} MP:{mc:<3} Hasar:{dmg:<4} {dtype:<8} {desc}',ck))
        print(col(f'\n  Mana:{p.mp}/{p.total_max_mp}   Harf:seç  ESC:iptal\n','blue'))
        print(col('  ╚═══════════════════════════════════════════════════════╝','cyan'))
        k=getch()
        if k=='\x1b': return
        if 97<=ord(k)<=122:
            idx=ord(k)-97
            if 0<=idx<len(p.spells): self._cast(p.spells[idx])

    def _cast(self,sid):
        p=self.player; d=self.dungeon
        if sid not in SPELLS: return
        name,mc,dmg,dtype,rad,desc=SPELLS[sid]
        if p.mp<mc: self.msg(f'Yeterli mana yok! ({mc}MP)','red'); return
        p.mp-=mc
        if sid=='shadow_step': p.add_status('invisible',8); self.msg('Gölgelere karıştınız! (8 tur)','white'); return
        targets=[m for m in d.monsters if d.tiles[m.pos.y][m.pos.x].visible]
        if not targets: self.msg('Görünürde düşman yok!','yellow'); return
        hits=[m for m in targets if p.pos.dist(m.pos)<=rad+8] if rad>0 else [min(targets,key=lambda m:p.pos.dist(m.pos))]
        for mon in hits:
            if dtype in mon.resistances: self.msg(f'{mon.name} dirençli!','cyan'); continue
            d2=max(0,dmg+random.randint(-3,3)+p.level); mon.hp-=d2
            self.msg(f'{col(name,"cyan")} → {col(mon.name,mon.color)} -{d2}HP','cyan')
            if dtype=='ice': mon.status['freeze']=max(mon.status.get('freeze',0),2)
            elif dtype=='poison': mon.status['poison']=max(mon.status.get('poison',0),5)
            elif dtype=='fire': mon.status['burn']=max(mon.status.get('burn',0),3)
            if mon.hp<=0: self._kill(mon)

    def _mons_turn(self):
        p=self.player; d=self.dungeon
        for mon in list(d.monsters):
            if mon.hp<=0: continue
            for e,dur in list(mon.status.items()):
                if e=='poison': mon.hp-=1
                elif e=='burn': mon.hp-=3
                mon.status[e]=dur-1
                if mon.status[e]<=0: del mon.status[e]
            if mon.hp<=0: d.monsters.remove(mon); self.msg(f'{col(mon.name,mon.color)} durumdan öldü!','green'); continue
            if mon.status.get('freeze',0)>0: continue
            if mon.special=='regen' and mon.hp<mon.max_hp: mon.hp=min(mon.max_hp,mon.hp+2)
            if mon.pos.dist(p.pos)<=10 or mon.awake: mon.awake=True
            if not mon.awake: continue
            flee=mon.flee_pct>0 and mon.hp/mon.max_hp<mon.flee_pct
            if flee:
                best=None; bd=mon.pos.dist(p.pos)
                for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                    nx,ny=mon.pos.x+dx,mon.pos.y+dy
                    if 0<=nx<MAP_W and 0<=ny<MAP_H and not d.tiles[ny][nx].blocked:
                        nd=Vec2(nx,ny).dist(p.pos)
                        if nd>bd and not d.get_monster_at(Vec2(nx,ny)): bd=nd; best=Vec2(nx,ny)
                if best: mon.pos=best; continue
            if mon.pos.manhattan(p.pos)==1:
                if not p.has_status('invisible'):
                    dmg=max(0,mon.atk-p.defense+random.randint(-2,2)); p.hp-=dmg
                    self.msg(f'{col(mon.name,mon.color)} -{dmg}HP (HP:{p.hp}/{p.total_max_hp})','red')
            else:
                if mon.special and mon.special_cd==0 and mon.pos.dist(p.pos)<=7:
                    if self._mspecial(mon,p): mon.special_cd=5; continue
                if mon.special_cd>0: mon.special_cd-=1
                path=astar(d.tiles,mon.pos,p.pos,20)
                if path:
                    nxt=path[0]
                    if not d.get_monster_at(nxt) and nxt!=p.pos: mon.pos=nxt

    def _mspecial(self,mon,p):
        s=mon.special
        if s=='fireball':
            d=random.randint(12,20); p.hp-=max(0,d-p.defense//2)
            self.msg(f'{col(mon.name,mon.color)} Ateş Topu! -{max(0,d-p.defense//2)}HP','red'); return True
        if s=='poison_bite':
            d=random.randint(5,10); p.hp-=max(0,d-p.defense); p.add_status('poison',6)
            self.msg(f'{col(mon.name,mon.color)} zehirli ısırdı!','green'); return True
        if s=='drain':
            dr=random.randint(8,15); p.hp-=max(0,dr); mon.hp=min(mon.max_hp,mon.hp+dr//2)
            self.msg(f'{col(mon.name,mon.color)} can çekti! -{dr}HP','red'); return True
        if s=='fire_breath':
            d=random.randint(20,35); p.hp-=max(0,d-p.defense); p.add_status('burn',3)
            self.msg(col(f'{mon.name} ATEŞ NEFES! -{max(0,d-p.defense)}HP','red','bold'),'red'); return True
        if s=='life_drain':
            p.max_hp=max(10,p.max_hp-2); p.hp=min(p.hp,p.max_hp)
            self.msg(f'{col(mon.name,mon.color)} max HP azalttı!','red'); return True
        if s=='infect' and random.random()<0.25:
            p.add_status('poison',4); self.msg(f'{col(mon.name,mon.color)} enfekte etti!','green'); return True
        return False

    def _tick(self):
        p=self.player
        for e,dur in list(p.status.items()):
            if e=='poison': p.hp-=1; self.msg('Zehir! -1HP','green')
            elif e=='burn': p.hp-=3; self.msg('Yanıyor! -3HP','red')
            p.status[e]=dur-1
            if p.status[e]<=0: del p.status[e]; self.msg(f'{e} bitti.')
        r=p.equipment.get('ring')
        if r and r.effect=='regen': p.hp=min(p.total_max_hp,p.hp+1)

    def _game_over(self):
        clear(); p=self.player
        print(col('\n\n  ╔══════════════════════════════╗','red','bold'))
        print(col(  '  ║          ÖLDÜN!              ║','red','bold'))
        print(col(  '  ╚══════════════════════════════╝\n','red','bold'))
        print(f'  {col(p.name,"white","bold")} - {col(p.cls.capitalize(),"cyan")} Seviye {p.level}')
        print(f'  Kat {p.depth}\'de hayatını kaybetti.')
        print(f'  {p.kills} düşman öldürüldü  •  {p.gold} altın  •  {p.turns} tur\n')
        print(col('  [Enter] Çıkış','white')); getch()

    def _victory(self):
        clear(); p=self.player1
        print(col('\n\n  ★═══════════════════════════★','yellow','bold'))
        print(col(  '  ★       KAZANDIN!           ★','yellow','bold'))
        print(col(  '  ★   Zindanı fethettın!      ★','yellow','bold'))
        print(col(  '  ★═══════════════════════════★\n','yellow','bold'))
        print(f'  Seviye:{p.level}  Öldürme:{p.kills}  Altın:{p.gold}g  Tur:{p.turns}\n')
        print(col('  [Enter] Çıkış','white')); getch(); self.running=False

    def _help(self):
        clear()
        print(col('\n  ╔══ YARDIM ══════════════════════════════╗','yellow','bold'))
        for k,d in [('w/a/s/d','Hareket'),('.','Bekle'),('>','Aşağı merdiven'),('<','Yukarı merdiven'),
                    ('g','Eşyayı topla'),('i','Envanter'),('z','Büyü menüsü'),
                    ('r','Dinlen (HP/MP+1)'),('q','Çıkış')]:
            print(f'  {col(k.ljust(10),"cyan")} {col(d,"white")}')
        print(col('  ╚════════════════════════════════════════╝\n','yellow'))
        print(col('  [Herhangi bir tuş] devam','gray')); getch()

# ─── MAIN ─────────────────────────────────────────────────
if __name__=='__main__':
    try:
        Game().run()
    except KeyboardInterrupt:
        pass
    print(col('\nGörüşürüz, kahraman!','yellow'))