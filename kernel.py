import time
import sys
import os
import readline
import json
import tkinter as tk
from colorama import Fore, init

init(autoreset=True)

start_time = time.time()

user = "liveuser"
hostname = "livesys"
current_dir = "~"
filesystem = {}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEM_FILE = os.path.join(SCRIPT_DIR, "penguwarp_system.json")

COMMAND_DESC = {
    "help":     "Display this comprehensive command reference",
    "ls":       "List files and directories in the current path",
    "cat":      "Read and display the contents of a file",
    "cd":       "Navigate between directories",
    "pwd":      "Show the current working directory path",
    "mkdir":    "Create a new directory",
    "touch":    "Create a new empty file",
    "rm":       "Remove a file",
    "echo":     "Display a line of text",
    "run":      "Execute a .pwe script file",
    "uname":    "Display kernel and system version",
    "whoami":   "Show current active user identity",
    "pwdit":    "Open the PenguWarp line editor for files",
    "pyufetch": "Show system hardware and OS branding",
    "clear":    "Wipe the terminal screen",
    "startx":   "Launch the WindowMaker GUI environment",
    "poweroff": "Shutdown the system and save all changes"
}

def load_system():
    global user, hostname, filesystem
    if os.path.exists(SYSTEM_FILE):
        try:
            with open(SYSTEM_FILE, 'r') as f:
                data = json.load(f)
                user = data["system"]["username"]
                hostname = data["system"]["hostname"]
                filesystem = data["filesystem"]
                return data["system"]["first_boot"]
        except:
            return True
    return True

def save_system():
    data = {
        "system": {"username": user, "hostname": hostname, "first_boot": False},
        "filesystem": filesystem
    }
    with open(SYSTEM_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def first_boot_setup():
    global user, hostname, filesystem
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Fore.CYAN}╔════════════════════════════════════════╗")
    print(f"{Fore.CYAN}║   ~ Welcome to PenguWarp OS Setup! ~   ║")
    print(f"{Fore.CYAN}╚════════════════════════════════════════╝\n")
    u_in = input(f"{Fore.GREEN}Choose Username: {Fore.WHITE}").strip()
    h_in = input(f"{Fore.GREEN}Choose Hostname: {Fore.WHITE}").strip()
    user = u_in if u_in else "user"
    hostname = h_in if h_in else "pengu"
    filesystem.update({
        "~": {"type": "dir", "contents": ["documents", "downloads", "pictures", "desktop", "welcome.txt"]},
        "~/documents": {"type": "dir", "contents": []},
        "~/downloads": {"type": "dir", "contents": []},
        "~/pictures": {"type": "dir", "contents": []},
        "~/desktop": {"type": "dir", "contents": []},
        "~/welcome.txt": {"type": "file", "content": f"Welcome to PenguWarp OS, {user}!\n\nThis is your persistent home directory.\nType 'help' to begin.\n\nBuilt with Python & Tkinter."}
    })
    save_system()
    print(f"\n{Fore.GREEN}System initialized. Booting...")
    time.sleep(1)

def boot_sequence():
    print(f"{Fore.GREEN}PenguWarp Kernel v0.1.5_generic-x86_64 initializing...")
    time.sleep(0.4)
    logs = ["Detecting Horizon V CPU...", "Mounting Crudal HDD V2...", "Initializing Memory Manager (128MB)...", "Loading PWShell..."]
    for log in logs:
        print(f"  [{Fore.CYAN}  OK  {Fore.WHITE}] {log}")
        time.sleep(0.2)
    print(f"\n{Fore.CYAN}   ___\n  <   o>  PenguWarp OS\n  ( | )   v0.1.5\n  /___\\ \n")

def get_dynamic_ram():
    base_usage = 1.2
    fs_size = sys.getsizeof(json.dumps(filesystem)) / (1024 * 1024)
    total_used = base_usage + fs_size
    return round(total_used, 2)

def create_wm_window(parent, title_text, width, height):
    win = tk.Toplevel(parent)
    win.overrideredirect(True)
    win.geometry(f"{width}x{height}+250+150")
    win.configure(bg="#2e2e2e", bd=3, relief="raised")
    title_bar = tk.Frame(win, bg="#4a4a4a", relief="raised", bd=2)
    title_bar.pack(fill="x", side="top")
    tk.Label(title_bar, text=title_text, fg="white", bg="#4a4a4a", font=("Courier", 10, "bold")).pack(side="left", padx=5)
    tk.Button(title_bar, text="X", command=win.destroy, bg="#c0c0c0", relief="raised", bd=2, font=("Courier", 8, "bold"), width=2).pack(side="right", padx=2, pady=2)
    content = tk.Frame(win, bg="black", bd=2, relief="sunken")
    content.pack(fill="both", expand=True, padx=4, pady=4)
    def set_offset(event):
        win._offsetx, win._offsety = event.x, event.y
    def move_window(event):
        win.geometry(f'+{event.x_root - win._offsetx}+{event.y_root - win._offsety}')
    title_bar.bind('<Button-1>', set_offset)
    title_bar.bind('<B1-Motion>', move_window)
    return win, content

# --- NEW GUI APPS --

def gui_sysinfo(parent):
    win, container = create_wm_window(parent, "System Info", 600, 600)
    
    tk.Label(container, text="🐧", font=("Courier", 40), bg="black", fg="cyan").pack(pady=10)
    
    info_text = (
        f"OS: PenguWarp v0.1.5\n"
        f"Kernel: PW-Generic-x86\n"
        f"User: {user}\n"
        f"RAM: {get_dynamic_ram()}MB / 128MB"
    )
    tk.Label(container, text=info_text, font=("Courier", 10), bg="black", fg="white", justify="left").pack()

    health_frame = tk.Frame(container, bg="#333", height=20, width=200)
    health_frame.pack(pady=10)
    tk.Frame(health_frame, bg="lime", height=20, width=180).place(x=0, y=0) 

    storage_size = os.path.getsize(SYSTEM_FILE) if os.path.exists(SYSTEM_FILE) else 0
    storage_kb = round(storage_size / 1024, 2)
    max_storage_kb = 512
    storage_percent = min((storage_kb / max_storage_kb) * 200, 200)

    tk.Label(container, text=f"DISK: {storage_kb}KB / {max_storage_kb}KB", 
             font=("Courier", 10), bg="black", fg="white").pack(pady=(10, 0))

    storage_bg = tk.Frame(container, bg="#333", height=15, width=200)
    storage_bg.pack(pady=5)
    tk.Frame(storage_bg, bg="cyan", height=15, width=storage_percent).place(x=0, y=0)

def gui_clock(parent):
    win, container = create_wm_window(parent, "System Clock", 300, 120)
    lbl = tk.Label(container, font=("Courier", 30, "bold"), fg="cyan", bg="black")
    lbl.pack(expand=True)
    def update():
        lbl.config(text=time.strftime("%H:%M:%S"))
        lbl.after(1000, update)
    update()

def gui_calculator(parent):
    win, container = create_wm_window(parent, "Calculator", 240, 320)
    expr = tk.StringVar()
    tk.Entry(container, textvariable=expr, font=("Courier", 16), bg="#222", fg="white", justify="right", bd=0).pack(fill="x", padx=5, pady=5)
    btn_frame = tk.Frame(container, bg="black")
    btn_frame.pack(fill="both", expand=True)
    btns = ['7','8','9','/', '4','5','6','*', '1','2','3','-', 'C','0','=','+']
    def click(b):
        if b == "=":
            try: expr.set(str(eval(expr.get())))
            except: expr.set("Error")
        elif b == "C": expr.set("")
        else: expr.set(expr.get() + b)
    for i, b in enumerate(btns):
        tk.Button(btn_frame, text=b, command=lambda x=b: click(x), bg="#444", fg="white", font=("Courier", 12, "bold"), bd=2).grid(row=i//4, column=i%4, sticky="nsew")
    for i in range(4):
        btn_frame.grid_columnconfigure(i, weight=1); btn_frame.grid_rowconfigure(i, weight=1)

def gui_paint(parent):
    win, container = create_wm_window(parent, "PenguPaint", 400, 450)
    canvas = tk.Canvas(container, bg="white", cursor="cross")
    canvas.pack(fill="both", expand=True)
    def paint(e):
        canvas.create_oval(e.x-2, e.y-2, e.x+2, e.y+2, fill="black", outline="black")
    canvas.bind("<B1-Motion>", paint)
    tk.Button(container, text="CLEAR CANVAS", command=lambda: canvas.delete("all"), bg="#8b0000", fg="white", font=("Courier", 8, "bold")).pack(fill="x")


def gui_pwdit(parent, filename=None):
    if not filename:
        filename = "new_file.txt"
        
    win, container = create_wm_window(parent, f"GPWDIT - {filename}", 500, 400)
    
    toolbar = tk.Frame(container, bg="#333")
    toolbar.pack(fill="x")
    
    text_area = tk.Text(container, bg="black", fg="white", insertbackground="white",
                        font=("Courier", 11), padx=10, pady=10, borderwidth=0)
    text_area.pack(fill="both", expand=True)

    path = f"{current_dir}/{filename}" if current_dir != "~" else f"~/{filename}"
    if path in filesystem and filesystem[path]["type"] == "file":
        text_area.insert("1.0", filesystem[path]["content"])

    def save_action():
        content = text_area.get("1.0", "end-1c")
        path = f"{current_dir}/{filename}" if current_dir != "~" else f"~/{filename}"
        
        filesystem[path] = {"type": "file", "content": content}
        if filename not in filesystem[current_dir]["contents"]:
            filesystem[current_dir]["contents"].append(filename)
            
        save_system()
        save_btn.config(bg="green", text="SAVED!")
        win.after(1000, lambda: save_btn.config(bg="#2e7d32", text="SAVE"))

    save_btn = tk.Button(toolbar, text="SAVE", command=save_action, 
                         bg="#2e7d32", fg="white", font=("Courier", 9, "bold"), 
                         relief="flat", padx=10)
    save_btn.pack(side="left", padx=5, pady=2)

# --- END NEW APPS ---

def gui_text_viewer(parent, filename, text_content):
    win, container = create_wm_window(parent, f"Text Viewer: {filename}", 450, 350)
    txt = tk.Text(container, bg="black", fg="white", font=("Courier", 10), padx=10, pady=10, borderwidth=0)
    txt.pack(fill="both", expand=True)
    txt.insert("1.0", text_content)
    txt.config(state="disabled")

def gui_file_browser(parent):
    win, container = create_wm_window(parent, "File Browser", 550, 400)
    curr_path = ["~"]
    hdr = tk.Frame(container, bg="#1a1a1a")
    hdr.pack(fill="x")
    path_lbl = tk.Label(hdr, text=f"Location: {curr_path[0]}", fg="cyan", bg="#1a1a1a", font=("Courier", 9))
    path_lbl.pack(side="left", padx=5)
    lb = tk.Listbox(container, bg="black", fg="white", font=("Courier", 11), borderwidth=0, highlightthickness=0)
    lb.pack(fill="both", expand=True, padx=5, pady=5)
    def refresh():
        lb.delete(0, tk.END)
        path_lbl.config(text=f"Location: {curr_path[0]}")
        if curr_path[0] != "~":
            lb.insert(tk.END, " .. [UP ONE LEVEL]")
            lb.itemconfig(tk.END, fg="yellow")
        for item in filesystem.get(curr_path[0], {}).get("contents", []):
            full_p = f"{curr_path[0]}/{item}" if curr_path[0] != "~" else f"~/{item}"
            icon = "📁" if full_p in filesystem and filesystem[full_p]["type"] == "dir" else "📄"
            lb.insert(tk.END, f" {icon} {item}")
            if icon == "📁": lb.itemconfig(tk.END, fg="cyan")
    def on_click(e):
        sel = lb.curselection()
        if not sel: return
        txt = lb.get(sel[0])
        if "[UP ONE LEVEL]" in txt:
            p = curr_path[0].split("/")
            curr_path[0] = "/".join(p[:-1]) if len(p) > 1 else "~"
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

def start_gui():
    root = tk.Tk()
    root.title("PenguWarp Desktop")
    root.geometry("1024x768")
    root.configure(bg="#1a1a1a")
    tk.Label(root, text="PENGUWARP WORKSTATION", font=("Courier", 24, "bold"), fg="#222222", bg="#1a1a1a").place(relx=0.5, rely=0.4, anchor="center")
    dock = tk.Frame(root, bg="#2e2e2e", bd=2, relief="raised", height=55)
    dock.pack(side="bottom", fill="x")
    
    # Dock Buttons
    tk.Button(dock, text="EDITOR", command=lambda: gui_pwdit(root), bg="#4a4a4a", fg="white", relief="raised", bd=3, font=("Courier", 9, "bold"), padx=10).pack(side="left", padx=5, pady=5)
    tk.Button(dock, text="SYS-INFO", command=lambda: gui_sysinfo(root), bg="#4a4a4a", fg="white", relief="raised", bd=3, font=("Courier", 9, "bold"), padx=10).pack(side="left", padx=5, pady=5)
    tk.Button(dock, text="FILES", command=lambda: gui_file_browser(root), bg="#4a4a4a", fg="white", relief="raised", bd=3, font=("Courier", 9, "bold"), padx=10).pack(side="left", padx=5, pady=5)
    tk.Button(dock, text="CALC", command=lambda: gui_calculator(root), bg="#4a4a4a", fg="white", relief="raised", bd=3, font=("Courier", 9, "bold"), padx=10).pack(side="left", padx=5, pady=5)
    tk.Button(dock, text="PAINT", command=lambda: gui_paint(root), bg="#4a4a4a", fg="white", relief="raised", bd=3, font=("Courier", 9, "bold"), padx=10).pack(side="left", padx=5, pady=5)
    tk.Button(dock, text="CLOCK", command=lambda: gui_clock(root), bg="#4a4a4a", fg="white", relief="raised", bd=3, font=("Courier", 9, "bold"), padx=10).pack(side="left", padx=5, pady=5)
    
    tk.Button(dock, text="LOGOUT", command=root.destroy, bg="#8b0000", fg="white", relief="raised", bd=3, font=("Courier", 9, "bold"), padx=10).pack(side="right", padx=10, pady=5)
    def create_icon(name, x, y, command):
        btn = tk.Button(root, text=f"🧊\n{name}", command=command, 
                        bg="#1a1a1a", fg="white", bd=0, 
                        activebackground="#333", font=("Courier", 10))
        btn.place(x=x, y=y)

    create_icon("FILES", 50, 50, lambda: gui_file_browser(root))
    create_icon("CALC", 50, 150, lambda: gui_calculator(root))
    create_icon("PAINT", 50, 250, lambda: gui_paint(root))

    root.mainloop()

def cmd_help(args):
    print(f"\n{Fore.CYAN}PENGUWARP OS v0.1.4 COMMAND REFERENCE")
    print(f"{Fore.WHITE}" + "-" * 60)
    for c, d in COMMAND_DESC.items():
        print(f"{Fore.GREEN}{c:<12}{Fore.WHITE} : {d}")
    print("-" * 60 + "\n")

def cmd_ls(args):
    if current_dir in filesystem:
        out = []
        for i in filesystem[current_dir]["contents"]:
            p = f"{current_dir}/{i}" if current_dir != "~" else f"~/{i}"
            out.append(f"{Fore.BLUE}{i}{Fore.WHITE}" if p in filesystem and filesystem[p]["type"] == "dir" else i)
        print("  ".join(out) if out else "(directory empty)")

def cmd_cd(args):
    global current_dir
    target = args[0] if args else "~"
    path = target if target.startswith("~") else f"{current_dir}/{target}" if current_dir != "~" else f"~/{target}"
    if path in filesystem and filesystem[path]["type"] == "dir":
        current_dir = path
    else:
        print(f"cd: no such directory: {target}")

def cmd_cat(args):
    if not args: return
    path = f"{current_dir}/{args[0]}" if current_dir != "~" else f"~/{args[0]}"
    if path in filesystem and filesystem[path]["type"] == "file":
        print(filesystem[path]["content"])
    else:
        print(f"cat: {args[0]}: file not found")

def cmd_mkdir(args):
    if not args: return
    path = f"{current_dir}/{args[0]}" if current_dir != "~" else f"~/{args[0]}"
    if path not in filesystem:
        filesystem[path] = {"type": "dir", "contents": []}
        filesystem[current_dir]["contents"].append(args[0])
        save_system()

def cmd_touch(args):
    if not args: return
    path = f"{current_dir}/{args[0]}" if current_dir != "~" else f"~/{args[0]}"
    if path not in filesystem:
        filesystem[path] = {"type": "file", "content": ""}
        filesystem[current_dir]["contents"].append(args[0])
        save_system()

def cmd_rm(args):
    if not args: return
    path = f"{current_dir}/{args[0]}" if current_dir != "~" else f"~/{args[0]}"
    if path in filesystem and filesystem[path]["type"] == "file":
        del filesystem[path]
        filesystem[current_dir]["contents"].remove(args[0])
        save_system()

def cmd_echo(args):
    print(" ".join(args))

def cmd_pwd(args):
    print(current_dir)

def cmd_whoami(args):
    print(user)

def cmd_uname(args):
    print("pengu-v0.1.5-generic_x86-64")

def cmd_clear(args):
    os.system('cls' if os.name == 'nt' else 'clear')

def cmd_pyufetch(args):
    uptime = int(time.time() - start_time)
    used_ram = get_dynamic_ram()
    total_ram = 128.0
    ascii_art = [
        f"{Fore.CYAN} _____  __          __",
        f"{Fore.CYAN}|  __ \\ \\ \\        / /",
        f"{Fore.CYAN}| |__) | \\ \\  /\\  / / ",
        f"{Fore.CYAN}|  ___/   \\ \\/  \\/ /  ",
        f"{Fore.CYAN}| |        \\  /\\  /   ",
        f"{Fore.CYAN}|_|         \\/  \\/    "
    ]
    info = [
        f"{Fore.GREEN}{user}@{hostname}",
        f"{Fore.WHITE}------------------",
        f"{Fore.YELLOW}OS: {Fore.WHITE}PenguWarp v0.1.4",
        f"{Fore.YELLOW}Kernel: {Fore.WHITE}0.1.4-generic",
        f"{Fore.YELLOW}Uptime: {Fore.WHITE}{uptime}s",
        f"{Fore.YELLOW}Shell: {Fore.WHITE}PWShell",
        f"{Fore.YELLOW}CPU: {Fore.WHITE}Horizon V @ 120 Hz",
        f"{Fore.YELLOW}RAM: {Fore.WHITE}{used_ram}MB / {total_ram}MB"
    ]
    for i in range(max(len(ascii_art), len(info))):
        left = ascii_art[i] if i < len(ascii_art) else " " * 22
        right = info[i] if i < len(info) else ""
        print(f"{left}    {right}")

def cmd_pwdit(args):
    if not args: return
    path = f"{current_dir}/{args[0]}" if current_dir != "~" else f"~/{args[0]}"
    print(f"Editing {args[0]} (Double Enter to save | Ctrl+C to cancel)")
    lines = []
    try:
        while True:
            l = input()
            if l == "" and lines and lines[-1] == "": break
            lines.append(l)
        filesystem[path] = {"type": "file", "content": "\n".join(lines).strip()}
        if args[0] not in filesystem[current_dir]["contents"]:
            filesystem[current_dir]["contents"].append(args[0])
        save_system()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Cancelling editing...")

def cmd_run(args):
    if not args: return
    path = f"{current_dir}/{args[0]}" if current_dir != "~" else f"~/{args[0]}"
    if path in filesystem and args[0].endswith(".pwe"):
        print(f"{Fore.YELLOW}Executing {args[0]}...")
        for script_line in filesystem[path]["content"].split("\n"):
            if script_line.strip():
                execute_command(script_line.strip())
    else:
        print(f"run: {args[0]} is not a valid script")

def cmd_startx(args):
    print(f"{Fore.CYAN}Loading Desktop Environment...")
    for i in range(11):
        sys.stdout.write(f"\r[{'#' * i}{'.' * (10-i)}] {i*10}%")
        sys.stdout.flush()
        time.sleep(0.08)
    print("\n")
    start_gui()

def cmd_poweroff(args):
    print(f"{Fore.RED}Shutting down...")
    save_system()
    time.sleep(1)
    sys.exit()

commands = {
    "help": cmd_help,
    "ls": cmd_ls,
    "cd": cmd_cd,
    "cat": cmd_cat,
    "pwd": cmd_pwd,
    "mkdir": cmd_mkdir,
    "touch": cmd_touch,
    "rm": cmd_rm,
    "echo": cmd_echo,
    "whoami": cmd_whoami,
    "uname": cmd_uname,
    "clear": cmd_clear,
    "pyufetch": cmd_pyufetch,
    "pwdit": cmd_pwdit,
    "run": cmd_run,
    "startx": cmd_startx,
    "poweroff": cmd_poweroff
}

def execute_command(line):
    parts = line.split()
    if not parts: return
    cmd = parts[0]
    args = parts[1:]
    if cmd in commands:
        commands[cmd](args)
    else:
        print(f"penguwarp: {cmd}: command not found")

if __name__ == "__main__":
    if load_system():
        first_boot_setup()
    boot_sequence()
    while True:
        try:
            line = input(f"{Fore.GREEN}{user}@{hostname}{Fore.WHITE}:{Fore.BLUE}{current_dir}{Fore.WHITE}$ ").strip()
            execute_command(line)
        except KeyboardInterrupt:
            print("\nType 'poweroff' to exit.")
