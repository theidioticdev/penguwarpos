# DashWarp - a TUI Dashboard app for PenguWarp OS
import curses
import datetime
import system as S
from system import save_system

# ── Colors ────────────────────────────────────────────────────────────────────

def _init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_YELLOW,  -1)  # header / labels
    curses.init_pair(2, curses.COLOR_WHITE,   -1)  # normal text
    curses.init_pair(3, curses.COLOR_GREEN,   -1)  # todo
    curses.init_pair(4, curses.COLOR_CYAN,    -1)  # filesystem
    curses.init_pair(5, curses.COLOR_RED,     -1)  # delete / error
    curses.init_pair(6, curses.COLOR_WHITE,   -1)  # dim
    curses.init_pair(7, curses.COLOR_MAGENTA, -1)  # clock

YEL = lambda: curses.color_pair(1) | curses.A_BOLD
FG  = lambda: curses.color_pair(2)
GRN = lambda: curses.color_pair(3) | curses.A_BOLD
CYN = lambda: curses.color_pair(4) | curses.A_BOLD
RED = lambda: curses.color_pair(5) | curses.A_BOLD
DIM = lambda: curses.color_pair(6) | curses.A_DIM
MAG = lambda: curses.color_pair(7) | curses.A_BOLD

# ── Safe draw ─────────────────────────────────────────────────────────────────

def _safe(win, y, x, text, attr=0):
    h, w = win.getmaxyx()
    if y < 0 or y >= h or x < 0 or x >= w:
        return
    max_len = w - x - 1
    if max_len <= 0:
        return
    try:
        win.addstr(y, x, text[:max_len], attr)
    except curses.error:
        pass


def _border(win, title: str, color):
    try:
        win.border()
        _, w = win.getmaxyx()
        label = f" {title} "
        win.addstr(0, max(2, (w - len(label)) // 2), label, color)
    except curses.error:
        pass


# ── Todos persistence ─────────────────────────────────────────────────────────

def _get_todos() -> list:
    return S.filesystem.get("~/.dashwarp_todos", {}).get("content_list", [])


def _save_todos(todos: list):
    S.filesystem["~/.dashwarp_todos"] = {
        "type":         "file",
        "content_list": todos,
        "content":      "\n".join(todos),
    }
    save_system()


# ── Filesystem helpers ────────────────────────────────────────────────────────

def _get_dir_contents(path: str) -> list:
    node     = S.filesystem.get(path, {})
    contents = node.get("contents", [])
    entries  = []
    if path != "~":
        entries.append(("..", "nav"))
    for item in contents:
        full = f"{path}/{item}" if path != "~" else f"~/{item}"
        kind = S.filesystem.get(full, {}).get("type", "file")
        entries.append((item, kind))
    return entries


# ── Clock panel ───────────────────────────────────────────────────────────────

def _draw_clock(win):
    _border(win, "  Clock  ", MAG())
    h, w  = win.getmaxyx()
    now   = datetime.datetime.now()
    tstr  = now.strftime("%I:%M:%S %p")
    dstr  = now.strftime("%A, %B %d %Y")
    ustr  = f"{S.user}@{S.hostname}"

    _safe(win, 2, max(0, (w - len(tstr)) // 2), tstr,  MAG())
    _safe(win, 3, max(0, (w - len(dstr)) // 2), dstr,  DIM())
    _safe(win, 5, max(0, w - len(ustr) - 2),    ustr,  YEL())


# ── Todo panel ────────────────────────────────────────────────────────────────

def _draw_todo(win, todos: list, sel: int, active: bool):
    tc = GRN() if active else (curses.color_pair(3) | curses.A_DIM)
    _border(win, "  Todo  ", tc)
    h, w = win.getmaxyx()

    if not todos:
        _safe(win, 2, 2, "No tasks! Press 'a' to add.", DIM())
    else:
        for i, task in enumerate(todos):
            row = 2 + i
            if row >= h - 2:
                break
            prefix = "> " if (i == sel and active) else "  "
            attr   = (GRN() | curses.A_REVERSE) if (i == sel and active) else FG()
            _safe(win, row, 2, f"{prefix}{i+1}. {task}", attr)

    if active:
        _safe(win, h - 2, 2, "a:add  d:delete  Tab:switch", DIM())


# ── Filesystem panel ──────────────────────────────────────────────────────────

def _draw_fs(win, path: str, entries: list, sel: int, active: bool):
    tc = CYN() if active else (curses.color_pair(4) | curses.A_DIM)
    _border(win, "  Filesystem  ", tc)
    h, w = win.getmaxyx()

    path_display = path if len(path) < w - 4 else "..." + path[-(w - 7):]
    _safe(win, 1, 2, path_display, YEL())

    if not entries:
        _safe(win, 3, 2, "(empty)", DIM())
    else:
        for i, (name, kind) in enumerate(entries):
            row = 3 + i
            if row >= h - 2:
                break
            if name == "..":
                icon = "↑ "
                attr = DIM()
            elif kind == "dir":
                icon = "▸ "
                attr = CYN()
            else:
                icon = "  "
                attr = FG()
            if i == sel and active:
                attr = attr | curses.A_REVERSE
            _safe(win, row, 2, f"{icon}{name}", attr)

    if active:
        _safe(win, h - 2, 2, "↑↓:nav  Enter:open  Tab:switch", DIM())


# ── Inline input ──────────────────────────────────────────────────────────────

def _read_input(stdscr, prompt: str, y: int, x: int, width: int) -> str:
    curses.curs_set(1)
    buf = []
    sh, sw = stdscr.getmaxyx()
    y = min(y, sh - 1)

    def _redraw():
        field = (prompt + "".join(buf)).ljust(width)[:width]
        try:
            stdscr.addstr(y, x, field, curses.color_pair(2) | curses.A_UNDERLINE)
            stdscr.move(y, x + len(prompt) + len(buf))
        except curses.error:
            pass
        stdscr.refresh()

    _redraw()
    while True:
        ch = stdscr.get_wch()
        if ch in ("\n", "\r", curses.KEY_ENTER):
            break
        elif ch in (curses.KEY_BACKSPACE, "\x7f", "\b"):
            if buf:
                buf.pop()
        elif isinstance(ch, str) and ch.isprintable():
            if len(buf) < width - len(prompt) - 1:
                buf.append(ch)
        _redraw()

    curses.curs_set(0)
    return "".join(buf).strip()


# ── Main loop ─────────────────────────────────────────────────────────────────

def _dashboard(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(500)
    _init_colors()

    focus     = 0   # 0 = todo, 1 = fs
    todo_sel  = 0
    fs_sel    = 0
    fs_path   = S.current_dir
    todos     = _get_todos()
    fs_entries = _get_dir_contents(fs_path)

    while True:
        stdscr.erase()
        sh, sw = stdscr.getmaxyx()

        clock_h  = 8
        bottom_h = max(4, sh - clock_h - 1)
        half_w   = sw // 2

        # panels
        clock_win = stdscr.derwin(clock_h, sw, 0, 0)
        todo_win  = stdscr.derwin(bottom_h, half_w, clock_h, 0)
        fs_win    = stdscr.derwin(bottom_h, sw - half_w, clock_h, half_w)

        _draw_clock(clock_win)
        _draw_todo(todo_win,  todos,      todo_sel, focus == 0)
        _draw_fs  (fs_win,    fs_path, fs_entries, fs_sel,    focus == 1)

        hint = " Tab:switch panels   Q:quit "
        _safe(stdscr, sh - 1, max(0, (sw - len(hint)) // 2), hint, YEL())

        stdscr.refresh()

        # input
        try:
            ch = stdscr.get_wch()
        except curses.error:
            continue

        if ch == "Q":
            break

        if ch == "\t":
            focus = 1 - focus
            continue

        # ── todo controls ─────────────────────────────────────────────────────
        if focus == 0:
            if ch == curses.KEY_UP:
                todo_sel = max(0, todo_sel - 1)
            elif ch == curses.KEY_DOWN:
                todo_sel = min(max(0, len(todos) - 1), todo_sel + 1)
            elif ch in ("a", "A"):
                stdscr.nodelay(False)
                task = _read_input(stdscr, "New task: ", sh - 1, 0, sw - 1)
                stdscr.nodelay(True)
                if task:
                    todos.append(task)
                    _save_todos(todos)
                    todo_sel = len(todos) - 1
            elif ch in ("d", "D"):
                if todos and 0 <= todo_sel < len(todos):
                    todos.pop(todo_sel)
                    _save_todos(todos)
                    todo_sel = max(0, min(todo_sel, len(todos) - 1))

        # ── filesystem controls ───────────────────────────────────────────────
        elif focus == 1:
            if ch == curses.KEY_UP:
                fs_sel = max(0, fs_sel - 1)
            elif ch == curses.KEY_DOWN:
                fs_sel = min(max(0, len(fs_entries) - 1), fs_sel + 1)
            elif ch in ("\n", "\r", curses.KEY_ENTER):
                if fs_entries:
                    name, kind = fs_entries[fs_sel]
                    if name == "..":
                        fs_path = S.resolve_path(f"{fs_path}/..")
                    elif kind == "dir":
                        new = f"{fs_path}/{name}" if fs_path != "~" else f"~/{name}"
                        fs_path = new
                    fs_entries = _get_dir_contents(fs_path)
                    fs_sel     = 0


def run():
    curses.wrapper(_dashboard)


if __name__ == "__main__":
    run()
