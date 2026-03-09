import os
import readline
import sys
import time

from colorama import Fore, Style, init

import system as S
from commands import COMMANDS, execute_command
from system import SYSTEM_FILE, load_system, save_system

init(autoreset=True)

# ── Boot visuals ──────────────────────────────────────────────────────────────

PENGUIN = [
    "    ___    ",
    "   (o o)   ",
    "   ( V )   ",
    "  /|___|\\  ",
    " / |   | \\ ",
    "   |___|   ",
]

PENGUIN_BLINK = [
    "    ___    ",
    "   (- -)   ",
    "   ( V )   ",
    "  /|___|\\  ",
    " / |   | \\ ",
    "   |___|   ",
]

BANNER = [
    " ██████╗ ███████╗███╗   ██╗ ██████╗ ██╗   ██╗██╗    ██╗ █████╗ ██████╗ ██████╗ ",
    " ██╔══██╗██╔════╝████╗  ██║██╔════╝ ██║   ██║██║    ██║██╔══██╗██╔══██╗██╔══██╗",
    " ██████╔╝█████╗  ██╔██╗ ██║██║  ███╗██║   ██║██║ █╗ ██║███████║██████╔╝██████╔╝",
    " ██╔═══╝ ██╔══╝  ██║╚██╗██║██║   ██║██║   ██║██║███╗██║██╔══██║██╔══██╗██╔═══╝ ",
    " ██║     ███████╗██║ ╚████║╚██████╔╝╚██████╔╝╚███╔███╔╝██║  ██║██║  ██║██║     ",
    " ╚═╝     ╚══════╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ",
]

BOOT_MSGS = [
    ("Detecting hardware...", True),
    ("Mounting /dev/sda...", True),
    ("Initializing Memory Manager...", True),
    ("Starting filesystem...", True),
    ("Loading PWShell...", True),
    ("Spawning user environment...", True),
]


def _clear():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def _color_banner():
    colors = [
        Fore.YELLOW,
        Fore.YELLOW,
        Fore.WHITE,
        Fore.WHITE,
        Fore.YELLOW,
        Fore.YELLOW,
    ]
    for i, line in enumerate(BANNER):
        print(colors[i % len(colors)] + line)


def _draw_frame(penguin_art, status_line="", progress=0, show_status=False):
    _clear()
    print()
    _color_banner()
    print()
    for line in penguin_art:
        print(f"         {Fore.YELLOW}{line}")
    print()
    print(
        f'         {Fore.WHITE}PenguWarp OS  {
            Fore.YELLOW}v0.1.8 "Lemon"{Fore.WHITE}  [Testing]'
    )
    print()
    if show_status and status_line:
        ok = f"{Fore.GREEN}  OK  {Fore.WHITE}"
        print(f"  [{ok}] {Fore.WHITE}{status_line}")
    elif status_line:
        print(f"  {Style.DIM}{status_line}")
    if progress > 0:
        bar_len = 40
        filled = int(bar_len * progress / 100)
        bar = f"{Fore.YELLOW}{
            '█' * filled}{Fore.WHITE}{'░' * (bar_len - filled)}"
        print(f"\n  [{bar}{Fore.WHITE}] {Fore.YELLOW}{progress}%")


def _boot_splash() -> None:
    # phase 1: penguin blinks while banner loads
    for i in range(3):
        _draw_frame(
            PENGUIN if i % 2 == 0 else PENGUIN_BLINK, "Waking up...", progress=0
        )
        time.sleep(0.35)
    # phase 2: boot messages with progress bar
    total = len(BOOT_MSGS)
    for idx, (msg, _) in enumerate(BOOT_MSGS):
        progress = int(((idx + 1) / total) * 100)
        _draw_frame(PENGUIN, msg, progress=progress, show_status=True)
        time.sleep(0.22)
    # phase 3: boot complete flash
    for _ in range(2):
        _draw_frame(
            PENGUIN, f"{Fore.GREEN}Boot complete!", progress=100, show_status=False
        )
        time.sleep(0.18)
        _draw_frame(
            PENGUIN_BLINK,
            f"{Fore.GREEN}Boot complete!",
            progress=100,
            show_status=False,
        )
        time.sleep(0.18)
    _draw_frame(PENGUIN, f"{Fore.GREEN}Boot complete!",
                progress=100, show_status=False)
    time.sleep(0.4)
    _clear()


# ── First boot setup ──────────────────────────────────────────────────────────


def _first_boot_setup() -> None:
    from setup import run_setup
    from system import hash_pw

    data = run_setup()

    hostname = data["hostname"]
    username = data["username"]
    password = data["password"]

    S.hostname = hostname

    # ── root: auto-created, home is ~, is_admin ───────────────────────────────
    root_pw = hash_pw(str(__import__("uuid").uuid4()))  # random unguessable pw
    S.users_list.append(
        {
            "username": "root",
            "password": root_pw,
            "is_admin": True,
            "home": "~",
        }
    )

    # ── regular user: home is ~/usr/<username> ────────────────────────────────
    S.users_list.append(
        {
            "username": username,
            "password": hash_pw(password),
            "is_admin": True,
            "home": f"~/usr/{username}",
        }
    )

    user_home = f"~/usr/{username}"

    # ── filesystem layout ─────────────────────────────────────────────────────
    S.filesystem.update(
        {
            # root dirs
            "~": {"type": "dir", "contents": ["sys", "usr", "pkgs", "tmp"]},
            "~/sys": {"type": "dir", "contents": ["version"]},
            "~/usr": {"type": "dir", "contents": [username]},
            "~/pkgs": {"type": "dir", "contents": []},
            "~/tmp": {"type": "dir", "contents": []},
            # system files
            "~/sys/version": {
                "type": "file",
                "content": 'PenguWarp OS v0.1.8 "Lemon" Testing\nKernel: v0.1.8-lemon-dev_x86_64',
            },
            # user home
            user_home: {"type": "dir", "contents": ["welcome.txt"]},
            f"{user_home}/welcome.txt": {
                "type": "file",
                "content": (
                    f'Welcome to PenguWarp OS "Lemon", {username}!\n\n'
                    f"Your home directory is {user_home}.\n"
                    "Type 'help' to see available commands.\n"
                    "Use 'pwpm search' to browse installable packages.\n\n"
                    "Built with Python & Dear PyGui."
                ),
            },
        }
    )

    # boot as the new regular user, starting in their home dir
    S.user = username
    S.current_dir = user_home

    save_system()


# ── Tab completion ────────────────────────────────────────────────────────────


def _setup_readline() -> None:
    def completer(text: str, state: int) -> str | None:
        buf = readline.get_line_buffer()
        parts = buf.split()
        # ── command completion ─────────────────────────────────────────
        if not parts or (len(parts) == 1 and not buf.endswith(" ")):
            all_cmds = list(COMMANDS.keys()) + S.installed_packages
            matches = [c for c in all_cmds if c.startswith(text)]
            return matches[state] if state < len(matches) else None
        # ── path completion ────────────────────────────────────────────
        if "/" in text:
            slash = text.rfind("/")
            dir_raw = text[:slash] or "~"
            prefix = text[slash + 1:]
            base_dir = S.resolve_path(dir_raw)
        else:
            base_dir = S.current_dir
            prefix = text

        contents = S.filesystem.get(base_dir, {}).get("contents", [])
        matches = [i for i in contents if i.startswith(prefix)]
        if state < len(matches):
            item = matches[state]
            full_path = f"{
                base_dir}/{item}" if base_dir != "~" else f"~/{item}"
            suffix = "/" if S.filesystem.get(full_path,
                                             {}).get("type") == "dir" else ""
            dir_prefix = text[: text.rfind("/") + 1] if "/" in text else ""
            return dir_prefix + item + suffix
        return None

    readline.set_completer(completer)
    readline.set_completer_delims(" \t")
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind('"\\e[A": previous-history')
    readline.parse_and_bind('"\\e[B": next-history')


# ── Shell loop ────────────────────────────────────────────────────────────────


def _shell_loop() -> None:
    _setup_readline()
    while True:
        try:
            prompt = (
                f"{Fore.YELLOW}{S.user} of {S.hostname}: "
                f"{Fore.WHITE}:{Fore.YELLOW}{S.current_dir}{Fore.WHITE}$ "
            )
            line = input(prompt).strip()
            execute_command(line)
        except KeyboardInterrupt:
            print("\nType 'poweroff' to exit.")
        except EOFError:
            execute_command("poweroff")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    is_first_boot = load_system()
    if is_first_boot:
        _first_boot_setup()
    else:
        _boot_splash()

    # ── Boot to GUI if penguwin is installed ─────────────────────────────────
    if "penguwin" in S.installed_packages:
        try:
            from packages.gui import start_gui
            result = start_gui()   # 'logout' | 'tty' | 'quit'
            if result == "tty":
                print(f"{Fore.YELLOW}Dropped to PWShell.{Fore.WHITE}")
            # all paths fall through to _shell_loop()
        except ImportError:
            print(f"{Fore.RED}pygame not available — falling back to PWShell{
                  Fore.WHITE}")

    _shell_loop()
