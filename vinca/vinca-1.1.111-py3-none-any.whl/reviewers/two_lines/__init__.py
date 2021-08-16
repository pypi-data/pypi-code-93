import readchar 

from vinca.lib.terminal import AlternateScreen

def make_string(card):
	f = ' / '.join((card.path / 'front').read_text().splitlines())
	b = ' / '.join((card.path / 'back').read_text().splitlines())
	return f + ' | ' + b

def review(card):

	with AlternateScreen():
		# front text
		front = (card.path / 'front').read_text()
		print(front)
		#TODO reveal tags

		char = readchar.readchar() # press any key to flip the card
		print('\n\n')
		if char in ['x','a','q']: # immediate exit actions
			return char
		# back text
		back = '\n' + (card.path / 'back').read_text()
		print(back)
	
		return readchar.readchar()
