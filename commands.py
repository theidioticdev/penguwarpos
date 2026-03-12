"""
commands.py — PWShell built-in commands for PenguWarp OS
"""

import os
import sys
import time
from colorama import Fore

import system as S
from system import (
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
    """Turn a path (relative or absolute) into a full filesystem key."""
    return S.resolve_path(name)


# ── Commands ─────────────────────────────────────────────────────────────────

def cmd_help(args: list[str]) -> None:
    print(f'\n{Fore.YELLOW}PENGUWARP OS v0.1.8 "LEMON" COMMAND REFERENCE')
    print(f"{Fore.WHITE}" + "-" * 60)
    for c, d in COMMAND_DESC.items():
        print(f"{Fore.YELLOW}{c:<12}{Fore.WHITE} : {d}")
    print("-" * 60 + "\n")


def _list_dir(path: str, show_header: bool = False) -> None:
    """Print the contents of a single resolved directory path."""
    entry = S.filesystem.get(path, {})
    if not entry:
        print(f"{Fore.RED}list: {path}: no such directory{Fore.WHITE}")
        return
    if entry.get("type") != "dir":
        print(f"{Fore.RED}list: {path}: not a directory{Fore.WHITE}")
        return
    if show_header:
        print(f"{Fore.YELLOW}{path}:{Fore.WHITE}")
    contents = entry.get("contents", [])
    if not contents:
        print("(directory empty)")
        return
    out = []
    for name in contents:
        full  = f"{path}/{name}" if path != "~" else f"~/{name}"
        color = Fore.YELLOW if S.filesystem.get(full, {}).get("type") == "dir" else Fore.WHITE
        out.append(f"{color}{name}{Fore.WHITE}")
    print("  ".join(out))


def cmd_list(args: list[str]) -> None:
    if not args:
        _list_dir(S.current_dir)
    elif len(args) == 1:
        _list_dir(_resolve(args[0]))
    else:
        # multiple paths: show a header for each like ls
        for i, arg in enumerate(args):
            if i > 0:
                print()
            _list_dir(_resolve(arg), show_header=True)


_prev_dir: str = "~"  # for cd -

def cmd_cd(args: list[str]) -> None:
    global _prev_dir
    target = args[0] if args else "~"

    if target == "-":
        target_path = _prev_dir
    else:
        target_path = _resolve(target)

    if S.filesystem.get(target_path, {}).get("type") == "dir":
        _prev_dir     = S.current_dir
        S.current_dir = target_path
    else:
        print(f"cd: no such directory: {target}")


def cmd_read(args: list[str]) -> None:
    if not _require_args(args, "provide a filename"):
        return
    path = _resolve(args[0])
    entry = S.filesystem.get(path, {})
    if entry.get("type") == "file":
        print(entry["content"])
    else:
        print(f"cat: {args[0]}: file not found")


def cmd_mkdir(args: list[str]) -> None:
    if not _require_args(args, "provide a directory name"):
        return
    path     = _resolve(args[0])
    basename = path.rsplit("/", 1)[-1]
    if path not in S.filesystem:
        S.filesystem[path] = {"type": "dir", "contents": []}
        parent = S.filesystem.get(S.current_dir, {})
        if basename not in parent.get("contents", []):
            parent.setdefault("contents", []).append(basename)
        save_system()


def cmd_mkfile(args: list[str]) -> None:
    if not _require_args(args, "provide a filename"):
        return
    path     = _resolve(args[0])
    basename = path.rsplit("/", 1)[-1]
    if path not in S.filesystem:
        S.filesystem[path] = {"type": "file", "content": ""}
        parent = S.filesystem.get(S.current_dir, {})
        if basename not in parent.get("contents", []):
            parent.setdefault("contents", []).append(basename)
        save_system()


def cmd_delete(args: list[str]) -> None:
    if not _require_args(args, "provide a filename"):
        return
    path     = _resolve(args[0])
    basename = path.rsplit("/", 1)[-1]
    if S.filesystem.get(path, {}).get("type") == "file":
        del S.filesystem[path]
        contents = S.filesystem.get(S.current_dir, {}).get("contents", [])
        if basename in contents:
            contents.remove(basename)
        save_system()
    else:
        print(f"delete: {args[0]}: file not found")


def cmd_rmdir(args: list[str]) -> None:
    if not _require_args(args, "provide a directory name"):
        return
    path     = _resolve(args[0])
    basename = path.rsplit("/", 1)[-1]
    entry    = S.filesystem.get(path, {})
    if entry.get("type") != "dir":
        print(f"rmdir: {args[0]}: no such directory")
        return
    if entry.get("contents"):
        print(f"rmdir: {args[0]}: directory not empty")
        return
    del S.filesystem[path]
    contents = S.filesystem.get(S.current_dir, {}).get("contents", [])
    if basename in contents:
        contents.remove(basename)
    save_system()


def cmd_echo(args: list[str]) -> None:
    print(" ".join(args))


def cmd_whereami(args: list[str]) -> None:
    print(S.current_dir)


def cmd_whoami(args: list[str]) -> None:
    print(S.user)


def cmd_uname(args: list[str]) -> None:
    print("v0.1.8-lemon-dev_x86-64")


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
        f'{Fore.YELLOW}OS: {Fore.WHITE}PenguWarp v0.1.8 "Lemon"',
        f"{Fore.YELLOW}Kernel: {Fore.WHITE}v0.1.8-lemon-dev_x86-64",
        f"{Fore.YELLOW}Uptime: {Fore.WHITE}{uptime}s",
        f"{Fore.YELLOW}Shell: {Fore.WHITE}PWShell",
        f"{Fore.YELLOW}Packages: {Fore.WHITE}{3 + len(S.installed_packages)}",
    ]
    for i in range(max(len(ascii_art), len(info))):
        left  = ascii_art[i] if i < len(ascii_art) else " " * 22
        right = info[i]      if i < len(info)       else ""
        print(f"{left}    {right}")


def cmd_pwdit(args: list[str]) -> None:
    if not _require_args(args, "provide a filename"):
        return
    path     = _resolve(args[0])
    basename = path.rsplit("/", 1)[-1]
    print(f"Editing {args[0]} (Double Enter to save | Ctrl+C to cancel)")
    lines: list[str] = []
    try:
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        S.filesystem[path] = {"type": "file", "content": "\n".join(lines).strip()}
        contents = S.filesystem.get(S.current_dir, {}).get("contents", [])
        if basename not in contents:
            contents.append(basename)
        save_system()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Cancelling editing...")


def cmd_run(args: list[str]) -> None:
    if not _require_args(args, "provide a script name"):
        return
    path = _resolve(args[0])
    if path not in S.filesystem or not args[0].endswith(".pwe"):
        print(f"run: {args[0]}: not a valid .pwe script")
        return
    lines  = S.filesystem[path]["content"].split("\n")
    errors = 0
    print(f"{Fore.YELLOW}Executing {args[0]}...")
    for i, raw in enumerate(lines, 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        cmd_name = stripped.split()[0]
        if cmd_name not in COMMANDS and cmd_name not in S.installed_packages:
            print(f"{Fore.RED}run: {args[0]}: line {i}: unknown command '{cmd_name}'{Fore.WHITE}")
            errors += 1
            continue
        execute_command(stripped)
    status = f"{Fore.RED}finished with {errors} error(s)" if errors else f"{Fore.YELLOW}done"
    print(f"run: {args[0]}: {status}{Fore.WHITE}")


def cmd_pwpm(args: list[str]) -> None:
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
            print(f"  {Fore.YELLOW}pwpm {flag:<16}{Fore.WHITE} - {desc}")
        return

    action = args[0]

    if action == "search":
        print(f"\n{Fore.YELLOW}=== AVAILABLE PACKAGES ==={Fore.WHITE}")
        for name, info in repo.AVAILABLE_PACKAGES.items():
            tag = f" {Fore.GREEN}[INSTALLED]{Fore.WHITE}" if name in S.installed_packages else ""
            print(f"{Fore.YELLOW}{name:<12}{Fore.WHITE} - {info['description']}{tag}")
        print()

    elif action == "list":
        if not S.installed_packages:
            print(f"{Fore.YELLOW}No packages installed. Use 'pwpm search' to browse.{Fore.WHITE}")
            return
        print(f"\n{Fore.YELLOW}=== INSTALLED PACKAGES ==={Fore.WHITE}")
        for pkg in S.installed_packages:
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
        if pkg in S.installed_packages:
            print(f"{Fore.YELLOW}'{pkg}' is already installed{Fore.WHITE}")
            return
        print(f"Downloading {pkg}...", end="", flush=True)
        for _ in range(10):
            time.sleep(0.1)
            print("█", end="", flush=True)
        S.installed_packages.append(pkg)
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
        if pkg not in S.installed_packages:
            print(f"{Fore.YELLOW}'{pkg}' is not installed{Fore.WHITE}")
            return
        S.installed_packages.remove(pkg)
        save_system()
        print(f"{Fore.GREEN}✓{Fore.WHITE} Removed {Fore.YELLOW}{pkg}{Fore.WHITE}")

    else:
        print(f"{Fore.RED}pwpm: unknown action '{action}'{Fore.WHITE}")


def cmd_penguwin(args: list[str]) -> None:
    if "penguwin" not in S.installed_packages:
        print(f"{Fore.RED}penguwin: not installed — run: {Fore.YELLOW}pwpm install penguwin{Fore.WHITE}")
        return
    _run_package("penguwin", args)


def cmd_poweroff(args: list[str]) -> None:
    print(f"{Fore.RED}Shutting down PenguWarp Lemon...")
    save_system()
    time.sleep(1)
    sys.exit(0)


def cmd_usercn(args: list[str]) -> None:
    if not _require_args(args, "provide a new username"):
        return
    new_name = args[0]
    # Sync the users_list entry so username doesn't go out of sync on reboot
    for u in S.users_list:
        if u["username"] == S.user:
            u["username"] = new_name
            break
    S.user = new_name
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
    for u in S.users_list:
        admin_tag = f" {Fore.CYAN}[admin]{Fore.WHITE}" if u.get("is_admin") else ""
        print(f"  {Fore.YELLOW}{u['username']}{Fore.WHITE}{admin_tag}")


def cmd_useradd(args: list[str]) -> None:
    if not _require_args(args, "provide a username"):
        return
    name = args[0]
    if name == "root":
        print(f"{Fore.RED}error: cannot create user 'root'{Fore.WHITE}")
        return
    if any(u["username"] == name for u in S.users_list):
        print(f"{Fore.RED}error: user '{name}' already exists{Fore.WHITE}")
        return
    pw   = input(f"{Fore.YELLOW}Set password for {name}: {Fore.WHITE}").strip()
    home = S.user_home(name)
    S.users_list.append({"username": name, "password": hash_pw(pw), "is_admin": False, "home": home})
    # create home directory under ~/usr/
    if "~/usr" in S.filesystem and name not in S.filesystem["~/usr"]["contents"]:
        S.filesystem["~/usr"]["contents"].append(name)
    S.filesystem[home] = {"type": "dir", "contents": []}
    save_system()
    print(f"{Fore.GREEN}✓{Fore.WHITE} User '{Fore.YELLOW}{name}{Fore.WHITE}' created  (home: {home})")


def cmd_su(args: list[str]) -> None:
    if not _require_args(args, "provide a username"):
        return
    target   = args[0]
    target_u = next((u for u in S.users_list if u["username"] == target), None)
    if not target_u:
        print(f"{Fore.RED}su: user '{target}' not found{Fore.WHITE}")
        return
    pw = input(f"{Fore.YELLOW}Password for {target}: {Fore.WHITE}").strip()
    if hash_pw(pw) == target_u["password"]:
        S.user        = target
        S.current_dir = S.user_home(target)
        save_system()
        print(f"{Fore.GREEN}✓{Fore.WHITE} Switched to {Fore.YELLOW}{target}{Fore.WHITE}  (home: {S.current_dir})")
    else:
        print(f"{Fore.RED}su: incorrect password{Fore.WHITE}")


def cmd_passwd(args: list[str]) -> None:
    target_name = args[0] if args else S.user
    target_u = next((u for u in S.users_list if u["username"] == target_name), None)
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


def cmd_promote(args: list[str]) -> None:
    if not _require_args(args, "provide a username"):
        return
    if not is_admin():
        print(f"{Fore.RED}promote: permission denied — must be admin{Fore.WHITE}")
        return
    name     = args[0]
    target_u = next((u for u in S.users_list if u["username"] == name), None)
    if not target_u:
        print(f"{Fore.RED}promote: user '{name}' not found{Fore.WHITE}")
        return
    if target_u.get("is_admin"):
        print(f"{Fore.YELLOW}promote: '{name}' is already an admin{Fore.WHITE}")
        return
    target_u["is_admin"] = True
    save_system()
    print(f"{Fore.GREEN}✓{Fore.WHITE} '{Fore.YELLOW}{name}{Fore.WHITE}' promoted to admin")


def cmd_adminrun(args: list[str]) -> None:
    if not _require_args(args, "provide a command"):
        return
    # admins run directly — no password needed
    if is_admin():
        S._adminrun_active = True
        execute_command(" ".join(args))
        S._adminrun_active = False
        return
    # non-admins must authenticate as any admin user
    admins = [u for u in S.users_list if u.get("is_admin")]
    if not admins:
        print(f"{Fore.RED}adminrun: no admin users exist on this system{Fore.WHITE}")
        return
    admin_names = ", ".join(u["username"] for u in admins)
    admin_name  = input(f"{Fore.YELLOW}[adminrun] Admin username ({admin_names}): {Fore.WHITE}").strip()
    admin_u     = next((u for u in admins if u["username"] == admin_name), None)
    if not admin_u:
        print(f"{Fore.RED}adminrun: '{admin_name}' is not an admin{Fore.WHITE}")
        return
    pw = input(f"{Fore.YELLOW}[adminrun] Password for {admin_name}: {Fore.WHITE}").strip()
    if hash_pw(pw) != admin_u["password"]:
        print(f"{Fore.RED}adminrun: incorrect password{Fore.WHITE}")
        return
    S._adminrun_active = True
    execute_command(" ".join(args))
    S._adminrun_active = False


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
    "pwpm":     cmd_pwpm,
    "poweroff": cmd_poweroff,
    "rmdir":    cmd_rmdir,
    "usercn":   cmd_usercn,
    "hostcn":   cmd_hostcn,
    "userlist": cmd_userlist,
    "useradd":  cmd_useradd,
    "passwd":   cmd_passwd,
    "su":       cmd_su,
    "adminrun": cmd_adminrun,
    "promote":  cmd_promote,
}


def execute_command(line: str) -> None:
    parts = line.split()
    if not parts:
        return
    cmd_name, *args = parts

    if cmd_name in COMMANDS:
        COMMANDS[cmd_name](args)  # type: ignore[operator]
    elif cmd_name == "penguwin":
        cmd_penguwin(args)
    elif cmd_name in S.installed_packages and repo is not None:
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
    # Re-sync persistent state (filesystem, packages) but preserve the
    # live session values that load_system() would otherwise stomp on.
    saved_dir  = S.current_dir
    saved_user = S.user
    S.load_system()
    S.current_dir = saved_dir
    S.user        = saved_user
