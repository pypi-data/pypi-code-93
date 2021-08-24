from rich.console import Console
from rich.panel import Panel

def get_table_choice(console: Console, w: int, has_next: bool, extra={}) -> str:
    options = ['[P]rev', '[E]xit']
    basic_choice = ['p', 'e']
    if has_next:
        options.append('[N]ext')
    count = len(options)
    space_w = int((w - (count-1) * 4 - 14) / (count - 1))
    sep = ' ' * space_w
    msg = '[bright_green]' + sep.join(options)
    if extra:
        basic_choice.extend(extra.keys())
        msg += '\n'
        for k in extra:
            msg += extra[k] + sep
        msg = msg[:-space_w]
        width = len(msg.split('\n')[-1]) - len(msg.split('\n')[0]) - 4
        msg = msg[0:21] + width * 2 * ' ' + msg[21:]
    p = Panel.fit(msg)
    console.print(p, justify='center')

    while True:
        choice = console.input('[green]navigate to: ')
        if choice.lower() in basic_choice:
            return choice.lower()
        elif has_next and choice.lower() in ['n']:
            return choice.lower()
