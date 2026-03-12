"""
gui.py — PenguWarp Desktop Environment (Dear PyGui)
PenguWin DE — polished, feature-rich edition
"""

import os
import re
import io
import queue
import threading
import time
from colorama import Fore

import system as S
from system import (
    filesystem, installed_packages,
    SYSTEM_FILE, save_system, get_dynamic_ram,
    GRV_BG, GRV_BG1, GRV_BG2, GRV_BG_HARD,
    GRV_FG, GRV_YELLOW, GRV_YELLOW_DIM,
    GRV_ORANGE, GRV_ORANGE_DIM, GRV_RED,
    GRV_GREEN, GRV_AQUA, GRV_GRAY,
)

try:
    import dearpygui.dearpygui as dpg
    HAS_DPG = True
except ImportError:
    HAS_DPG = False

# ── Toast state ───────────────────────────────────────────────────────────────
_toast_queue: list[tuple[str, tuple]] = []
_toast_timer: float = 0.0

# ── Terminal state ────────────────────────────────────────────────────────────
_terminal_pollers: set[str] = set()
_terminal_output_pollers: dict[str, object] = {}


def _toast(msg: str, color: tuple | None = None) -> None:
    _toast_queue.append((msg, color or GRV_GREEN))


# ── Theme helpers ─────────────────────────────────────────────────────────────

def _apply_gruvbox_theme() -> None:
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg,             GRV_BG)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg,              GRV_BG)
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg,              GRV_BG1)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg,              GRV_BG1)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered,       GRV_BG2)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive,        GRV_BG2)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg,
                                GRV_BG_HARD)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive,        GRV_BG1)
            dpg.add_theme_color(
                dpg.mvThemeCol_TitleBgCollapsed,     GRV_BG_HARD)
            dpg.add_theme_color(dpg.mvThemeCol_Button,
                                GRV_ORANGE_DIM)
            dpg.add_theme_color(
                dpg.mvThemeCol_ButtonHovered,        GRV_ORANGE)
            dpg.add_theme_color(
                dpg.mvThemeCol_ButtonActive,         GRV_YELLOW_DIM)
            dpg.add_theme_color(dpg.mvThemeCol_Text,                 GRV_FG)
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled,         GRV_GRAY)
            dpg.add_theme_color(dpg.mvThemeCol_Header,               GRV_BG2)
            dpg.add_theme_color(
                dpg.mvThemeCol_HeaderHovered,        GRV_ORANGE_DIM)
            dpg.add_theme_color(
                dpg.mvThemeCol_HeaderActive,         GRV_ORANGE)
            dpg.add_theme_color(
                dpg.mvThemeCol_ScrollbarBg,          GRV_BG_HARD)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab,        GRV_BG2)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, GRV_GRAY)
            dpg.add_theme_color(dpg.mvThemeCol_Separator,            GRV_BG2)
            dpg.add_theme_color(dpg.mvThemeCol_Border,               GRV_BG2)
            dpg.add_theme_color(
                dpg.mvThemeCol_MenuBarBg,            GRV_BG_HARD)
            dpg.add_theme_color(
                dpg.mvThemeCol_NavHighlight,         GRV_ORANGE)
            dpg.add_theme_color(dpg.mvThemeCol_Tab,                  GRV_BG1)
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered,
                                GRV_ORANGE_DIM)
            dpg.add_theme_color(
                dpg.mvThemeCol_TabActive,            GRV_ORANGE)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding,  6)
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding,   6)
            dpg.add_theme_style(dpg.mvStyleVar_PopupRounding,  6)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding,  12, 12)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding,   8,  5)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing,    8,  6)
    dpg.bind_theme(global_theme)


def _make_icon_theme():
    with dpg.theme() as t:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button,        GRV_ORANGE_DIM)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, GRV_ORANGE)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,  GRV_YELLOW_DIM)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 10)
    return t


def _colored_progress_bar(pct: float, overlay: str, color: tuple) -> None:
    with dpg.theme() as t:
        with dpg.theme_component(dpg.mvProgressBar):
            dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, color)
    bar = dpg.add_progress_bar(default_value=pct, width=-1, overlay=overlay)
    dpg.bind_item_theme(bar, t)


# ── App: Gardener (sysinfo) ───────────────────────────────────────────────────

def _dpg_sysinfo() -> None:
    if dpg.does_item_exist("win_sysinfo"):
        dpg.delete_item("win_sysinfo")

    uptime = int(time.time() - S.start_time)
    storage_kb = round(os.path.getsize(SYSTEM_FILE) / 1024,
                       2) if os.path.exists(SYSTEM_FILE) else 0
    ram = get_dynamic_ram()
    m, s = divmod(uptime, 60)
    h, m = divmod(m, 60)
    uptime_str = f"{h:02d}:{m:02d}:{s:02d}"

    with dpg.window(label="Gardener -- System Info", tag="win_sysinfo",
                    width=440, height=400, pos=(200, 150),
                    on_close=lambda: dpg.delete_item("win_sysinfo")):

        with dpg.group(horizontal=True):
            dpg.add_text("PenguWarp OS", color=GRV_YELLOW)
            dpg.add_text('  v0.1.7 "Lemon" Testing', color=GRV_ORANGE)
        dpg.add_separator()
        dpg.add_spacer(height=6)

        with dpg.table(header_row=False, borders_innerV=False):
            dpg.add_table_column(width_fixed=True, init_width_or_weight=90)
            dpg.add_table_column()
            for label, val in [
                ("User",   f"{S.user}@{S.hostname}"),
                ("Kernel", "v0.1.7-lemon-dev_x86_64"),
                ("Shell",  "PWShell"),
                ("Uptime", uptime_str),
                ("Pkgs",   f"{len(installed_packages)} installed"),
                ("RAM",    f"{ram} MB / 128 MB"),
                ("Disk",   f"{storage_kb} KB / 512 KB"),
            ]:
                with dpg.table_row():
                    dpg.add_text(label, color=GRV_GRAY)
                    dpg.add_text(val,   color=GRV_FG)

        dpg.add_spacer(height=10)
        dpg.add_separator()
        dpg.add_spacer(height=8)

        ram_pct = min(ram / 128, 1.0)
        disk_pct = min(storage_kb / 512, 1.0)
        ram_col = GRV_GREEN if ram_pct < 0.6 else (
            GRV_YELLOW if ram_pct < 0.85 else GRV_RED)
        disk_col = GRV_GREEN if disk_pct < 0.6 else (
            GRV_YELLOW if disk_pct < 0.85 else GRV_RED)

        dpg.add_text("RAM Usage",  color=GRV_GRAY)
        _colored_progress_bar(ram_pct,  f"{ram} MB / 128 MB",         ram_col)
        dpg.add_spacer(height=6)
        dpg.add_text("Disk Usage", color=GRV_GRAY)
        _colored_progress_bar(disk_pct, f"{storage_kb} KB / 512 KB",  disk_col)

        dpg.add_spacer(height=8)
        dpg.add_separator()
        dpg.add_spacer(height=4)
        dpg.add_text(
            f"Session started  {time.strftime(
                '%H:%M:%S', time.localtime(S.start_time))}",
            color=GRV_GRAY,
        )


# ── App: ClockWarp ────────────────────────────────────────────────────────────

def _dpg_clock() -> None:
    if dpg.does_item_exist("win_clock"):
        dpg.delete_item("win_clock")
    with dpg.window(label="ClockWarp", tag="win_clock",
                    width=290, height=140, pos=(380, 300),
                    on_close=lambda: dpg.delete_item("win_clock")):
        dpg.add_spacer(height=4)
        dpg.add_text(time.strftime("%H:%M:%S"),
                     tag="clock_text",   color=GRV_YELLOW)
        dpg.add_text(time.strftime("%A, %B %d %Y"),
                     tag="clock_date",   color=GRV_GRAY)
        dpg.add_separator()
        dpg.add_spacer(height=4)
        uptime = int(time.time() - S.start_time)
        m, s = divmod(uptime, 60)
        h, m = divmod(m, 60)
        dpg.add_text(f"Uptime  {h:02d}:{m:02d}:{s:02d}",
                     tag="clock_uptime", color=GRV_ORANGE)


# ── App: WarpCalc ─────────────────────────────────────────────────────────────

def _dpg_calculator() -> None:
    if dpg.does_item_exist("win_calc"):
        dpg.delete_item("win_calc")

    expr_val: list[str] = [""]
    hist:     list[str] = []

    def _safe_eval(expr: str) -> str:
        import ast
        import operator as op
        allowed = {ast.Add: op.add, ast.Sub: op.sub,
                   ast.Mult: op.mul, ast.Div: op.truediv, ast.USub: op.neg}

        def _ev(node):
            match node:
                case ast.Constant(value=v) if isinstance(v, int | float): return float(v)
                case ast.BinOp(left=l, op=o, right=r): return allowed[type(o)](_ev(l), _ev(r))
                case ast.UnaryOp(op=o, operand=v): return allowed[type(o)](_ev(v))
                case _: raise ValueError
        res = _ev(ast.parse(expr, mode="eval").body)
        return str(int(res)) if res == int(res) else str(res)

    def click(b: str) -> None:
        if b == "=":
            try:
                result = _safe_eval(expr_val[0])
                hist.append(f"{expr_val[0]} = {result}")
                if len(hist) > 5:
                    hist.pop(0)
                expr_val[0] = result
                if dpg.does_item_exist("calc_hist"):
                    dpg.set_value("calc_hist", "\n".join(hist))
            except Exception:
                expr_val[0] = "Error"
        elif b == "C":
            expr_val[0] = ""
        elif b == "⌫":
            expr_val[0] = expr_val[0][:-1]
        else:
            expr_val[0] += b
        dpg.set_value("calc_display", expr_val[0])

    with dpg.window(label="WarpCalc", tag="win_calc",
                    width=290, height=440, pos=(300, 180),
                    on_close=lambda: dpg.delete_item("win_calc")):

        dpg.add_input_text(tag="calc_hist", default_value="", multiline=True,
                           readonly=True, width=-1, height=75)
        dpg.add_separator()
        dpg.add_input_text(tag="calc_display", default_value="",
                           width=-1, readonly=True, hint="0")
        dpg.add_spacer(height=4)

        BTN_ROWS = [
            ("7", "8", "9", "/"),
            ("4", "5", "6", "*"),
            ("1", "2", "3", "-"),
            ("C", "0", "=", "+"),
            ("⌫", ".", "%", "**"),
        ]
        for row in BTN_ROWS:
            with dpg.group(horizontal=True):
                for b in row:
                    col = (GRV_ORANGE_DIM if b in ("/*-+**%", "/", "*", "-", "+", "**", "%")
                           else GRV_RED if b == "C"
                           else GRV_GREEN if b == "="
                           else (100, 80, 70, 255) if b == "⌫"
                           else GRV_BG1)
                    with dpg.theme() as t:
                        with dpg.theme_component(dpg.mvButton):
                            dpg.add_theme_color(dpg.mvThemeCol_Button, col)
                            dpg.add_theme_style(
                                dpg.mvStyleVar_FrameRounding, 4)
                    btn = dpg.add_button(label=b, width=54, height=44,
                                         callback=lambda s, a, u: click(u), user_data=b)
                    dpg.bind_item_theme(btn, t)


# ── App: File Browser ─────────────────────────────────────────────────────────

_fb_path = ["~"]


def _dpg_file_browser() -> None:
    global _fb_path
    _fb_path = ["~"]
    if dpg.does_item_exist("win_fb"):
        dpg.delete_item("win_fb")

    def refresh() -> None:
        dpg.delete_item("fb_list", children_only=True)
        dpg.set_value("fb_path_text", f"  {_fb_path[0]}")

        if _fb_path[0] != "~":
            dpg.add_selectable(
                label="  ^  ..", parent="fb_list", callback=_go_up)

        contents = filesystem.get(_fb_path[0], {}).get("contents", [])
        dirs = [i for i in contents
                if filesystem.get(f"~/{i}" if _fb_path[0] == "~" else f"{_fb_path[0]}/{i}", {}).get("type") == "dir"]
        files = [i for i in contents if i not in dirs]

        for item in sorted(dirs) + sorted(files):
            full = f"~/{item}" if _fb_path[0] == "~" else f"{
                _fb_path[0]}/{item}"
            is_dir = item in dirs
            col = GRV_YELLOW if is_dir else GRV_FG
            icon = "  [DIR] " if is_dir else "  [FILE] "
            dpg.add_selectable(label=f"{icon}{item}",
                               parent="fb_list", callback=_on_fb_click, user_data=item)
            kids = dpg.get_item_children("fb_list", 1)
            if kids:
                with dpg.theme() as t:
                    with dpg.theme_component(dpg.mvSelectable):
                        dpg.add_theme_color(dpg.mvThemeCol_Text, col)
                dpg.bind_item_theme(kids[-1], t)

        dpg.set_value("fb_status",
                      f"  {len(dirs)} folder(s)   {len(files)} file(s)   {len(contents)} total")

    def _go_up() -> None:
        parts = _fb_path[0].split("/")
        _fb_path[0] = "/".join(parts[:-1]) if len(parts) > 1 else "~"
        refresh()

    def _on_fb_click(sender, app_data, user_data) -> None:
        full = f"~/{user_data}" if _fb_path[0] == "~" else f"{
            _fb_path[0]}/{user_data}"
        entry = filesystem.get(full, {})
        if entry.get("type") == "dir":
            _fb_path[0] = full
            refresh()
        elif entry.get("type") == "file":
            _dpg_text_viewer(user_data, entry["content"])

    with dpg.window(label="Tree -- File Browser", tag="win_fb",
                    width=500, height=480, pos=(120, 90),
                    on_close=lambda: dpg.delete_item("win_fb")):

        with dpg.group(horizontal=True):
            dpg.add_button(label="^ Up",      width=70,  callback=_go_up)
            dpg.add_button(label="~ Home",    width=80,
                           callback=lambda: (_fb_path.__setitem__(0, "~"), refresh()))
            dpg.add_button(label="* Refresh", width=90,
                           callback=lambda: refresh())
        dpg.add_separator()
        dpg.add_text("~", tag="fb_path_text", color=GRV_YELLOW)
        dpg.add_separator()

        with dpg.child_window(tag="fb_list", height=-30, border=False):
            pass

        dpg.add_separator()
        dpg.add_text("", tag="fb_status", color=GRV_GRAY)

    refresh()


# ── App: Text Viewer ──────────────────────────────────────────────────────────

def _dpg_text_viewer(filename: str, content: str) -> None:
    tag = f"win_viewer_{filename}"
    if dpg.does_item_exist(tag):
        dpg.delete_item(tag)
    lines = content.count("\n") + 1
    words = len(content.split())
    with dpg.window(label=f"Viewer -- {filename}", tag=tag,
                    width=500, height=370, pos=(200, 170),
                    on_close=lambda: dpg.delete_item(tag)):
        with dpg.group(horizontal=True):
            dpg.add_text(f"{lines} lines", color=GRV_GRAY)
            dpg.add_text(f"  {words} words", color=GRV_GRAY)
            dpg.add_text(f"  {len(content)} chars", color=GRV_GRAY)
        dpg.add_separator()
        dpg.add_input_text(default_value=content, multiline=True,
                           readonly=True, width=-1, height=-1)


# ── App: GPWDIT editor ────────────────────────────────────────────────────────

def _dpg_pwdit(filename: str | None = None) -> None:
    tag = "win_pwdit"
    if dpg.does_item_exist(tag):
        dpg.delete_item(tag)

    cur_file = [filename or "new_file.txt"]
    is_modified = [False]
    initial = ""
    if filename:
        path = f"~/{filename}" if S.current_dir == "~" else f"{S.current_dir}/{filename}"
        initial = filesystem.get(path, {}).get("content", "")

    def _update_stats() -> None:
        if not dpg.does_item_exist("pwdit_text"):
            return
        content = dpg.get_value("pwdit_text")
        lines = content.count("\n") + 1
        words = len(content.split()) if content.strip() else 0
        mod = "  [modified]" if is_modified[0] else ""
        if dpg.does_item_exist("pwdit_stats"):
            dpg.set_value("pwdit_stats", f"  Ln {lines}  Wrd {
                          words}  Chr {len(content)}{mod}")

    def save() -> None:
        content = dpg.get_value("pwdit_text")
        path = f"~/{cur_file[0]
                    }" if S.current_dir == "~" else f"{S.current_dir}/{cur_file[0]}"
        filesystem[path] = {"type": "file", "content": content}
        if cur_file[0] not in filesystem[S.current_dir]["contents"]:
            filesystem[S.current_dir]["contents"].append(cur_file[0])
        save_system()
        is_modified[0] = False
        if dpg.does_item_exist("pwdit_status"):
            dpg.set_value("pwdit_status", f"  OK  Saved -- {cur_file[0]}")
        _update_stats()
        _toast(f"Saved {cur_file[0]}")

    def save_as() -> None:
        if dpg.does_item_exist("pwdit_saveas_popup"):
            dpg.delete_item("pwdit_saveas_popup")
        with dpg.window(label="Save As", tag="pwdit_saveas_popup",
                        width=340, height=120, pos=(310, 260), modal=True,
                        on_close=lambda: dpg.delete_item("pwdit_saveas_popup")):
            dpg.add_text("Filename:", color=GRV_YELLOW)
            dpg.add_input_text(tag="pwdit_saveas_input",
                               default_value=cur_file[0], width=-1)
            dpg.add_spacer(height=6)
            with dpg.group(horizontal=True):
                def do_save_as() -> None:
                    new = dpg.get_value("pwdit_saveas_input").strip()
                    if new:
                        cur_file[0] = new
                        dpg.configure_item(
                            "win_pwdit", label=f"GPWDIT -- {new}")
                        save()
                    dpg.delete_item("pwdit_saveas_popup")
                dpg.add_button(label="Save",   width=110, callback=do_save_as)
                dpg.add_button(label="Cancel", width=90,
                               callback=lambda: dpg.delete_item("pwdit_saveas_popup"))

    with dpg.window(label=f"GPWDIT -- {cur_file[0]}", tag=tag,
                    width=720, height=560, pos=(140, 70),
                    on_close=lambda: dpg.delete_item(tag)):
        with dpg.group(horizontal=True):
            dpg.add_button(label="[N] New",     width=80, callback=lambda: (
                dpg.set_value("pwdit_text", ""),
                cur_file.__setitem__(0, "new_file.txt"),
                dpg.configure_item(
                    "win_pwdit", label="GPWDIT -- new_file.txt"),
                dpg.set_value("pwdit_status", "  New file"),
                _update_stats(),
            ))
            dpg.add_button(label="[S] Save",    width=90,
                           callback=lambda: save())
            dpg.add_button(label="[A] Save As", width=100,
                           callback=lambda: save_as())
        dpg.add_separator()
        dpg.add_input_text(
            tag="pwdit_text", default_value=initial,
            multiline=True, width=-1, height=-50, tab_input=True,
            callback=lambda: (is_modified.__setitem__(
                0, True), _update_stats()),
        )
        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_text("", tag="pwdit_status", color=GRV_GREEN)
            dpg.add_text("", tag="pwdit_stats",  color=GRV_GRAY)
    _update_stats()


# ── App: PenguPaint ───────────────────────────────────────────────────────────

def _dpg_paint() -> None:
    for tag in ("win_paint", "paint_drag_handler"):
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)

    current_color = [GRV_ORANGE_DIM]
    brush_size = [5]

    COLORS = [GRV_BG, GRV_RED, GRV_ORANGE, GRV_YELLOW,
              GRV_GREEN, GRV_AQUA, GRV_FG, (255, 255, 255, 255)]

    with dpg.window(label="PenguPaint", tag="win_paint",
                    width=560, height=540, pos=(160, 80),
                    on_close=lambda: (
                        dpg.delete_item("win_paint"),
                        dpg.delete_item("paint_drag_handler")
                        if dpg.does_item_exist("paint_drag_handler") else None,
                    )):

        with dpg.group(horizontal=True):
            for c in COLORS:
                with dpg.theme() as sw:
                    with dpg.theme_component(dpg.mvButton):
                        for k in (dpg.mvThemeCol_Button,
                                  dpg.mvThemeCol_ButtonHovered,
                                  dpg.mvThemeCol_ButtonActive):
                            dpg.add_theme_color(k, c)
                        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 14)
                btn = dpg.add_button(
                    label="   ", width=34, height=28,
                    callback=lambda s, a, u: current_color.__setitem__(0, u),
                    user_data=c,
                )
                dpg.bind_item_theme(btn, sw)

            dpg.add_text("  Size:", color=GRV_GRAY)
            dpg.add_slider_int(
                tag="brush_slider", default_value=5, min_value=1, max_value=20,
                width=100,
                callback=lambda s, a: brush_size.__setitem__(
                    0, dpg.get_value("brush_slider")),
            )
            dpg.add_button(
                label="Clear",
                callback=lambda: dpg.delete_item(
                    "paint_canvas", children_only=True),
            )
        dpg.add_separator()
        with dpg.drawlist(width=534, height=450, tag="paint_canvas"):
            pass

    with dpg.handler_registry(tag="paint_drag_handler"):
        def on_draw(sender, app_data) -> None:
            if not dpg.does_item_exist("paint_canvas"):
                return
            if not dpg.is_item_hovered("paint_canvas"):
                return
            x, y = dpg.get_drawing_mouse_pos()
            dpg.draw_circle((x, y), brush_size[0],
                            color=current_color[0], fill=current_color[0],
                            parent="paint_canvas")
        dpg.add_mouse_drag_handler(callback=on_draw)


# ── App: PWShell Terminal ─────────────────────────────────────────────────────

def _dpg_terminal() -> None:
    if dpg.does_item_exist("win_terminal"):
        dpg.focus_item("win_terminal")
        return

    output_q: queue.Queue[str] = queue.Queue()
    cmd_running = [False]

    # ── stdout redirector ──────────────────────────────
    class _Writer(io.TextIOBase):
        def write(self, s: str) -> int:
            if s:
                output_q.put(s)
            return len(s)

        def flush(self): pass

    def _strip_ansi(text: str) -> str:
        return re.sub(r'\x1b\[[0-9;]*[mGKHF]', '', text)

    def _append(text: str) -> None:
        if not dpg.does_item_exist("term_output"):
            return
        clean = _strip_ansi(text)
        current = dpg.get_value("term_output")
        merged = current + clean
        lines = merged.split("\n")
        if len(lines) > 300:
            lines = lines[-300:]
        dpg.set_value("term_output", "\n".join(lines))
        # autoscroll
        dpg.set_y_scroll("term_scroll", dpg.get_y_scroll_max("term_scroll"))

    def _update_prompt() -> None:
        if dpg.does_item_exist("term_prompt"):
            dpg.set_value("term_prompt", f"{
                          S.user}@{S.hostname}:{S.current_dir}$ ")

    BLOCKED = {"startx", "poweroff", "clear", "cls"}

    def _run_cmd(cmd_line: str) -> None:
        import sys
        from commands import execute_command
        old = sys.stdout
        sys.stdout = _Writer()
        try:
            execute_command(cmd_line)
        except SystemExit:
            output_q.put("error: cannot exit from terminal window\n")
        except Exception as e:
            output_q.put(f"error: {e}\n")
        finally:
            sys.stdout = old
            cmd_running[0] = False
            # push a sentinel so we know to update prompt after output drains
            output_q.put("\x00PROMPT_UPDATE\x00")

    def _submit() -> None:
        if cmd_running[0]:
            return
        raw = dpg.get_value("term_input").strip()
        dpg.set_value("term_input", "")
        if not raw:
            return

        prompt_line = f"{S.user}@{S.hostname}:{S.current_dir}$ {raw}\n"
        _append(prompt_line)

        first_word = raw.split()[0]
        if first_word in BLOCKED:
            _append(f"[terminal] '{
                    first_word}' is not available in the GUI terminal\n\n")
            return

        # commands that need interactive input — run inline with a friendly message
        INPUT_CMDS = {"su", "passwd", "useradd", "adminrun"}
        if first_word in INPUT_CMDS:
            _append(f"[terminal] '{
                    first_word}' requires interactive input — use PWShell directly\n\n")
            return

        cmd_running[0] = True
        threading.Thread(target=_run_cmd, args=(raw,), daemon=True).start()

    def _poll() -> None:
        drained = False
        while not output_q.empty():
            try:
                chunk = output_q.get_nowait()
                if chunk == "\x00PROMPT_UPDATE\x00":
                    _update_prompt()
                    if dpg.does_item_exist("term_output"):
                        current = dpg.get_value("term_output")
                        if not current.endswith("\n\n"):
                            dpg.set_value("term_output", current + "\n")
                else:
                    _append(chunk)
                drained = True
            except queue.Empty:
                break
        if drained:
            dpg.set_y_scroll(
                "term_scroll", dpg.get_y_scroll_max("term_scroll"))

    # register poller
    _terminal_output_pollers["win_terminal"] = _poll

    # ── build window ───────────────────────────────────
    with dpg.window(label="PWShell Terminal", tag="win_terminal",
                    width=700, height=520, pos=(150, 100),
                    on_close=lambda: (
                        dpg.delete_item("win_terminal"),
                        _terminal_output_pollers.pop("win_terminal", None),
                    )):

        with dpg.child_window(tag="term_scroll", height=-50, border=True,
                              horizontal_scrollbar=False):
            dpg.add_input_text(
                tag="term_output",
                default_value=(
                    f'PWShell -- PenguWarp v0.1.7 "Lemon"\n'
                    f"Type 'help' for available commands.\n"
                    f"Note: su/passwd/useradd/adminrun need interactive input.\n\n"
                ),
                multiline=True, readonly=True,
                width=-1, height=-1,
                tab_input=False,
            )

        dpg.add_separator()

        with dpg.group(horizontal=True):
            dpg.add_text(
                f"{S.user}@{S.hostname}:{S.current_dir}$ ",
                tag="term_prompt",
                color=GRV_GREEN,
            )
            dpg.add_input_text(
                tag="term_input",
                hint="enter command...",
                width=-1,
                on_enter=True,
                callback=lambda: _submit(),
            )

    _toast("Launched PWShell Terminal")


# ── App: App Launcher (spotlight-style) ──────────────────────────────────────

def _dpg_app_launcher() -> None:
    if dpg.does_item_exist("win_launcher"):
        dpg.delete_item("win_launcher")
        return

    APP_LIST = [
        ("File Browser",      _dpg_file_browser),
        ("GPWDIT Editor", lambda: _dpg_pwdit()),
        ("WarpCalc",          _dpg_calculator),
        ("PenguPaint",        _dpg_paint),
        ("ClockWarp",         _dpg_clock),
        ("Gardener",          _dpg_sysinfo),
        ("PWShell Terminal",  _dpg_terminal),
    ]

    def _launch(name: str, cb) -> None:
        cb()
        if dpg.does_item_exist("win_launcher"):
            dpg.delete_item("win_launcher")
        _toast(f"Launched {name}")

    def _search_launch() -> None:
        query = dpg.get_value("launcher_input").strip().lower()
        for name, cb in APP_LIST:
            if query in name.lower():
                _launch(name, cb)
                return
        _toast("No matching app found", GRV_RED)

    with dpg.window(label="App Launcher", tag="win_launcher",
                    width=420, height=360, pos=(302, 190),
                    on_close=lambda: dpg.delete_item("win_launcher")):
        dpg.add_text("Search & Launch", color=GRV_YELLOW)
        dpg.add_input_text(tag="launcher_input", hint="type app name, press Enter...",
                           width=-1, on_enter=True, callback=lambda: _search_launch())
        dpg.add_separator()
        dpg.add_spacer(height=4)
        for name, cb in APP_LIST:
            dpg.add_button(label=f"  {name}", width=-1, height=36,
                           callback=lambda s, a, u: _launch(u[0], u[1]),
                           user_data=(name, cb))
            dpg.add_spacer(height=2)


# ── App: About ────────────────────────────────────────────────────────────────

def _dpg_about() -> None:
    if dpg.does_item_exist("win_about"):
        dpg.delete_item("win_about")
    with dpg.window(label="About PenguWarp", tag="win_about",
                    width=360, height=270, pos=(332, 230),
                    on_close=lambda: dpg.delete_item("win_about")):
        dpg.add_spacer(height=6)
        dpg.add_text("PenguWarp OS",                   color=GRV_YELLOW)
        dpg.add_text('Version 0.1.7 "Lemon" Testing',  color=GRV_ORANGE)
        dpg.add_spacer(height=6)
        dpg.add_separator()
        dpg.add_spacer(height=6)
        for line, col in [
            ("A Python-based OS simulation",  GRV_FG),
            ("Desktop: PenguWin DE",          GRV_FG),
            ("Shell: PWShell",                GRV_FG),
            ("GUI toolkit: Dear PyGui",       GRV_FG),
            ("Theme: Gruvbox Dark",           GRV_FG),
            ("",                              GRV_FG),
            (f"User: {S.user}@{S.hostname}",  GRV_GRAY),
        ]:
            dpg.add_text(line, color=col)
        dpg.add_spacer(height=10)
        dpg.add_separator()
        dpg.add_spacer(height=6)
        dpg.add_button(label="Close", width=-1,
                       callback=lambda: dpg.delete_item("win_about"))


# ── Desktop / main entry ──────────────────────────────────────────────────────

def _logout() -> None:
    """Cleanly stop the render loop — destroy_context() handles the rest."""
    dpg.stop_dearpygui()


def start_gui() -> None:
    if not HAS_DPG:
        print(f"{Fore.RED}error: dearpygui not installed. "
              f"run: pip install dearpygui --break-system-packages{Fore.WHITE}")
        return

    global _toast_queue, _toast_timer

    dpg.create_context()
    dpg.create_viewport(title="PenguWarp Desktop",
                        width=1024, height=768, min_width=800, min_height=600)
    _apply_gruvbox_theme()
    icon_theme = _make_icon_theme()

    # ── Menu bar ──────────────────────────────────────
    with dpg.viewport_menu_bar():
        dpg.add_menu_item(label=" PenguWarp ", enabled=False)

        with dpg.menu(label="Apps"):
            dpg.add_menu_item(label="[F]  File Browser",
                              callback=_dpg_file_browser)
            dpg.add_menu_item(label="[E]  GPWDIT Editor",
                              callback=lambda: _dpg_pwdit())
            dpg.add_menu_item(label="[C]  WarpCalc",
                              callback=_dpg_calculator)
            dpg.add_menu_item(label="[P]  PenguPaint",
                              callback=_dpg_paint)
            dpg.add_menu_item(label="[K]  ClockWarp",
                              callback=_dpg_clock)
            dpg.add_menu_item(label="[S]  Gardener",
                              callback=_dpg_sysinfo)
            dpg.add_menu_item(label="[T]  Terminal",
                              callback=_dpg_terminal)
            dpg.add_separator()
            dpg.add_menu_item(label="[L]  App Launcher",
                              callback=_dpg_app_launcher)

        with dpg.menu(label="System"):
            dpg.add_menu_item(label="About PenguWarp", callback=_dpg_about)
            dpg.add_separator()
            dpg.add_menu_item(label="[X]  Logout", callback=_logout)

        # right-side status pills
        dpg.add_menu_item(label="",  tag="topbar_pkgs",  enabled=False)
        dpg.add_menu_item(label="",  tag="topbar_ram",   enabled=False)
        dpg.add_menu_item(label="",  tag="topbar_clock", enabled=False)
        dpg.add_menu_item(label=f"  {S.user}@{S.hostname}  ",
                          tag="topbar_user", enabled=False)

    # ── Desktop window ────────────────────────────────
    with dpg.window(label="Desktop", tag="win_desktop",
                    width=1920, height=1080, pos=(0, 0),
                    no_title_bar=True, no_move=True, no_resize=True,
                    no_bring_to_front_on_focus=True, no_scrollbar=True):

        dpg.add_spacer(height=400)
        with dpg.group(horizontal=False):
            dpg.add_text("PENGUWARP WORKSTATION",
                         color=GRV_YELLOW, tag="desktop_title")
            dpg.add_text('v0.1.7 "Lemon" Testing',
                         color=GRV_ORANGE, tag="desktop_sub")
            dpg.add_spacer(height=4)
            dpg.add_text(f"{S.user}@{S.hostname}",
                         color=GRV_GRAY, tag="desktop_user")

        # Sidebar icon launcher
        ICONS = [
            ("[F]\nTree",       _dpg_file_browser,    30,  50),
            ("[C]\nWarpCalc",   _dpg_calculator,      30, 155),
            ("[P]\nPenguPaint", _dpg_paint,           30, 260),
            ("[G]\nGPWDIT", lambda: _dpg_pwdit(), 30, 365),
            ("[S]\nGardener",   _dpg_sysinfo,         30, 470),
            ("[T]\nTerminal",   _dpg_terminal,        30, 575),
            ("[K]\nClock",      _dpg_clock,           30, 660),
            ("[L]\nLauncher",   _dpg_app_launcher,    30, 745),
        ]
        for label, cb, x, y in ICONS:
            btn = dpg.add_button(label=label, callback=cb,
                                 width=76, height=76, pos=(x, y))
            dpg.bind_item_theme(btn, icon_theme)

    # ── Toast overlay ─────────────────────────────────
    with dpg.window(label="", tag="win_toast",
                    width=300, height=36, pos=(710, 730),
                    no_title_bar=True, no_move=True, no_resize=True,
                    no_scrollbar=True, show=False):
        dpg.add_text("", tag="toast_text", color=GRV_GREEN)

    # ── Render loop ───────────────────────────────────
    _last_sec = [0]

    def _render_loop() -> None:
        global _toast_timer, _toast_queue
        now = time.time()

        # throttle to once per second for non-animation updates
        if int(now) != _last_sec[0]:
            _last_sec[0] = int(now)
            ts = time.strftime(" %H:%M:%S ")
            uptime = int(now - S.start_time)
            ram = get_dynamic_ram()
            pkgs = len(installed_packages)
            m, s = divmod(uptime, 60)
            h, m = divmod(m, 60)

            for tag, val in [
                ("topbar_clock",  ts),
                ("topbar_ram",    f" RAM {ram}MB "),
                ("topbar_pkgs",   f" {pkgs} pkgs "),
            ]:
                if dpg.does_item_exist(tag):
                    dpg.set_item_label(tag, val)

            if dpg.does_item_exist("clock_text"):
                dpg.set_value("clock_text",   time.strftime("%H:%M:%S"))
            if dpg.does_item_exist("clock_date"):
                dpg.set_value("clock_date",   time.strftime("%A, %B %d %Y"))
            if dpg.does_item_exist("clock_uptime"):
                dpg.set_value("clock_uptime", f"Uptime  {
                              h:02d}:{m:02d}:{s:02d}")

        # center desktop branding
        if dpg.does_item_exist("win_desktop"):
            w = dpg.get_item_width("win_desktop")
            for tag, offset in [
                ("desktop_title", 210),
                ("desktop_sub",   178),
                ("desktop_user",  90),
            ]:
                if dpg.does_item_exist(tag):
                    dpg.configure_item(tag, indent=max(0, (w - offset) // 2))

        # toast pop-ups
        if _toast_queue and dpg.does_item_exist("toast_text"):
            msg, col = _toast_queue.pop(0)
            dpg.set_value("toast_text", f"  OK  {msg}")
            with dpg.theme() as t:
                with dpg.theme_component(dpg.mvText):
                    dpg.add_theme_color(dpg.mvThemeCol_Text, col)
            kids = dpg.get_item_children("win_toast", 1)
            if kids:
                dpg.bind_item_theme(kids[0], t)
            dpg.configure_item("win_toast", show=True)
            _toast_timer = now

        if _toast_timer and now - _toast_timer > 2.5:
            if dpg.does_item_exist("win_toast"):
                dpg.configure_item("win_toast", show=False)
            _toast_timer = 0.0

        # poll all terminal output queues
        for tag, poller in list(_terminal_output_pollers.items()):
            if dpg.does_item_exist(tag):
                poller()
            else:
                _terminal_output_pollers.pop(tag, None)

    dpg.set_frame_callback(2, callback=lambda: None)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        _render_loop()
        dpg.render_dearpygui_frame()

    dpg.close_viewport()
    dpg.destroy_context()
