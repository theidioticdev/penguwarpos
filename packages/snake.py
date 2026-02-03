import random
import time
from colorama import Fore


def run():
    """Simple snake game - auto-play demo version"""
    print(f"{Fore.GREEN}=== SNAKE GAME (AUTO-PLAY DEMO) ==={Fore.WHITE}")
    print("Watch the snake eat food automatically!")
    print("Press Ctrl+C to stop\n")

    time.sleep(1)

    width, height = 20, 10
    snake = [(5, 5), (5, 4), (5, 3)]
    direction = (0, 1)  # right
    food = (random.randint(0, height - 1), random.randint(0, width - 1))
    score = 0

    def draw():
        print("\033[H\033[J")  # clear screen
        print(f"{Fore.CYAN}Score: {score} | Auto-playing...{Fore.WHITE}")
        for y in range(height):
            for x in range(width):
                if (y, x) in snake:
                    print(f"{Fore.GREEN}O{Fore.WHITE}", end="")
                elif (y, x) == food:
                    print(f"{Fore.RED}@{Fore.WHITE}", end="")
                else:
                    print(".", end="")
            print()
        print(f"\n{Fore.YELLOW}Press Ctrl+C to stop{Fore.WHITE}")

    try:
        while True:
            draw()
            time.sleep(0.3)

            # Simple AI: move towards food
            head = snake[0]

            # Calculate direction to food
            dy = food[0] - head[0]
            dx = food[1] - head[1]

            # Choose direction (avoid going backwards)
            if abs(dx) > abs(dy):
                if dx > 0 and direction != (0, -1):
                    direction = (0, 1)  # right
                elif dx < 0 and direction != (0, 1):
                    direction = (0, -1)  # left
            else:
                if dy > 0 and direction != (-1, 0):
                    direction = (1, 0)  # down
                elif dy < 0 and direction != (1, 0):
                    direction = (-1, 0)  # up

            # Move snake
            new_head = (head[0] + direction[0], head[1] + direction[1])

            # Check collision with walls
            if (
                new_head[0] < 0
                or new_head[0] >= height
                or new_head[1] < 0
                or new_head[1] >= width
            ):
                print(f"\n{Fore.RED}GAME OVER! Hit a wall!{Fore.WHITE}")
                print(f"{Fore.YELLOW}Final Score: {score}{Fore.WHITE}")
                break

            # Check collision with self
            if new_head in snake:
                print(f"\n{Fore.RED}GAME OVER! Hit itself!{Fore.WHITE}")
                print(f"{Fore.YELLOW}Final Score: {score}{Fore.WHITE}")
                break

            snake.insert(0, new_head)

            # Check if ate food
            if new_head == food:
                score += 10
                food = (random.randint(0, height - 1), random.randint(0, width - 1))
                while food in snake:
                    food = (random.randint(0, height - 1), random.randint(0, width - 1))
            else:
                snake.pop()

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Game stopped!{Fore.WHITE}")
        print(f"Final Score: {score}")


if __name__ == "__main__":
    run()
