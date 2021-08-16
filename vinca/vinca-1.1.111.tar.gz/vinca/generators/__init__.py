import importlib
import datetime, time
TODAY = datetime.date.today()
GENERATORS_DICT = {'m': 'media', 'v':'verses', '2': 'two_lines'}


def generate(generator, default_tags):
	start = time.time()
	m = importlib.import_module('.'+generator, package = 'vinca.generators')
	new_cards = m.generate()
	stop = time.time()
	elapsed = int(stop - start)
	
	for card in new_cards:
		# card.tags = card.tags + args.tags
		card.make_string()
		card.add_history(TODAY, elapsed, 'create')
		card.load_metadata()  # TODO why is this necessary?

	return new_cards
