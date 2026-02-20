import time
import sys
import os
import json
import tkinter as tk
from collections.abc import Callable
from colorama import Fore, init

import readline

try:
    import repo
except ImportError:
    repo = None

init(autoreset=True)


def boot_animation_splash() -> None:
    try:
        from rich.console import Console
        from rich.panel import Panel

        console = Console()

        penguin = """
           ___
          <   o>
          ( | )
          /___\\
        """

        for i in range(6):
            console.clear()
            console.print(
                Panel(
                    f"[yellow]{penguin}[/yellow]\n"
                    f'[bold orange1]PenguWarp OS v0.1.6 "Peach"[/bold orange1]\n'
                    f"[dim]Initializing{'.' * (i + 1)}[/dim]",
                    border_style="yellow",
                    title="[bold]PENGUWARP[/bold]",
                )
            )
            time.sleep(0.5)

        console.clear()
    except ImportError:
        pass


start_time = time.time()

user = "liveuser"
hostname = "livesys"
current_dir = "~"
filesystem: dict = {}
installed_packages: list = []

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEM_FILE = os.path.join(SCRIPT_DIR, "penguwarp_system.json")

GRV_BG = "#282828"
GRV_BG1 = "#3c3836"
GRV_FG = "#ebdbb2"
GRV_YELLOW = "#fabd2f"
GRV_YELLOW_DIM = "#d79921"
GRV_ORANGE = "#fe8019"
GRV_ORANGE_DIM = "#d65d0e"
GRV_RED = "#fb4934"
GRV_GREEN = "#b8bb26"
GRV_AQUA = "#8ec07c"
GRV_GRAY = "#928374"
GRV_BG_HARD = "#1d2021"
WINDOW_CHROME = "#504945"
TITLE_BAR = "#3c3836"
DOCK_BG = "#1d2021"

COMMAND_DESC = {
    "help": "Display this comprehensive command reference",
    "list": "List files and directories in the current path",
    "read": "Read and display the contents of a file",
    "cd": "Navigate between directories",
    "whereami": "Show the current working directory path",
    "mkdir": "Create a new directory",
    "mkfile": "Create a new empty file",
    "delete": "Remove a file",
    "echo": "Display a line of text",
    "run": "Execute a .pwe script file",
    "uname": "Display kernel and system version",
    "whoami": "Show current active user identity",
    "pwdit": "Open the PenguWarp line editor for files",
    "pyufetch": "Show system hardware and OS branding",
    "clear": "Wipe the terminal screen",
    "startx": "Launch the PenguWin GUI environment",
    "pkgmgr": "Manage packages (install/remove/list/search)",
    "poweroff": "Shutdown the system and save all changes",
    "rmdir": "Remove an empty directory"
}


def load_system() -> bool:
    global user, hostname, filesystem, installed_packages
    if os.path.exists(SYSTEM_FILE):
        try:
            with open(SYSTEM_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                user = data["system"]["username"]
                hostname = data["system"]["hostname"]
                filesystem = data["filesystem"]
                installed_packages = data.get("installed_packages", [])
                return data["system"]["first_boot"]
        except (json.JSONDecodeError, KeyError, OSError):
            return True
    return True


def save_system() -> None:
    data = {
        "system": {"username": user, "hostname": hostname, "first_boot": False},
        "filesystem": filesystem,
        "installed_packages": installed_packages,
    }
    with open(SYSTEM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def first_boot_setup() -> None:
    global user, hostname, filesystem
    os.system("cls" if os.name == "nt" else "clear")
    print(f"{Fore.YELLOW}╔════════════════════════════════════════╗")
    print(f'{Fore.YELLOW}║  ~ Welcome to PenguWarp OS "Peach"!  ~ ║')
    print(f"{Fore.YELLOW}╚════════════════════════════════════════╝\n")
    u_in = input(f"{Fore.YELLOW}Choose Username: {Fore.WHITE}").strip()
    h_in = input(f"{Fore.YELLOW}Choose Hostname: {Fore.WHITE}").strip()
    user = u_in if u_in else "user"
    hostname = h_in if h_in else "pengu"
    filesystem.update(
        {
            "~": {
                "type": "dir",
                "contents": [
                    "Documents",
                    "Downloads",
                    "Pictures",
                    "Desktop",
                    "welcome.txt",
                ],
            },
            "~/Documents": {"type": "dir", "contents": []},
            "~/Downloads": {"type": "dir", "contents": []},
            "~/Pictures": {"type": "dir", "contents": []},
            "~/Desktop": {"type": "dir", "contents": []},
            "~/welcome.txt": {
                "type": "file",
                "content": (
                    f'Welcome to PenguWarp OS "Peach", {user}!\n\n'
                    "Explore around, and do not forget to run 'pkgmgr search' daily to find new packages!.\n"
                    "Type 'help' to begin.\n\n"
                    "Built with Python & Tkinter."
                ),
            },
        }
    )
    save_system()
    print(f"\n{Fore.YELLOW}System initialized. Booting...")
    time.sleep(1)


def boot_sequence() -> None:
    print(f"{Fore.YELLOW}PenguWarp Kernel v0.1.6-peach_x86_64 initializing...")
    time.sleep(0.4)
    logs = [
        "Detecting hardware...",
        "Mounting drive /dev/sda...",
        "Initializing Memory Manager ...",
        "Loading PWShell...",
    ]
    for log in logs:
        print(f"  [{Fore.YELLOW}  OK  {Fore.WHITE}] {log}")
        time.sleep(0.2)
    print(
        f'\n{Fore.YELLOW}   ___\n  <   o>  PenguWarp OS\n  ( | )   v0.1.6 "Peach"\n  /___\\ \n'
    )


def get_dynamic_ram() -> float:
    base_usage = 1.2
    fs_size = sys.getsizeof(json.dumps(filesystem)) / (1024 * 1024)
    return round(base_usage + fs_size, 2)


def create_wm_window(
    parent: tk.Misc, title_text: str, width: int, height: int
) -> tuple[tk.Toplevel, tk.Frame]:
    win = tk.Toplevel(parent)
    win.overrideredirect(True)
    win.geometry(f"{width}x{height}+250+150")
    win.configure(bg=WINDOW_CHROME, bd=0)

    title_bar = tk.Frame(win, bg=TITLE_BAR, relief="flat", bd=0)
    title_bar.pack(fill="x", side="top")

    tk.Label(
        title_bar,
        text=f"  {title_text}",
        fg=GRV_YELLOW,
        bg=TITLE_BAR,
        font=("Monospace", 10, "bold"),
    ).pack(side="left", padx=5, pady=4)

    tk.Button(
        title_bar,
        text=" × ",
        command=win.destroy,
        bg=GRV_RED,
        fg=GRV_BG,
        relief="flat",
        bd=0,
        font=("Monospace", 10, "bold"),
        cursor="hand2",
    ).pack(side="right", padx=4, pady=3)

    content = tk.Frame(win, bg=GRV_BG, bd=0)
    content.pack(fill="both", expand=True, padx=2, pady=2)

    def set_offset(event: tk.Event) -> None:
        win._offsetx = event.x  # type: ignore[attr-defined]
        win._offsety = event.y  # type: ignore[attr-defined]

    def move_window(event: tk.Event) -> None:
        win.geometry(
            f"+{event.x_root - win._offsetx}+{event.y_root - win._offsety}"  # type: ignore[attr-defined]
        )

    title_bar.bind("<Button-1>", set_offset)
    title_bar.bind("<B1-Motion>", move_window)
    return win, content


def gui_sysinfo(parent: tk.Misc) -> None:
    win, container = create_wm_window(parent, "System Info", 600, 600)

    tk.Label(
        container, text="🐧", font=("Monospace", 40), bg=GRV_BG, fg=GRV_ORANGE
    ).pack(pady=10)

    info_text = (
        f'OS: PenguWarp v0.1.6 "Peach"\n'
        f"Kernel: pwos-peach-v0.1.6-x86_64\n"
        f"User: {user}\n"
        f"RAM: {get_dynamic_ram()}MB / 128MB"
    )
    tk.Label(
        container,
        text=info_text,
        font=("Monospace", 10),
        bg=GRV_BG,
        fg=GRV_FG,
        justify="left",
    ).pack()

    health_frame = tk.Frame(container, bg=GRV_BG1, height=20, width=200)
    health_frame.pack(pady=10)
    tk.Frame(health_frame, bg=GRV_GREEN, height=20, width=180).place(x=0, y=0)

    storage_size = os.path.getsize(SYSTEM_FILE) if os.path.exists(SYSTEM_FILE) else 0
    storage_kb = round(storage_size / 1024, 2)
    max_storage_kb = 512
    storage_percent = min((storage_kb / max_storage_kb) * 200, 200)

    tk.Label(
        container,
        text=f"DISK: {storage_kb}KB / {max_storage_kb}KB",
        font=("Monospace", 10),
        bg=GRV_BG,
        fg=GRV_FG,
    ).pack(pady=(10, 0))

    storage_bg = tk.Frame(container, bg=GRV_BG1, height=15, width=200)
    storage_bg.pack(pady=5)
    tk.Frame(storage_bg, bg=GRV_ORANGE, height=15, width=int(storage_percent)).place(
        x=0, y=0
    )


def gui_clock(parent: tk.Misc) -> None:
    win, container = create_wm_window(parent, "System Clock", 300, 120)
    lbl = tk.Label(
        container, font=("Monospace", 30, "bold"), fg=GRV_YELLOW, bg=GRV_BG
    )
    lbl.pack(expand=True)

    def update() -> None:
        lbl.config(text=time.strftime("%H:%M:%S"))
        lbl.after(1000, update)

    update()


def _safe_eval(expression: str) -> str:
    """Safely evaluate a basic arithmetic expression without using eval()."""
    import ast
    import operator as op

    allowed_ops: dict = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.USub: op.neg,
    }

    def _eval(node: ast.expr) -> float:
        match node:
            case ast.Constant(value=v) if isinstance(v, int | float):
                return float(v)
            case ast.BinOp(left=left, op=oper, right=right):
                op_type = type(oper)
                if op_type not in allowed_ops:
                    raise ValueError(f"Unsupported operator: {op_type}")
                return allowed_ops[op_type](_eval(left), _eval(right))
            case ast.UnaryOp(op=oper, operand=operand):
                op_type = type(oper)
                if op_type not in allowed_ops:
                    raise ValueError(f"Unsupported operator: {op_type}")
                return allowed_ops[op_type](_eval(operand))
            case _:
                raise ValueError(f"Unsupported expression: {type(node)}")

    tree = ast.parse(expression, mode="eval")
    result = _eval(tree.body)
    return str(int(result)) if result == int(result) else str(result)


def gui_calculator(parent: tk.Misc) -> None:
    win, container = create_wm_window(parent, "Calculator", 240, 320)
    expr = tk.StringVar()
    tk.Entry(
        container,
        textvariable=expr,
        font=("Monospace", 16),
        bg=GRV_BG1,
        fg=GRV_YELLOW,
        justify="right",
        bd=0,
        insertbackground=GRV_ORANGE,
        relief="flat",
    ).pack(fill="x", padx=5, pady=5)

    btn_frame = tk.Frame(container, bg=GRV_BG)
    btn_frame.pack(fill="both", expand=True)
    btns = [
        "7", "8", "9", "/",
        "4", "5", "6", "*",
        "1", "2", "3", "-",
        "C", "0", "=", "+",
    ]

    def click(b: str) -> None:
        if b == "=":
            try:
                expr.set(_safe_eval(expr.get()))
            except Exception:
                expr.set("Error")
        elif b == "C":
            expr.set("")
        else:
            expr.set(expr.get() + b)

    for i, b in enumerate(btns):
        is_op = b in "/*-+="
        is_clear = b == "C"
        bg = GRV_ORANGE_DIM if is_op else (GRV_RED if is_clear else GRV_BG1)
        fg = GRV_BG if is_op or is_clear else GRV_FG
        tk.Button(
            btn_frame,
            text=b,
            command=lambda x=b: click(x),
            bg=bg,
            fg=fg,
            font=("Monospace", 12, "bold"),
            bd=0,
            relief="flat",
            activebackground=GRV_YELLOW,
            activeforeground=GRV_BG,
            cursor="hand2",
        ).grid(row=i // 4, column=i % 4, sticky="nsew", padx=1, pady=1)

    for i in range(4):
        btn_frame.grid_columnconfigure(i, weight=1)
        btn_frame.grid_rowconfigure(i, weight=1)


def gui_paint(parent: tk.Misc) -> None:
    win, container = create_wm_window(parent, "PenguPaint", 400, 450)
    canvas = tk.Canvas(
        container, bg=GRV_FG, cursor="cross", bd=0, highlightthickness=0
    )
    canvas.pack(fill="both", expand=True)

    current_color = [GRV_BG]

    color_bar = tk.Frame(container, bg=GRV_BG, height=30)
    color_bar.pack(fill="x")

    colors = [
        GRV_BG, GRV_RED, GRV_ORANGE, GRV_YELLOW, GRV_GREEN, GRV_AQUA, GRV_FG,
    ]
    for c in colors:
        tk.Button(
            color_bar,
            bg=c,
            width=3,
            relief="flat",
            bd=0,
            command=lambda col=c: current_color.__setitem__(0, col),
            cursor="hand2",
        ).pack(side="left", padx=1, pady=2)

    def paint(e: tk.Event) -> None:
        canvas.create_oval(
            e.x - 3, e.y - 3, e.x + 3, e.y + 3,
            fill=current_color[0], outline=current_color[0],
        )

    canvas.bind("<B1-Motion>", paint)

    tk.Button(
        container,
        text="CLEAR CANVAS",
        command=lambda: canvas.delete("all"),
        bg=GRV_RED,
        fg=GRV_BG,
        font=("Monospace", 8, "bold"),
        relief="flat",
        bd=0,
        cursor="hand2",
    ).pack(fill="x")


def gui_pwdit(parent: tk.Misc, filename: str | None = None) -> None:
    current_file = [filename if filename else "new_file.txt"]
    is_modified = [False]

    win, container = create_wm_window(parent, f"GPWDIT - {current_file[0]}", 700, 500)

    toolbar = tk.Frame(container, bg=GRV_BG1, relief="flat", bd=0)
    toolbar.pack(fill="x")

    editor_frame = tk.Frame(container, bg=GRV_BG)
    editor_frame.pack(fill="both", expand=True)

    line_numbers = tk.Text(
        editor_frame,
        width=4,
        bg=GRV_BG1,
        fg=GRV_GRAY,
        font=("Monospace", 10),
        padx=5,
        pady=10,
        state="disabled",
        borderwidth=0,
        takefocus=0,
    )
    line_numbers.pack(side="left", fill="y")

    text_area = tk.Text(
        editor_frame,
        bg=GRV_BG,
        fg=GRV_FG,
        insertbackground=GRV_ORANGE,
        font=("Monospace", 10),
        padx=10,
        pady=10,
        borderwidth=0,
        undo=True,
        maxundo=-1,
        wrap="word",
        selectbackground=GRV_BG1,
        selectforeground=GRV_YELLOW,
    )
    text_area.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(
        editor_frame, command=text_area.yview, bg=GRV_BG1, troughcolor=GRV_BG
    )
    scrollbar.pack(side="right", fill="y")
    text_area.config(yscrollcommand=scrollbar.set)

    status_bar = tk.Frame(container, bg=GRV_BG_HARD, height=25, relief="flat", bd=0)
    status_bar.pack(fill="x", side="bottom")

    status_left = tk.Label(
        status_bar,
        text="Line: 1, Col: 1",
        bg=GRV_BG_HARD,
        fg=GRV_GRAY,
        font=("Monospace", 9),
        anchor="w",
    )
    status_left.pack(side="left", padx=10)

    status_right = tk.Label(
        status_bar,
        text="",
        bg=GRV_BG_HARD,
        fg=GRV_GRAY,
        font=("Monospace", 9),
        anchor="e",
    )
    status_right.pack(side="right", padx=10)

    text_area.tag_config("command", foreground=GRV_YELLOW)
    text_area.tag_config("string", foreground=GRV_GREEN)
    text_area.tag_config("comment", foreground=GRV_GRAY)

    PWE_COMMANDS = [
        "help", "list", "read", "cd", "whereami", "mkdir", "mkfile", "delete",
        "rmdir", "echo", "run", "uname", "whoami", "pwdit", "pyufetch",
        "clear", "startx", "poweroff", "about", "rmdir",
    ]

    def update_line_numbers(event: tk.Event | None = None) -> None:
        line_numbers.config(state="normal")
        line_numbers.delete("1.0", "end")
        line_count = int(text_area.index("end-1c").split(".")[0])
        line_numbers.insert("1.0", "\n".join(str(i) for i in range(1, line_count + 1)))
        line_numbers.config(state="disabled")

    def update_status_bar(event: tk.Event | None = None) -> None:
        row, col = text_area.index("insert").split(".")
        status_left.config(text=f"Line: {row}, Col: {int(col) + 1}")
        char_count = len(text_area.get("1.0", "end-1c"))
        mod_indicator = " [+]" if is_modified[0] else ""
        status_right.config(text=f"{char_count} chars{mod_indicator}")

    def apply_syntax_highlighting(event: tk.Event | None = None) -> None:
        if not current_file[0].endswith(".pwe"):
            return
        for tag in ["command", "string", "comment"]:
            text_area.tag_remove(tag, "1.0", "end")
        content = text_area.get("1.0", "end-1c")
        for line_num, line in enumerate(content.split("\n"), 1):
            words = line.split()
            if words and words[0] in PWE_COMMANDS:
                text_area.tag_add(
                    "command", f"{line_num}.0", f"{line_num}.{len(words[0])}"
                )
            in_quote = False
            quote_start = 0
            for i, char in enumerate(line):
                if char == '"':
                    if not in_quote:
                        in_quote = True
                        quote_start = i
                    else:
                        text_area.tag_add(
                            "string", f"{line_num}.{quote_start}", f"{line_num}.{i + 1}"
                        )
                        in_quote = False
            if line.strip().startswith("#"):
                text_area.tag_add("comment", f"{line_num}.0", f"{line_num}.end")

    def on_text_change(event: tk.Event | None = None) -> None:
        is_modified[0] = True
        update_line_numbers()
        update_status_bar()
        text_area.after(300, apply_syntax_highlighting)

    def load_file(filepath: str) -> None:
        if filepath in filesystem and filesystem[filepath]["type"] == "file":
            text_area.delete("1.0", "end")
            text_area.insert("1.0", filesystem[filepath]["content"])
            is_modified[0] = False
            update_line_numbers()
            update_status_bar()
            apply_syntax_highlighting()

    def save_file() -> None:
        content = text_area.get("1.0", "end-1c")
        path = (
            f"{current_dir}/{current_file[0]}"
            if current_dir != "~"
            else f"~/{current_file[0]}"
        )
        filesystem[path] = {"type": "file", "content": content}
        if current_file[0] not in filesystem[current_dir]["contents"]:
            filesystem[current_dir]["contents"].append(current_file[0])
        save_system()
        is_modified[0] = False
        save_btn.config(bg=GRV_GREEN, fg=GRV_BG, text="✓ SAVED!")
        update_status_bar()
        win.after(
            1000,
            lambda: save_btn.config(bg=GRV_ORANGE_DIM, fg=GRV_FG, text="💾 SAVE"),
        )

    def open_file_dialog() -> None:
        picker_win = tk.Toplevel(win)
        picker_win.title("Open File")
        picker_win.geometry("450x350")
        picker_win.configure(bg=GRV_BG)
        picker_win.transient(win)

        tk.Label(
            picker_win,
            text="Select a file to open:",
            bg=GRV_BG,
            fg=GRV_YELLOW,
            font=("Monospace", 11, "bold"),
        ).pack(pady=10)

        listbox = tk.Listbox(
            picker_win,
            bg=GRV_BG1,
            fg=GRV_FG,
            font=("Monospace", 10),
            selectbackground=GRV_ORANGE_DIM,
            selectforeground=GRV_BG,
            borderwidth=0,
            highlightthickness=0,
        )
        listbox.pack(fill="both", expand=True, padx=10, pady=10)

        if current_dir in filesystem:
            for item in filesystem[current_dir]["contents"]:
                full_path = (
                    f"{current_dir}/{item}" if current_dir != "~" else f"~/{item}"
                )
                if full_path in filesystem and filesystem[full_path]["type"] == "file":
                    listbox.insert("end", item)

        def on_select() -> None:
            selection = listbox.curselection()
            if selection:
                selected_file = listbox.get(selection[0])
                current_file[0] = selected_file
                win.title(f"GPWDIT - {selected_file}")
                full_path = (
                    f"{current_dir}/{selected_file}"
                    if current_dir != "~"
                    else f"~/{selected_file}"
                )
                load_file(full_path)
                picker_win.destroy()

        btn_frame = tk.Frame(picker_win, bg=GRV_BG)
        btn_frame.pack(pady=10)

        for text, cmd, padx in [
            ("Open", on_select, 20),
            ("Cancel", picker_win.destroy, 15),
        ]:
            bg = GRV_ORANGE_DIM if text == "Open" else GRV_RED
            tk.Button(
                btn_frame,
                text=text,
                command=cmd,
                bg=bg,
                fg=GRV_BG,
                font=("Monospace", 10, "bold"),
                relief="flat",
                bd=0,
                padx=padx,
                pady=5,
                cursor="hand2",
            ).pack(side="left", padx=5)

        listbox.bind("<Double-Button-1>", lambda e: on_select())

    def save_as_dialog() -> None:
        dialog = tk.Toplevel(win)
        dialog.title("Save As")
        dialog.geometry("400x150")
        dialog.configure(bg=GRV_BG)
        dialog.transient(win)

        tk.Label(
            dialog,
            text="Enter filename:",
            bg=GRV_BG,
            fg=GRV_YELLOW,
            font=("Monospace", 10, "bold"),
        ).pack(pady=15)

        filename_entry = tk.Entry(
            dialog,
            bg=GRV_BG1,
            fg=GRV_FG,
            font=("Monospace", 11),
            insertbackground=GRV_ORANGE,
            relief="flat",
            bd=4,
        )
        filename_entry.pack(padx=20, pady=10, fill="x")
        filename_entry.insert(0, current_file[0])
        filename_entry.focus()

        def do_save() -> None:
            new_name = filename_entry.get().strip()
            if new_name:
                current_file[0] = new_name
                win.title(f"GPWDIT - {new_name}")
                save_file()
                dialog.destroy()

        btn_frame = tk.Frame(dialog, bg=GRV_BG)
        btn_frame.pack(pady=10)

        for text, cmd, padx in [
            ("Save", do_save, 20),
            ("Cancel", dialog.destroy, 15),
        ]:
            bg = GRV_ORANGE_DIM if text == "Save" else GRV_RED
            tk.Button(
                btn_frame,
                text=text,
                command=cmd,
                bg=bg,
                fg=GRV_BG,
                font=("Monospace", 10, "bold"),
                relief="flat",
                bd=0,
                padx=padx,
                pady=5,
                cursor="hand2",
            ).pack(side="left", padx=5)

        filename_entry.bind("<Return>", lambda e: do_save())

    def new_file() -> None:
        text_area.delete("1.0", "end")
        current_file[0] = "new_file.txt"
        win.title(f"GPWDIT - {current_file[0]}")
        is_modified[0] = False
        update_line_numbers()
        update_status_bar()

    text_area.bind("<Control-s>", lambda _: (save_file(), "break")[1])
    text_area.bind("<Control-o>", lambda _: (open_file_dialog(), "break")[1])
    text_area.bind("<Control-n>", lambda _: (new_file(), "break")[1])
    text_area.bind("<KeyRelease>", on_text_change)
    text_area.bind(
        "<KeyPress-Return>", lambda _: text_area.after(10, update_line_numbers)
    )

    def on_scroll(first: float, last: float) -> None:
        line_numbers.yview_moveto(first)
        scrollbar.set(first, last)

    text_area.config(yscrollcommand=on_scroll)

    for text, cmd, bg in [
        ("📄 NEW", new_file, GRV_BG1),
        ("📂 OPEN", open_file_dialog, GRV_BG1),
    ]:
        tk.Button(
            toolbar,
            text=text,
            command=cmd,
            bg=bg,
            fg=GRV_FG,
            font=("Monospace", 9),
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
        ).pack(side="left", padx=1, pady=2)

    save_btn = tk.Button(
        toolbar,
        text="💾 SAVE",
        command=save_file,
        bg=GRV_ORANGE_DIM,
        fg=GRV_FG,
        font=("Monospace", 9),
        relief="flat",
        bd=0,
        padx=8,
        pady=4,
        cursor="hand2",
    )
    save_btn.pack(side="left", padx=1, pady=2)

    tk.Button(
        toolbar,
        text="💾 SAVE AS",
        command=save_as_dialog,
        bg=GRV_BG1,
        fg=GRV_FG,
        font=("Monospace", 9),
        relief="flat",
        bd=0,
        padx=8,
        pady=4,
        cursor="hand2",
    ).pack(side="left", padx=1, pady=2)

    tk.Label(
        toolbar,
        text="^S Save  ^O Open  ^N New",
        bg=GRV_BG1,
        fg=GRV_GRAY,
        font=("Monospace", 8),
    ).pack(side="right", padx=10)

    if filename:
        path = f"{current_dir}/{filename}" if current_dir != "~" else f"~/{filename}"
        load_file(path)
    else:
        update_line_numbers()
        update_status_bar()


def gui_text_viewer(parent: tk.Misc, filename: str, text_content: str) -> None:
    win, container = create_wm_window(parent, f"Text Viewer: {filename}", 450, 350)
    txt = tk.Text(
        container,
        bg=GRV_BG,
        fg=GRV_FG,
        font=("Monospace", 10),
        padx=10,
        pady=10,
        borderwidth=0,
    )
    txt.pack(fill="both", expand=True)
    txt.insert("1.0", text_content)
    txt.config(state="disabled")


def gui_file_browser(parent: tk.Misc) -> None:
    win, container = create_wm_window(parent, "File Browser", 550, 400)
    curr_path = ["~"]
    hdr = tk.Frame(container, bg=GRV_BG1)
    hdr.pack(fill="x")
    path_lbl = tk.Label(
        hdr,
        text=f"  {curr_path[0]}",
        fg=GRV_YELLOW,
        bg=GRV_BG1,
        font=("Monospace", 9),
    )
    path_lbl.pack(side="left", padx=5, pady=4)
    lb = tk.Listbox(
        container,
        bg=GRV_BG,
        fg=GRV_FG,
        font=("Monospace", 11),
        borderwidth=0,
        highlightthickness=0,
        selectbackground=GRV_ORANGE_DIM,
        selectforeground=GRV_BG,
    )
    lb.pack(fill="both", expand=True, padx=5, pady=5)

    def refresh() -> None:
        lb.delete(0, tk.END)
        path_lbl.config(text=f"  {curr_path[0]}")
        if curr_path[0] != "~":
            lb.insert(tk.END, " .. [UP ONE LEVEL]")
            lb.itemconfig(tk.END, fg=GRV_ORANGE)
        for item in filesystem.get(curr_path[0], {}).get("contents", []):
            full_p = f"{curr_path[0]}/{item}" if curr_path[0] != "~" else f"~/{item}"
            icon = (
                "📁"
                if full_p in filesystem and filesystem[full_p]["type"] == "dir"
                else "📄"
            )
            lb.insert(tk.END, f" {icon} {item}")
            if icon == "📁":
                lb.itemconfig(tk.END, fg=GRV_YELLOW)

    def on_click(e: tk.Event) -> None:
        sel = lb.curselection()
        if not sel:
            return
        txt = lb.get(sel[0])
        if "[UP ONE LEVEL]" in txt:
            parts = curr_path[0].split("/")
            curr_path[0] = "/".join(parts[:-1]) if len(parts) > 1 else "~"
            refresh()
        else:
            name = txt.replace(" 📁 ", "").replace(" 📄 ", "").strip()
            full_p = f"{curr_path[0]}/{name}" if curr_path[0] != "~" else f"~/{name}"
            if full_p in filesystem:
                if filesystem[full_p]["type"] == "dir":
                    curr_path[0] = full_p
                    refresh()
                else:
                    gui_text_viewer(win, name, filesystem[full_p]["content"])

    lb.bind("<Double-Button-1>", on_click)
    refresh()


def start_gui() -> None:
    root = tk.Tk()
    root.title("PenguWarp Desktop")
    root.geometry("1024x768")
    root.configure(bg=GRV_BG)

    tk.Label(
        root,
        text="PENGUWARP WORKSTATION",
        font=("Monospace", 28, "bold"),
        fg=GRV_YELLOW,
        bg=GRV_BG,
    ).place(relx=0.5, rely=0.4, anchor="center")

    tk.Label(
        root,
        text="v0.1.6",
        font=("Monospace", 12),
        fg=GRV_ORANGE,
        bg=GRV_BG,
    ).place(relx=0.5, rely=0.47, anchor="center")

    dock = tk.Frame(root, bg=DOCK_BG, bd=0, relief="flat", height=50)
    dock.pack(side="bottom", fill="x")
    tk.Frame(root, bg=GRV_ORANGE_DIM, height=2).pack(side="bottom", fill="x")

    dock_buttons = [
        ("📝 GPWDIT", lambda: gui_pwdit(root)),
        ("📊 Gardener", lambda: gui_sysinfo(root)),
        ("📁 Tree", lambda: gui_file_browser(root)),
        ("🔢 WarpCalc", lambda: gui_calculator(root)),
        ("🎨 Pengupaint", lambda: gui_paint(root)),
        ("⏰ ClockWarp", lambda: gui_clock(root)),
    ]

    for text, cmd in dock_buttons:
        tk.Button(
            dock,
            text=text,
            command=cmd,
            bg=DOCK_BG,
            fg=GRV_FG,
            relief="flat",
            bd=0,
            font=("Monospace", 9),
            padx=14,
            pady=8,
            activebackground=GRV_BG1,
            activeforeground=GRV_YELLOW,
            cursor="hand2",
        ).pack(side="left", padx=1)

    tk.Button(
        dock,
        text="🚪 LOGOUT",
        command=root.destroy,
        bg=DOCK_BG,
        fg=GRV_RED,
        relief="flat",
        bd=0,
        font=("Monospace", 9, "bold"),
        padx=14,
        pady=8,
        activebackground=GRV_RED,
        activeforeground=GRV_BG,
        cursor="hand2",
    ).pack(side="right", padx=8)

    def create_icon(name: str, x: int, y: int, command: Callable[[], None]) -> None:
        tk.Button(
            root,
            text=f"🍑\n{name}",
            command=command,
            bg=GRV_BG,
            fg=GRV_FG,
            bd=0,
            relief="flat",
            activebackground=GRV_BG1,
            activeforeground=GRV_YELLOW,
            font=("Monospace", 9, "bold"),
            padx=10,
            pady=5,
            cursor="hand2",
        ).place(x=x, y=y)

    create_icon("FILES", 30, 30, lambda: gui_file_browser(root))
    create_icon("CALC", 30, 120, lambda: gui_calculator(root))
    create_icon("PAINT", 30, 210, lambda: gui_paint(root))

    root.mainloop()

# ----- SHELL COMMANDS -----

def cmd_rmdir(args: list[str]) -> None:
    if not args:
        return
    path = f"{current_dir}/{args[0]}" if current_dir != "~" else f"~/{args[0]}"
    if path in filesystem and filesystem[path]["type"] == "dir":
        if filesystem[path]["contents"]:
            print(f"rmdir: {args[0]}: directory not empty")
            return
        del filesystem[path]
        filesystem[current_dir]["contents"].remove(args[0])
        save_system()
    else:
        print(f"rmdir: {args[0]}: no such directory")

def cmd_help(args: list[str]) -> None:
    print(f'\n{Fore.YELLOW}PENGUWARP OS v0.1.6 "PEACH" COMMAND REFERENCE')
    print(f"{Fore.WHITE}" + "-" * 60)
    for c, d in COMMAND_DESC.items():
        print(f"{Fore.YELLOW}{c:<12}{Fore.WHITE} : {d}")
    print("-" * 60 + "\n")


def cmd_list(args: list[str]) -> None:
    if current_dir in filesystem:
        out = []
        for i in filesystem[current_dir]["contents"]:
            p = f"{current_dir}/{i}" if current_dir != "~" else f"~/{i}"
            out.append(
                f"{Fore.YELLOW}{i}{Fore.WHITE}"
                if p in filesystem and filesystem[p]["type"] == "dir"
                else f"{Fore.WHITE}{i}"
            )
        print("  ".join(out) if out else "(directory empty)")


def cmd_cd(args: list[str]) -> None:
    global current_dir
    target = args[0] if args else "~"
    path = (
        target
        if target.startswith("~")
        else f"{current_dir}/{target}"
        if current_dir != "~"
        else f"~/{target}"
    )
    if path in filesystem and filesystem[path]["type"] == "dir":
        current_dir = path
    else:
        print(f"cd: no such directory: {target}")


def cmd_read(args: list[str]) -> None:
    if not args:
        return
    path = f"{current_dir}/{args[0]}" if current_dir != "~" else f"~/{args[0]}"
    if path in filesystem and filesystem[path]["type"] == "file":
        print(filesystem[path]["content"])
    else:
        print(f"cat: {args[0]}: file not found")


def cmd_mkdir(args: list[str]) -> None:
    if not args:
        return
    path = f"{current_dir}/{args[0]}" if current_dir != "~" else f"~/{args[0]}"
    if path not in filesystem:
        filesystem[path] = {"type": "dir", "contents": []}
        filesystem[current_dir]["contents"].append(args[0])
        save_system()


def cmd_mkfile(args: list[str]) -> None:
    if not args:
        return
    path = f"{current_dir}/{args[0]}" if current_dir != "~" else f"~/{args[0]}"
    if path not in filesystem:
        filesystem[path] = {"type": "file", "content": ""}
        filesystem[current_dir]["contents"].append(args[0])
        save_system()


def cmd_delete(args: list[str]) -> None:
    if not args:
        return
    path = f"{current_dir}/{args[0]}" if current_dir != "~" else f"~/{args[0]}"
    if path in filesystem and filesystem[path]["type"] == "file":
        del filesystem[path]
        filesystem[current_dir]["contents"].remove(args[0])
        save_system()


def cmd_echo(args: list[str]) -> None:
    print(" ".join(args))


def cmd_whereami(args: list[str]) -> None:
    print(current_dir)


def cmd_whoami(args: list[str]) -> None:
    print(user)


def cmd_uname(args: list[str]) -> None:
    print("pengu-v0.1.6-peach_x86-64")


def cmd_clear(args: list[str]) -> None:
    os.system("cls" if os.name == "nt" else "clear")


def cmd_pyufetch(args: list[str]) -> None:
    uptime = int(time.time() - start_time)
    used_ram = get_dynamic_ram()
    ascii_art = [
        f"{Fore.YELLOW} _____  __          __",
        f"{Fore.YELLOW}|  __ \\ \\ \\        / /",
        f"{Fore.YELLOW}| |__) | \\ \\  /\\  / / ",
        f"{Fore.YELLOW}|  ___/   \\ \\/  \\/ /  ",
        f"{Fore.YELLOW}| |        \\  /\\  /   ",
        f"{Fore.YELLOW}|_|         \\/  \\/    ",
    ]
    info = [
        f"{Fore.YELLOW}{user}@{hostname}",
        f"{Fore.WHITE}------------------",
        f'{Fore.YELLOW}OS: {Fore.WHITE}PenguWarp v0.1.6 "Peach"',
        f"{Fore.YELLOW}Kernel: {Fore.WHITE}pengu-v0.1.6-peach_x86-64",
        f"{Fore.YELLOW}Uptime: {Fore.WHITE}{uptime}s",
        f"{Fore.YELLOW}Shell: {Fore.WHITE}PWShell",
        f"{Fore.YELLOW}RAM: {Fore.WHITE}{used_ram}MB / 128.0MB",
    ]
    for i in range(max(len(ascii_art), len(info))):
        left = ascii_art[i] if i < len(ascii_art) else " " * 22
        right = info[i] if i < len(info) else ""
        print(f"{left}    {right}")


def cmd_pwdit(args: list[str]) -> None:
    if not args:
        return
    path = f"{current_dir}/{args[0]}" if current_dir != "~" else f"~/{args[0]}"
    print(f"Editing {args[0]} (Double Enter to save | Ctrl+C to cancel)")
    lines: list[str] = []
    try:
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        filesystem[path] = {"type": "file", "content": "\n".join(lines).strip()}
        if args[0] not in filesystem[current_dir]["contents"]:
            filesystem[current_dir]["contents"].append(args[0])
        save_system()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Cancelling editing...")


def cmd_run(args: list[str]) -> None:
    if not args:
        return
    path = f"{current_dir}/{args[0]}" if current_dir != "~" else f"~/{args[0]}"
    if path in filesystem and args[0].endswith(".pwe"):
        print(f"{Fore.YELLOW}Executing {args[0]}...")
        for script_line in filesystem[path]["content"].split("\n"):
            if script_line.strip():
                execute_command(script_line.strip())
    else:
        print(f"run: {args[0]} is not a valid script")


def cmd_pkgmgr(args: list[str]) -> None:
    if repo is None:
        print(f"{Fore.RED}Error: Package repository not available{Fore.WHITE}")
        print("Please ensure repo.py exists in the same directory")
        return

    if not args:
        print(f"{Fore.YELLOW}=== PENGUWARP PACKAGE MANAGER ==={Fore.WHITE}")
        print("Usage:")
        print(f"  {Fore.YELLOW}pkgmgr search{Fore.WHITE}           - Show all available packages")
        print(f"  {Fore.YELLOW}pkgmgr list{Fore.WHITE}             - Show installed packages")
        print(f"  {Fore.YELLOW}pkgmgr install <pkg>{Fore.WHITE}    - Install a package")
        print(f"  {Fore.YELLOW}pkgmgr remove <pkg>{Fore.WHITE}     - Remove a package")
        return

    action = args[0]

    if action == "search":
        print(f"\n{Fore.YELLOW}=== AVAILABLE PACKAGES ==={Fore.WHITE}")
        for pkg_name, pkg_info in repo.AVAILABLE_PACKAGES.items():
            installed_tag = (
                f"{Fore.GREEN}[INSTALLED]{Fore.WHITE}"
                if pkg_name in installed_packages
                else ""
            )
            print(f"{Fore.YELLOW}{pkg_name:<12}{Fore.WHITE} - {pkg_info['description']} {installed_tag}")
        print()

    elif action == "list":
        if not installed_packages:
            print(f"{Fore.YELLOW}No packages installed yet!{Fore.WHITE}")
            print(f"Use {Fore.YELLOW}pkgmgr search{Fore.WHITE} to see available packages")
        else:
            print(f"\n{Fore.YELLOW}=== INSTALLED PACKAGES ==={Fore.WHITE}")
            for pkg in installed_packages:
                if pkg in repo.AVAILABLE_PACKAGES:
                    info = repo.AVAILABLE_PACKAGES[pkg]
                    print(f"{Fore.YELLOW}{pkg:<12}{Fore.WHITE} - {info['description']}")
            print()

    elif action == "install":
        if len(args) < 2:
            print(f"{Fore.RED}Error: Please specify a package name{Fore.WHITE}")
            return
        pkg_name = args[1]
        if pkg_name not in repo.AVAILABLE_PACKAGES:
            print(f"{Fore.RED}Error: Package '{pkg_name}' not found{Fore.WHITE}")
            return
        if pkg_name in installed_packages:
            print(f"{Fore.YELLOW}Package '{pkg_name}' is already installed{Fore.WHITE}")
            return
        installed_packages.append(pkg_name)
        save_system()
        pkg_info = repo.AVAILABLE_PACKAGES[pkg_name]
        print(f"{Fore.GREEN}✓{Fore.WHITE} Successfully installed {Fore.YELLOW}{pkg_info['name']}{Fore.WHITE}")
        print(f"  You can now run it by typing: {Fore.YELLOW}{pkg_name}{Fore.WHITE}")

    elif action == "remove":
        if len(args) < 2:
            print(f"{Fore.RED}Error: Please specify a package name{Fore.WHITE}")
            return
        pkg_name = args[1]
        if pkg_name not in installed_packages:
            print(f"{Fore.YELLOW}Package '{pkg_name}' is not installed{Fore.WHITE}")
            return
        installed_packages.remove(pkg_name)
        save_system()
        print(f"{Fore.GREEN}✓{Fore.WHITE} Successfully removed {Fore.YELLOW}{pkg_name}{Fore.WHITE}")

    else:
        print(f"{Fore.RED}Unknown action: {action}{Fore.WHITE}")


def cmd_startx(args: list[str]) -> None:
    print(f"{Fore.YELLOW}Loading Desktop Environment...")
    for i in range(11):
        sys.stdout.write(f"\r[{'#' * i}{'.' * (10 - i)}] {i * 10}%")
        sys.stdout.flush()
        time.sleep(0.08)
    print("\n")
    start_gui()


def cmd_poweroff(args: list[str]) -> None:
    print(f"{Fore.RED}Shutting down PenguWarp Peach...")
    save_system()
    time.sleep(1)
    sys.exit(0)


commands: dict[str, object] = {
    "help": cmd_help,
    "list": cmd_list,
    "cd": cmd_cd,
    "read": cmd_read,
    "whereami": cmd_whereami,
    "mkdir": cmd_mkdir,
    "mkfile": cmd_mkfile,
    "delete": cmd_delete,
    "echo": cmd_echo,
    "whoami": cmd_whoami,
    "uname": cmd_uname,
    "clear": cmd_clear,
    "pyufetch": cmd_pyufetch,
    "pwdit": cmd_pwdit,
    "run": cmd_run,
    "pkgmgr": cmd_pkgmgr,
    "startx": cmd_startx,
    "poweroff": cmd_poweroff,
    "rmdir": cmd_rmdir,
}


def setup_readline() -> None:
    """Configure readline with tab completion for commands and filesystem paths."""

    def completer(text: str, state: int) -> str | None:
        parts = readline.get_line_buffer().split()
        if len(parts) == 0 or (
            len(parts) == 1 and not readline.get_line_buffer().endswith(" ")
        ):
            all_cmds = list(commands.keys()) + installed_packages
            matches = [c for c in all_cmds if c.startswith(text)]
            return matches[state] if state < len(matches) else None

        prefix = text
        base_dir = current_dir

        if "/" in prefix:
            slash_idx = prefix.rfind("/")
            base_dir = prefix[:slash_idx] or "~"
            prefix = prefix[slash_idx + 1 :]

        contents = filesystem.get(base_dir, {}).get("contents", [])
        matches = [item for item in contents if item.startswith(prefix)]

        if state < len(matches):
            item = matches[state]
            full = f"{base_dir}/{item}" if base_dir != "~" else f"~/{item}"
            return item + ("/" if filesystem.get(full, {}).get("type") == "dir" else "")
        return None

    readline.set_completer(completer)
    readline.set_completer_delims(" \t")
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind('"\\e[A": previous-history')
    readline.parse_and_bind('"\\e[B": next-history')


def execute_command(line: str) -> None:
    parts = line.split()
    if not parts:
        return
    cmd, *args = parts

    if cmd in commands:
        commands[cmd](args)  # type: ignore[operator]
    elif cmd in installed_packages and repo is not None:
        if cmd in repo.AVAILABLE_PACKAGES:
            pkg_file = repo.AVAILABLE_PACKAGES[cmd]["file"]
            pkg_path = os.path.join(SCRIPT_DIR, "packages", pkg_file)
            sys.argv = [cmd, *args]
            try:
                with open(pkg_path, "r", encoding="utf-8") as f:
                    code = f.read()
                exec(
                    compile(code, pkg_path, "exec"),
                    {"__name__": "__main__", "__file__": pkg_path},
                )
            except FileNotFoundError:
                print(f"{Fore.RED}Error: Package file not found: {pkg_file}{Fore.WHITE}")
            except Exception as e:
                print(f"{Fore.RED}Error running package: {e}{Fore.WHITE}")
    else:
        print(f"penguwarp: {cmd}: command not found")


if __name__ == "__main__":
    if load_system():
        first_boot_setup()
    else:
        boot_animation_splash()

    boot_sequence()
    setup_readline()
    while True:
        try:
            line = input(
                f"{Fore.YELLOW}{user}@{hostname}{Fore.WHITE}:{Fore.YELLOW}{current_dir}{Fore.WHITE}$ "
            ).strip()
            execute_command(line)
        except KeyboardInterrupt:
            print("\nType 'poweroff' to exit.")
        except EOFError:
            cmd_poweroff([])
