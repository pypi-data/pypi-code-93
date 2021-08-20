# -*- coding: utf-8 -*-

import webbrowser, sys, pyperclip

def map_it():
    """ A function to open a map in browser from commandline or clipboard """
    if len(sys.argv) > 1:
        # Get the address from commandline if user types more information
        # after the name of the script
        address = ' '.join(sys.argv[1:])
    else:
        # Get the address from clip board
        address = pyperclip.paste()

    if webbrowser.open_new_tab("https://www.google.com/maps/place/" + address):
        print("You may now look at your map. Happy adventure!")
    else:
        print("\nSorry, we could not open your map. Look at your internet connection.\n")

def main():
    print("---Welcome to Map Address---")
    print("usage: \n-map_address [address].\n-copy adress from clipboard and run map_it")

    map_it()