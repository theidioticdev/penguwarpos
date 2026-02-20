import sys
import random
import time
import shutil

# Characters to use
CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*"


def matrix_rain():
    cols, rows = shutil.get_terminal_size()

    # Single array, reused every frame
    drops = [0] * cols

    # Hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    try:
        while True:
            # Clear and reset - don't accumulate
            sys.stdout.write("\033[2J\033[H")

            # Update drops
            for i in range(cols):
                if drops[i] == 0:
                    if random.random() > 0.975:
                        drops[i] = 1
                elif drops[i] > rows:
                    drops[i] = 0
                else:
                    # Draw character
                    char = random.choice(CHARS)
                    sys.stdout.write(f"\033[{drops[i]};{i + 1}H\033[92m{char}")
                    drops[i] += 1

            sys.stdout.flush()
            time.sleep(0.05)

    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h\033[2J\033[H")
        sys.stdout.flush()


if __name__ == "__main__":
    matrix_rain()
