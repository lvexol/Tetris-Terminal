import curses
import random
import time
from integrity_checker import IntegrityChecker
from anti_debug import AntiDebugger
from input_validator import InputValidator

# Define the shapes of the Tetriminos
SHAPES = [
    [[1, 1, 1],
     [0, 1, 0]],  # T-shape

    [[0, 1, 1],
     [1, 1, 0]],  # Z-shape

    [[1, 1, 0],
     [0, 1, 1]],  # S-shape

    [[1, 1, 1, 1]],  # I-shape

    [[1, 1],
     [1, 1]],  # O-shape

    [[1, 1, 1],
     [1, 0, 0]],  # L-shape

    [[1, 1, 1],
     [0, 0, 1]]   # J-shape
]

# Define game board dimensions
BOARD_WIDTH = 10
BOARD_HEIGHT = 20

class SecurityError(Exception):
    pass

def main(window):
    # Initialize security components
    integrity_checker = IntegrityChecker()
    anti_debugger = AntiDebugger()
    input_validator = InputValidator()

    # Get the terminal dimensions
    max_y, max_x = window.getmaxyx()
    
    # Check if terminal is large enough
    if max_y < BOARD_HEIGHT + 3 or max_x < (BOARD_WIDTH * 2 + 15):
        raise curses.error("Terminal window too small! Please resize.")

    # Initialize the window
    curses.curs_set(0)  # Hide cursor
    window.nodelay(1)  # Non-blocking input
    window.timeout(100)  # Refresh every 100 ms
    curses.start_color()  # Initialize color
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)  # For security warnings

    # Create an empty game board
    board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
    lines_cleared = 0  # Counter for lines cleared
    game_over = False
    score = 0

    def security_check():
        """Perform security checks"""
        if anti_debugger.is_debugger_present():
            raise SecurityError("Debugging detected!")
            
        if not integrity_checker.check_integrity(board, score, SHAPES):
            raise SecurityError("Game state integrity check failed!")

    def draw_board():
        try:
            for y, row in enumerate(board):
                for x, cell in enumerate(row):
                    if cell == 0:
                        window.addstr(y + 1, x * 2 + 2, '  ', curses.color_pair(2))
                    else:
                        window.addstr(y + 1, x * 2 + 2, '██', curses.color_pair(1))
        except curses.error:
            pass

    def draw_border():
        try:
            # Draw corners
            window.addch(0, 0, '┌')
            window.addch(0, BOARD_WIDTH * 2 + 2, '┐')
            window.addch(BOARD_HEIGHT + 1, 0, '└')
            window.addch(BOARD_HEIGHT + 1, BOARD_WIDTH * 2 + 2, '┘')

            # Draw horizontal borders
            for x in range(1, BOARD_WIDTH * 2 + 2):
                window.addch(0, x, '─')
                if x < max_x - 1:
                    window.addch(BOARD_HEIGHT + 1, x, '─')

            # Draw vertical borders
            for y in range(1, BOARD_HEIGHT + 1):
                window.addch(y, 0, '│')
                window.addch(y, BOARD_WIDTH * 2 + 2, '│')
        except curses.error:
            pass

    def display_info():
        try:
            window.addstr(2, BOARD_WIDTH * 2 + 5, f"Lines: {lines_cleared}")
            window.addstr(3, BOARD_WIDTH * 2 + 5, f"Score: {score}")
            if game_over:
                window.addstr(BOARD_HEIGHT // 2, (BOARD_WIDTH + 2), "GAME OVER!", curses.color_pair(3))
                window.addstr(BOARD_HEIGHT // 2 + 1, (BOARD_WIDTH + 2), "Press 'q' to quit")
        except curses.error:
            pass

    def valid_move(shape, offset_y, offset_x):
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    if (y + offset_y >= BOARD_HEIGHT or
                        x + offset_x >= BOARD_WIDTH or
                        x + offset_x < 0 or
                        y + offset_y < 0 or
                        board[y + offset_y][x + offset_x]):
                        return False
        return True

    def rotate_shape(shape):
        return [[shape[y][x] for y in range(len(shape))] for x in range(len(shape[0]) - 1, -1, -1)]

    def place_tetrimino(shape, offset_y, offset_x):
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    board[y + offset_y][x + offset_x] = cell

    def eliminate_lines():
        nonlocal board, lines_cleared, score
        new_board = [row for row in board if any(cell == 0 for cell in row)]
        lines_removed = BOARD_HEIGHT - len(new_board)
        if lines_removed > 0:
            lines_cleared += lines_removed
            # Score calculation: more points for more lines cleared at once
            score += (lines_removed * lines_removed) * 100
        board = [[0] * BOARD_WIDTH for _ in range(lines_removed)] + new_board

    def new_tetrimino():
        shape = random.choice(SHAPES)
        return shape, 0, BOARD_WIDTH // 2 - len(shape[0]) // 2

    def show_security_error(message):
        try:
            window.clear()
            window.addstr(BOARD_HEIGHT // 2, BOARD_WIDTH // 2 - len(message) // 2, 
                         message, curses.color_pair(3) | curses.A_BOLD)
            window.addstr(BOARD_HEIGHT // 2 + 1, BOARD_WIDTH // 2 - 10, 
                         "Game terminated due to security violation", curses.color_pair(3))
            window.refresh()
            time.sleep(3)
        except curses.error:
            pass

    # Initialize the first Tetrimino
    shape, shape_y, shape_x = new_tetrimino()
    last_fall_time = time.time()
    last_security_check = time.time()

    # Main game loop
    while True:
        try:
            # Perform periodic security checks
            if time.time() - last_security_check > 1:  # Check every second
                security_check()
                last_security_check = time.time()

            window.clear()
            draw_border()
            draw_board()
            display_info()

            if not game_over:
                # Draw the current Tetrimino
                try:
                    for y, row in enumerate(shape):
                        for x, cell in enumerate(row):
                            if cell:
                                window.addstr(shape_y + y + 1, (shape_x + x) * 2 + 2, '██', 
                                            curses.color_pair(1))
                except curses.error:
                    pass

            window.refresh()

            # Handle user input
            key = window.getch()
            if key != -1:  # If there is input
                if not input_validator.validate_input(key):
                    raise SecurityError("Suspicious input pattern detected!")

            if key == ord('q'):
                break
            
            if not game_over:
                if key == curses.KEY_LEFT and valid_move(shape, shape_y, shape_x - 1):
                    shape_x -= 1
                elif key == curses.KEY_RIGHT and valid_move(shape, shape_y, shape_x + 1):
                    shape_x += 1
                elif key == curses.KEY_DOWN and valid_move(shape, shape_y + 1, shape_x):
                    shape_y += 1
                    score += 1  # Small score bonus for manual drop
                elif key == ord(' '):  # Space bar for rotation
                    rotated_shape = rotate_shape(shape)
                    if valid_move(rotated_shape, shape_y, shape_x):
                        shape = rotated_shape
                elif key == ord('p'):  # Hard drop
                    while valid_move(shape, shape_y + 1, shape_x):
                        shape_y += 1
                        score += 2  # Bonus points for hard drop

                # Automatically move the Tetrimino down every second
                if time.time() - last_fall_time > 1:
                    if valid_move(shape, shape_y + 1, shape_x):
                        shape_y += 1
                    else:
                        place_tetrimino(shape, shape_y, shape_x)
                        eliminate_lines()
                        shape, shape_y, shape_x = new_tetrimino()
                        if not valid_move(shape, shape_y, shape_x):
                            game_over = True
                    last_fall_time = time.time()

        except SecurityError as e:
            show_security_error(str(e))
            break
        except curses.error:
            continue

# Run the game
if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"Error: {e}")
        print("Game terminated due to an error.")