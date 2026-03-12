"""
system.py — PenguWarp OS state, persistence, and constants
"""

import os
import json
import hashlib
import time
from colorama import Fore

# ── Runtime state ────────────────────────────────────────────────────────────
start_time: float = time.time()

user:               str  = "liveuser"
hostname:           str  = "livesys"
current_dir:        str  = "~"
filesystem:         dict = {}
installed_packages: list = []
users_list:         list = []
_adminrun_active:   bool = False

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
SYSTEM_FILE = os.path.join(SCRIPT_DIR, "penguwarp_system.json")

# ── Gruvbox palette (RGBA tuples for DearPyGui) ──────────────────────────────
GRV_BG         = (40,  40,  40,  255)
GRV_BG1        = (60,  56,  54,  255)
GRV_BG2        = (80,  73,  69,  255)
GRV_BG_HARD    = (29,  32,  33,  255)
GRV_FG         = (235, 219, 178, 255)
GRV_YELLOW     = (250, 189, 47,  255)
GRV_YELLOW_DIM = (215, 153, 33,  255)
GRV_ORANGE     = (254, 128, 25,  255)
GRV_ORANGE_DIM = (214, 93,  14,  255)
GRV_RED        = (251, 73,  52,  255)
GRV_GREEN      = (184, 187, 38,  255)
GRV_AQUA       = (142, 192, 124, 255)
GRV_GRAY       = (146, 131, 116, 255)

# ── Command descriptions (used by help + tab completion) ─────────────────────
COMMAND_DESC: dict[str, str] = {
    "help":     "Display this comprehensive command reference",
    "list":     "List files and directories in the current path",
    "read":     "Read and display the contents of a file",
    "cd":       "Navigate between directories",
    "whereami": "Show the current working directory path",
    "mkdir":    "Create a new directory",
    "mkfile":   "Create a new empty file",
    "delete":   "Remove a file",
    "echo":     "Display a line of text",
    "run":      "Execute a .pwe script file",
    "uname":    "Display kernel and system version",
    "whoami":   "Show current active user identity",
    "pwdit":    "Open the PenguWarp line editor for files",
    "pyufetch": "Show system hardware and OS branding",
    "clear":    "Wipe the terminal screen",
    "penguwin": "Launch PenguWin DE (install via: pwpm install penguwin)",
    "pwpm":     "Manage packages (install/remove/list/search)",
    "poweroff": "Shutdown the system and save all changes",
    "rmdir":    "Remove an empty directory",
    "usercn":   "Changes the username",
    "hostcn":   "Changes the hostname",
    "su":       "Switches users",
    "userlist": "Lists users",
    "useradd":  "Add a new user",
    "passwd":   "Change a user's password",
    "adminrun": "Run a command as admin",
    "promote":  "Grant admin privileges to a user",
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def resolve_path(path: str) -> str:
    """
    Resolve a path string Linux-style into an absolute filesystem key.

    Rules:
      - '~' or '~/' alone → '~'
      - '~/foo/bar'        → absolute from root
      - 'foo/bar'          → relative to current_dir
      - '..'               → parent dir  (stops at '~')
      - '.'                → current dir
    The returned key always starts with '~' and has no trailing slash,
    and no double-slashes.  Example: '~/Documents/notes.txt'
    """
    if not path or path == ".":
        return current_dir

    # Absolute path: starts with ~ → start from root
    if path.startswith("~"):
        base = "~"
        rest = path[1:].lstrip("/")  # strip leading ~/ or ~/
    else:
        # Relative: start from current dir
        base = current_dir
        rest = path

    # Split into segments and resolve . / ..
    # Convert base to segment list  e.g. '~/a/b' → ['~', 'a', 'b']
    parts = base.split("/") if base != "~" else ["~"]
    for seg in rest.split("/"):
        if seg == "" or seg == ".":
            continue
        elif seg == "..":
            if len(parts) > 1:          # can go up
                parts.pop()
            # else: already at ~ root, stay put
        else:
            parts.append(seg)

    if not parts:
        return "~"
    if parts[0] != "~":
        parts.insert(0, "~")
    return "/".join(parts)


def fs_path(name: str) -> str:
    """Backwards-compat shim — use resolve_path for new code."""
    return resolve_path(name)


def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_dynamic_ram() -> float:
    import sys
    base = 1.2
    fs_size = sys.getsizeof(json.dumps(filesystem)) / (1024 * 1024)
    return round(base + fs_size, 2)


def current_user_data() -> dict | None:
    return next((u for u in users_list if u["username"] == user), None)


def is_admin() -> bool:
    u = current_user_data()
    return bool(u and u.get("is_admin"))


# ── Persistence ──────────────────────────────────────────────────────────────

def migrate_system(data: dict) -> dict:
    """Forward-migrate old save files."""
    for u in data.get("users", []):
        if "password" not in u:
            u["password"] = hash_pw("admin")
            print(
                f"{Fore.YELLOW}migrate: user '{u['username']}' had no password "
                f"— set to 'admin'. Change it with passwd.{Fore.WHITE}"
            )
        # add home field if missing (pre-new-layout saves)
        if "home" not in u:
            u["home"] = "~" if u["username"] == "root" else f"~/usr/{u['username']}"
    return data


def user_home(username: str = "") -> str:
    """Return the home directory path for a given user (defaults to current)."""
    name = username or user
    if name == "root":
        return "~"
    return f"~/usr/{name}"


def load_system() -> bool:
    """Load state from disk. Returns True if this is a first boot."""
    global user, hostname, current_dir, filesystem, installed_packages, users_list
    if not os.path.exists(SYSTEM_FILE):
        return True
    try:
        with open(SYSTEM_FILE, "r", encoding="utf-8") as f:
            data = migrate_system(json.load(f))
        user               = data["system"]["username"]
        hostname           = data["system"]["hostname"]
        filesystem         = data["filesystem"]
        installed_packages = data.get("installed_packages", [])
        users_list         = data.get("users", [])
        # restore current_dir to user's home on login
        current_dir        = user_home(user)
        return data["system"]["first_boot"]
    except (json.JSONDecodeError, KeyError, OSError):
        return True


def save_system() -> None:
    data = {
        "users":              users_list,
        "system":             {"username": user, "hostname": hostname, "first_boot": False},
        "filesystem":         filesystem,
        "installed_packages": installed_packages,
    }
    with open(SYSTEM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
