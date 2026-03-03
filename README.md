# 🐧 PenguWarp OS
*A persistent Unix-inspired virtual OS built in Python*

![Version](https://img.shields.io/badge/version-0.1.7%20%22Lemon%22-yellow?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Python-blue?style=flat-square)
![License](https://img.shields.io/badge/license-GPL--3.0-green?style=flat-square)

> Inspired by GNU/Linux and Unix philosophy

---

## Setup

**Requirements:** Python 3.7+, `colorama`, `tkinter`, `rich`

```bash
git clone https://github.com/TheIdioticDev/penguwarpos
cd penguwarpos
pip install colorama rich
python3 kernel.py
```

**File structure:**
```
PenguWarp/
├── kernel.py  
├── repo.py
├── packages/
│   ├── snake.py
│   ├── cowsay.py
│   ├── matrix.py
│   ├── todo.py
│   ├── tpwdit.py
│   └── dungeon.py

└── penguwarp_system.json
```

---

## PWShell Commands

| Command | Description |
|---------|-------------|
| `list` | List files in current directory |
| `cd <dir>` | Change directory |
| `whereami` | Print current path |
| `mkdir <n>` | Create directory |
| `mkfile <file>` | Create empty file |
| `delete <file>` | Remove a file |
| `rmdir <dir>` | Remove empty directory |
| `read <file>` | Print file contents |
| `echo <text>` | Print text |
| `pwdit <file>` | Open line editor |
| `run <script.pwe>` | Execute a .pwe script |
| `pkgmgr <action>` | Package manager |
| `startx` | Launch PenguWin desktop |
| `pyufetch` | System info |
| `uname` | Kernel version |
| `whoami` | Current user |
| `clear` | Clear screen |
| `poweroff` | Shutdown and save |

---

## Package Manager

```bash
pkgmgr search           # browse available packages
pkgmgr install <pkg>    # install a package
pkgmgr remove <pkg>     # remove a package
pkgmgr list             # show installed packages
```

**Available packages:** `snake` `cowsay` `matrix` `todo` `dungeon`

---

## PenguWin Desktop

```bash
startx
```

Launches a Tkinter-based desktop with draggable windows, a dock, and the following apps: file browser, text editor (GPWDIT), calculator, paint, system info, and clock.

---

## Scripting (.pwe)

```bash
# example.pwe
echo "Hello from PenguWarp!"
mkdir projects
cd projects
mkfile README.md
```

Run with `run example.pwe`. Supports syntax highlighting in GPWDIT.

---

## Version History

| Version | Codename | Highlights |
|---------|----------|------------|
| **v0.1.6** | 🍑 Peach | Dungeon Crawler, GRV theme cleanup, bug fixes (current stable release) |
| **v0.1.5** | 🥭 Mango | Package manager, tab completion, security fixes |
| **v0.1.4** | 🍎 Apple | PenguWin desktop environment |
| **v0.1.3** | 🍌 Banana | Dynamic storage, colored output |
| **v0.1.2** | 🍊 Orange | Script support (.pwe files) |
| **v0.1.1** | 🍓 Strawberry | Persistent filesystem |
| **v0.1.0** | 🍇 Grape | Initial release |

---

## Roadmap

- **v0.2.0 "Dragon Fruit"** — multi-user support, permissions, GUI themes
- **v0.3.0 "Kiwi"** — simulated networking, expanded package repo
- **v1.0.0 "Watermelon"** — stable release, plugin system, advanced scripting

---

*Built by **TheIdioticDev** with Python, Tkinter, Colorama, and Rich*
