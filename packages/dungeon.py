"""
dungeon.py - PenguWarp Repository Package
A roguelike dungeon crawler for PenguWarp OS
Install: pkgmgr install dungeon
"""

import curses
import random
import sys

# ── constants ─────────────────────────────────────────────────────────────────

VERSION = "1.0.0"

TILE_WALL    = "#"
TILE_FLOOR   = "."
TILE_STAIRS  = ">"
TILE_PLAYER  = "@"
TILE_ENEMY   = "E"
TILE_ITEM    = "!"
TILE_GOLD    = "$"
TILE_EMPTY   = " "

MAP_W, MAP_H = 60, 30
MIN_ROOMS, MAX_ROOMS = 6, 12
MIN_ROOM_SIZE, MAX_ROOM_SIZE = 4, 10

ENEMY_TYPES = [
    {"name": "Rat",     "hp": 5,  "atk": 2,  "xp": 5,  "char": "r"},
    {"name": "Goblin",  "hp": 10, "atk": 4,  "xp": 10, "char": "g"},
    {"name": "Orc",     "hp": 18, "atk": 7,  "xp": 20, "char": "O"},
    {"name": "Troll",   "hp": 30, "atk": 11, "xp": 40, "char": "T"},
    {"name": "Dragon",  "hp": 50, "atk": 18, "xp": 80, "char": "D"},
]

ITEM_TYPES = [
    {"name": "Health Potion", "type": "heal",   "value": 20, "char": "!"},
    {"name": "Sword",         "type": "weapon", "value": 5,  "char": "/"},
    {"name": "Shield",        "type": "armor",  "value": 3,  "char": "]"},
]

# ── map generation ─────────────────────────────────────────────────────────────

class Rect:
    def __init__(self, x, y, w, h):
        self.x1, self.y1 = x, y
        self.x2, self.y2 = x + w, y + h

    def center(self):
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    def intersects(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


def generate_map(floor_num):
    grid = [[TILE_WALL] * MAP_W for _ in range(MAP_H)]
    rooms = []

    num_rooms = random.randint(MIN_ROOMS, MAX_ROOMS)

    for _ in range(num_rooms * 5):  # try many times to place rooms
        if len(rooms) >= num_rooms:
            break
        w = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
        h = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
        x = random.randint(1, MAP_W - w - 2)
        y = random.randint(1, MAP_H - h - 2)
        r = Rect(x, y, w, h)

        if any(r.intersects(other) for other in rooms):
            continue

        # carve room
        for ry in range(r.y1, r.y2):
            for rx in range(r.x1, r.x2):
                grid[ry][rx] = TILE_FLOOR

        # connect to previous room with tunnels
        if rooms:
            cx, cy = r.center()
            px, py = rooms[-1].center()
            if random.randint(0, 1):
                for rx in range(min(cx, px), max(cx, px) + 1):
                    grid[cy][rx] = TILE_FLOOR
                for ry in range(min(cy, py), max(cy, py) + 1):
                    grid[ry][cx] = TILE_FLOOR
            else:
                for ry in range(min(cy, py), max(cy, py) + 1):
                    grid[ry][px] = TILE_FLOOR
                for rx in range(min(cx, px), max(cx, px) + 1):
                    grid[cy][rx] = TILE_FLOOR

        rooms.append(r)

    # place stairs in last room
    last_cx, last_cy = rooms[-1].center()
    grid[last_cy][last_cx] = TILE_STAIRS

    # place enemies and items
    entities = []
    for room in rooms[1:]:  # skip spawn room
        num_enemies = random.randint(0, 2 + floor_num // 2)
        for _ in range(num_enemies):
            ex = random.randint(room.x1, room.x2 - 1)
            ey = random.randint(room.y1, room.y2 - 1)
            # scale enemy difficulty with floor
            max_tier = min(floor_num, len(ENEMY_TYPES) - 1)
            tier = random.randint(0, max_tier)
            e = dict(ENEMY_TYPES[tier])
            e["x"], e["y"] = ex, ey
            e["max_hp"] = e["hp"]
            entities.append(("enemy", e))

        if random.random() < 0.4:
            ix = random.randint(room.x1, room.x2 - 1)
            iy = random.randint(room.y1, room.y2 - 1)
            item = dict(random.choice(ITEM_TYPES))
            item["x"], item["y"] = ix, iy
            entities.append(("item", item))

        if random.random() < 0.3:
            gx = random.randint(room.x1, room.x2 - 1)
            gy = random.randint(room.y1, room.y2 - 1)
            gold_amt = random.randint(5, 15 + floor_num * 3)
            entities.append(("gold", {"x": gx, "y": gy, "value": gold_amt}))

    spawn_x, spawn_y = rooms[0].center()
    return grid, entities, spawn_x, spawn_y


# ── game state ─────────────────────────────────────────────────────────────────

class Player:
    def __init__(self):
        self.x = self.y = 0
        self.hp = self.max_hp = 30
        self.atk = 5
        self.defense = 0
        self.gold = 0
        self.xp = 0
        self.level = 1
        self.xp_next = 20
        self.floor = 1
        self.kills = 0

    def gain_xp(self, amount):
        self.xp += amount
        msgs = []
        while self.xp >= self.xp_next:
            self.xp -= self.xp_next
            self.level += 1
            self.xp_next = int(self.xp_next * 1.5)
            self.max_hp += 8
            self.hp = min(self.hp + 8, self.max_hp)
            self.atk += 2
            msgs.append(f"LEVEL UP! Now level {self.level}!")
        return msgs

    def take_damage(self, amount):
        dmg = max(1, amount - self.defense)
        self.hp -= dmg
        return dmg

    def heal(self, amount):
        old = self.hp
        self.hp = min(self.hp + amount, self.max_hp)
        return self.hp - old

    def is_alive(self):
        return self.hp > 0


# ── main game ──────────────────────────────────────────────────────────────────

def run_game(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    # color pairs
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1,  curses.COLOR_YELLOW,  -1)  # player / gold
    curses.init_pair(2,  curses.COLOR_RED,     -1)  # enemies / danger
    curses.init_pair(3,  curses.COLOR_GREEN,   -1)  # items / good
    curses.init_pair(4,  curses.COLOR_CYAN,    -1)  # stairs / info
    curses.init_pair(5,  curses.COLOR_WHITE,   -1)  # floor tiles
    curses.init_pair(6,  curses.COLOR_MAGENTA, -1)  # walls
    curses.init_pair(7,  curses.COLOR_BLACK,   curses.COLOR_RED)    # hp critical
    curses.init_pair(8,  curses.COLOR_BLACK,   curses.COLOR_GREEN)  # hp good

    YELLOW  = curses.color_pair(1)
    RED     = curses.color_pair(2)
    GREEN   = curses.color_pair(3)
    CYAN    = curses.color_pair(4)
    WHITE   = curses.color_pair(5)
    MAGENTA = curses.color_pair(6)

    player = Player()
    grid, entities, px, py = generate_map(player.floor)
    player.x, player.y = px, py

    messages = [f'Welcome to Dungeon Crawler v{VERSION}! Find the stairs (>) to descend.']
    log_max = 4

    def get_entity_at(x, y):
        for kind, e in entities:
            if e["x"] == x and e["y"] == y:
                return kind, e
        return None, None

    def add_msg(msg):
        messages.append(msg)
        if len(messages) > log_max:
            messages.pop(0)

    def next_floor():
        nonlocal grid, entities
        player.floor += 1
        grid, entities, sx, sy = generate_map(player.floor)
        player.x, player.y = sx, sy
        add_msg(f"You descend to floor {player.floor}. The darkness grows deeper...")

    def do_combat(enemy):
        # player attacks enemy
        p_dmg = max(1, player.atk + random.randint(-2, 2))
        enemy["hp"] -= p_dmg

        if enemy["hp"] <= 0:
            xp_msgs = player.gain_xp(enemy["xp"])
            player.kills += 1
            entities[:] = [(k, e) for k, e in entities
                           if not (k == "enemy" and e is enemy)]
            add_msg(f"Killed {enemy['name']}! +{enemy['xp']} XP")
            for m in xp_msgs:
                add_msg(m)
            return

        # enemy fights back
        e_dmg = player.take_damage(enemy["atk"] + random.randint(-1, 2))
        add_msg(f"Hit {enemy['name']} for {p_dmg}dmg. It hits back for {e_dmg}dmg!")

    def draw():
        stdscr.erase()
        sh, sw = stdscr.getmaxyx()

        # camera: center on player
        cam_x = max(0, min(player.x - sw // 2, MAP_W - sw))
        cam_y = max(0, min(player.y - (sh - 8) // 2, MAP_H - (sh - 8)))

        # draw map
        view_h = sh - 7
        for vy in range(view_h):
            my = vy + cam_y
            if my >= MAP_H:
                break
            for vx in range(sw - 1):
                mx = vx + cam_x
                if mx >= MAP_W:
                    break
                tile = grid[my][mx]
                attr = WHITE
                if tile == TILE_WALL:
                    attr = MAGENTA | curses.A_DIM
                elif tile == TILE_STAIRS:
                    attr = CYAN | curses.A_BOLD
                try:
                    stdscr.addch(vy, vx, tile, attr)
                except curses.error:
                    pass

        # draw entities
        for kind, e in entities:
            ex, ey = e["x"] - cam_x, e["y"] - cam_y
            if 0 <= ex < sw - 1 and 0 <= ey < view_h:
                if kind == "enemy":
                    attr = RED | curses.A_BOLD
                    ch = e["char"]
                elif kind == "item":
                    attr = GREEN | curses.A_BOLD
                    ch = e["char"]
                elif kind == "gold":
                    attr = YELLOW
                    ch = TILE_GOLD
                else:
                    continue
                try:
                    stdscr.addch(ey, ex, ch, attr)
                except curses.error:
                    pass

        # draw player
        px_s = player.x - cam_x
        py_s = player.y - cam_y
        if 0 <= px_s < sw - 1 and 0 <= py_s < view_h:
            try:
                stdscr.addch(py_s, px_s, TILE_PLAYER, YELLOW | curses.A_BOLD)
            except curses.error:
                pass

        # ── HUD ──
        hud_y = sh - 7
        stdscr.attron(curses.A_REVERSE)
        stdscr.addstr(hud_y, 0, " " * (sw - 1))
        stdscr.attroff(curses.A_REVERSE)

        hp_color = GREEN if player.hp > player.max_hp * 0.5 else (YELLOW if player.hp > player.max_hp * 0.25 else RED)
        hp_bar_len = 20
        hp_filled = int((player.hp / player.max_hp) * hp_bar_len)
        hp_bar = "[" + "█" * hp_filled + "░" * (hp_bar_len - hp_filled) + "]"

        hud_str = (f" HP:{player.hp}/{player.max_hp} {hp_bar} "
                   f"| LVL:{player.level} XP:{player.xp}/{player.xp_next} "
                   f"| ATK:{player.atk} DEF:{player.defense} "
                   f"| Gold:{player.gold} "
                   f"| Floor:{player.floor} "
                   f"| Kills:{player.kills} ")
        try:
            stdscr.addstr(hud_y, 0, hud_str[:sw-1], curses.A_BOLD)
        except curses.error:
            pass

        # message log
        for i, msg in enumerate(messages[-log_max:]):
            color = CYAN if i == len(messages[-log_max:]) - 1 else WHITE | curses.A_DIM
            try:
                stdscr.addstr(hud_y + 1 + i, 1, msg[:sw-2], color)
            except curses.error:
                pass

        # controls hint
        try:
            stdscr.addstr(sh - 1, 0,
                " [arrows/wasd] move  [.] wait  [q] quit "[:sw-1],
                curses.A_DIM)
        except curses.error:
            pass

        stdscr.refresh()

    # ── main loop ──
    while True:
        if not player.is_alive():
            break

        draw()
        key = stdscr.getch()

        dx, dy = 0, 0
        if key in (curses.KEY_UP,    ord('w'), ord('k')): dy = -1
        elif key in (curses.KEY_DOWN,  ord('s'), ord('j')): dy =  1
        elif key in (curses.KEY_LEFT,  ord('a'), ord('h')): dx = -1
        elif key in (curses.KEY_RIGHT, ord('d'), ord('l')): dx =  1
        elif key == ord('.'): pass  # wait
        elif key == ord('q'): break
        else: continue

        nx, ny = player.x + dx, player.y + dy

        # bounds check
        if not (0 <= nx < MAP_W and 0 <= ny < MAP_H):
            continue

        # wall check
        if grid[ny][nx] == TILE_WALL:
            continue

        # entity interaction
        kind, ent = get_entity_at(nx, ny)

        if kind == "enemy":
            do_combat(ent)
            continue

        if kind == "item":
            if ent["type"] == "heal":
                healed = player.heal(ent["value"])
                add_msg(f"Used {ent['name']}! Healed {healed} HP.")
            elif ent["type"] == "weapon":
                player.atk += ent["value"]
                add_msg(f"Equipped {ent['name']}! ATK +{ent['value']}.")
            elif ent["type"] == "armor":
                player.defense += ent["value"]
                add_msg(f"Equipped {ent['name']}! DEF +{ent['value']}.")
            entities[:] = [(k, e) for k, e in entities if e is not ent]

        elif kind == "gold":
            player.gold += ent["value"]
            add_msg(f"Picked up {ent['value']} gold!")
            entities[:] = [(k, e) for k, e in entities if e is not ent]

        # move player
        player.x, player.y = nx, ny

        # check stairs
        if grid[ny][nx] == TILE_STAIRS:
            next_floor()

    # ── game over screen ──
    stdscr.erase()
    sh, sw = stdscr.getmaxyx()
    cy = sh // 2

    if not player.is_alive():
        msg = "YOU DIED"
        color = RED | curses.A_BOLD
    else:
        msg = "FAREWELL, ADVENTURER"
        color = YELLOW | curses.A_BOLD

    try:
        stdscr.addstr(cy - 3, (sw - len(msg)) // 2, msg, color)
        stats = [
            f"Floor reached : {player.floor}",
            f"Level         : {player.level}",
            f"Enemies slain : {player.kills}",
            f"Gold collected: {player.gold}",
        ]
        for i, s in enumerate(stats):
            stdscr.addstr(cy - 1 + i, (sw - len(s)) // 2, s, WHITE)
        stdscr.addstr(cy + 5, (sw - 20) // 2, "Press any key to exit", curses.A_DIM)
    except curses.error:
        pass

    stdscr.refresh()
    stdscr.getch()


def main():
    try:
        curses.wrapper(run_game)
    except KeyboardInterrupt:
        pass
    print("Thanks for playing PenguWarp Dungeon Crawler!")


if __name__ == "__main__":
    main()
