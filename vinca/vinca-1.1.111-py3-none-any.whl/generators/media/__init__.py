from vinca.lib import classes

def generate():
	new_card = classes.Card(create=True)
	new_card.editor, new_card.reviewer, new_card.scheduler = 'media', 'media', 'base'
	for side in ('front', 'back'):
		(new_card.path / side).touch()
	new_card.edit()  
	return [new_card]
