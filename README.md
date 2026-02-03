# 🐧 PenguWarp OS
### *A Persistent Unix-Inspired Virtual Operating System*

![Version](https://img.shields.io/badge/version-0.1.5%20%22Mango%22-orange?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Python-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

> **Developed by Mostafa**  
> *Inspired by GNU/Linux and Unix*

---

## 📖 Table of Contents
- [Introduction](#-introduction)
- [Features](#-features)
- [System Specifications](#-system-specifications)
- [Installation](#-installation)
- [Boot Process](#-boot-process)
- [PWShell Commands](#-pwshell-commands)
- [Package Management](#-package-management)
- [PenguWin Desktop](#-penguwin-desktop)
- [Scripting (.pwe)](#-scripting-pwe)
- [Shortcuts & Tips](#-shortcuts--tips)
- [Version History](#-version-history)
- [Roadmap](#-roadmap)

---

## 🌟 Introduction

**PenguWarp** is a persistent, Unix-inspired operating system simulation built entirely in Python. It features a robust command-line interface (**PWShell**), a custom graphical desktop environment (**PenguWin**), and a package management system — all wrapped in a lightweight virtual filesystem.

**Key Highlights:**
- 🖥️ Full terminal emulation with tab completion
- 🎨 Custom GUI desktop environment
- 📦 Built-in package manager
- 💾 Persistent JSON-based filesystem
- 🐧 Unix-like command structure
- 🎯 Scripting support via `.pwe` files

---

## ✨ Features

### **PWShell (Terminal)**
- Tab auto-completion for commands, files, and packages
- Unix-like filesystem navigation (`cd`, `ls`, `pwd`)
- File operations (`touch`, `mkdir`, `rm`, `cat`)
- Text editing with `pwdit`
- Script execution with `.pwe` files
- System information display (`pyufetch`, `uname`)

### **PenguWin (Desktop Environment)**
- Draggable windows with title bars
- Full GUI application suite
- NeXTSTEP/WindowMaker-inspired aesthetics
- Dock-based application launcher
- Desktop icons

### **Package Management**
- Install/remove packages dynamically
- Persistent package tracking
- Pre-built packages included (snake, cowsay, matrix, todo)
- Easy package creation via Python modules

---

## 🖥️ System Specifications

| Component | Specification |
|-----------|---------------|
| **CPU** | Horizon V @ 120 Hz |
| **GPU** | ASG 256g |
| **RAM** | 128 MB (dynamic usage tracking) |
| **Storage** | Crudal HDD V2 (512 MiB max) |
| **Kernel** | pengu-v0.1.5-generic_x86-64 |
| **Shell** | PWShell v0.1.5 |
| **Desktop** | PenguWin v0.1.5 |

---

## 📥 Installation

### **Requirements:**
- Python 3.7+
- `colorama` library
- `tkinter` (usually included with Python)

### **Setup:**
```bash
# Clone or download the project
cd PenguWarp/

# Install dependencies
pip install colorama

# Run the OS
python kernel.py
```

### **File Structure:**
```
PenguWarp/
├── kernel.py                  # Main OS kernel
├── repo.py                    # Package repository
├── packages/                  # Package directory
│   ├── snake.py
│   ├── cowsay.py
│   ├── matrix.py
│   └── todo.py
└── penguwarp_system.json      # Persistent storage (auto-generated)
```

---

## 🚀 Boot Process

**First Boot:**
1. Launch `kernel.py`
2. Enter your desired **Username** and **Hostname**
3. The system initializes the virtual filesystem
4. All settings are saved to `penguwarp_system.json`

**Subsequent Boots:**
- Your filesystem and installed packages persist automatically
- No re-configuration needed

**Boot Sequence:**
```
PenguWarp Kernel v0.1.5_generic-x86_64 initializing...
  [  OK  ] Detecting Horizon V CPU...
  [  OK  ] Mounting Crudal HDD V2...
  [  OK  ] Initializing Memory Manager (128MB)...
  [  OK  ] Loading PWShell...

   ___
  <   o>  PenguWarp OS
  ( | )   v0.1.5
  /___\ 
```

---

## 💻 PWShell Commands

### **File Management**
| Command | Description |
|---------|-------------|
| `ls` | List files and directories in current path |
| `cd <dir>` | Navigate to directory |
| `pwd` | Show current working directory |
| `mkdir <name>` | Create a new directory |
| `touch <file>` | Create a new empty file |
| `rm <file>` | Remove a file |
| `cat <file>` | Display file contents |

### **Text Editing**
| Command | Description |
|---------|-------------|
| `pwdit <file>` | Open PenguWarp line editor (double Enter to save) |
| `echo <text>` | Display a line of text |

### **System Commands**
| Command | Description |
|---------|-------------|
| `help` | Display comprehensive command reference |
| `uname` | Display kernel and system version |
| `whoami` | Show current active user |
| `pyufetch` | Show system hardware and OS branding |
| `clear` | Clear the terminal screen |
| `poweroff` | Shutdown and save all changes |

### **Advanced Features**
| Command | Description |
|---------|-------------|
| `run <script.pwe>` | Execute a .pwe script file |
| `startx` | Launch the PenguWin GUI desktop |
| `pkgmgr <action>` | Manage packages (see below) |

---

## 📦 Package Management

PenguWarp features a built-in package manager for extending functionality.

### **Commands:**
```bash
pkgmgr search           # Show all available packages
pkgmgr list             # Show installed packages
pkgmgr install <pkg>    # Install a package
pkgmgr remove <pkg>     # Remove a package
```

### **Pre-installed Packages:**
| Package | Description |
|---------|-------------|
| `snake` | Classic snake game (auto-play demo) |
| `cowsay` | Make a cow say things |
| `matrix` | Cool matrix falling text effect |
| `todo` | Simple todo list manager |

### **Using Packages:**
```bash
# Install a package
pkgmgr install snake

# Run it (with tab completion!)
snake
```

---

## 🎨 PenguWin Desktop

Launch the graphical desktop environment with:
```bash
startx
```

### **Application Suite:**

#### **🌳 Tree** - File Manager
- Browse your virtual filesystem graphically
- Navigate folders with double-click
- View text files
- Go up directories with ".." option

#### **🔢 WarpCalc** - Calculator
- Basic arithmetic operations (+, -, *, /)
- Clean, button-based interface
- Security-hardened (regex-validated input)
- Error handling

#### **🎨 PenguPaint** - Drawing Tool
- Freehand drawing on canvas
- Clear canvas functionality
- Simple and intuitive

#### **📊 SysMonitor** - System Information
- Real-time RAM usage display
- Disk space monitoring
- System specifications
- Health bars and visual feedback

#### **⏰ WarpClock** - System Clock
- Real-time clock display
- Large, readable format
- Updates every second

#### **📝 GPWDIT** - Graphical Text Editor
- File open/save/save-as dialogs
- Line numbers
- Syntax highlighting for `.pwe` files
- Keyboard shortcuts (Ctrl+S, Ctrl+O, Ctrl+N)
- Status bar with line/column tracking

### **Desktop Features:**
- **Dock**: Quick access to all applications
- **Desktop Icons**: Launch apps from the desktop
- **Window Management**: Drag windows by title bar
- **Multi-Window**: Open multiple apps simultaneously

---

## 📜 Scripting (.pwe)

Automate tasks with PenguWarp Scripts (`.pwe` files).

### **Example Script:**
```bash
# setup.pwe
echo "Setting up project environment..."
mkdir projects
cd projects
mkdir src
mkdir docs
touch README.md
echo "Environment ready!"
pyufetch
```

### **Running Scripts:**
```bash
# Create the script
pwdit setup.pwe

# Execute it
run setup.pwe
```

### **Features:**
- Execute multiple commands sequentially
- Automate filesystem operations
- Chain system commands
- Syntax highlighting in GPWDIT

---

## ⚡ Shortcuts & Tips

### **Terminal Shortcuts:**
- **Tab**: Auto-complete commands, files, and packages
- **Ctrl+C**: Cancel current operation
- **Up/Down Arrows**: Command history (via readline)

### **GPWDIT Shortcuts:**
- **Ctrl+S**: Save file
- **Ctrl+O**: Open file dialog
- **Ctrl+N**: New file

### **Tips:**
- Use `pyufetch` to check system resources
- Tab completion works on installed packages too!
- Scripts can call other scripts with `run`
- All GUI windows are draggable by the title bar

---

## 🥭 Version History

PenguWarp follows a **fruit-based codename scheme** for all releases.

| Version | Codename | Release Date | Key Features |
|---------|----------|--------------|--------------|
| **v0.1.5** | 🥭 **Mango** | 2025-02 | Package Manager, Tab Completion, Security Fixes |
| **v0.1.4** | 🍎 **Apple** | 2025-01 | PenguWin Desktop Environment |
| **v0.1.3** | 🍌 **Banana** | 2025-01 | Dynamic Storage, Colored Output |
| **v0.1.2** | 🍊 **Orange** | 2025-01 | Script Support (.pwe files) |
| **v0.1.1** | 🍓 **Strawberry** | 2025-01 | Persistent Filesystem |
| **v0.1.0** | 🍇 **Grape** | 2025-01 | Initial Release |

---

## 🗺️ Roadmap

### **v0.1.6 "Peach"** 🍑 (Planned)
- Bug fixes and performance improvements
- More default packages
- Improved error handling

### **v0.2.0 "Dragon Fruit"** 🐉 (Future)
- Multi-user support
- User permissions system
- Enhanced GUI themes

### **v0.3.0 "Kiwi"** 🥝 (Future)
- Simulated networking features
- Package repository system
- Cloud sync simulation

### **v1.0.0 "Watermelon"** 🍉 (Long-term)
- Stable release
- Complete documentation
- Plugin system
- Advanced scripting engine

---

## 🛠️ Technical Details

### **Built With:**
- **Python 3** - Core language
- **Tkinter** - GUI framework
- **Colorama** - Terminal colors
- **JSON** - Data persistence
- **Readline** - Tab completion

### **Architecture:**
- **Kernel**: Main OS loop and system management
- **Filesystem**: JSON-based virtual filesystem
- **Package System**: Modular Python-based packages
- **GUI**: Tkinter-based window manager

---

## 📄 License

MIT License - Feel free to fork, modify, and use!

---

## 👨‍💻 Developer

**Mostafa**  
*Crafted with Python, Tkinter, and Colorama*

> *"Inspired by GNU/Linux and Unix"*

---

## 🙏 Acknowledgments

- GNU/Linux community for inspiration
- Unix philosophy for design principles
- NeXTSTEP/WindowMaker for GUI aesthetics
- Catppuccin color scheme (Mocha variant)

---

**🐧Enjoy!**
