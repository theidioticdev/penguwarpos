"""
setup.py — PenguWarp OS first-boot installer (curses TUI)
"""

import curses
import curses.textpad
import time
import uuid

# ── Gruvbox ANSI-ish colour pairs (curses) ───────────────────────────────────
# pair indices:  1=yellow  2=white/fg  3=black/bg  4=red  5=green  6=dim/gray

PENGUIN = [
    r"    ___    ",
    r"   <   o>  ",
    r"   ( | )   ",
    r"   /___\   ",
]

TITLE   = 'PenguWarp OS  v0.1.8 "Lemon"'
SUBTITLE = "First-Boot Setup"


def _init_colors() -> None:
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_YELLOW,  -1)   # yellow
    curses.init_pair(2, curses.COLOR_WHITE,   -1)   # white/fg
    curses.init_pair(3, curses.COLOR_BLACK,   -1)   # black
    curses.init_pair(4, curses.COLOR_RED,     -1)   # red / error
    curses.init_pair(5, curses.COLOR_GREEN,   -1)   # green / ok
    curses.init_pair(6, curses.COLOR_WHITE,   -1)   # dim (gray fallback)


YEL  = lambda: curses.color_pair(1) | curses.A_BOLD
FG   = lambda: curses.color_pair(2)
ERR  = lambda: curses.color_pair(4) | curses.A_BOLD
OK   = lambda: curses.color_pair(5) | curses.A_BOLD
DIM  = lambda: curses.color_pair(6) | curses.A_DIM


def _draw_box(win, title: str = "") -> None:
    """Draw a rounded-ish border with optional title."""
    win.border()
    if title:
        h, w = win.getmaxyx()
        label = f" {title} "
        win.addstr(0, max(2, (w - len(label)) // 2), label, YEL())


def _draw_penguin(win, row: int, col: int) -> None:
    for i, line in enumerate(PENGUIN):
        try:
            win.addstr(row + i, col, line, YEL())
        except curses.error:
            pass


def _centered(win, row: int, text: str, attr: int = 0) -> None:
    _, w = win.getmaxyx()
    col  = max(0, (w - len(text)) // 2)
    try:
        win.addstr(row, col, text, attr)
    except curses.error:
        pass


def _read_field(win, row: int, col: int, width: int,
                secret: bool = False) -> str:
    """
    Simple single-line input field.
    Supports: printable chars, backspace, Enter to submit.
    Returns the entered string.
    """
    buf    = []
    cursor = 0
    win.move(row, col)
    curses.curs_set(1)

    while True:
        # redraw field
        display = ("*" * len(buf)) if secret else "".join(buf)
        field   = display.ljust(width)[:width]
        try:
            win.addstr(row, col, field, curses.color_pair(2) | curses.A_UNDERLINE)
            win.move(row, col + min(cursor, width - 1))
        except curses.error:
            pass
        win.refresh()

        ch = win.get_wch()

        if ch in ("\n", "\r", curses.KEY_ENTER):
            break
        elif ch in (curses.KEY_BACKSPACE, "\x7f", "\b"):
            if buf:
                buf.pop()
                cursor = max(0, cursor - 1)
        elif isinstance(ch, str) and ch.isprintable():
            buf.append(ch)
            cursor += 1

    curses.curs_set(0)
    return "".join(buf).strip()


def _installer(stdscr) -> dict:
    """Main curses installer. Returns dict with setup results."""
    curses.curs_set(0)
    stdscr.clear()
    _init_colors()

    sh, sw = stdscr.getmaxyx()

    # ── Outer frame ───────────────────────────────────────────────────────────
    box_h, box_w = min(sh, 32), min(sw, 72)
    box_y = (sh - box_h) // 2
    box_x = (sw - box_w) // 2
    frame = curses.newwin(box_h, box_w, box_y, box_x)
    _draw_box(frame, "PENGUWARP INSTALLER")

    # penguin + title
    _draw_penguin(frame, 2, (box_w - 12) // 2)
    _centered(frame, 7, TITLE,    YEL())
    _centered(frame, 8, SUBTITLE, DIM())
    frame.hline(9, 1, curses.ACS_HLINE, box_w - 2)
    frame.refresh()

    FIELD_W = 30
    LABEL_C = 6
    INPUT_C  = LABEL_C + 18

    result   = {}
    error    = ""
    step     = 0   # 0=hostname 1=username 2=password 3=confirm 4=done

    steps = [
        ("hostname",  "Hostname",         False),
        ("username",  "Username",         False),
        ("password",  "Password",         True),
        ("confirm",   "Confirm password", True),
    ]

    while step < len(steps):
        frame.clear()
        _draw_box(frame, "PENGUWARP INSTALLER")
        _draw_penguin(frame, 2, (box_w - 12) // 2)
        _centered(frame, 7, TITLE,    YEL())
        _centered(frame, 8, SUBTITLE, DIM())
        frame.hline(9, 1, curses.ACS_HLINE, box_w - 2)

        # draw all fields (filled or blank)
        for i, (key, label, secret) in enumerate(steps):
            row = 11 + i * 3
            frame.addstr(row, LABEL_C, f"{label}:", FG())
            val = result.get(key, "")
            display = ("*" * len(val)) if (secret and val) else val
            frame.addstr(row, INPUT_C, display.ljust(FIELD_W)[:FIELD_W],
                         curses.A_UNDERLINE | FG())

        # instructions
        frame.hline(box_h - 5, 1, curses.ACS_HLINE, box_w - 2)
        _centered(frame, box_h - 4, "Enter to confirm each field", DIM())
        _centered(frame, box_h - 3, "Ctrl+C to quit", DIM())

        # error banner
        if error:
            _centered(frame, box_h - 7, error, ERR())

        frame.refresh()

        # active field
        key_name, label, secret = steps[step]
        active_row = 11 + step * 3
        frame.addstr(active_row, LABEL_C, f"{label}:", YEL())
        frame.refresh()

        val = _read_field(frame, active_row, INPUT_C, FIELD_W, secret=secret)

        # ── validation ────────────────────────────────────────────────
        error = ""
        if not val:
            error = f"  ✗  {label} cannot be empty  "
            continue

        if key_name == "hostname":
            if len(val) > 32 or not all(c.isalnum() or c == "-" for c in val):
                error = "  ✗  Hostname: letters, numbers and hyphens only  "
                continue

        if key_name == "username":
            if len(val) > 32 or not all(c.isalnum() or c in "_-" for c in val):
                error = "  ✗  Username: letters, numbers, _ and - only  "
                continue
            if val == "root":
                error = "  ✗  Cannot use 'root' as username  "
                continue

        if key_name == "confirm":
            if val != result.get("password", ""):
                error = "  ✗  Passwords do not match  "
                # clear both password fields and restart from password step
                result.pop("password", None)
                result.pop("confirm",  None)
                step = 2
                continue

        result[key_name] = val
        step += 1

    # ── Done screen ───────────────────────────────────────────────────────────
    frame.clear()
    _draw_box(frame, "PENGUWARP INSTALLER")
    _draw_penguin(frame, 2, (box_w - 12) // 2)
    _centered(frame, 7, TITLE, YEL())
    frame.hline(9, 1, curses.ACS_HLINE, box_w - 2)

    _centered(frame, 11, "Setup complete!", OK())
    _centered(frame, 13, f"Hostname  :  {result['hostname']}", FG())
    _centered(frame, 14, f"User      :  {result['username']}", FG())
    _centered(frame, 15, f"Home      :  ~/usr/{result['username']}", DIM())
    frame.hline(17, 1, curses.ACS_HLINE, box_w - 2)
    _centered(frame, 19, "Booting PenguWarp...", YEL())

    frame.refresh()
    time.sleep(2)

    return result


def run_setup() -> dict:
    """Entry point — run the curses installer and return setup data."""
    return curses.wrapper(_installer)
