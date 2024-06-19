import curses
import random
import time

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

def main(window):
    # Initialize the window
    curses.curs_set(0)  # Hide cursor
    window.nodelay(1)  # Non-blocking input
    window.timeout(100)  # Refresh every 100 ms

    # Create an empty game board
    board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

    # Function to draw the game board
    def draw_board():
        for y, row in enumerate(board):
            for x, cell in enumerate(row):
                # Use '□' for empty cells and '■' for filled cells
                if cell == 0:
                    window.addstr(y, x, '□')
                else:
                      window.addstr(y, x, '■')

    # Function to check if the Tetrimino can be placed at the given position
    def valid_move(shape, offset_y, offset_x):
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    if (y + offset_y >= BOARD_HEIGHT or
                        x + offset_x >= BOARD_WIDTH or
                        x + offset_x < 0 or
                        board[y + offset_y][x + offset_x]):
                        return False
        return True

    # Function to rotate the Tetrimino
    def rotate_shape(shape):
        return [[shape[y][x] for y in range(len(shape))] for x in range(len(shape[0]) - 1, -1, -1)]

    # Function to merge the Tetrimino with the board
    def place_tetrimino(shape, offset_y, offset_x):
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    board[y + offset_y][x + offset_x] = cell

    # Function to eliminate full lines
    def eliminate_lines():
        nonlocal board
        new_board = [row for row in board if any(cell == 0 for cell in row)]
        lines_cleared = BOARD_HEIGHT - len(new_board)
        board = [[0] * BOARD_WIDTH for _ in range(lines_cleared)] + new_board

    # Add a new Tetrimino to the board
    def new_tetrimino():
        shape = random.choice(SHAPES)
        return shape, 0, BOARD_WIDTH // 2 - len(shape[0]) // 2

    # Initialize the first Tetrimino
    shape, shape_y, shape_x = new_tetrimino()

    last_fall_time = time.time()

    # Main game loop
    while True:
        window.clear()
        draw_board()

        # Draw the current Tetrimino
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    window.addstr(shape_y + y, (shape_x + x), '■')

        window.refresh()

        # Handle user input
        key = window.getch()
        if key == curses.KEY_EXIT or key == ord('q'):
            break
        elif key == curses.KEY_LEFT and valid_move(shape, shape_y, shape_x - 1):
            shape_x -= 1
        elif key == curses.KEY_RIGHT and valid_move(shape, shape_y, shape_x + 1):
            shape_x += 1
        elif key == curses.KEY_DOWN and valid_move(shape, shape_y + 1, shape_x):
            shape_y += 1
        elif key == ord(' '):  # Space bar for rotation
            rotated_shape = rotate_shape(shape)
            if valid_move(rotated_shape, shape_y, shape_x):
                shape = rotated_shape

        # Automatically move the Tetrimino down every second
        if time.time() - last_fall_time > 1:
            if valid_move(shape, shape_y + 1, shape_x):
                shape_y += 1
            else:
                place_tetrimino(shape, shape_y, shape_x)
                eliminate_lines()
                shape, shape_y, shape_x = new_tetrimino()
                if not valid_move(shape, shape_y, shape_x):
                    break  # Game over
            last_fall_time = time.time()

# Run the game
if __name__ == "__main__":
    curses.wrapper(main)

