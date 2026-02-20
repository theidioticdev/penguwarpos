from colorama import Fore


def run():
    import sys
    import json
    import os

    TODO_FILE = os.path.join(os.path.dirname(__file__), "..", "penguwarp_todos.json")

    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as f:
            todos = json.load(f)
    else:
        todos = []

    def save_todos():
        with open(TODO_FILE, "w") as f:
            json.dump(todos, f, indent=2)

    if len(sys.argv) < 2:
        print(f"{Fore.CYAN}=== TODO LIST ==={Fore.WHITE}")
        print("Usage:")
        print("  todo add <task>    - Add a new task")
        print("  todo list          - Show all tasks")
        print("  todo done <num>    - Mark task as done")
        print("  todo clear         - Clear all tasks")
        return

    action = sys.argv[1]

    if action == "list":
        if not todos:
            print(f"{Fore.YELLOW}No tasks yet!{Fore.WHITE}")
        else:
            print(f"{Fore.CYAN}=== YOUR TASKS ==={Fore.WHITE}")
            for i, task in enumerate(todos, 1):
                print(f"{Fore.GREEN}{i}.{Fore.WHITE} {task}")

    elif action == "add":
        if len(sys.argv) < 3:
            print(f"{Fore.RED}Error: Please specify a task{Fore.WHITE}")
        else:
            task = " ".join(sys.argv[2:])
            todos.append(task)
            save_todos()
            print(f"{Fore.GREEN}✓{Fore.WHITE} Added: {task}")

    elif action == "done":
        if len(sys.argv) < 3:
            print(f"{Fore.RED}Error: Please specify task number{Fore.WHITE}")
        else:
            try:
                num = int(sys.argv[2])
                if 1 <= num <= len(todos):
                    completed = todos.pop(num - 1)
                    save_todos()
                    print(f"{Fore.GREEN}✓{Fore.WHITE} Completed: {completed}")
                else:
                    print(f"{Fore.RED}Error: Invalid task number{Fore.WHITE}")
            except ValueError:
                print(f"{Fore.RED}Error: Please enter a valid number{Fore.WHITE}")

    elif action == "clear":
        todos.clear()
        save_todos()
        print(f"{Fore.YELLOW}All tasks cleared!{Fore.WHITE}")


if __name__ == "__main__":
    run()
