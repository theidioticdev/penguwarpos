# 🐧 PenguWarp OS
*A persistent Unix-inspired virtual OS built in Python*

![Version](https://img.shields.io/badge/version-0.1.8%20%22Lemon%22-yellow?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Python-blue?style=flat-square)
![License](https://img.shields.io/badge/license-GPL--3.0-green?style=flat-square)

> Inspired by GNU/Linux and Unix philosophy

---

## Setup

**Requirements:** Python 3.7+, `colorama`, `dear pygui`, `rich`, `curses`

```bash
git clone -b testing https://github.com/theidioticdev/penguwarpos
cd penguwarpos
pip install colorama rich curses
python3 kernel.py
```

**File structure:**
```
├── commands.py
├── gui.py
├── kernel.py
├── LICENSE
├── packages
│   ├── cowsay.py
│   ├── dashwarp.py
│   ├── dungeon.py
│   ├── matrix.py
│   ├── snake.py
│   ├── todo.py
│   └── tpwdit.py
├── README.md
├── repo.py
├── setup.py
└── system.py
```

---

## PWShell Commands

| Command | Description |
|---------|-------------|
| `help` | Display command reference |
| `list` | List files and directories |
| `cd <dir>` | Change directory |
| `whereami` | Print current path |
| `mkdir <name>` | Create directory |
| `mkfile <file>` | Create empty file |
| `delete <file>` | Remove a file |
| `rmdir <dir>` | Remove empty directory |
| `read <file>` | Print file contents |
| `echo <text>` | Print text |
| `run <script.pwe>` | Execute a .pwe script |
| `pwdit <file>` | Open line editor |
| `pwpm <action>` | Package manager |
| `penguwin` | Launch PenguWin desktop |
| `pyufetch` | System info |
| `uname` | Kernel version |
| `whoami` | Current user |
| `clear` | Clear screen |
| `poweroff` | Shutdown and save |
| `usercn <name>` | Change username |
| `hostcn <name>` | Change hostname |
| `su <user>` | Switch user |
| `userlist` | List all users |
| `useradd <user>` | Add new user |
| `passwd <user>` | Change password |
| `adminrun <cmd>` | Run command as admin |
| `promote <user>` | Grant admin privileges |

## Package Manager

```bash
pwpm search           # browse available packages
pwpm install <pkg>    # install a package
pwpm remove <pkg>     # remove a package
pwpm list             # show installed packages
```

**Available packages:** `snake` `cowsay` `matrix` `todo` `dungeon` `tpwdit` `dashwarp`

---

## PenguWin Desktop

```bash
penguwin
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
