# 🐧 PenguWarp OS

> An OS simulator made in Python so Linux newbies can learn how to navigate their system from a terminal — and break stuff without messing up their actual system.

---

## What is this?

PenguWarp OS is an interactive terminal simulator that gives beginners a safe sandbox to get comfortable with the command line. No risk of deleting something important, no cryptic commands — just a clean environment to learn how terminals actually work.

Instead of throwing you into real bash and watching you panic, PenguWarp gives you a simplified shell called **PWShell** with commands that actually make sense:

| PenguWarp  | Real Linux | What it does               |
|------------|------------|----------------------------|
| `read`     | `cat`      | Read a file                |
| `list`     | `ls`       | List directory contents    |
| `mkfile`   | `touch`    | Create a new file          |
| `delete`   | `rm`       | Delete a file              |
| `mkdir`    | `mkdir`    | Create a directory         |
| `rmdir`    | `rmdir`    | Remove an empty directory  |
| `cd`       | `cd`       | Navigate directories       |
| `whereami` | `pwd`      | Show current directory     |
| `echo`     | `echo`     | Print text                 |
| `uname`    | `uname`    | Show system/kernel info    |
| `whoami`   | `whoami`   | Show current user          |
| `clear`    | `clear`    | Clear the terminal         |
| `run`      | `bash`     | Execute a `.pwe` script    |
| `pyufetch` | `neofetch` | Show system info + branding|
| `poweroff` | `shutdown` | Shutdown and save          |

Once you get comfortable with how terminals work, making the jump to real Linux feels way less scary.

---

## Getting Started

**Requirements:** Python 3.10+, `colorama`

```bash
git clone https://github.com/theidioticdev/penguwarpos                   # for stable release
git clone -b testing https://github.com/theidioticdev/penguwarpos        # for testing branch
cd penguwarpos
pip install colorama
pip install curses
python3 kernel.py
```


---

## Multi-User System

PenguWarp has a real permission hierarchy:


***APPLIES TO THE TESTING RELEASE ONLY***
- **root** — exists but is inaccessible. Its password is randomly generated at first boot and never exposed.
- **first user** — automatically becomes the sudoer (admin).
- **any other user** — standard user. Must use `adminrun` to run privileged commands.

### User commands

| Command    | What it does                        |
|------------|-------------------------------------|
| `useradd`  | Add a new user (admin only)         |
| `userlist` | List all users                      |
| `su`       | Switch to another user              |
| `usercn`   | Change your username                |
| `hostcn`   | Change the hostname                 |
| `passwd`   | Change a user's password            |
| `promote`  | Grant admin privileges to a user    |
| `adminrun` | Run a command with admin privileges |

---

## Package Manager — PKGMGR

PenguWarp has its own package manager. Install, remove, search, and list packages straight from PWShell.

```bash
pkgmgr search        # browse available packages
pkgmgr install snake # install a package
pkgmgr remove snake  # remove a package
pkgmgr list          # list installed packages
```

### Available packages

| Package     | Description                                        |
|-------------|----------------------------------------------------|
| `snake`     | Classic snake game (auto-play with A* pathfinding) |
| `cowsay`    | Make a cow say things                              |
| `matrix`    | Matrix rain effect in terminal                     |
| `todo`      | CLI todo list manager                              |
---

## PenguWin Desktop Environment
This stable release comes with a desktop environment built with TkInter named PenguWin
the testing release has the new version of PenguWin which uses Dear PyGUI now

---

## Built-in Editor — pwdit

PenguWarp ships with a built-in line editor:

```bash
pwdit filename.txt
```

for a graphical, windows-like editing experience, use GPWDIT via PenguWin
---

## Other Features

- 🐧 **Boot animation** — animated boot sequence with progress bar and a blinking penguin
- 🐧 **Curses TUI installer** — first-boot setup with a proper terminal UI
- 🐧 **Tab completion** — for both commands and filesystem paths
- 🐧 **Command history** — arrow keys to navigate previous commands
- 🐧 **Scripting** — write `.pwe` scripts and run them with `run`
- 🐧 **Persistent state** — filesystem, users, and installed packages all save to disk

---

## Branches

| Branch    | Description                    |
|-----------|--------------------------------|
| `main`    | Stable releases                |
| `testing` | Latest features, may have bugs |

---

## Why?

Because `cat`, `ls`, `touch`, and `rm` are terrible names for commands and everyone deserves a less terrifying introduction to the terminal.

---

## Dependencies

- `colorama` — terminal colors
- `curses` — TUI installer, dashwarp, tpwdit, dungeon (stdlib on Linux/macOS)

---

## License

Check `LICENSE` in the repo.
