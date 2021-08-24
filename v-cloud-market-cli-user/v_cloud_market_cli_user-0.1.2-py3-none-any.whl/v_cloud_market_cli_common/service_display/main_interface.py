from rich.console import Console
from pyfiglet import Figlet

class MainInterface:

    def __init__(self):
        pass

    @staticmethod
    def display_title(console: Console, title: str):
        align = 'left'
        f = Figlet(font='big')
        console.clear()
        splitted = f.renderText(title).split("\n")
        length = len(splitted[0])
        titleBox = ''

        for i in range(len(splitted)-1):
            titleBox += '||    ' + splitted[i] + '    ||\n'

        console.print('=' * (length + 12), justify=align)
        console.print(titleBox + '=' * (length + 12), justify=align)

    @staticmethod
    def display_service_choice(console: Console, title: str, choices: [str], isSub=False):
        MainInterface.display_title(console, title)
        align = 'left'
        if isSub:
            console.print('[red][B][/] Press B to UpperLevel', justify=align)

        style = 'bold blue'
        index = 1
        for choice in choices:
            numPrefix = f'[{index}]' + ' ' * 4
            console.print(numPrefix+choice, style=style, justify=align)
            index += 1
        console.line(1)
        return console.input('[dark_sea_green4]Please Select Your Choice[/]: ')






