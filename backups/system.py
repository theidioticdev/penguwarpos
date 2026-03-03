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
    "startx":   "Launch the PenguWin GUI environment",
    "pkgmgr":   "Manage packages (install/remove/list/search)",
    "poweroff": "Shutdown the system and save all changes",
    "rmdir":    "Remove an empty directory",
    "usercn":   "Changes the username",
    "hostcn":   "Changes the hostname",
    "su":       "Switches users",
    "userlist": "Lists users",
    "useradd":  "Add a new user",
    "passwd":   "Change a user's password",
    "adminrun": "Run a command as admin",
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def fs_path(name: str) -> str:
    """Resolve a filename relative to current_dir into a filesystem key."""
    if name.startswith("~") or "/" not in name and current_dir == "~":
        return f"~/{name}" if not name.startswith("~") else name
    return f"{current_dir}/{name}"


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
    """Forward-migrate old save files (e.g. add missing password fields)."""
    for u in data.get("users", []):
        if "password" not in u:
            u["password"] = hash_pw("admin")
            print(
                f"{Fore.YELLOW}migrate: user '{u['username']}' had no password "
                f"— set to 'admin'. Change it with passwd.{Fore.WHITE}"
            )
    return data


def load_system() -> bool:
    """Load state from disk. Returns True if this is a first boot."""
    global user, hostname, filesystem, installed_packages, users_list
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
