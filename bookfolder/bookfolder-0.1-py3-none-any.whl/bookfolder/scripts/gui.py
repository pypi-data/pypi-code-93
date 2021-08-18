"""
Graphical user interface for bookfolder
"""

from bookfolder.gui.gui import GUI


def start():
    """
    Start the graphical user interface.
    """
    gui = GUI()
    gui.show()


if __name__ == "__main__":
    start()
