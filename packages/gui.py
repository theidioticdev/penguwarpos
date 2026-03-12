"""
gui.py — PenguWarp OS  •  PenguWin Desktop Environment
Pygame-based DE: gruvbox colours, Windows-style titlebar, top taskbar,
start menu, desktop icons, draggable windows.
"""

import os
import time
import threading
import queue
import sys

import pygame
import pygame.gfxdraw

import system as S
from system import save_system, get_dynamic_ram, SYSTEM_FILE

# ── Gruvbox palette ───────────────────────────────────────────────────────────
BG = (40,  40,  40)
BG1 = (60,  56,  54)
BG2 = (80,  73,  69)
BG_HARD = (29,  32,  33)
FG = (235, 219, 178)
YELLOW = (250, 189,  47)
YELLOW_DIM = (215, 153,  33)
ORANGE = (254, 128,  25)
ORANGE_DIM = (214,  93,  14)
RED = (251,  73,  52)
GREEN = (184, 187,  38)
AQUA = (142, 192, 124)
GRAY = (146, 131, 116)

BTN_CLOSE = (251,  73,  52)
WHITE = (255, 255, 255)
TASKBAR_H = 32
FONT_SMALL = 12
FONT_MED = 14
FONT_LARGE = 20
TITLEBAR_H = 26
ICON_SIZE = 64
TERM_FONT = 11
TERM_LINE_H = 14

# ── Helpers ───────────────────────────────────────────────────────────────────


def _aa_rounded_rect(surf, rect, color, radius=8, alpha=255):
    x, y, w, h = rect
    r = min(radius, w // 2, h // 2)
    shape = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(shape, (*color, alpha), (0, 0, w, h), border_radius=r)
    surf.blit(shape, (x, y))


def _text(surf, font, txt, color, x, y, anchor="topleft"):
    s = font.render(str(txt), True, color)
    r = s.get_rect(**{anchor: (x, y)})
    surf.blit(s, r)
    return r


def _shadow(surf, rect, radius=8, strength=60):
    for i in range(6, 0, -1):
        a = strength * i // 6
        sr = (rect[0]-i, rect[1]+i, rect[2]+i*2, rect[3]+i)
        _aa_rounded_rect(surf, sr, BG_HARD, radius+i, alpha=a)


# ── Widget: Button ────────────────────────────────────────────────────────────

class Button:
    def __init__(self, rect, label, color=ORANGE_DIM, hover_color=ORANGE,
                 text_color=FG, radius=6, font=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.radius = radius
        self.font = font
        self.hovered = False

    def draw(self, surf):
        col = self.hover_color if self.hovered else self.color
        _aa_rounded_rect(surf, self.rect, col, self.radius)
        if self.font and self.label:
            _text(surf, self.font, self.label, self.text_color,
                  self.rect.centerx, self.rect.centery, anchor="center")

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


# ── Widget: TextInput ─────────────────────────────────────────────────────────

class TextInput:
    def __init__(self, rect, hint="", password=False, font=None):
        self.rect = pygame.Rect(rect)
        self.hint = hint
        self.password = password
        self.font = font
        self.text = ""
        self.active = False

    def draw(self, surf):
        border_col = YELLOW if self.active else BG2
        _aa_rounded_rect(surf, self.rect, BG1, 5)
        pygame.draw.rect(surf, border_col, self.rect, 1, border_radius=5)
        display = ("•" * len(self.text)) if self.password else self.text
        if display and self.font:
            _text(surf, self.font, display, FG,
                  self.rect.x + 8, self.rect.centery, anchor="midleft")
        elif self.hint and self.font:
            _text(surf, self.font, self.hint, GRAY,
                  self.rect.x + 8, self.rect.centery, anchor="midleft")
        if self.active:
            cx = self.rect.x + 8
            if display and self.font:
                cx += self.font.size(display)[0] + 2
            if int(time.time() * 2) % 2 == 0:
                pygame.draw.line(surf, FG,
                                 (cx, self.rect.y + 5),
                                 (cx, self.rect.bottom - 5), 1)

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return "enter"
            elif event.unicode and event.unicode.isprintable():
                self.text += event.unicode
        return None


# ── Draggable Window base ─────────────────────────────────────────────────────

_window_order: list = []


class Window:
    def __init__(self, title, x, y, w, h, on_close=None):
        self.title = title
        self.rect = pygame.Rect(x, y, w, h)
        self.on_close = on_close
        self.alive = True
        self.dragging = False
        self.drag_off = (0, 0)
        _window_order.append(self)

    @property
    def titlebar_rect(self):
        return pygame.Rect(self.rect.x, self.rect.y, self.rect.w, TITLEBAR_H)

    @property
    def close_btn(self):
        return pygame.Rect(self.rect.right - 20, self.rect.y + 7, 14, 14)

    @property
    def content_rect(self):
        return pygame.Rect(self.rect.x, self.rect.y + TITLEBAR_H,
                           self.rect.w, self.rect.h - TITLEBAR_H)

    def draw_chrome(self, surf, fonts):
        _shadow(surf, self.rect)
        _aa_rounded_rect(surf, self.rect, BG, radius=8)
        _aa_rounded_rect(surf, self.titlebar_rect, BG_HARD, radius=8)
        pygame.draw.rect(surf, BG_HARD,
                         (self.rect.x, self.rect.y + TITLEBAR_H - 6,
                          self.rect.w, 6))
        _text(surf, fonts["med"], self.title, FG,
              self.rect.x + 10, self.rect.y + TITLEBAR_H // 2, anchor="midleft")
        pygame.draw.circle(surf, BTN_CLOSE, self.close_btn.center, 7)

    def handle_chrome(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_btn.collidepoint(event.pos):
                self.alive = False
                if self.on_close:
                    self.on_close()
                return True
            if self.titlebar_rect.collidepoint(event.pos):
                self.dragging = True
                self.drag_off = (event.pos[0] - self.rect.x,
                                 event.pos[1] - self.rect.y)
                if self in _window_order:
                    _window_order.remove(self)
                    _window_order.append(self)
                return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        if event.type == pygame.MOUSEMOTION and self.dragging:
            sw, sh = pygame.display.get_surface().get_size()
            self.rect.x = max(
                0, min(event.pos[0] - self.drag_off[0], sw - self.rect.w))
            self.rect.y = max(TASKBAR_H, min(
                event.pos[1] - self.drag_off[1], sh - TITLEBAR_H))
        return False


# ── App: System Info ──────────────────────────────────────────────────────────

class SysinfoWindow(Window):
    def __init__(self, fonts):
        super().__init__("Gardener — System Info", 200, 80, 400, 280)
        self.fonts = fonts

    def draw(self, surf):
        if not self.alive:
            return
        self.draw_chrome(surf, self.fonts)
        cr = self.content_rect
        pygame.draw.rect(surf, BG, cr)
        uptime = int(time.time() - S.start_time)
        m, s = divmod(uptime, 60)
        h, m = divmod(m, 60)
        ram = get_dynamic_ram()
        disk = round(os.path.getsize(SYSTEM_FILE)/1024,
                     1) if os.path.exists(SYSTEM_FILE) else 0
        rows = [
            ("User",   f"{S.user}@{S.hostname}"),
            ("OS",     'PenguWarp v0.1.8 "Lemon"'),
            ("Kernel", "v0.1.8-lemon-dev_x86_64"),
            ("Shell",  "PWShell"),
            ("Uptime", f"{h:02d}:{m:02d}:{s:02d}"),
            ("Pkgs",   f"{len(S.installed_packages)} installed"),
            ("RAM",    f"{ram} MB / 128 MB"),
            ("Disk",   f"{disk} KB / 512 KB"),
        ]
        y = cr.y + 10
        for label, val in rows:
            _text(surf, self.fonts["small"], label, GRAY,  cr.x + 14, y)
            _text(surf, self.fonts["small"], val,   FG,    cr.x + 100, y)
            y += 22
        pct = min(ram / 128, 1.0)
        bw = cr.w - 28
        pygame.draw.rect(surf, BG2, (cr.x+14, y+4, bw, 8), border_radius=4)
        col = GREEN if pct < 0.6 else YELLOW if pct < 0.85 else RED
        pygame.draw.rect(
            surf, col, (cr.x+14, y+4, int(bw*pct), 8), border_radius=4)

    def handle(self, event):
        self.handle_chrome(event)


# ── App: Calculator ───────────────────────────────────────────────────────────

class CalcWindow(Window):
    def __init__(self, fonts):
        super().__init__("WarpCalc", 300, 100, 290, 390)
        self.fonts = fonts
        self.display = ""
        self.history = []
        self._build_btns()

    def _build_btns(self):
        self.btns = []
        rows = [["7", "8", "9", "/"], ["4", "5", "6", "*"],
                ["1", "2", "3", "-"], ["C", "0", "=", "+"], ["+/-", ".", "%", "**"]]
        bw, bh, pad = 54, 40, 6
        for ri, row in enumerate(rows):
            for ci, lbl in enumerate(row):
                col = (ORANGE_DIM if lbl in "/+-*%**" else
                       RED if lbl == "C" else GREEN if lbl == "=" else BG1)
                x = self.rect.x + 10 + ci*(bw+pad)
                y = self.rect.y + TITLEBAR_H + 76 + ri*(bh+pad)
                self.btns.append([lbl, pygame.Rect(x, y, bw, bh), col, False])

    def _click(self, lbl):
        import ast
        import operator as op
        if lbl == "C":
            self.display = ""
        elif lbl == "⌫":
            self.display = self.display[:-1]
        elif lbl == "+/-":
            self.display = str(-float(self.display)) if self.display else ""
        elif lbl == "=":
            try:
                allowed = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
                           ast.Div: op.truediv, ast.USub: op.neg, ast.Pow: op.pow, ast.Mod: op.mod}

                def ev(n):
                    match n:
                        case ast.Constant(value=v) if isinstance(v, (int, float)): return float(v)
                        case ast.BinOp(left=l, op=o, right=r): return allowed[type(o)](ev(l), ev(r))
                        case ast.UnaryOp(op=o, operand=v): return allowed[type(o)](ev(v))
                        case _: raise ValueError
                res = ev(ast.parse(self.display, mode="eval").body)
                r = str(int(res)) if res == int(res) else str(round(res, 6))
                self.history.append(f"{self.display}={r}")
                if len(self.history) > 4:
                    self.history.pop(0)
                self.display = r
            except:
                self.display = "Error"
        else:
            self.display += lbl

    def draw(self, surf):
        if not self.alive:
            return
        self.draw_chrome(surf, self.fonts)
        cr = self.content_rect
        pygame.draw.rect(surf, BG, cr)
        y = cr.y + 4
        for h in self.history[-3:]:
            _text(surf, self.fonts["small"], h, GRAY, cr.x+10, y)
            y += 18
        _aa_rounded_rect(surf, (cr.x+8, cr.y+44, cr.w-16, 26), BG1, 5)
        _text(surf, self.fonts["med"], self.display or "0", FG,
              cr.right-14, cr.y+57, anchor="midright")
        bw, bh, pad = 54, 40, 6
        x0 = self.rect.x+10
        y0 = self.rect.y+TITLEBAR_H+76
        for i, (lbl, _, col, hov) in enumerate(self.btns):
            row, ci = divmod(i, 4)
            r = pygame.Rect(x0+ci*(bw+pad), y0+row*(bh+pad), bw, bh)
            self.btns[i][1] = r
            c = ORANGE if hov else col
            _aa_rounded_rect(surf, r, c, 5)
            _text(surf, self.fonts["small"], lbl, FG,
                  r.centerx, r.centery, anchor="center")

    def handle(self, event):
        if self.handle_chrome(event):
            return
        if event.type == pygame.MOUSEMOTION:
            for b in self.btns:
                b[3] = b[1].collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for lbl, r, _, _ in self.btns:
                if r.collidepoint(event.pos):
                    self._click(lbl)


# ── App: File Browser ─────────────────────────────────────────────────────────

class FileBrowserWindow(Window):
    def __init__(self, fonts):
        super().__init__("Tree — File Browser", 120, 70, 460, 400)
        self.fonts = fonts
        self.path = S.current_dir
        self.scroll = 0
        self.selected = None

    def _entries(self):
        node = S.filesystem.get(self.path, {})
        entries = []
        for name in sorted(node.get("contents", [])):
            full = ("~/"+name) if self.path == "~" else (self.path+"/"+name)
            t = S.filesystem.get(full, {}).get("type", "file")
            entries.append((name, full, t))
        return entries

    def draw(self, surf):
        if not self.alive:
            return
        self.draw_chrome(surf, self.fonts)
        cr = self.content_rect
        pygame.draw.rect(surf, BG, cr)
        # toolbar
        up_r = pygame.Rect(cr.x+8,    cr.y+6, 58, 22)
        home_r = pygame.Rect(cr.x+72,   cr.y+6, 68, 22)
        for r, lbl, hov_attr in [(up_r, "^ Up", "_uh"), (home_r, "~ Home", "_hh")]:
            hov = getattr(self, hov_attr, False)
            _aa_rounded_rect(surf, r, ORANGE if hov else ORANGE_DIM, 4)
            _text(surf, self.fonts["small"], lbl, FG,
                  r.centerx, r.centery, anchor="center")
        _text(surf, self.fonts["small"], self.path,
              YELLOW, cr.x+148, cr.y+14, anchor="midleft")
        pygame.draw.line(surf, BG2, (cr.x, cr.y+32), (cr.right, cr.y+32))
        entries = self._entries()
        row_h = 24
        clip = surf.get_clip()
        surf.set_clip(pygame.Rect(cr.x, cr.y+34, cr.w, cr.h-34))
        y = cr.y + 40 - self.scroll
        for name, full, ftype in entries:
            if cr.y+34 <= y <= cr.bottom:
                row_r = pygame.Rect(cr.x+4, y-2, cr.w-8, row_h-2)
                if self.selected == full:
                    _aa_rounded_rect(surf, row_r, BG2, 4)
                icon = "[D]" if ftype == "dir" else "[F]"
                col = YELLOW if ftype == "dir" else FG
                _text(surf, self.fonts["small"], f"{icon}  {name}", col,
                      cr.x+12, y+row_h//2, anchor="midleft")
            y += row_h
        surf.set_clip(clip)

    def handle(self, event):
        if self.handle_chrome(event):
            return
        cr = self.content_rect
        self._uh = False
        self._hh = False
        if hasattr(event, "pos"):
            up_r = pygame.Rect(cr.x+8,  cr.y+6, 58, 22)
            home_r = pygame.Rect(cr.x+72, cr.y+6, 68, 22)
            self._uh = up_r.collidepoint(event.pos)
            self._hh = home_r.collidepoint(event.pos)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._uh:
                    parts = self.path.split("/")
                    self.path = "/".join(parts[:-1]) if len(parts) > 1 else "~"
                    self.scroll = 0
                    return
                if self._hh:
                    self.path = "~"
                    self.scroll = 0
                    return
        if event.type == pygame.MOUSEWHEEL:
            if cr.collidepoint(pygame.mouse.get_pos()):
                self.scroll = max(0, self.scroll-event.y*20)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            entries = self._entries()
            y = cr.y+40-self.scroll
            for name, full, ftype in entries:
                if pygame.Rect(cr.x+4, y-2, cr.w-8, 22).collidepoint(event.pos):
                    if ftype == "dir":
                        self.path = full
                        self.scroll = 0
                    else:
                        self.selected = full
                y += 24


# ── App: Terminal ─────────────────────────────────────────────────────────────

class TerminalWindow(Window):
    def __init__(self, fonts):
        super().__init__("PWShell Terminal", 150, 80, 660, 460)
        self.fonts = fonts
        self.lines = ['PWShell -- PenguWarp v0.1.8 "Lemon"',
                      "Type 'help' for available commands.", ""]
        self.input_text = ""
        self.scroll = 0
        self.running = False
        self.q: queue.Queue = queue.Queue()

    def _run_cmd(self, cmd):
        import io
        import sys as _sys
        from commands import execute_command

        class W(io.TextIOBase):
            def __init__(self, q): self.q = q

            def write(self, s):
                if s:
                    self.q.put(s)
                return len(s)

            def flush(self): pass
        old = _sys.stdout
        _sys.stdout = W(self.q)
        try:
            execute_command(cmd)
        except SystemExit:
            self.q.put("error: cannot exit from terminal\n")
        except Exception as e:
            self.q.put(f"error: {e}\n")
        finally:
            _sys.stdout = old
            self.running = False
            self.q.put("\x00PROMPT\x00")

    def _submit(self):
        cmd = self.input_text.strip()
        self.input_text = ""
        prompt = f"{S.user}@{S.hostname}:{S.current_dir}$ "
        self.lines.append(prompt+cmd)
        if not cmd:
            return
        if cmd.split()[0] in {"startx", "poweroff", "clear"}:
            self.lines.append(f"[terminal] not available here\n")
            return
        self.running = True
        threading.Thread(target=self._run_cmd,
                         args=(cmd,), daemon=True).start()

    def _poll(self):
        while not self.q.empty():
            try:
                chunk = self.q.get_nowait()
                if chunk == "\x00PROMPT\x00":
                    self.lines.append("")
                else:
                    import re
                    clean = re.sub(r'\x1b\[[0-9;]*[mGKHF]', '', chunk)
                    # split on newlines but don't add trailing blank from print()'s \n
                    parts = clean.split("\n")
                    for i, part in enumerate(parts):
                        # skip the trailing empty string that print() always adds
                        if i == len(parts)-1 and part == "":
                            continue
                        self.lines.append(part)
            except queue.Empty:
                break
        if len(self.lines) > 500:
            self.lines = self.lines[-500:]

    def draw(self, surf):
        if not self.alive:
            return
        self._poll()
        self.draw_chrome(surf, self.fonts)
        cr = self.content_rect
        pygame.draw.rect(surf, BG_HARD, cr)
        tf = self.fonts.get("term", self.fonts["mono"])
        line_h = TERM_LINE_H
        visible = (cr.h - 36) // line_h
        start = max(0, len(self.lines)-visible-self.scroll)
        clip = surf.get_clip()
        surf.set_clip(pygame.Rect(cr.x, cr.y, cr.w, cr.h-30))
        y = cr.y + 4
        for line in self.lines[start:start+visible]:
            if line:
                _text(surf, tf, line, FG, cr.x+8, y)
            y += line_h
        surf.set_clip(clip)
        pygame.draw.line(surf, BG2, (cr.x, cr.bottom-28),
                         (cr.right, cr.bottom-28))
        prompt = f"{S.user}@{S.hostname}:{S.current_dir}$ "
        pw = tf.size(prompt)[0]
        _text(surf, tf, prompt, GREEN, cr.x+6, cr.bottom-20, anchor="midleft")
        _text(surf, tf, self.input_text, FG, cr.x +
              6+pw, cr.bottom-20, anchor="midleft")
        if int(time.time()*2) % 2 == 0:
            cx = cr.x+6+pw+tf.size(self.input_text)[0]
            pygame.draw.line(surf, FG, (cx, cr.bottom-26), (cx, cr.bottom-12))

    def handle(self, event):
        if self.handle_chrome(event):
            return
        cr = self.content_rect
        if event.type == pygame.MOUSEWHEEL:
            if cr.collidepoint(pygame.mouse.get_pos()):
                self.scroll = max(0, min(self.scroll-event.y,
                                  max(0, len(self.lines)-10)))
        if event.type == pygame.KEYDOWN:
            if not self.running:
                if event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._submit()
                    self.scroll = 0
                elif event.unicode and event.unicode.isprintable():
                    self.input_text += event.unicode


# ── App: About ────────────────────────────────────────────────────────────────

class AboutWindow(Window):
    def __init__(self, fonts):
        super().__init__("About PenguWarp", 340, 180, 300, 240)
        self.fonts = fonts

    def draw(self, surf):
        if not self.alive:
            return
        self.draw_chrome(surf, self.fonts)
        cr = self.content_rect
        pygame.draw.rect(surf, BG, cr)
        lines = [
            ("PenguWarp OS",              YELLOW, "large"),
            ('v0.1.8 "Lemon" Testing',    ORANGE, "med"),
            ("", FG, "small"),
            ("Python-based OS simulation", FG, "small"),
            ("Desktop: PenguWin DE",      FG, "small"),
            ("Shell:   PWShell",          FG, "small"),
            ("GUI:     Pygame",           FG, "small"),
            ("Theme:   Gruvbox Dark",     FG, "small"),
            ("", FG, "small"),
            (f"User: {S.user}@{S.hostname}", GRAY, "small"),
        ]
        y = cr.y+12
        for txt, col, size in lines:
            if txt:
                _text(surf, self.fonts[size], txt, col,
                      cr.centerx, y, anchor="midtop")
            y += self.fonts[size].get_height()+4

    def handle(self, event):
        self.handle_chrome(event)


# ── App: Text Viewer ─────────────────────────────────────────────────────────

class TextViewerWindow(Window):
    def __init__(self, fonts, filename="", content=""):
        super().__init__(f"Viewer — {filename}", 180, 100, 500, 400)
        self.fonts = fonts
        self.filename = filename
        self.lines = content.split("\n")
        self.scroll = 0

    def draw(self, surf):
        if not self.alive:
            return
        self.draw_chrome(surf, self.fonts)
        cr = self.content_rect
        pygame.draw.rect(surf, BG_HARD, cr)
        line_h = 18
        visible = (cr.h - 8) // line_h
        start = max(0, self.scroll)
        clip = surf.get_clip()
        surf.set_clip(cr)
        y = cr.y + 6
        for line in self.lines[start:start+visible]:
            _text(surf, self.fonts["mono"], line, FG, cr.x+10, y)
            y += line_h
        surf.set_clip(clip)
        # scrollbar
        if len(self.lines) > visible:
            sb_h = cr.h
            thumb = max(20, sb_h * visible // len(self.lines))
            thumb_y = cr.y + sb_h * start // max(1, len(self.lines))
            pygame.draw.rect(surf, BG2,  (cr.right-6, cr.y, 6, sb_h))
            pygame.draw.rect(surf, GRAY, (cr.right-6, thumb_y,
                             6, thumb), border_radius=3)

    def handle(self, event):
        if self.handle_chrome(event):
            return
        if event.type == pygame.MOUSEWHEEL:
            if self.content_rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll = max(
                    0, min(self.scroll - event.y*2, max(0, len(self.lines)-10)))


# ── App: GPWDIT Editor ────────────────────────────────────────────────────────

class GPWDITWindow(Window):
    def __init__(self, fonts, filepath=None):
        super().__init__("GPWDIT — Editor", 160, 80, 620, 480)
        self.fonts = fonts
        self.filepath = filepath
        self.lines = [""]
        self.cursor_row = 0
        self.cursor_col = 0
        self.scroll = 0
        self.dirty = False
        self.status = "New file — Ctrl+S save  Ctrl+O open"
        if filepath:
            node = S.filesystem.get(filepath, {})
            if node.get("type") == "file":
                self.lines = node.get("content", "").split("\n")
                self.status = f"Opened: {filepath}"

    def _save(self):
        if not self.filepath:
            self.status = "No path set — use pwdit <file> from terminal to open"
            return
        content = "\n".join(self.lines)
        if self.filepath in S.filesystem:
            S.filesystem[self.filepath]["content"] = content
        else:
            # find parent dir and add entry
            parts = self.filepath.rsplit("/", 1)
            parent = parts[0] if len(parts) > 1 else "~"
            fname = parts[-1]
            if parent in S.filesystem:
                if fname not in S.filesystem[parent].get("contents", []):
                    S.filesystem[parent].setdefault(
                        "contents", []).append(fname)
            S.filesystem[self.filepath] = {"type": "file", "content": content}
        save_system()
        self.dirty = False
        self.status = f"Saved: {self.filepath}"

    def draw(self, surf):
        if not self.alive:
            return
        self.draw_chrome(surf, self.fonts)
        cr = self.content_rect
        pygame.draw.rect(surf, BG_HARD, cr)

        line_h = 18
        gutter_w = 48
        visible = (cr.h - 26) // line_h

        # gutter bg
        pygame.draw.rect(surf, BG1, (cr.x, cr.y, gutter_w, cr.h - 24))
        pygame.draw.line(surf, BG2, (cr.x+gutter_w, cr.y),
                         (cr.x+gutter_w, cr.bottom-24))

        clip = surf.get_clip()
        surf.set_clip(pygame.Rect(cr.x, cr.y, cr.w, cr.h-24))

        for i, line in enumerate(self.lines[self.scroll:self.scroll+visible]):
            abs_i = i + self.scroll
            y = cr.y + i * line_h + 4
            # highlight current line
            if abs_i == self.cursor_row:
                pygame.draw.rect(surf, BG2, (cr.x+gutter_w+1,
                                 y-1, cr.w-gutter_w-1, line_h))
            # line number
            _text(surf, self.fonts["mono"], str(abs_i+1), GRAY,
                  cr.x+gutter_w-6, y, anchor="topright")
            # line content
            _text(surf, self.fonts["mono"], line, FG, cr.x+gutter_w+6, y)
            # cursor
            if abs_i == self.cursor_row:
                cx = cr.x + gutter_w + 6 + \
                    self.fonts["mono"].size(line[:self.cursor_col])[0]
                if int(time.time()*2) % 2 == 0:
                    pygame.draw.line(surf, YELLOW, (cx, y),
                                     (cx, y+line_h-2), 2)

        surf.set_clip(clip)

        # status bar
        pygame.draw.rect(surf, BG1, (cr.x, cr.bottom-22, cr.w, 22))
        dirty_marker = "●" if self.dirty else "○"
        _text(surf, self.fonts["small"],
              f" {dirty_marker}  {self.status}   Ln {
                  self.cursor_row+1}  Col {self.cursor_col+1}",
              GRAY, cr.x+6, cr.bottom-14, anchor="midleft")

    def handle(self, event):
        if self.handle_chrome(event):
            return
        if event.type == pygame.MOUSEWHEEL:
            if self.content_rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll = max(
                    0, min(self.scroll - event.y, max(0, len(self.lines)-5)))
        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            if mods & pygame.KMOD_CTRL:
                if event.key == pygame.K_s:
                    self._save()
                    return
                if event.key == pygame.K_HOME:
                    self.cursor_row = 0
                    self.cursor_col = 0
                    return
                if event.key == pygame.K_END:
                    self.cursor_row = len(self.lines)-1
                    self.cursor_col = len(self.lines[-1])
                    return

            row = self.lines[self.cursor_row]
            if event.key == pygame.K_RETURN:
                rest = row[self.cursor_col:]
                self.lines[self.cursor_row] = row[:self.cursor_col]
                self.cursor_row += 1
                self.lines.insert(self.cursor_row, rest)
                self.cursor_col = 0
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_col > 0:
                    self.lines[self.cursor_row] = row[:self.cursor_col -
                                                      1] + row[self.cursor_col:]
                    self.cursor_col -= 1
                elif self.cursor_row > 0:
                    prev = self.lines[self.cursor_row-1]
                    self.cursor_col = len(prev)
                    self.lines[self.cursor_row-1] = prev + row
                    self.lines.pop(self.cursor_row)
                    self.cursor_row -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_col < len(row):
                    self.lines[self.cursor_row] = row[:self.cursor_col] + \
                        row[self.cursor_col+1:]
                elif self.cursor_row < len(self.lines)-1:
                    self.lines[self.cursor_row] += self.lines.pop(
                        self.cursor_row+1)
            elif event.key == pygame.K_LEFT:
                if self.cursor_col > 0:
                    self.cursor_col -= 1
                elif self.cursor_row > 0:
                    self.cursor_row -= 1
                    self.cursor_col = len(self.lines[self.cursor_row])
            elif event.key == pygame.K_RIGHT:
                if self.cursor_col < len(row):
                    self.cursor_col += 1
                elif self.cursor_row < len(self.lines)-1:
                    self.cursor_row += 1
                    self.cursor_col = 0
            elif event.key == pygame.K_UP:
                if self.cursor_row > 0:
                    self.cursor_row -= 1
                    self.cursor_col = min(self.cursor_col, len(
                        self.lines[self.cursor_row]))
            elif event.key == pygame.K_DOWN:
                if self.cursor_row < len(self.lines)-1:
                    self.cursor_row += 1
                    self.cursor_col = min(self.cursor_col, len(
                        self.lines[self.cursor_row]))
            elif event.key == pygame.K_HOME:
                self.cursor_col = 0
            elif event.key == pygame.K_END:
                self.cursor_col = len(self.lines[self.cursor_row])
            elif event.key == pygame.K_TAB:
                self.lines[self.cursor_row] = row[:self.cursor_col] + \
                    "    " + row[self.cursor_col:]
                self.cursor_col += 4
            elif event.unicode and event.unicode.isprintable():
                self.lines[self.cursor_row] = row[:self.cursor_col] + \
                    event.unicode + row[self.cursor_col:]
                self.cursor_col += 1
                self.dirty = True
            else:
                return
            self.dirty = True
            # scroll to keep cursor visible
            line_h = 18
            visible = (self.content_rect.h - 26) // line_h
            if self.cursor_row < self.scroll:
                self.scroll = self.cursor_row
            if self.cursor_row >= self.scroll + visible:
                self.scroll = self.cursor_row - visible + 1


# ── App: PenguPaint ───────────────────────────────────────────────────────────

class PenguPaintWindow(Window):
    def __init__(self, fonts):
        super().__init__("PenguPaint", 100, 80, 600, 460)
        self.fonts = fonts
        self.canvas = None
        self.drawing = False
        self.last_pos = None
        self.color = ORANGE
        self.brush_size = 4
        self.palette = [RED, ORANGE, YELLOW, GREEN, AQUA, FG, GRAY, BG2,
                        (255, 255, 255), (0, 0, 0), (100, 200, 255), (200, 100, 255)]
        self.tool = "brush"  # brush | eraser

    def _ensure_canvas(self):
        cr = self.content_rect
        cw, ch = cr.w - 8, cr.h - 44
        if self.canvas is None or self.canvas.get_size() != (cw, ch):
            old = self.canvas
            self.canvas = pygame.Surface((cw, ch))
            self.canvas.fill(BG_HARD)
            if old:
                self.canvas.blit(old, (0, 0))

    def draw(self, surf):
        if not self.alive:
            return
        self._ensure_canvas()
        self.draw_chrome(surf, self.fonts)
        cr = self.content_rect
        pygame.draw.rect(surf, BG, cr)

        # toolbar
        tool_y = cr.y + 6
        # palette
        px = cr.x + 8
        for i, col in enumerate(self.palette):
            r = pygame.Rect(px + i*22, tool_y, 18, 18)
            pygame.draw.rect(surf, col, r, border_radius=3)
            if col == self.color:
                pygame.draw.rect(surf, WHITE, r, 2, border_radius=3)

        # brush size
        bx = cr.x + 8 + len(self.palette)*22 + 10
        for i, sz in enumerate([2, 4, 8, 14]):
            r = pygame.Rect(bx + i*26, tool_y+1, 22, 16)
            active = sz == self.brush_size
            _aa_rounded_rect(surf, r, ORANGE_DIM if active else BG1, 4)
            pygame.draw.circle(surf, FG, r.center, sz//2+1)

        # eraser button
        ex = bx + 4*26 + 8
        er = pygame.Rect(ex, tool_y, 52, 18)
        _aa_rounded_rect(surf, er, ORANGE_DIM if self.tool ==
                         "eraser" else BG1, 4)
        _text(surf, self.fonts["small"], "Eraser", FG,
              er.centerx, er.centery, anchor="center")

        # clear button
        cx2 = ex + 60
        clr = pygame.Rect(cx2, tool_y, 44, 18)
        _aa_rounded_rect(surf, clr, RED, 4)
        _text(surf, self.fonts["small"], "Clear", FG,
              clr.centerx, clr.centery, anchor="center")

        # canvas
        canvas_rect = pygame.Rect(
            cr.x+4, cr.y+32, self.canvas.get_width(), self.canvas.get_height())
        surf.blit(self.canvas, canvas_rect.topleft)
        pygame.draw.rect(surf, BG2, canvas_rect, 1)

    def handle(self, event):
        if self.handle_chrome(event):
            return
        self._ensure_canvas()
        cr = self.content_rect
        canvas_rect = pygame.Rect(cr.x+4, cr.y+32,
                                  self.canvas.get_width(), self.canvas.get_height())

        # toolbar clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            tool_y = cr.y + 6
            px = cr.x + 8
            for i, col in enumerate(self.palette):
                if pygame.Rect(px+i*22, tool_y, 18, 18).collidepoint(event.pos):
                    self.color = col
                    self.tool = "brush"
                    return
            bx = px + len(self.palette)*22 + 10
            for i, sz in enumerate([2, 4, 8, 14]):
                if pygame.Rect(bx+i*26, tool_y+1, 22, 16).collidepoint(event.pos):
                    self.brush_size = sz
                    return
            ex = bx + 4*26 + 8
            if pygame.Rect(ex, tool_y, 52, 18).collidepoint(event.pos):
                self.tool = "eraser"
                return
            cx2 = ex + 60
            if pygame.Rect(cx2, tool_y, 44, 18).collidepoint(event.pos):
                self.canvas.fill(BG_HARD)
                return

        # drawing
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if canvas_rect.collidepoint(event.pos):
                self.drawing = True
                self.last_pos = (
                    event.pos[0]-canvas_rect.x, event.pos[1]-canvas_rect.y)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.drawing = False
            self.last_pos = None
        if event.type == pygame.MOUSEMOTION and self.drawing:
            if canvas_rect.collidepoint(event.pos):
                cur = (event.pos[0]-canvas_rect.x, event.pos[1]-canvas_rect.y)
                col = BG_HARD if self.tool == "eraser" else self.color
                sz = self.brush_size * 3 if self.tool == "eraser" else self.brush_size
                if self.last_pos:
                    pygame.draw.line(self.canvas, col,
                                     self.last_pos, cur, sz*2)
                pygame.draw.circle(self.canvas, col, cur, sz)
                self.last_pos = cur


# ── Desktop Icon ──────────────────────────────────────────────────────────────

class DesktopIcon:
    def __init__(self, label, x, y, callback, fonts):
        self.label = label
        self.rect = pygame.Rect(x, y, ICON_SIZE, ICON_SIZE+20)
        self.callback = callback
        self.fonts = fonts
        self.hovered = False
        self._last_click = 0.0

    def draw(self, surf):
        col = BG2 if self.hovered else BG1
        _aa_rounded_rect(surf, (self.rect.x, self.rect.y,
                         ICON_SIZE, ICON_SIZE), col, 10)
        abbr = self.label[:2].upper()
        _text(surf, self.fonts["large"], abbr, YELLOW,
              self.rect.centerx, self.rect.y+ICON_SIZE//2, anchor="center")
        _text(surf, self.fonts["small"], self.label, FG,
              self.rect.centerx, self.rect.y+ICON_SIZE+4, anchor="midtop")

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()


# ── Start Menu ────────────────────────────────────────────────────────────────

class StartMenu:
    ITEMS = [
        ("File Browser", "browser"),
        ("Terminal",     "terminal"),
        ("GPWDIT",       "editor"),
        ("PenguPaint",   "paint"),
        ("WarpCalc",     "calc"),
        ("Gardener",     "sysinfo"),
        ("About",        "about"),
    ]
    W = 200
    ITEM_H = 30

    def __init__(self, fonts, open_app_cb, logout_cb, tty_cb):
        self.fonts = fonts
        self.open_app = open_app_cb
        self.logout = logout_cb
        self.tty = tty_cb
        self.visible = False
        self.hovered = -1

    def _h(self):
        return 40 + len(self.ITEMS)*self.ITEM_H + 10 + 2*(self.ITEM_H+4)

    def _rect(self, sh):
        return pygame.Rect(0, sh-TASKBAR_H-self._h(), self.W, self._h())

    def draw(self, surf):
        if not self.visible:
            return
        sw, sh = surf.get_size()
        r = self._rect(sh)
        _shadow(surf, r, strength=80)
        _aa_rounded_rect(surf, r, BG_HARD, 8)
        pygame.draw.rect(surf, BG2, r, 1, border_radius=8)
        _aa_rounded_rect(surf, (r.x, r.y, r.w, 36), BG1, 8)
        _text(surf, self.fonts["med"], f"  {S.user}@{S.hostname}", YELLOW,
              r.x+10, r.y+18, anchor="midleft")
        y = r.y+42
        for i, (label, _) in enumerate(self.ITEMS):
            if label == "About":
                pygame.draw.line(surf, BG2, (r.x+8, y-3), (r.right-8, y-3))
            row = pygame.Rect(r.x+4, y, r.w-8, self.ITEM_H)
            if self.hovered == i:
                _aa_rounded_rect(surf, row, BG2, 4)
            _text(surf, self.fonts["small"], label, FG,
                  r.x+14, y+self.ITEM_H//2, anchor="midleft")
            y += self.ITEM_H
        pygame.draw.line(surf, BG2, (r.x+8, y+2), (r.right-8, y+2))
        y += 8
        for i2, (label, col) in enumerate([("Logout", ORANGE_DIM), ("Exit to TTY", GRAY)]):
            idx = len(self.ITEMS)+i2
            row = pygame.Rect(r.x+4, y, r.w-8, self.ITEM_H)
            if self.hovered == idx:
                _aa_rounded_rect(surf, row, BG2, 4)
            _text(surf, self.fonts["small"], label, col,
                  r.x+14, y+self.ITEM_H//2, anchor="midleft")
            y += self.ITEM_H+4

    def handle(self, event, sh):
        if not self.visible:
            return False
        r = self._rect(sh)
        if event.type == pygame.MOUSEMOTION:
            self.hovered = -1
            y = r.y+42
            for i in range(len(self.ITEMS)):
                if pygame.Rect(r.x+4, y, r.w-8, self.ITEM_H).collidepoint(event.pos):
                    self.hovered = i
                y += self.ITEM_H
            y += 8
            for i2 in range(2):
                if pygame.Rect(r.x+4, y, r.w-8, self.ITEM_H).collidepoint(event.pos):
                    self.hovered = len(self.ITEMS)+i2
                y += self.ITEM_H+4
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not r.collidepoint(event.pos):
                self.visible = False
                return False
            y = r.y+42
            for i, (label, key) in enumerate(self.ITEMS):
                if pygame.Rect(r.x+4, y, r.w-8, self.ITEM_H).collidepoint(event.pos):
                    self.open_app(key)
                    self.visible = False
                    return True
                y += self.ITEM_H
            y += 8
            for i2, action in enumerate([self.logout, self.tty]):
                if pygame.Rect(r.x+4, y, r.w-8, self.ITEM_H).collidepoint(event.pos):
                    action()
                    self.visible = False
                    return True
                y += self.ITEM_H+4
        return False


# ── Taskbar ───────────────────────────────────────────────────────────────────

class Taskbar:
    def __init__(self, fonts, toggle_start_cb):
        self.fonts = fonts
        self.toggle_start = toggle_start_cb
        self.start_rect = pygame.Rect(0, 0, 90, TASKBAR_H)
        self.start_hovered = False

    def draw(self, surf, windows):
        sw = surf.get_width()
        _aa_rounded_rect(surf, (0, 0, sw, TASKBAR_H), BG_HARD)
        col = ORANGE if self.start_hovered else ORANGE_DIM
        _aa_rounded_rect(surf, self.start_rect, col, 0)
        _text(surf, self.fonts["med"], " PenguWarp", FG,
              self.start_rect.centerx, self.start_rect.centery, anchor="center")
        x = 96
        for win in windows:
            tab = pygame.Rect(x, 3, 150, TASKBAR_H-6)
            active = _window_order and _window_order[-1] is win
            _aa_rounded_rect(surf, tab, BG2 if active else BG1, 4)
            label = win.title[:20]+("…" if len(win.title) > 20 else "")
            _text(surf, self.fonts["small"], label, FG,
                  tab.x+8, tab.centery, anchor="midleft")
            x += 156
        ts = time.strftime("%H:%M:%S")
        ram = get_dynamic_ram()
        info = f"RAM {ram}MB  |  {S.user}@{S.hostname}  |  {ts}"
        _text(surf, self.fonts["small"], info, GRAY,
              sw-10, TASKBAR_H//2, anchor="midright")
        pygame.draw.line(surf, BG2, (0, TASKBAR_H-1), (sw, TASKBAR_H-1))

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.start_hovered = self.start_rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_rect.collidepoint(event.pos):
                self.toggle_start()
                return True
        return False


# ── Login Screen ──────────────────────────────────────────────────────────────

def run_login(screen, fonts) -> str:
    """
    Returns 'ok' on success, 'tty' for Exit to TTY, 'quit' if window closed.
    Sets S.user on success.
    """
    sw, sh = screen.get_size()
    bw, bh = 360, 420
    bx, by = (sw-bw)//2, (sh-bh)//2

    user_input = TextInput((bx+20, by+180, bw-40, 32),
                           "enter username...", font=fonts["small"])
    pass_input = TextInput((bx+20, by+240, bw-40, 32),
                           "enter password...", password=True, font=fonts["small"])
    login_btn = Button((bx+20, by+292, bw-40, 38), "Log In", font=fonts["med"])
    tty_btn = Button((bx+20, by+342, bw-40, 28), "Exit to TTY",
                     color=BG2, hover_color=BG1, text_color=GRAY, font=fonts["small"])

    user_input.text = S.user
    user_input.active = True
    error = ""
    clock = pygame.time.Clock()

    PENGUIN = ["    ___    ", "   <   o>  ", "   ( | )   ", "   /___\\   "]

    while True:
        sw, sh = screen.get_size()
        bx, by = (sw-bw)//2, (sh-bh)//2
        for widget in (user_input, pass_input, login_btn, tty_btn):
            widget.rect.x = bx+20
        user_input.rect.y = by+180
        pass_input.rect.y = by+240
        login_btn.rect.y = by+292
        tty_btn.rect.y = by+342

        screen.fill(BG_HARD)
        # subtle dot grid bg
        for gx in range(0, sw, 30):
            for gy in range(0, sh, 30):
                pygame.draw.circle(screen, BG1, (gx, gy), 1)

        _shadow(screen, (bx, by, bw, bh), strength=80)
        _aa_rounded_rect(screen, (bx, by, bw, bh), BG, 10)
        _aa_rounded_rect(screen, (bx, by, bw, 50), BG_HARD, 10)
        pygame.draw.rect(screen, BG_HARD, (bx, by+40, bw, 10))
        _text(screen, fonts["small"], "PenguWarp Login",
              GRAY, bx+bw//2, by+25, anchor="center")

        # penguin
        for i, line in enumerate(PENGUIN):
            _text(screen, fonts["med"], line, YELLOW,
                  bx+bw//2, by+60+i*20, anchor="midtop")

        _text(screen, fonts["large"], "PenguWarp OS",
              YELLOW, bx+bw//2, by+148, anchor="midtop")
        _text(screen, fonts["small"], f'v0.1.8 "Lemon"',
              ORANGE, bx+bw//2, by+172, anchor="midtop")

        _text(screen, fonts["small"], "Username", GRAY, bx+20, by+162)
        _text(screen, fonts["small"], "Password", GRAY, bx+20, by+222)

        user_input.draw(screen)
        pass_input.draw(screen)
        login_btn.draw(screen)
        tty_btn.draw(screen)

        if error:
            _text(screen, fonts["small"], error, RED,
                  bx+bw//2, by+380, anchor="midtop")

        _text(screen, fonts["small"], f"  {
              S.hostname}", GRAY, bx+bw//2, by+404, anchor="midtop")

        pygame.display.flip()
        clock.tick(60)

        def _try_login():
            nonlocal error
            uname = user_input.text.strip()
            pw = pass_input.text.strip()
            if not uname or not pw:
                error = "Username and password required"
                return "none"
            target = next(
                (u for u in S.users_list if u["username"] == uname), None)
            if not target:
                error = f"User '{uname}' not found"
                pass_input.text = ""
                return "none"
            from system import hash_pw
            if hash_pw(pw) != target["password"]:
                error = "Incorrect password"
                pass_input.text = ""
                return "none"
            S.user = uname
            S.current_dir = target.get("home", f"~/usr/{uname}")
            save_system()
            return "ok"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            res = user_input.handle(event)
            if res == "enter":
                pass_input.active = True
                user_input.active = False
            res = pass_input.handle(event)
            if res == "enter":
                r = _try_login()
                if r == "ok":
                    return "ok"
            if login_btn.handle(event):
                r = _try_login()
                if r == "ok":
                    return "ok"
            if tty_btn.handle(event):
                return "tty"


# ── Main entry ────────────────────────────────────────────────────────────────

def start_gui() -> str:
    """
    Run PenguWin. Returns 'logout', 'tty', or 'quit'.
    """
    pygame.init()
    pygame.display.set_caption("PenguWarp OS")
    screen = pygame.display.set_mode((1024, 768), pygame.RESIZABLE)

    fonts = {
        "small": pygame.font.SysFont("monospace", FONT_SMALL),
        "med":   pygame.font.SysFont("monospace", FONT_MED),
        "large": pygame.font.SysFont("monospace", FONT_LARGE),
        "mono":  pygame.font.SysFont("monospace", FONT_SMALL),
        "term":  pygame.font.SysFont("monospace", TERM_FONT),
    }

    clock = pygame.time.Clock()

    while True:
        # ── Login loop ────────────────────────────────────────────────────────
        result = run_login(screen, fonts)
        if result in ("quit", "tty"):
            pygame.quit()
            return result

        # ── Desktop loop ──────────────────────────────────────────────────────
        _window_order.clear()
        windows: list[Window] = []
        logout_flag = [False]
        tty_flag = [False]

        def open_app(key):
            existing = {w.__class__.__name__ for w in windows if w.alive}
            mapping = {
                "browser":  ("FileBrowserWindow", lambda: FileBrowserWindow(fonts)),
                "terminal": ("TerminalWindow", lambda: TerminalWindow(fonts)),
                "calc":     ("CalcWindow", lambda: CalcWindow(fonts)),
                "sysinfo":  ("SysinfoWindow", lambda: SysinfoWindow(fonts)),
                "about":    ("AboutWindow", lambda: AboutWindow(fonts)),
                "editor":   ("GPWDITWindow", lambda: GPWDITWindow(fonts)),
                "paint":    ("PenguPaintWindow", lambda: PenguPaintWindow(fonts)),
            }
            if key in mapping:
                cls_name, factory = mapping[key]
                if cls_name not in existing:
                    w = factory()
                    windows.append(w)

        start_menu = StartMenu(
            fonts,
            open_app,
            lambda: logout_flag.__setitem__(0, True),
            lambda: tty_flag.__setitem__(0, True),
        )
        taskbar = Taskbar(fonts, lambda: start_menu.__setattr__(
            "visible", not start_menu.visible))

        desktop_icons = []
        icon_defs = [("Browser", "browser"), ("Terminal", "terminal"),
                     ("GPWDIT", "editor"), ("Paint", "paint"),
                     ("Calc", "calc"), ("Gardener", "sysinfo"), ("About", "about")]
        ix, iy = 20, TASKBAR_H+20
        for label, key in icon_defs:
            desktop_icons.append(DesktopIcon(label, ix, iy,
                                             lambda k=key: open_app(k), fonts))
            iy += ICON_SIZE+28
            if iy > 768-ICON_SIZE-40:
                iy = TASKBAR_H+20
                ix += ICON_SIZE+16

        while True:
            sw, sh = screen.get_size()
            screen.fill(BG)
            for gx in range(0, sw, 40):
                pygame.draw.line(screen, (45, 43, 43),
                                 (gx, TASKBAR_H), (gx, sh), 1)
            for gy in range(TASKBAR_H, sh, 40):
                pygame.draw.line(screen, (45, 43, 43), (0, gy), (sw, gy), 1)

            for icon in desktop_icons:
                icon.draw(screen)

            alive = [w for w in _window_order if w.alive]
            for win in alive:
                win.draw(screen)

            taskbar.draw(screen, alive)
            start_menu.draw(screen)
            pygame.display.flip()
            clock.tick(60)

            # prune dead windows
            for w in list(_window_order):
                if not w.alive:
                    _window_order.remove(w)
            windows[:] = [w for w in windows if w.alive]

            if logout_flag[0]:
                _window_order.clear()
                break
            if tty_flag[0]:
                pygame.quit()
                return "tty"

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return "quit"
                if taskbar.handle(event):
                    continue
                if start_menu.handle(event, sh):
                    continue
                alive_rev = list(
                    reversed([w for w in _window_order if w.alive]))
                for win in alive_rev:
                    win.handle(event)
                    if win.dragging:
                        break
                else:
                    for icon in desktop_icons:
                        icon.handle(event)
