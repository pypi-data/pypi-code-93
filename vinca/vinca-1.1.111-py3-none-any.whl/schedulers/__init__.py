import importlib

def schedule(card):

	if card.last_grade == 'delete':
		card.deleted = True

	# import the specific scheduler module
	m = importlib.import_module('.' + card.scheduler, package = 'vinca.schedulers')
	# invoke the specific scheduler
	m.schedule(card)
