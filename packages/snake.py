import random
import time
import heapq
from colorama import Fore, Style

def run():
    print(f"{Fore.GREEN}=== SNAKE GAME (AUTO-PLAY DEMO) ==={Style.RESET_ALL}")
    print("Watch the snake eat food automatically!")
    print("Press Ctrl+C to stop\n")
    time.sleep(1)

    width, height = 20, 10
    snake = [(5, 5), (5, 4), (5, 3)]
    direction = (0, 1)
    food = place_food(snake, width, height)
    score = 0
    high_score = 0

    def draw():
        print("\033[H\033[J")
        print(f"{Fore.CYAN}Score: {score} | High Score: {high_score} | Auto-playing...{Style.RESET_ALL}")
        print(f"{Fore.WHITE}+" + "-" * width + "+{Style.RESET_ALL}")
        for y in range(height):
            print(f"{Fore.WHITE}|{Style.RESET_ALL}", end="")
            for x in range(width):
                pos = (y, x)
                if pos == snake[0]:
                    print(f"{Fore.YELLOW}O{Style.RESET_ALL}", end="")  # head
                elif pos in snake:
                    print(f"{Fore.GREEN}o{Style.RESET_ALL}", end="")  # body
                elif pos == food:
                    print(f"{Fore.RED}@{Style.RESET_ALL}", end="")
                else:
                    print(f"{Fore.WHITE}.{Style.RESET_ALL}", end="")
            print(f"{Fore.WHITE}|{Style.RESET_ALL}")
        print(f"{Fore.WHITE}+" + "-" * width + f"+{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Press Ctrl+C to stop{Style.RESET_ALL}")

    try:
        while True:
            draw()
            time.sleep(0.15)

            head = snake[0]
            snake_set = set(snake)

            # Try A* to food first
            path = astar(head, food, snake_set, width, height)

            if path and len(path) > 1:
                next_pos = path[1]
            else:
                # A* failed - survival mode: pick safest direction
                next_pos = survival_move(head, direction, snake_set, width, height)

            if next_pos is None:
                # truly cooked, just go forward and die with dignity
                next_pos = (
                    (head[0] + direction[0]) % height,
                    (head[1] + direction[1]) % width,
                )

            direction = (next_pos[0] - head[0], next_pos[1] - head[1])
            # fix wrap-around direction weirdness
            if direction[0] > 1: direction = (-1, direction[1])
            if direction[0] < -1: direction = (1, direction[1])
            if direction[1] > 1: direction = (direction[0], -1)
            if direction[1] < -1: direction = (direction[0], 1)

            new_head = (
                (head[0] + direction[0]) % height,
                (head[1] + direction[1]) % width,
            )

            # self collision = game over
            if new_head in snake_set:
                high_score = max(high_score, score)
                print(f"\n{Fore.RED}GAME OVER! Hit itself! 💀{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Score: {score} | High Score: {high_score}{Style.RESET_ALL}")
                time.sleep(1.5)
                # restart
                snake = [(5, 5), (5, 4), (5, 3)]
                direction = (0, 1)
                food = place_food(snake, width, height)
                score = 0
                continue

            snake.insert(0, new_head)

            if new_head == food:
                score += 10
                food = place_food(snake, width, height)
            else:
                snake.pop()

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Game stopped!{Style.RESET_ALL}")
        print(f"Final Score: {score} | High Score: {high_score}")


def place_food(snake, width, height):
    snake_set = set(snake)
    while True:
        pos = (random.randint(0, height - 1), random.randint(0, width - 1))
        if pos not in snake_set:
            return pos


def neighbors(pos, width, height):
    y, x = pos
    return [
        ((y - 1) % height, x),
        ((y + 1) % height, x),
        (y, (x - 1) % width),
        (y, (x + 1) % width),
    ]


def heuristic(a, b, width, height):
    # toroidal (wrap-aware) manhattan distance
    dy = abs(a[0] - b[0])
    dx = abs(a[1] - b[1])
    dy = min(dy, height - dy)
    dx = min(dx, width - dx)
    return dy + dx


def astar(start, goal, snake_set, width, height):
    open_heap = []
    heapq.heappush(open_heap, (0, start))
    came_from = {start: None}
    g_score = {start: 0}

    while open_heap:
        _, current = heapq.heappop(open_heap)

        if current == goal:
            # reconstruct path
            path = []
            while current is not None:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for nb in neighbors(current, width, height):
            if nb in snake_set and nb != goal:
                continue
            tentative_g = g_score[current] + 1
            if tentative_g < g_score.get(nb, float('inf')):
                came_from[nb] = current
                g_score[nb] = tentative_g
                f = tentative_g + heuristic(nb, goal, width, height)
                heapq.heappush(open_heap, (f, nb))

    return None  # no path found


def flood_fill_count(pos, snake_set, width, height):
    """count reachable cells from pos - used to pick safest move"""
    visited = set()
    stack = [pos]
    while stack:
        cur = stack.pop()
        if cur in visited or cur in snake_set:
            continue
        visited.add(cur)
        stack.extend(neighbors(cur, width, height))
    return len(visited)


def survival_move(head, direction, snake_set, width, height):
    """when A* finds no path, pick the move with most open space"""
    best = None
    best_score = -1

    for nb in neighbors(head, width, height):
        if nb in snake_set:
            continue
        space = flood_fill_count(nb, snake_set, width, height)
        if space > best_score:
            best_score = space
            best = nb

    return best


if __name__ == "__main__":
    run()
