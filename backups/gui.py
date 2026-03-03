import os
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

# ── Gruvbox theme ─────────────────────────────────────────────────────────────

def _apply_gruvbox_theme() -> None:
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg,              GRV_BG)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg,               GRV_BG)
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg,               GRV_BG1)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg,               GRV_BG1)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered,        GRV_BG2)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive,         GRV_BG2)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg,               GRV_BG_HARD)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive,         GRV_BG1)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgCollapsed,      GRV_BG_HARD)
            dpg.add_theme_color(dpg.mvThemeCol_Button,                GRV_ORANGE_DIM)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,         GRV_ORANGE)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,          GRV_YELLOW_DIM)
            dpg.add_theme_color(dpg.mvThemeCol_Text,                  GRV_FG)
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled,          GRV_GRAY)
            dpg.add_theme_color(dpg.mvThemeCol_Header,                GRV_BG2)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered,         GRV_ORANGE_DIM)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive,          GRV_ORANGE)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg,           GRV_BG_HARD)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab,         GRV_BG2)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered,  GRV_GRAY)
            dpg.add_theme_color(dpg.mvThemeCol_Separator,             GRV_BG2)
            dpg.add_theme_color(dpg.mvThemeCol_Border,                GRV_BG2)
            dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg,             GRV_BG_HARD)
            dpg.add_theme_color(dpg.mvThemeCol_NavHighlight,          GRV_ORANGE)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding,  8)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding,   6)
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding,    6)
            dpg.add_theme_style(dpg.mvStyleVar_PopupRounding,   6)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding,   12, 12)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding,    8,  5)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing,     8,  6)
    dpg.bind_theme(global_theme)


# ── App windows ───────────────────────────────────────────────────────────────

def _dpg_sysinfo() -> None:
    if dpg.does_item_exist("win_sysinfo"):
        dpg.delete_item("win_sysinfo")
    uptime     = int(time.time() - S.start_time)
    storage_kb = round(os.path.getsize(SYSTEM_FILE) / 1024, 2) if os.path.exists(SYSTEM_FILE) else 0
    ram        = get_dynamic_ram()

    with dpg.window(label="System Info — Gardener", tag="win_sysinfo",
                    width=420, height=320, pos=(200, 150),
                    on_close=lambda: dpg.delete_item("win_sysinfo")):
        dpg.add_text("PenguWarp OS", color=GRV_YELLOW)
        dpg.add_text('v0.1.7 "Lemon" Testing', color=GRV_ORANGE)
        dpg.add_separator(); dpg.add_spacer(height=6)

        with dpg.table(header_row=False, borders_innerV=False):
            dpg.add_table_column(); dpg.add_table_column()
            for label, val in [
                ("User",   f"{S.user}@{S.hostname}"),
                ("Kernel", "v0.1.7-lemon-dev_x86_64"),
                ("Shell",  "PWShell"),
                ("Uptime", f"{uptime}s"),
                ("Pkgs",   str(len(installed_packages))),
                ("RAM",    f"{ram} MB / 128 MB"),
                ("Disk",   f"{storage_kb} KB / 512 KB"),
            ]:
                with dpg.table_row():
                    dpg.add_text(label, color=GRV_YELLOW)
                    dpg.add_text(val,   color=GRV_FG)

        dpg.add_spacer(height=8); dpg.add_separator(); dpg.add_spacer(height=6)
        dpg.add_text("RAM Usage",  color=GRV_GRAY)
        dpg.add_progress_bar(default_value=min(ram / 128, 1.0), width=-1,
                             overlay=f"{ram} MB / 128 MB")
        dpg.add_spacer(height=4)
        dpg.add_text("Disk Usage", color=GRV_GRAY)
        dpg.add_progress_bar(default_value=min(storage_kb / 512, 1.0), width=-1,
                             overlay=f"{storage_kb} KB / 512 KB")


def _dpg_clock() -> None:
    if dpg.does_item_exist("win_clock"):
        dpg.delete_item("win_clock")
    with dpg.window(label="ClockWarp", tag="win_clock",
                    width=260, height=100, pos=(380, 300),
                    on_close=lambda: dpg.delete_item("win_clock")):
        dpg.add_text(time.strftime("%H:%M:%S"), tag="clock_text", color=GRV_YELLOW)


def _dpg_calculator() -> None:
    if dpg.does_item_exist("win_calc"):
        dpg.delete_item("win_calc")

    expr_val = [""]

    def _safe_eval(expression: str) -> str:
        import ast, operator as op
        allowed = {ast.Add: op.add, ast.Sub: op.sub,
                   ast.Mult: op.mul, ast.Div: op.truediv, ast.USub: op.neg}
        def _ev(node):
            match node:
                case ast.Constant(value=v) if isinstance(v, int | float): return float(v)
                case ast.BinOp(left=l, op=o, right=r):  return allowed[type(o)](_ev(l), _ev(r))
                case ast.UnaryOp(op=o, operand=v):       return allowed[type(o)](_ev(v))
                case _: raise ValueError
        res = _ev(ast.parse(expression, mode="eval").body)
        return str(int(res)) if res == int(res) else str(res)

    def click(b: str) -> None:
        if   b == "=": 
            try: expr_val[0] = _safe_eval(expr_val[0])
            except Exception: expr_val[0] = "Error"
        elif b == "C": expr_val[0] = ""
        else:          expr_val[0] += b
        dpg.set_value("calc_display", expr_val[0])

    with dpg.window(label="WarpCalc", tag="win_calc",
                    width=260, height=340, pos=(300, 200),
                    on_close=lambda: dpg.delete_item("win_calc")):
        dpg.add_input_text(tag="calc_display", default_value="",
                           width=-1, readonly=True, hint="0")
        dpg.add_spacer(height=4)
        for row in [("7","8","9","/"), ("4","5","6","*"),
                    ("1","2","3","-"), ("C","0","=","+")]:
            with dpg.group(horizontal=True):
                for b in row:
                    col = GRV_ORANGE_DIM if b in "/*-+=" else (GRV_RED if b == "C" else GRV_BG1)
                    with dpg.theme() as btn_theme:
                        with dpg.theme_component(dpg.mvButton):
                            dpg.add_theme_color(dpg.mvThemeCol_Button, col)
                    btn = dpg.add_button(label=b, width=54, height=54,
                                         callback=lambda s, a, u: click(u), user_data=b)
                    dpg.bind_item_theme(btn, btn_theme)


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
            dpg.add_selectable(label=" .. [up one level]", parent="fb_list", callback=_go_up)
        for item in filesystem.get(_fb_path[0], {}).get("contents", []):
            full   = f"~/{item}" if _fb_path[0] == "~" else f"{_fb_path[0]}/{item}"
            is_dir = filesystem.get(full, {}).get("type") == "dir"
            col    = GRV_YELLOW if is_dir else GRV_FG
            dpg.add_selectable(label=f" {'[D]' if is_dir else '[F]'}  {item}",
                               parent="fb_list", callback=_on_fb_click, user_data=item)
            kids = dpg.get_item_children("fb_list", 1)
            if kids:
                with dpg.theme() as t:
                    with dpg.theme_component(dpg.mvSelectable):
                        dpg.add_theme_color(dpg.mvThemeCol_Text, col)
                dpg.bind_item_theme(kids[-1], t)

    def _go_up() -> None:
        parts = _fb_path[0].split("/")
        _fb_path[0] = "/".join(parts[:-1]) if len(parts) > 1 else "~"
        refresh()

    def _on_fb_click(sender, app_data, user_data) -> None:
        full  = f"~/{user_data}" if _fb_path[0] == "~" else f"{_fb_path[0]}/{user_data}"
        entry = filesystem.get(full, {})
        if entry.get("type") == "dir":
            _fb_path[0] = full; refresh()
        elif entry.get("type") == "file":
            _dpg_text_viewer(user_data, entry["content"])

    with dpg.window(label="Tree — File Browser", tag="win_fb",
                    width=480, height=420, pos=(120, 100),
                    on_close=lambda: dpg.delete_item("win_fb")):
        dpg.add_text("~", tag="fb_path_text", color=GRV_YELLOW)
        dpg.add_separator()
        with dpg.child_window(tag="fb_list", height=-1, border=False):
            pass
    refresh()


def _dpg_text_viewer(filename: str, content: str) -> None:
    tag = f"win_viewer_{filename}"
    if dpg.does_item_exist(tag):
        dpg.delete_item(tag)
    with dpg.window(label=f"Viewer: {filename}", tag=tag,
                    width=480, height=340, pos=(200, 180),
                    on_close=lambda: dpg.delete_item(tag)):
        dpg.add_input_text(default_value=content, multiline=True,
                           readonly=True, width=-1, height=-1)


def _dpg_pwdit(filename: str | None = None) -> None:
    tag = "win_pwdit"
    if dpg.does_item_exist(tag):
        dpg.delete_item(tag)

    cur_file    = [filename or "new_file.txt"]
    is_modified = [False]
    initial     = ""
    if filename:
        path    = f"~/{filename}" if S.current_dir == "~" else f"{S.current_dir}/{filename}"
        initial = filesystem.get(path, {}).get("content", "")

    def save() -> None:
        content = dpg.get_value("pwdit_text")
        path    = f"~/{cur_file[0]}" if S.current_dir == "~" else f"{S.current_dir}/{cur_file[0]}"
        filesystem[path] = {"type": "file", "content": content}
        if cur_file[0] not in filesystem[S.current_dir]["contents"]:
            filesystem[S.current_dir]["contents"].append(cur_file[0])
        save_system()
        is_modified[0] = False
        dpg.set_value("pwdit_status", f"saved: {cur_file[0]}")

    def save_as() -> None:
        if dpg.does_item_exist("pwdit_saveas_popup"):
            dpg.delete_item("pwdit_saveas_popup")
        with dpg.window(label="Save As", tag="pwdit_saveas_popup",
                        width=320, height=110, pos=(300, 250), modal=True,
                        on_close=lambda: dpg.delete_item("pwdit_saveas_popup")):
            dpg.add_text("Enter filename:", color=GRV_YELLOW)
            dpg.add_input_text(tag="pwdit_saveas_input", default_value=cur_file[0], width=-1)
            with dpg.group(horizontal=True):
                def do_save_as() -> None:
                    new = dpg.get_value("pwdit_saveas_input").strip()
                    if new:
                        cur_file[0] = new
                        dpg.configure_item("win_pwdit", label=f"GPWDIT — {new}")
                        save()
                    dpg.delete_item("pwdit_saveas_popup")
                dpg.add_button(label="Save",   width=100, callback=do_save_as)
                dpg.add_button(label="Cancel", width=80,
                               callback=lambda: dpg.delete_item("pwdit_saveas_popup"))

    with dpg.window(label=f"GPWDIT — {cur_file[0]}", tag=tag,
                    width=700, height=520, pos=(150, 80),
                    on_close=lambda: dpg.delete_item(tag)):
        with dpg.group(horizontal=True):
            dpg.add_button(label="Save",    callback=lambda: save(),    width=80)
            dpg.add_button(label="Save As", callback=lambda: save_as(), width=90)
            dpg.add_button(label="New", width=70, callback=lambda: (
                dpg.set_value("pwdit_text", ""),
                cur_file.__setitem__(0, "new_file.txt"),
                dpg.set_value("pwdit_status", "new file"),
            ))
        dpg.add_separator()
        dpg.add_input_text(tag="pwdit_text", default_value=initial,
                           multiline=True, width=-1, height=-40,
                           tab_input=True,
                           callback=lambda: is_modified.__setitem__(0, True))
        dpg.add_text("", tag="pwdit_status", color=GRV_GRAY)


def _dpg_paint() -> None:
    for tag in ("win_paint", "paint_drag_handler"):
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)

    current_color = [GRV_ORANGE_DIM]
    COLORS = [GRV_BG, GRV_RED, GRV_ORANGE, GRV_YELLOW, GRV_GREEN, GRV_AQUA, GRV_FG]

    with dpg.window(label="PenguPaint", tag="win_paint",
                    width=520, height=480, pos=(160, 100),
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
                btn = dpg.add_button(label="   ", width=36, height=26,
                                     callback=lambda s, a, u: current_color.__setitem__(0, u),
                                     user_data=c)
                dpg.bind_item_theme(btn, sw)
            dpg.add_button(label="Clear",
                           callback=lambda: dpg.delete_item("paint_canvas", children_only=True))
        dpg.add_separator()
        with dpg.drawlist(width=494, height=390, tag="paint_canvas"):
            pass

    with dpg.handler_registry(tag="paint_drag_handler"):
        def on_draw(sender, app_data) -> None:
            if not dpg.does_item_exist("paint_canvas"): return
            if not dpg.is_item_hovered("paint_canvas"):  return
            x, y = dpg.get_drawing_mouse_pos()
            dpg.draw_circle((x, y), 5, color=current_color[0],
                            fill=current_color[0], parent="paint_canvas")
        dpg.add_mouse_drag_handler(callback=on_draw)


# ── Desktop / main entry ──────────────────────────────────────────────────────

def start_gui() -> None:
    if not HAS_DPG:
        print(f"{Fore.RED}error: dearpygui not installed."
              f" run: pip install dearpygui --break-system-packages{Fore.WHITE}")
        return

    dpg.create_context()
    dpg.create_viewport(title="PenguWarp Desktop", width=1024, height=768)
    _apply_gruvbox_theme()

    # Menu bar
    with dpg.viewport_menu_bar():
        dpg.add_menu_item(label="PenguWarp", enabled=False)
        with dpg.menu(label="Apps"):
            dpg.add_menu_item(label="[F]  File Browser",  callback=_dpg_file_browser)
            dpg.add_menu_item(label="[E]  GPWDIT Editor", callback=lambda: _dpg_pwdit())
            dpg.add_menu_item(label="[C]  WarpCalc",      callback=_dpg_calculator)
            dpg.add_menu_item(label="[P]  PenguPaint",    callback=_dpg_paint)
            dpg.add_menu_item(label="[K]  ClockWarp",     callback=_dpg_clock)
            dpg.add_menu_item(label="[S]  Gardener",      callback=_dpg_sysinfo)
        with dpg.menu(label="Session"):
            dpg.add_menu_item(label="[X]  Logout", callback=lambda: dpg.stop_dearpygui())
        dpg.add_menu_item(label=time.strftime("%H:%M"), tag="topbar_clock", enabled=False)
        dpg.add_menu_item(label=f"  {S.user}@{S.hostname}  ", tag="topbar_user", enabled=False)

    # Desktop background window
    with dpg.window(label="Desktop", tag="win_desktop",
                    width=1920, height=1040, pos=(0, 0),
                    no_title_bar=True, no_move=True, no_resize=True,
                    no_bring_to_front_on_focus=True, no_scrollbar=True):
        dpg.add_spacer(height=440)
        with dpg.group(horizontal=False):
            dpg.add_text("PENGUWARP WORKSTATION", color=GRV_YELLOW, tag="desktop_title")
            dpg.add_text('v0.1.7 "Lemon" Testing', color=GRV_ORANGE, tag="desktop_sub")

        for label, cb, x, y in [
            ("[F]\nTree",       _dpg_file_browser,    30,  50),
            ("[C]\nWarpCalc",   _dpg_calculator,      30, 150),
            ("[P]\nPenguPaint", _dpg_paint,           30, 250),
            ("[G]\nGPWDIT",     lambda: _dpg_pwdit(), 30, 350),
            ("[S]\nGardener",   _dpg_sysinfo,         30, 450),
            ("[K]\nClockWarp",  _dpg_clock,           30, 550),
        ]:
            dpg.add_button(label=label, callback=cb, width=70, height=70, pos=(x, y))

    def _render_loop() -> None:
        if dpg.does_item_exist("topbar_clock"):
            dpg.set_item_label("topbar_clock", time.strftime(" %H:%M:%S "))
        if dpg.does_item_exist("clock_text"):
            dpg.set_value("clock_text", time.strftime("%H:%M:%S"))
        if dpg.does_item_exist("desktop_title") and dpg.does_item_exist("win_desktop"):
            w = dpg.get_item_width("win_desktop")
            dpg.configure_item("desktop_title", indent=max(0, (w - 200) // 2))
            dpg.configure_item("desktop_sub",   indent=max(0, (w - 170) // 2))

    dpg.set_frame_callback(2, callback=lambda: None)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    while dpg.is_dearpygui_running():
        _render_loop()
        dpg.render_dearpygui_frame()
    dpg.destroy_context()
