import argparse
from lineConsole_int import lineConsoleGame
from chess_GUI import *
from board import Board

if __name__ == "__main__":
    B = Board()
    parser = argparse.ArgumentParser()
    parser.add_argument("-cl", "--commandlign", action="store_true")
    parser.add_argument("-i", "--interface", action="store_true")
    args = parser.parse_args()

    if args.commandlign:
        lineConsoleGame(B.get_filledboard())
    else:
        GUI().lancement(B.get_filledboard())
