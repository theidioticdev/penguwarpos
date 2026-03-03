"""
kernel.py — PenguWarp OS  v0.1.7 "Lemon" (Testing)
Entry point: boot sequence, shell loop, tab completion.
"""

import os
import sys
import time
import readline
from colorama import Fore, init

import system as S
from system import load_system, save_system, SYSTEM_FILE
from commands import COMMANDS, execute_command

init(autoreset=True)

# ── Boot visuals ──────────────────────────────────────────────────────────────

def _boot_splash() -> None:
    try:
        from rich.console import Console
        from rich.panel import Panel
        console = Console()
        penguin = "\n           ___\n          <   o>\n          ( | )\n          /___\\\n        "
        for i in range(6):
            console.clear()
            console.print(Panel(
                f"[yellow]{penguin}[/yellow]\n"
                f'[bold orange1]PenguWarp OS v0.1.7 "Lemon" (Testing)[/bold orange1]\n'
                f"[dim]Initializing{'.' * (i + 1)}[/dim]",
                border_style="yellow",
                title="[bold]PENGUWARP[/bold]",
            ))
            time.sleep(0.5)
        console.clear()
    except ImportError:
        pass


def _boot_sequence() -> None:
    print(f"{Fore.YELLOW}PenguWarp Kernel v0.1.7-lemon-dev_x86_64 initializing...")
    time.sleep(0.4)
    for msg in [
        "Detecting hardware...",
        "Mounting drive /dev/sda...",
        "Initializing Memory Manager...",
        "Loading PWShell...",
    ]:
        print(f"  [{Fore.YELLOW}  OK  {Fore.WHITE}] {msg}")
        time.sleep(0.2)
    print(f'\n{Fore.YELLOW}   ___\n  <   o>  PenguWarp OS\n  ( | )   v0.1.7 "Lemon" Testing\n  /___\\ \n')


def _first_boot_setup() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    print(f"{Fore.YELLOW}╔══════════════════════════════════════════════════╗")
    print(f'{Fore.YELLOW}║  ~ Welcome to PenguWarp OS "Lemon (Testing)"!  ~ ║')
    print(f"{Fore.YELLOW}╚══════════════════════════════════════════════════╝\n")

    S.user     = input(f"{Fore.YELLOW}Choose Username: {Fore.WHITE}").strip() or "user"
    raw_pw     = input(f"{Fore.YELLOW}Choose Password: {Fore.WHITE}").strip()
    S.hostname = input(f"{Fore.YELLOW}Choose Hostname: {Fore.WHITE}").strip() or "pengu"

    from system import hash_pw
    S.users_list.append({"username": S.user, "password": hash_pw(raw_pw), "is_admin": True})
    S.filesystem.update({
        "~": {"type": "dir", "contents": ["Documents", "Downloads", "Pictures", "Desktop", "welcome.txt"]},
        "~/Documents": {"type": "dir", "contents": []},
        "~/Downloads": {"type": "dir", "contents": []},
        "~/Pictures":  {"type": "dir", "contents": []},
        "~/Desktop":   {"type": "dir", "contents": []},
        "~/welcome.txt": {"type": "file", "content": (
            f'Welcome to PenguWarp OS "Lemon", {S.user}!\n\n'
            "Explore around, and run 'pkgmgr search' to find packages.\n"
            "Type 'help' to begin.\n\n"
            "Built with Python & Dear PyGui."
        )},
    })
    save_system()
    print(f"\n{Fore.YELLOW}System initialized. Booting...")
    time.sleep(1)


# ── Tab completion ────────────────────────────────────────────────────────────

def _setup_readline() -> None:
    def completer(text: str, state: int) -> str | None:
        buf   = readline.get_line_buffer()
        parts = buf.split()
        # command completion
        if not parts or (len(parts) == 1 and not buf.endswith(" ")):
            all_cmds = list(COMMANDS.keys()) + S.installed_packages
            matches  = [c for c in all_cmds if c.startswith(text)]
            return matches[state] if state < len(matches) else None
        # path completion
        prefix   = text
        base_dir = S.current_dir
        if "/" in prefix:
            idx      = prefix.rfind("/")
            base_dir = prefix[:idx] or "~"
            prefix   = prefix[idx + 1:]
        contents = S.filesystem.get(base_dir, {}).get("contents", [])
        matches  = [i for i in contents if i.startswith(prefix)]
        if state < len(matches):
            item = matches[state]
            full = f"~/{item}" if base_dir == "~" else f"{base_dir}/{item}"
            return item + ("/" if S.filesystem.get(full, {}).get("type") == "dir" else "")
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
                f"{Fore.YELLOW}{S.user}@{S.hostname}"
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
    _boot_sequence()
    _shell_loop()
