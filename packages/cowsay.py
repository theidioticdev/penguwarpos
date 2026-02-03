from colorama import Fore

def run():
    """Make a cow say things"""
    import sys
    
    # Get message from command line or ask for it
    message = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    
    if not message:
        message = input(f"{Fore.CYAN}What should the cow say? {Fore.WHITE}")
    
    # Create the speech bubble
    length = len(message)
    border = "-" * (length + 2)
    
    print(f"\n {border}")
    print(f"< {message} >")
    print(f" {border}")
    print(f"{Fore.YELLOW}        \\   ^__^")
    print(f"         \\  (oo)\\_______")
    print(f"            (__)\\       )\\/\\")
    print(f"                ||----w |")
    print(f"                ||     ||{Fore.WHITE}\n")

if __name__ == "__main__":
    run()
