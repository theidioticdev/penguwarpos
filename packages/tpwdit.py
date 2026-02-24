import curses
import json
import os
import sys
import time

# ── Color pair IDs ───────────────────────────────────────────────────────────
PAIR_NORMAL_BAR  = 1   # status bar in NORMAL mode
PAIR_INSERT_BAR  = 2   # status bar in INSERT mode
PAIR_COMMAND_BAR = 3   # status bar in COMMAND mode
PAIR_LINE_NUM    = 4   # line numbers / tilde rows
PAIR_TEXT        = 5   # normal text
PAIR_CMD_KEYWORD = 6   # .pwe syntax: commands
PAIR_CMD_STRING  = 7   # .pwe syntax: strings
PAIR_CMD_COMMENT = 8   # .pwe syntax: comments
PAIR_MODIFIED    = 9   # messages / [+] indicator
PAIR_CURSOR_LINE = 10  # current line highlight

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
# tpwdit always lives in packages/ — system file is always one level up next to the kernel
SYSTEM_FILE = os.path.join(os.path.dirname(SCRIPT_DIR), "penguwarp_system.json")

PWE_COMMANDS = {
    "help", "list", "read", "cd", "whereami", "mkdir", "mkfile", "delete",
    "rmdir", "echo", "run", "uname", "whoami", "pwdit", "tpwdit", "pyufetch",
    "clear", "startx", "poweroff", "about", "pkgmgr","usercn","hostcn",
}


# ── Filesystem helpers ───────────────────────────────────────────────────────

def load_system() -> dict:
    if os.path.exists(SYSTEM_FILE):
        try:
            with open(SYSTEM_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_system(data: dict) -> None:
    with open(SYSTEM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ── Color setup ──────────────────────────────────────────────────────────────

def init_colors() -> None:
    curses.start_color()
    curses.use_default_colors()

    # Gruvbox-approximate 256-color values
    BG     = 235   # #262626
    FG     = 223   # close to #ebdbb2
    YELLOW = 214   # #ffaf00
    GREEN  = 142   # #afaf00
    AQUA   = 108   # #87af87
    GRAY   = 102   # #878787
    BG1    = 237   # #3a3a3a 
    ORANGE = 208   # #ff8700

    curses.init_pair(PAIR_NORMAL_BAR,  BG,    YELLOW)
    curses.init_pair(PAIR_INSERT_BAR,  BG,    GREEN)
    curses.init_pair(PAIR_COMMAND_BAR, BG,    AQUA)
    curses.init_pair(PAIR_LINE_NUM,    GRAY,  BG)
    curses.init_pair(PAIR_TEXT,        FG,    BG)
    curses.init_pair(PAIR_CMD_KEYWORD, YELLOW, BG)
    curses.init_pair(PAIR_CMD_STRING,  GREEN,  BG)
    curses.init_pair(PAIR_CMD_COMMENT, GRAY,   BG)
    curses.init_pair(PAIR_MODIFIED,    ORANGE, BG)
    curses.init_pair(PAIR_CURSOR_LINE, FG,    BG1)


# ── Syntax highlighting ──────────────────────────────────────────────────────

def highlight_line(win, y: int, x_off: int, line: str,
                   is_pwe: bool, is_cursor: bool, max_w: int) -> None:
    base = curses.color_pair(PAIR_CURSOR_LINE if is_cursor else PAIR_TEXT)

    # Fill row background
    try:
        win.addstr(y, x_off, " " * max(0, max_w - x_off), base)
    except curses.error:
        pass

    visible = line[:max_w - x_off]

    if not is_pwe:
        try:
            win.addstr(y, x_off, visible, base)
        except curses.error:
            pass
        return

    # Comment lines
    if line.lstrip().startswith("#"):
        try:
            win.addstr(y, x_off, visible,
                       curses.color_pair(PAIR_CMD_COMMENT) | curses.A_ITALIC)
        except curses.error:
            pass
        return

    # Tokenise on double-quotes for string highlighting
    col = x_off
    tokens = line.split('"')

    pre   = tokens[0] if tokens else line
    words = pre.split()

    # First word → keyword?
    if words and words[0] in PWE_COMMANDS:
        kw = words[0]
        try:
            win.addstr(y, col, kw[:max_w - col],
                       curses.color_pair(PAIR_CMD_KEYWORD) | curses.A_BOLD)
        except curses.error:
            pass
        col += len(kw)
        rest = pre[len(kw):]
    else:
        rest = pre

    if rest and col < max_w:
        try:
            win.addstr(y, col, rest[:max_w - col], base)
        except curses.error:
            pass
        col += len(rest)

    # Quoted strings (odd-indexed tokens are inside quotes)
    for i in range(1, len(tokens)):
        if col >= max_w:
            break
        seg = tokens[i]
        if i % 2 == 1:
            s = f'"{seg}"' if i < len(tokens) - 1 else f'"{seg}'
            try:
                win.addstr(y, col, s[:max_w - col],
                           curses.color_pair(PAIR_CMD_STRING))
            except curses.error:
                pass
            col += len(s)
        else:
            try:
                win.addstr(y, col, seg[:max_w - col], base)
            except curses.error:
                pass
            col += len(seg)


# ── Editor ───────────────────────────────────────────────────────────────────

class Editor:
    NORMAL  = "NORMAL"
    INSERT  = "INSERT"
    COMMAND = "COMMAND"

    def __init__(self, pw_path: str) -> None:
        if not pw_path.startswith("~") and "/" not in pw_path:
            pw_path = f"~/{pw_path}"
        self.pw_path  = pw_path
        self.filename = pw_path.split("/")[-1]
        self.is_pwe   = self.filename.endswith(".pwe")

        self.mode       = self.NORMAL
        self.lines: list[str] = [""]
        self.crow       = 0   
        self.ccol       = 0   
        self.scroll_top = 0
        self.modified   = False
        self.cmd_buf    = ""
        self.msg        = ""
        self.msg_ts     = 0.0
        self.running    = True

    # ── I/O ──────────────────────────────────────────────────────────────────

    def load(self) -> None:
        data = load_system()
        fs   = data.get("filesystem", {})
        entry = fs.get(self.pw_path)
        if entry and entry.get("type") == "file":
            content    = entry.get("content", "")
            self.lines = content.split("\n") if content else [""]
        else:
            self.lines = [""]

    def save(self) -> bool:
        data = load_system()
        fs   = data.get("filesystem", {})

        parts   = self.pw_path.rsplit("/", 1)
        par_key = parts[0] if len(parts) > 1 else "~"

        if par_key not in fs:
            self.flash(f"ERROR: parent dir '{par_key}' not in filesystem")
            return False

        fs[self.pw_path] = {"type": "file", "content": "\n".join(self.lines)}
        if self.filename not in fs[par_key].get("contents", []):
            fs[par_key].setdefault("contents", []).append(self.filename)

        data["filesystem"] = fs
        save_system(data)
        self.modified = False
        self.flash(f'"{self.filename}" written, {len(self.lines)}L')
        return True

    # ── Helpers ──────────────────────────────────────────────────────────────

    def flash(self, msg: str) -> None:
        self.msg    = msg
        self.msg_ts = time.time()

    def vis_rows(self, h: int) -> int:
        return h - 2  # status bar + message line

    def clamp(self) -> None:
        self.crow = max(0, min(self.crow, len(self.lines) - 1))
        line_len  = len(self.lines[self.crow])
        if self.mode == self.NORMAL:
            self.ccol = max(0, min(self.ccol, max(0, line_len - 1)))
        else:
            self.ccol = max(0, min(self.ccol, line_len))

    def scroll(self, h: int) -> None:
        vis = self.vis_rows(h)
        if self.crow < self.scroll_top:
            self.scroll_top = self.crow
        elif self.crow >= self.scroll_top + vis:
            self.scroll_top = self.crow - vis + 1

    # ── Draw ─────────────────────────────────────────────────────────────────

    def draw(self, scr) -> None:
        scr.erase()
        h, w   = scr.getmaxyx()
        vis    = self.vis_rows(h)
        lnum_w = len(str(len(self.lines))) + 2  

        # Text rows
        for sr in range(vis):
            fr = self.scroll_top + sr
            if fr >= len(self.lines):
                try:
                    scr.addstr(sr, 0, "~", curses.color_pair(PAIR_LINE_NUM))
                except curses.error:
                    pass
                continue

            is_cur = (fr == self.crow)
            lnum   = f"{fr + 1:>{lnum_w - 1}} "
            lattr  = curses.color_pair(PAIR_CURSOR_LINE if is_cur else PAIR_LINE_NUM)
            try:
                scr.addstr(sr, 0, lnum, lattr)
            except curses.error:
                pass

            highlight_line(scr, sr, lnum_w, self.lines[fr],
                           self.is_pwe, is_cur, w)

        bar_row = h - 2
        if self.mode == self.NORMAL:
            bar_pair, mode_tag = curses.color_pair(PAIR_NORMAL_BAR),  " NORMAL "
        elif self.mode == self.INSERT:
            bar_pair, mode_tag = curses.color_pair(PAIR_INSERT_BAR),  " INSERT "
        else:
            bar_pair, mode_tag = curses.color_pair(PAIR_COMMAND_BAR), " COMMAND "

        flag     = " [+]" if self.modified else ""
        fname    = f" {self.filename}{flag} "
        pos      = f" {self.crow + 1}:{self.ccol + 1} "
        pad      = " " * max(0, w - len(mode_tag) - len(fname) - len(pos))
        bar_text = (mode_tag + fname + pad + pos)[:w]
        try:
            scr.addstr(bar_row, 0, bar_text, bar_pair | curses.A_BOLD)
        except curses.error:
            pass

        # Message / command line
        msg_row = h - 1
        if self.mode == self.COMMAND:
            try:
                scr.addstr(msg_row, 0, f":{self.cmd_buf}"[:w],
                           curses.color_pair(PAIR_TEXT))
            except curses.error:
                pass
        elif self.msg and (time.time() - self.msg_ts < 4.0):
            try:
                scr.addstr(msg_row, 0, self.msg[:w],
                           curses.color_pair(PAIR_MODIFIED))
            except curses.error:
                pass
        else:
            hints = {
                self.NORMAL:  " hjkl=move  i=insert  a=append  o=newline  :=command  x=del ",
                self.INSERT:  " ESC=normal  type to edit  arrows ok ",
                self.COMMAND: " :w save  :q quit  :wq save+quit  :q! force quit  ESC cancel ",
            }
            try:
                scr.addstr(msg_row, 0, hints[self.mode][:w],
                           curses.color_pair(PAIR_LINE_NUM))
            except curses.error:
                pass

        if self.mode == self.COMMAND:
            try:
                scr.move(msg_row, min(len(self.cmd_buf) + 1, w - 1))
            except curses.error:
                pass
        else:
            sr = self.crow - self.scroll_top
            sc = lnum_w + self.ccol
            if 0 <= sr < vis:
                try:
                    scr.move(sr, min(sc, w - 1))
                except curses.error:
                    pass

        scr.refresh()

    # ── Key handlers ─────────────────────────────────────────────────────────

    def handle_normal(self, key: int) -> None:
        ch = chr(key) if 0 < key < 256 else ""

        # ─ Movement ─
        if   ch == "h" or key == curses.KEY_LEFT:  self.ccol = max(0, self.ccol - 1)
        elif ch == "l" or key == curses.KEY_RIGHT:  self.ccol += 1
        elif ch == "k" or key == curses.KEY_UP:     self.crow = max(0, self.crow - 1)
        elif ch == "j" or key == curses.KEY_DOWN:   self.crow = min(len(self.lines) - 1, self.crow + 1)
        elif ch == "0" or key == curses.KEY_HOME:   self.ccol = 0
        elif ch == "$" or key == curses.KEY_END:    self.ccol = max(0, len(self.lines[self.crow]) - 1)
        elif ch == "g":  self.crow = 0;  self.ccol = 0
        elif ch == "G":  self.crow = len(self.lines) - 1;  self.ccol = 0
        elif key == curses.KEY_PPAGE: self.crow = max(0, self.crow - 20)
        elif key == curses.KEY_NPAGE: self.crow = min(len(self.lines) - 1, self.crow + 20)

        # Word hop (basic)
        elif ch == "w":
            line = self.lines[self.crow]; p = self.ccol + 1
            while p < len(line) and line[p] != " ": p += 1
            while p < len(line) and line[p] == " ": p += 1
            self.ccol = min(p, max(0, len(line) - 1))
        elif ch == "b":
            line = self.lines[self.crow]; p = self.ccol - 1
            while p > 0 and line[p] == " ": p -= 1
            while p > 0 and line[p - 1] != " ": p -= 1
            self.ccol = max(0, p)

        # ─ Enter INSERT ─
        elif ch == "i": self.mode = self.INSERT
        elif ch == "a":
            self.ccol = min(self.ccol + 1, len(self.lines[self.crow]))
            self.mode = self.INSERT
        elif ch == "A":
            self.ccol = len(self.lines[self.crow])
            self.mode = self.INSERT
        elif ch == "o":
            self.lines.insert(self.crow + 1, "")
            self.crow += 1; self.ccol = 0
            self.modified = True; self.mode = self.INSERT
        elif ch == "O":
            self.lines.insert(self.crow, "")
            self.ccol = 0
            self.modified = True; self.mode = self.INSERT

        # ─ Enter COMMAND ─
        elif ch == ":": self.mode = self.COMMAND; self.cmd_buf = ""

        # ─ Delete char (x) ─
        elif ch == "x":
            line = self.lines[self.crow]
            if self.ccol < len(line):
                self.lines[self.crow] = line[:self.ccol] + line[self.ccol + 1:]
                self.modified = True

        # ─ Delete line (d) ─
        elif ch == "d":
            if len(self.lines) > 1:
                self.lines.pop(self.crow)
                self.crow = min(self.crow, len(self.lines) - 1)
            else:
                self.lines[0] = ""
            self.modified = True

        self.clamp()

    def handle_insert(self, key: int) -> None:
        if key == 27:  # ESC → NORMAL
            self.mode = self.NORMAL
            self.ccol = max(0, self.ccol - 1)
            self.clamp()
            return

        if key in (curses.KEY_BACKSPACE, 127, 8):
            if self.ccol > 0:
                ln = self.lines[self.crow]
                self.lines[self.crow] = ln[:self.ccol - 1] + ln[self.ccol:]
                self.ccol -= 1
            elif self.crow > 0:
                prev = self.lines[self.crow - 1]
                self.ccol = len(prev)
                self.lines[self.crow - 1] = prev + self.lines[self.crow]
                self.lines.pop(self.crow)
                self.crow -= 1
            self.modified = True

        elif key in (curses.KEY_ENTER, 10, 13):
            ln = self.lines[self.crow]
            self.lines[self.crow] = ln[:self.ccol]
            self.lines.insert(self.crow + 1, ln[self.ccol:])
            self.crow += 1; self.ccol = 0
            self.modified = True

        elif key == curses.KEY_LEFT:  self.ccol = max(0, self.ccol - 1)
        elif key == curses.KEY_RIGHT: self.ccol = min(len(self.lines[self.crow]), self.ccol + 1)
        elif key == curses.KEY_UP:    self.crow = max(0, self.crow - 1);  self.clamp()
        elif key == curses.KEY_DOWN:  self.crow = min(len(self.lines) - 1, self.crow + 1); self.clamp()
        elif key == curses.KEY_HOME:  self.ccol = 0
        elif key == curses.KEY_END:   self.ccol = len(self.lines[self.crow])

        elif 32 <= key < 256:
            ch = chr(key)
            ln = self.lines[self.crow]
            self.lines[self.crow] = ln[:self.ccol] + ch + ln[self.ccol:]
            self.ccol += 1
            self.modified = True

    def handle_command(self, key: int) -> None:
        if key == 27:  # ESC
            self.mode = self.NORMAL; self.cmd_buf = ""; return

        if key in (curses.KEY_BACKSPACE, 127, 8):
            if self.cmd_buf: self.cmd_buf = self.cmd_buf[:-1]
            else: self.mode = self.NORMAL
            return

        if key in (curses.KEY_ENTER, 10, 13):
            self.exec_cmd(self.cmd_buf.strip())
            if self.mode == self.COMMAND: self.mode = self.NORMAL
            self.cmd_buf = ""
            return

        if 32 <= key < 256:
            self.cmd_buf += chr(key)

    def exec_cmd(self, cmd: str) -> None:
        if cmd == "w":
            self.save()
        elif cmd == "q":
            if self.modified:
                self.flash("Unsaved changes! :q! to force quit, :wq to save & quit")
            else:
                self.running = False
        elif cmd == "q!":
            self.running = False
        elif cmd in ("wq", "x"):
            if self.save(): self.running = False
        elif cmd.startswith("w "):
            new_name     = cmd[2:].strip()
            par          = self.pw_path.rsplit("/", 1)
            par_key      = par[0] if len(par) > 1 else "~"
            self.pw_path  = f"{par_key}/{new_name}"
            self.filename = new_name
            self.is_pwe   = new_name.endswith(".pwe")
            self.save()
        else:
            self.flash(f"Not a tpwdit command: :{cmd}")
            self.mode = self.NORMAL

    # ── Main loop ────────────────────────────────────────────────────────────

    def run(self, scr) -> None:
        init_colors()
        curses.curs_set(1)
        scr.keypad(True)
        scr.timeout(100)
        self.load()

        while self.running:
            h, _ = scr.getmaxyx()
            self.scroll(h)
            self.draw(scr)

            key = scr.getch()
            if key == curses.ERR:
                continue

            if self.mode == self.NORMAL:
                self.handle_normal(key)
            elif self.mode == self.INSERT:
                self.handle_insert(key)
            elif self.mode == self.COMMAND:
                self.handle_command(key)


# ── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) < 2:
        print("tpwdit: TUI PenguWarp eDITor")
        print("Usage: tpwdit <filename>")
        return

    pw_path = sys.argv[1]

    if not os.path.exists(SYSTEM_FILE):
        print(f"tpwdit: system file not found → {SYSTEM_FILE}")
        print("Looked one level above packages/ — is the kernel there?")
        return

    editor = Editor(pw_path)
    try:
        curses.wrapper(editor.run)
    except KeyboardInterrupt:
        pass

    print(f'tpwdit: Done editing "{editor.filename}"'
          + (" (unsaved changes discarded)" if editor.modified else ""))


if __name__ == "__main__":
    main()
