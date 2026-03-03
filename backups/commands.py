"""
commands.py — PWShell built-in commands for PenguWarp OS
"""

import os
import sys
import time
from colorama import Fore

import system as S
from system import (
    filesystem, installed_packages, users_list,
    COMMAND_DESC, SCRIPT_DIR,
    fs_path, hash_pw, get_dynamic_ram, is_admin, current_user_data,
    save_system, start_time,
)

try:
    import repo
except ImportError:
    repo = None


# ── Helpers ──────────────────────────────────────────────────────────────────

def _require_args(args: list, msg: str) -> bool:
    """Print error and return False if args is empty."""
    if not args:
        print(f"{Fore.RED}error: {msg}{Fore.WHITE}")
        return False
    return True


def _resolve(name: str) -> str:
    """Turn a bare filename into a full filesystem key."""
    if name.startswith("~"):
        return name
    if S.current_dir == "~":
        return f"~/{name}"
    return f"{S.current_dir}/{name}"


# ── Commands ─────────────────────────────────────────────────────────────────

def cmd_help(args: list[str]) -> None:
    print(f'\n{Fore.YELLOW}PENGUWARP OS v0.1.7 "LEMON" COMMAND REFERENCE')
    print(f"{Fore.WHITE}" + "-" * 60)
    for c, d in COMMAND_DESC.items():
        print(f"{Fore.YELLOW}{c:<12}{Fore.WHITE} : {d}")
    print("-" * 60 + "\n")


def cmd_list(args: list[str]) -> None:
    contents = filesystem.get(S.current_dir, {}).get("contents", [])
    if not contents:
        print("(directory empty)")
        return
    out = []
    for name in contents:
        full = _resolve(name)
        color = Fore.YELLOW if filesystem.get(full, {}).get("type") == "dir" else Fore.WHITE
        out.append(f"{color}{name}{Fore.WHITE}")
    print("  ".join(out))


def cmd_cd(args: list[str]) -> None:
    target = args[0] if args else "~"
    path = target if target.startswith("~") else _resolve(target)
    if filesystem.get(path, {}).get("type") == "dir":
        S.current_dir = path
    else:
        print(f"cd: no such directory: {target}")


def cmd_read(args: list[str]) -> None:
    if not _require_args(args, "provide a filename"):
        return
    path = _resolve(args[0])
    entry = filesystem.get(path, {})
    if entry.get("type") == "file":
        print(entry["content"])
    else:
        print(f"cat: {args[0]}: file not found")


def cmd_mkdir(args: list[str]) -> None:
    if not _require_args(args, "provide a directory name"):
        return
    path = _resolve(args[0])
    if path not in filesystem:
        filesystem[path] = {"type": "dir", "contents": []}
        filesystem[S.current_dir]["contents"].append(args[0])
        save_system()


def cmd_mkfile(args: list[str]) -> None:
    if not _require_args(args, "provide a filename"):
        return
    path = _resolve(args[0])
    if path not in filesystem:
        filesystem[path] = {"type": "file", "content": ""}
        filesystem[S.current_dir]["contents"].append(args[0])
        save_system()


def cmd_delete(args: list[str]) -> None:
    if not _require_args(args, "provide a filename"):
        return
    path = _resolve(args[0])
    if filesystem.get(path, {}).get("type") == "file":
        del filesystem[path]
        filesystem[S.current_dir]["contents"].remove(args[0])
        save_system()
    else:
        print(f"delete: {args[0]}: file not found")


def cmd_rmdir(args: list[str]) -> None:
    if not _require_args(args, "provide a directory name"):
        return
    path = _resolve(args[0])
    entry = filesystem.get(path, {})
    if entry.get("type") != "dir":
        print(f"rmdir: {args[0]}: no such directory")
        return
    if entry.get("contents"):
        print(f"rmdir: {args[0]}: directory not empty")
        return
    del filesystem[path]
    filesystem[S.current_dir]["contents"].remove(args[0])
    save_system()


def cmd_echo(args: list[str]) -> None:
    print(" ".join(args))


def cmd_whereami(args: list[str]) -> None:
    print(S.current_dir)


def cmd_whoami(args: list[str]) -> None:
    print(S.user)


def cmd_uname(args: list[str]) -> None:
    print("v0.1.7-lemon-dev_x86-64")


def cmd_clear(args: list[str]) -> None:
    os.system("cls" if os.name == "nt" else "clear")


def cmd_pyufetch(args: list[str]) -> None:
    uptime = int(time.time() - start_time)
    ascii_art = [
        f"{Fore.YELLOW} _____  __          __",
        f"{Fore.YELLOW}|  __ \\ \\ \\        / /",
        f"{Fore.YELLOW}| |__) | \\ \\  /\\  / / ",
        f"{Fore.YELLOW}|  ___/   \\ \\/  \\/ /  ",
        f"{Fore.YELLOW}| |        \\  /\\  /   ",
        f"{Fore.YELLOW}|_|         \\/  \\/    ",
    ]
    info = [
        f"{Fore.YELLOW}{S.user}@{S.hostname}",
        f"{Fore.WHITE}------------------",
        f'{Fore.YELLOW}OS: {Fore.WHITE}PenguWarp v0.1.7 "Lemon"',
        f"{Fore.YELLOW}Kernel: {Fore.WHITE}v0.1.7-lemon-dev_x86-64",
        f"{Fore.YELLOW}Uptime: {Fore.WHITE}{uptime}s",
        f"{Fore.YELLOW}Shell: {Fore.WHITE}PWShell",
        f"{Fore.YELLOW}Packages: {Fore.WHITE}{3 + len(installed_packages)}",
    ]
    for i in range(max(len(ascii_art), len(info))):
        left  = ascii_art[i] if i < len(ascii_art) else " " * 22
        right = info[i]      if i < len(info)       else ""
        print(f"{left}    {right}")


def cmd_pwdit(args: list[str]) -> None:
    if not _require_args(args, "provide a filename"):
        return
    path = _resolve(args[0])
    print(f"Editing {args[0]} (Double Enter to save | Ctrl+C to cancel)")
    lines: list[str] = []
    try:
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        filesystem[path] = {"type": "file", "content": "\n".join(lines).strip()}
        if args[0] not in filesystem[S.current_dir]["contents"]:
            filesystem[S.current_dir]["contents"].append(args[0])
        save_system()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Cancelling editing...")


def cmd_run(args: list[str]) -> None:
    if not _require_args(args, "provide a script name"):
        return
    path = _resolve(args[0])
    if path not in filesystem or not args[0].endswith(".pwe"):
        print(f"run: {args[0]}: not a valid .pwe script")
        return
    lines  = filesystem[path]["content"].split("\n")
    errors = 0
    print(f"{Fore.YELLOW}Executing {args[0]}...")
    for i, raw in enumerate(lines, 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        cmd_name = stripped.split()[0]
        if cmd_name not in COMMANDS and cmd_name not in installed_packages:
            print(f"{Fore.RED}run: {args[0]}: line {i}: unknown command '{cmd_name}'{Fore.WHITE}")
            errors += 1
            continue
        execute_command(stripped)
    status = f"{Fore.RED}finished with {errors} error(s)" if errors else f"{Fore.YELLOW}done"
    print(f"run: {args[0]}: {status}{Fore.WHITE}")


def cmd_pkgmgr(args: list[str]) -> None:
    if repo is None:
        print(f"{Fore.RED}Error: repo.py not found — package manager unavailable{Fore.WHITE}")
        return

    if not args:
        print(f"{Fore.YELLOW}=== PENGUWARP PACKAGE MANAGER ==={Fore.WHITE}")
        for flag, desc in [
            ("search",       "Show all available packages"),
            ("list",         "Show installed packages"),
            ("install <pkg>","Install a package"),
            ("remove <pkg>", "Remove a package"),
        ]:
            print(f"  {Fore.YELLOW}pkgmgr {flag:<16}{Fore.WHITE} - {desc}")
        return

    action = args[0]

    if action == "search":
        print(f"\n{Fore.YELLOW}=== AVAILABLE PACKAGES ==={Fore.WHITE}")
        for name, info in repo.AVAILABLE_PACKAGES.items():
            tag = f" {Fore.GREEN}[INSTALLED]{Fore.WHITE}" if name in installed_packages else ""
            print(f"{Fore.YELLOW}{name:<12}{Fore.WHITE} - {info['description']}{tag}")
        print()

    elif action == "list":
        if not installed_packages:
            print(f"{Fore.YELLOW}No packages installed. Use 'pkgmgr search' to browse.{Fore.WHITE}")
            return
        print(f"\n{Fore.YELLOW}=== INSTALLED PACKAGES ==={Fore.WHITE}")
        for pkg in installed_packages:
            if pkg in repo.AVAILABLE_PACKAGES:
                print(f"{Fore.YELLOW}{pkg:<12}{Fore.WHITE} - {repo.AVAILABLE_PACKAGES[pkg]['description']}")
        print()

    elif action == "install":
        if not (S._adminrun_active or is_admin()):
            print(f"{Fore.RED}error: permission denied — use adminrun{Fore.WHITE}")
            return
        if len(args) < 2:
            print(f"{Fore.RED}Error: specify a package name{Fore.WHITE}")
            return
        pkg = args[1]
        if pkg not in repo.AVAILABLE_PACKAGES:
            print(f"{Fore.RED}Error: package '{pkg}' not found{Fore.WHITE}")
            return
        if pkg in installed_packages:
            print(f"{Fore.YELLOW}'{pkg}' is already installed{Fore.WHITE}")
            return
        print(f"Downloading {pkg}...", end="", flush=True)
        for _ in range(10):
            time.sleep(0.1)
            print("█", end="", flush=True)
        installed_packages.append(pkg)
        save_system()
        print(f"\n{Fore.GREEN}✓{Fore.WHITE} Installed {Fore.YELLOW}{repo.AVAILABLE_PACKAGES[pkg]['name']}{Fore.WHITE}")
        print(f"  Run it with: {Fore.YELLOW}{pkg}{Fore.WHITE}")

    elif action == "remove":
        if not (S._adminrun_active or is_admin()):
            print(f"{Fore.RED}error: permission denied — use adminrun{Fore.WHITE}")
            return
        if len(args) < 2:
            print(f"{Fore.RED}Error: specify a package name{Fore.WHITE}")
            return
        pkg = args[1]
        if pkg not in installed_packages:
            print(f"{Fore.YELLOW}'{pkg}' is not installed{Fore.WHITE}")
            return
        installed_packages.remove(pkg)
        save_system()
        print(f"{Fore.GREEN}✓{Fore.WHITE} Removed {Fore.YELLOW}{pkg}{Fore.WHITE}")

    else:
        print(f"{Fore.RED}pkgmgr: unknown action '{action}'{Fore.WHITE}")


def cmd_startx(args: list[str]) -> None:
    print(f"{Fore.YELLOW}Loading Desktop Environment...")
    for i in range(11):
        sys.stdout.write(f"\r[{'#' * i}{'.' * (10 - i)}] {i * 10}%")
        sys.stdout.flush()
        time.sleep(0.08)
    print("\n")
    from gui import start_gui
    start_gui()
    print(f"{Fore.YELLOW}Desktop closed. Back in PWShell.{Fore.WHITE}")


def cmd_poweroff(args: list[str]) -> None:
    print(f"{Fore.RED}Shutting down PenguWarp Lemon...")
    save_system()
    time.sleep(1)
    sys.exit(0)


def cmd_usercn(args: list[str]) -> None:
    if not _require_args(args, "provide a new username"):
        return
    S.user = args[0]
    save_system()
    print(f"{Fore.YELLOW}usercn: username changed to '{S.user}'{Fore.WHITE}")


def cmd_hostcn(args: list[str]) -> None:
    if not _require_args(args, "provide a new hostname"):
        return
    S.hostname = args[0]
    save_system()
    print(f"{Fore.YELLOW}hostcn: hostname changed to '{S.hostname}'{Fore.WHITE}")


def cmd_userlist(args: list[str]) -> None:
    print(f"{Fore.YELLOW}=== USERS ==={Fore.WHITE}")
    for u in users_list:
        admin_tag = f" {Fore.CYAN}[admin]{Fore.WHITE}" if u.get("is_admin") else ""
        print(f"  {Fore.YELLOW}{u['username']}{Fore.WHITE}{admin_tag}")


def cmd_useradd(args: list[str]) -> None:
    if not _require_args(args, "provide a username"):
        return
    name = args[0]
    if any(u["username"] == name for u in users_list):
        print(f"{Fore.RED}error: user '{name}' already exists{Fore.WHITE}")
        return
    pw = input(f"{Fore.YELLOW}Set password for {name}: {Fore.WHITE}").strip()
    users_list.append({"username": name, "password": hash_pw(pw), "is_admin": False})
    save_system()
    print(f"{Fore.GREEN}✓{Fore.WHITE} User '{Fore.YELLOW}{name}{Fore.WHITE}' created")


def cmd_su(args: list[str]) -> None:
    if not _require_args(args, "provide a username"):
        return
    target = args[0]
    target_u = next((u for u in users_list if u["username"] == target), None)
    if not target_u:
        print(f"{Fore.RED}su: user '{target}' not found{Fore.WHITE}")
        return
    pw = input(f"{Fore.YELLOW}Password for {target}: {Fore.WHITE}").strip()
    if hash_pw(pw) == target_u["password"]:
        S.user = target
        save_system()
        print(f"{Fore.GREEN}✓{Fore.WHITE} Switched to {Fore.YELLOW}{target}{Fore.WHITE}")
    else:
        print(f"{Fore.RED}su: incorrect password{Fore.WHITE}")


def cmd_passwd(args: list[str]) -> None:
    target_name = args[0] if args else S.user
    target_u = next((u for u in users_list if u["username"] == target_name), None)
    if not target_u:
        print(f"{Fore.RED}passwd: user '{target_name}' not found{Fore.WHITE}")
        return
    if target_name != S.user and not is_admin():
        print(f"{Fore.RED}passwd: permission denied — use adminrun{Fore.WHITE}")
        return
    old = input(f"{Fore.YELLOW}Current password: {Fore.WHITE}").strip()
    if hash_pw(old) != target_u["password"]:
        print(f"{Fore.RED}passwd: incorrect password{Fore.WHITE}")
        return
    new  = input(f"{Fore.YELLOW}New password: {Fore.WHITE}").strip()
    conf = input(f"{Fore.YELLOW}Confirm new password: {Fore.WHITE}").strip()
    if new != conf:
        print(f"{Fore.RED}passwd: passwords do not match{Fore.WHITE}")
        return
    target_u["password"] = hash_pw(new)
    save_system()
    print(f"{Fore.GREEN}✓{Fore.WHITE} Password changed successfully")


def cmd_adminrun(args: list[str]) -> None:
    if not _require_args(args, "provide a command"):
        return
    if is_admin():
        execute_command(" ".join(args))
        return
    admins = [u for u in users_list if u.get("is_admin")]
    if not admins:
        print(f"{Fore.RED}error: no admin users found{Fore.WHITE}")
        return
    pw = input(f"{Fore.YELLOW}[adminrun] Password: {Fore.WHITE}").strip()
    hashed = hash_pw(pw)
    if any(u["password"] == hashed for u in admins):
        S._adminrun_active = True
        execute_command(" ".join(args))
        S._adminrun_active = False
    else:
        print(f"{Fore.RED}adminrun: incorrect password{Fore.WHITE}")


# ── Command registry ─────────────────────────────────────────────────────────

COMMANDS: dict[str, object] = {
    "help":     cmd_help,
    "list":     cmd_list,
    "cd":       cmd_cd,
    "read":     cmd_read,
    "whereami": cmd_whereami,
    "mkdir":    cmd_mkdir,
    "mkfile":   cmd_mkfile,
    "delete":   cmd_delete,
    "echo":     cmd_echo,
    "whoami":   cmd_whoami,
    "uname":    cmd_uname,
    "clear":    cmd_clear,
    "pyufetch": cmd_pyufetch,
    "pwdit":    cmd_pwdit,
    "run":      cmd_run,
    "pkgmgr":   cmd_pkgmgr,
    "startx":   cmd_startx,
    "poweroff": cmd_poweroff,
    "rmdir":    cmd_rmdir,
    "usercn":   cmd_usercn,
    "hostcn":   cmd_hostcn,
    "userlist": cmd_userlist,
    "useradd":  cmd_useradd,
    "passwd":   cmd_passwd,
    "su":       cmd_su,
    "adminrun": cmd_adminrun,
}


def execute_command(line: str) -> None:
    parts = line.split()
    if not parts:
        return
    cmd_name, *args = parts

    if cmd_name in COMMANDS:
        COMMANDS[cmd_name](args)  # type: ignore[operator]
    elif cmd_name in installed_packages and repo is not None:
        _run_package(cmd_name, args)
    else:
        print(f"penguwarp: {cmd_name}: command not found")


def _run_package(pkg: str, args: list[str]) -> None:
    pkg_file = repo.AVAILABLE_PACKAGES[pkg]["file"]
    pkg_path = os.path.join(SCRIPT_DIR, "packages", pkg_file)
    sys.argv  = [pkg, *args]
    try:
        with open(pkg_path, "r", encoding="utf-8") as f:
            code = f.read()
        exec(compile(code, pkg_path, "exec"), {"__name__": "__main__", "__file__": pkg_path})
    except FileNotFoundError:
        print(f"{Fore.RED}Error: package file not found: {pkg_file}{Fore.WHITE}")
    except Exception as e:
        print(f"{Fore.RED}Error running package '{pkg}': {e}{Fore.WHITE}")
    S.load_system()  # re-sync state after package execution
