"""
loginmgr.py — PenguWarp Graphical Login Manager (LightWarp)
Boots directly into PenguWin DE after successful authentication.
"""

import sys
import time

import system as S
from system import hash_pw, save_system

try:
    import dearpygui.dearpygui as dpg
    HAS_DPG = True
except ImportError:
    HAS_DPG = False

from colorama import Fore

# ── Gruvbox palette (reuse from system) ──────────────────────────────────────
from system import (
    GRV_BG, GRV_BG1, GRV_BG2, GRV_BG_HARD,
    GRV_FG, GRV_YELLOW, GRV_YELLOW_DIM,
    GRV_ORANGE, GRV_ORANGE_DIM, GRV_RED,
    GRV_GREEN, GRV_AQUA, GRV_GRAY,
)

PENGUIN = (
    "        ___\n"
    "       <   o>\n"
    "       ( | )\n"
    "       /___\\"
)


# ── Theme ─────────────────────────────────────────────────────────────────────

def _apply_login_theme() -> None:
    with dpg.theme() as t:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg,       GRV_BG_HARD)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg,        GRV_BG_HARD)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg,        GRV_BG1)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, GRV_BG2)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive,  GRV_BG2)
            dpg.add_theme_color(dpg.mvThemeCol_Button,         GRV_ORANGE_DIM)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,  GRV_ORANGE)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,   GRV_YELLOW_DIM)
            dpg.add_theme_color(dpg.mvThemeCol_Text,           GRV_FG)
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled,   GRV_GRAY)
            dpg.add_theme_color(dpg.mvThemeCol_Border,         GRV_BG2)
            dpg.add_theme_color(dpg.mvThemeCol_Separator,      GRV_BG2)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding,  6)
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding,   6)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding,  16, 16)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding,   10, 6)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing,    8, 8)
    dpg.bind_theme(t)


# ── Login window ──────────────────────────────────────────────────────────────

def _build_login_window(vw: int, vh: int) -> None:
    WIN_W, WIN_H = 380, 420
    px = (vw - WIN_W) // 2
    py = (vh - WIN_H) // 2

    if dpg.does_item_exist("win_login"):
        dpg.delete_item("win_login")

    with dpg.window(
        tag="win_login",
        label="",
        width=WIN_W, height=WIN_H,
        pos=(px, py),
        no_title_bar=True,
        no_move=True,
        no_resize=True,
        no_close=True,
        no_scrollbar=True,
    ):
        dpg.add_spacer(height=10)

        # penguin + title
        dpg.add_text(PENGUIN, color=GRV_YELLOW)
        dpg.add_spacer(height=6)
        dpg.add_text("PenguWarp OS", color=GRV_YELLOW)
        dpg.add_text(f'v0.1.8 "Lemon" Testing', color=GRV_ORANGE)
        dpg.add_spacer(height=2)
        dpg.add_text(f"  {S.hostname}", color=GRV_GRAY)

        dpg.add_spacer(height=14)
        dpg.add_separator()
        dpg.add_spacer(height=14)

        # username field
        dpg.add_text("Username", color=GRV_GRAY)
        dpg.add_input_text(
            tag="login_user",
            hint="enter username...",
            width=-1,
            default_value=S.user,
            on_enter=True,
            callback=lambda: dpg.focus_item("login_pass"),
        )

        dpg.add_spacer(height=10)

        # password field
        dpg.add_text("Password", color=GRV_GRAY)
        dpg.add_input_text(
            tag="login_pass",
            hint="enter password...",
            width=-1,
            password=True,
            on_enter=True,
            callback=_attempt_login,
        )

        dpg.add_spacer(height=6)

        # error label (hidden until needed)
        dpg.add_text("", tag="login_error", color=GRV_RED)

        dpg.add_spacer(height=10)

        # login button
        dpg.add_button(
            label="Log In",
            width=-1,
            height=42,
            callback=_attempt_login,
            tag="login_btn",
        )

        dpg.add_spacer(height=8)
        dpg.add_separator()
        dpg.add_spacer(height=6)
        dpg.add_text("Type username + password, then press Enter or Log In.",
                     color=GRV_GRAY)


# ── Auth logic ────────────────────────────────────────────────────────────────

_login_success = [False]
_logged_in_user = [""]


def _attempt_login() -> None:
    username = dpg.get_value("login_user").strip()
    password = dpg.get_value("login_pass").strip()

    if not username or not password:
        dpg.set_value("login_error", "  ✗  Username and password required")
        return

    target = next((u for u in S.users_list if u["username"] == username), None)

    if target is None:
        dpg.set_value("login_error", f"  ✗  User '{username}' not found")
        dpg.set_value("login_pass", "")
        return

    if hash_pw(password) != target["password"]:
        dpg.set_value("login_error", "  ✗  Incorrect password")
        dpg.set_value("login_pass", "")
        return

    # ── success ───────────────────────────────────────────────────────────────
    dpg.set_value("login_error", "")
    dpg.configure_item("login_btn", label="Logging in...")
    dpg.configure_item("login_btn", enabled=False)

    # update system state to the authenticated user
    S.user = username
    S.current_dir = target.get("home", f"~/usr/{username}")
    save_system()

    _logged_in_user[0] = username
    _login_success[0] = True
    dpg.stop_dearpygui()


# ── Main entry ────────────────────────────────────────────────────────────────

def start_login() -> bool:
    """
    Show the graphical login manager.
    Returns True if login succeeded and DE should launch,
    False if it should fall back to PWShell.
    """
    if not HAS_DPG:
        print(f"{Fore.RED}loginmgr: dearpygui not available — falling back to PWShell{
              Fore.WHITE}")
        return False

    dpg.create_context()
    dpg.create_viewport(
        title="PenguWarp Login",
        width=1024, height=768,
        min_width=640, min_height=480,
    )
    _apply_login_theme()

    vw = dpg.get_viewport_width()
    vh = dpg.get_viewport_height()

    # fullscreen dark background
    with dpg.window(
        tag="win_bg",
        label="",
        width=1920, height=1080,
        pos=(0, 0),
        no_title_bar=True, no_move=True, no_resize=True,
        no_close=True, no_scrollbar=True,
        no_bring_to_front_on_focus=True,
    ):
        pass

    _build_login_window(vw, vh)

    # re-center on resize
    def _on_resize() -> None:
        nw = dpg.get_viewport_width()
        nh = dpg.get_viewport_height()
        _build_login_window(nw, nh)

    with dpg.handler_registry():
        dpg.add_key_press_handler(
            key=dpg.mvKey_F5,
            callback=lambda: _build_login_window(
                dpg.get_viewport_width(), dpg.get_viewport_height()
            ),
        )

    dpg.setup_dearpygui()
    dpg.show_viewport()

    # render loop — stays alive until login succeeds or window closed
    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()

    dpg.close_viewport()
    dpg.destroy_context()

    return _login_success[0]
