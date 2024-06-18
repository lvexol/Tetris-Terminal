import curses
import time

# Board size
BOARD_WIDTH = 10
BOARD_HEIGHT = 20

def main(stdscr):
    stdscr.clear()
    while i<20:
        while j<10:
            stdscr.addstr(j,i,"[ ]")
        stdscr.addstr("\n")
    stdscr.refresh()
    stdscr.getch()

curses.wrapper(main)
