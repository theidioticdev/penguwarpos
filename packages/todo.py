from colorama import Fore

def run():
    """Simple todo list manager"""
    import sys
    
    if len(sys.argv) < 2:
        print(f"{Fore.CYAN}=== TODO LIST ==={Fore.WHITE}")
        print("Usage:")
        print("  todo add <task>    - Add a new task")
        print("  todo list          - Show all tasks")
        print("  todo done <num>    - Mark task as done")
        print("  todo clear         - Clear all tasks")
        return
    
    # Load todos from a fake file (could be implemented with real filesystem)
    todos = [
        "Install more packages",
        "Try the snake game",
        "Explore PenguWarp GUI"
    ]
    
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
            print(f"{Fore.GREEN}✓{Fore.WHITE} Added: {task}")
    
    elif action == "done":
        if len(sys.argv) < 3:
            print(f"{Fore.RED}Error: Please specify task number{Fore.WHITE}")
        else:
            try:
                num = int(sys.argv[2])
                if 1 <= num <= len(todos):
                    print(f"{Fore.GREEN}✓{Fore.WHITE} Completed: {todos[num-1]}")
                else:
                    print(f"{Fore.RED}Error: Invalid task number{Fore.WHITE}")
            except ValueError:
                print(f"{Fore.RED}Error: Please enter a valid number{Fore.WHITE}")
    
    elif action == "clear":
        print(f"{Fore.YELLOW}All tasks cleared!{Fore.WHITE}")
    
    else:
        print(f"{Fore.RED}Error: Unknown action '{action}'{Fore.WHITE}")
        print("Use 'todo' with no arguments to see usage")

if __name__ == "__main__":
    run()
