from vinca.lib import ansi
from vinca.lib.terminal import COLUMNS
from vinca.lib.input import input

def edit(card, scrollback = True):
	front_path = (card.path / 'front')
	back_path  = (card.path / 'back')
	front = front_path.read_text()
	back  =  back_path.read_text()

	# TODO multiline input using Alt+Enter
	new_front = input(vi_mode = True, text = front, prompt = 'Q: ')
	front_path.write_text(new_front)
	
	new_back = input(vi_mode = True, text = back, prompt = 'A: ')
	back_path.write_text(new_back)

	if scrollback:
		ansi.up_line(2)

