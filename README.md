# 🐧 PenguWarp OS

> An OS simulator made in Python so Linux newbies can learn how to navigate their system from a terminal — and break stuff without messing up their actual system.

---

## What is this?

PenguWarp OS is an interactive terminal simulator that gives beginners a safe sandbox to get comfortable with the command line. No risk of deleting something important, no confusing cryptic commands — just a clean environment to learn how terminals actually work.

Instead of throwing you into real bash and watching you panic, PenguWarp gives you a familiar-but-simplified shell called **PWShell** with commands that actually make sense:

| PenguWarp | Real Linux | What it does |
|-----------|------------|--------------|
| `read`    | `cat`      | Read a file  |
| `list`    | `ls`       | List directory contents |
| `mkfile`  | `touch`    | Create a file |
| `delete`  | `rm`       | Delete a file |
| `help`    | —          | Show all commands |

Once you get comfortable with how terminals work, making the jump to real Linux feels way less scary.

---

## Getting Started

**Requirements:** Python 3.10+, `colorama`

```bash
git clone https://github.com/theidioticdev/penguwarpos
cd penguwarpos
pip install -r requirements.txt
python kernel.py
```

On first boot, you'll be walked through a quick setup to create your hostname and user. After that, you're dropped straight into PWShell.

---

## Features

- 🐧 **PWShell** — a simplified shell with beginner-friendly commands
- 📁 **Virtual filesystem** — navigate dirs, create files, delete stuff, all sandboxed
- 🖥️ **Boot animation** — full boot sequence with progress bar because it looks cool
- 📦 **PWPM** — a package manager to install extras (`pwpm search`)
- 🖱️ **PenguWin** — optional GUI desktop environment (installable via PWPM)
- 🔍 **Tab completion** — because even simulators should have good UX
- `pyufetch` — a neofetch-style system info display

---

## Branches

| Branch | Description |
|--------|-------------|
| `main` | Stable releases |
| `testing` | Latest features, may have bugs |

---

## Why?

Because `cat`, `ls`, `touch`, and `rm` are terrible names for commands and everyone deserves a less terrifying introduction to the terminal.

---

## License

Check `LICENSE` in the repo.
