from pynput.keyboard import Key, Listener
from SimpleR0cKyMenu.exceptions import IncorrectArguments
from os import name, system

class Menu:
    def __init__(self, title: str, fcolor: tuple = (0, 0, 0), bcolor: tuple = (0, 0, 0)):
        """
        Menu class allowes to create menu for your application with specified elements.
        NOTE: Colors not added yet.
        """
        self.title = title
        self.fcolor = fcolor
        self.bcolor = bcolor
        self.buttons = []
        self.KEYS = {
            "UP": '\'w\'',
            "DOWN": '\'s\'',
            "ENTER": Key.enter
            }
        self.option = 0
        if name == "nt":
            self.clear_comm = 'cls'
        else:
            self.clear_comm = 'clear'

        self.check_type()
    
    
    def check_type(self):
        """Checks whether the arguments have correct format."""
        if type(self.title) != type("OK"):
            raise IncorrectArguments("Title is not a string!")
        if type(self.fcolor) != type((1, 1)):
            raise IncorrectArguments("fColor is not a tuple!")
        if type(self.bcolor) != type((1, 1)):
            raise IncorrectArguments("bColor is not a tuple!")
    
    def add_button(self, name: str):
        """Adds a new button."""
        self.buttons.append(name)

    def key_handler(self, key) -> str:
        """KeyHandler"""
        if str(key) == self.KEYS["UP"]:
            self.option -= 1
            if self.option < 0:
                self.option = len(self.buttons)-1
            self.draw_menu()
        if str(key) == self.KEYS["DOWN"]:
            self.option += 1
            if self.option > len(self.buttons)-1:
                self.option = 0
            self.draw_menu()
        if key == self.KEYS["ENTER"]:
            input()
            return False
        if key == Key.esc:
            exit(0)
    
    def draw_menu(self) -> str:
        """Outputs menu"""
        system(self.clear_comm)
        print(self.title)
        print("="*len(self.title))
        for button in range(len(self.buttons)):
            if button == self.option:
                print("["+self.buttons[button]+"]")
                continue
            print(self.buttons[button])
            

    def show(self) -> str:
        """Launch Whole Menu Infrastructure."""
        print(self.title)
        print("="*len(self.title))
        for button in range(len(self.buttons)):
            if button == self.option:
                print("["+self.buttons[button]+"]")
                continue
            print(self.buttons[button])
        with Listener(on_press = self.key_handler) as listener:
            listener.join()
    
    def result(self) -> int:
        """Returns a result, chosen button"""
        return int(self.option)