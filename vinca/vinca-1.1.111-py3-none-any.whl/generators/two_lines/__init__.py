from vinca.lib import classes
from vinca.lib import ansi

def generate(scrollback = True):
	new_card = classes.Card(create=True)
	new_card.editor, new_card.reviewer, new_card.scheduler = 'two_lines', 'two_lines', 'base'
	(new_card.path / 'front').touch()
	(new_card.path / 'back').touch()
	new_card.edit()
	if scrollback:
		ansi.up_line(2)
	return [new_card]
