import random
import time
from colorama import Fore

def run():
    """Cool matrix falling text effect"""
    print(f"{Fore.GREEN}=== MATRIX RAIN ==={Fore.WHITE}")
    print("Press Ctrl+C to stop\n")
    time.sleep(1)
    
    try:
        import os
        width = 60
        height = 20
        
        # Initialize columns
        columns = []
        for _ in range(width):
            columns.append({
                'chars': [],
                'y': random.randint(-height, 0),
                'speed': random.choice([1, 2, 3])
            })
        
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        frame = 0
        while True:
            # Clear screen
            print("\033[H\033[J", end="")
            
            # Update and draw
            grid = [[' ' for _ in range(width)] for _ in range(height)]
            
            for i, col in enumerate(columns):
                col['y'] += col['speed']
                
                if col['y'] > height + 10:
                    col['y'] = random.randint(-height, 0)
                    col['speed'] = random.choice([1, 2, 3])
                
                # Draw trail
                for offset in range(10):
                    y = col['y'] - offset
                    if 0 <= y < height:
                        char = random.choice(chars)
                        if offset == 0:
                            grid[y][i] = f"{Fore.WHITE}{char}"
                        elif offset < 3:
                            grid[y][i] = f"{Fore.LIGHTGREEN_EX}{char}"
                        else:
                            grid[y][i] = f"{Fore.GREEN}{char}"
            
            # Print grid
            for row in grid:
                print(''.join(row))
            
            time.sleep(0.05)
            frame += 1
            
    except KeyboardInterrupt:
        print(f"\n{Fore.WHITE}Matrix stopped.")

if __name__ == "__main__":
    run()
