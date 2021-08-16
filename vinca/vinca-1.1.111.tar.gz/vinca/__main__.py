import sys
import inspect
import readchar
import readline as rl
import argparse
import datetime
from pathlib import Path
from shutil import copytree, rmtree

from vinca.lib.classes import Card
from vinca.lib import ansi
from vinca.lib import filter
from vinca.generators import generate, GENERATORS_DICT

# TODO: media cards without vim
# TODO: better alternative for readline.
##	tab completion
##	vim style navigation
##	up arrows
##	shortcut for cloze?
# TODO: convert maps/anatomy to ansi/ascii outlines

TODAY = datetime.date.today()
DAY = datetime.timedelta(days=1)

PIPE_IN = not sys.stdin.isatty()
PIPE_OUT = not sys.stdout.isatty()
QUIT_KEYS = ['q', readchar.key.ESC, '\n', '\r',' ']

vinca_path = Path(__file__).parent 
cards_path = Path.home() / 'cards'
ALL_CARDS = [Card(int(id.name)) for id in cards_path.iterdir()] # TODO: load cards otf
ALL_TAGS = [tag for card in ALL_CARDS for tag in card.tags] # TODO: cache
VERSION = 115

# ARGUMENT PARSING
parser = argparse.ArgumentParser(usage=argparse.SUPPRESS, epilog='Use -h to see help for any command. Visit the manual for usage examples.')
subparsers = parser.add_subparsers(metavar='')
def card_type(arg):
	id = int(arg.split()[0])  # grab the first field of the argument
	return Card(id)
def date_type(s):
	if s[s[0] in ['+','-']:].isdigit():
		return TODAY + int(s) * DAY
	try:
		return datetime.datetime.strptime(s, '%Y-%m-%d').date()
	except ValueError:
		raise argparse.ArgumentTypeError(f'''\n\n
			Invalid Date: {s}. Valid dates are:
			1) -7		(one week ago)
			2) 2021-06-03	(June 3rd)''')
def arg(*names_or_flags, **kwargs):
	return names_or_flags, kwargs
CARDS = arg('cards',nargs='*',type=card_type, default=ALL_CARDS)
CARD = arg('card',type=card_type)
OPTIONAL_CARDS = arg('--cards',nargs='*',type=card_type,default=ALL_CARDS)
OPTIONAL_CARD = arg('card', nargs='?', type=card_type)
OPTIONAL_CARDS_DEFAULT_NONE = arg('--cards',nargs='*',type=card_type,default=[])
def subcommand(*subparser_args, parent=subparsers, alias='', name=None):
	def decorator(func, alias=alias, name=name):
		name = name if name else func.__name__
		description = func.__doc__
		aliases = [alias] if alias else []
		parser = parent.add_parser(name, help='', description=description, aliases=aliases,
		                           usage=argparse.SUPPRESS)
		for args, kwargs in subparser_args:
			parser.add_argument(*args, **kwargs)
		parser.set_defaults(func=func)
		return func
	return decorator

@subcommand(arg('-t','--default_tags', nargs='+', default=[]), alias='a')
def add(): 
	'''Add several cards and browse them.'''
	ansi.hide_cursor()
	print(*[f'{key}\t{generator}' for key, generator in GENERATORS_DICT.items()],sep='\n')
	k = readchar.readchar()
	if k not in GENERATORS_DICT: return
	cards = generate(generator = GENERATORS_DICT[k], scrollback = True)
	ansi.up_line(len(GENERATORS_DICT) + 2)
	ansi.clear_to_end()
	browse(card, cards)

@subcommand(OPTIONAL_CARD, OPTIONAL_CARDS, alias='s')
def statistics(card, cards, scrollback = False):
	'''Simple summary statistics. Use `S` for more advanced statistics.'''
	if card:
		print(f'\nCard #{card.id}')
		print(str(card))
		print(f'Tags: {" ".join(card.tags)}')
		print(f'Due: {card.due_date}')
		print('Date\t\tTime\tGrade')
		print(*[f'{date}\t{time}\t{grade}' for date, time, grade in card.history],sep='\n',end='')
		lines = 5+len(card.history)
	elif cards:
		due_cards = filter.filter(cards, due_only=True)
		new_cards = filter.filter(cards, new_only=True)
		print('Total', len(cards), sep='\t')
		print('Due', len(due_cards), sep='\t')
		print('New', len(new_cards), sep='\t')
		lines = 3
	if scrollback:
		ansi.up_line(lines)
		ansi.hide_cursor()

@subcommand(OPTIONAL_CARD, OPTIONAL_CARDS, alias='S')
def advanced_statistics(card, cards):
	''' Advanced statistics for a card or collection of cards. '''
	if card:
		raise NotImplementedError
	elif cards:
		raise NotImplementedError

@subcommand(CARD,alias='e')
def edit(card):
	''' edit a single card '''
	card.edit()

@subcommand(CARD,alias='E')
def edit_metadata(card):
	''' edit the metadata of a card '''
	card.edit_metadata()

@subcommand(OPTIONAL_CARD, OPTIONAL_CARDS_DEFAULT_NONE, alias='x')
def delete(card, cards):
	''' Delete (or undelete) a card. These cards will continue to be stored. Use purge to permanently delete these cards.'''
	if card:
		card.deleted = not card.deleted
	elif cards:
		for card in cards:
			card.deleted = not card.deleted

@subcommand(CARDS, alias='r')
def review(card, cards):
	''' Review a card or collection of cards. Grading is as follows:
	1 hard
	2 again
	3 good
	4 easy. '''
	if card:
		card.review()
		card.schedule()
	elif cards:
		cards = filter.filter(cards, due_only = True)
		if not cards:
			print('No cards due.')
			return
		browse(None, cards, reviewing = True)

@subcommand(arg('tag'), OPTIONAL_CARD, OPTIONAL_CARDS_DEFAULT_NONE)
def add_tag(card, cards, tag):
	''' Add a single tag to a collection of cards. '''
	for card in [card] if card else cards:
		card.tags += [tag]

@subcommand(arg('tag'), OPTIONAL_CARD, OPTIONAL_CARDS_DEFAULT_NONE)
def remove_tag(card, cards, tag):
	''' Remove a single tag from a collection of cards. '''
	for card in [card] if card else cards:
		if tag in card.tags:
			card.tags.remove(tag)
		# TODO do this with set removal
		card.save_metadata()

@subcommand(OPTIONAL_CARD, OPTIONAL_CARDS_DEFAULT_NONE, alias='t')
def edit_tags(card, cards, scrollback = False):
	# TODO rewrite completion
	def complete(text, state):
		for tag in ALL_TAGS:
			if tag.startswith(text):
				if not state:
					return tag
				else:
					state -= 1
	rl.parse_and_bind('tab: complete')
	rl.set_completer(complete)

	if card:
		pass #TODO lineedit tags with tab complete
		tags = ' '.join(card.tags)
		rl.set_startup_hook(lambda: rl.insert_text(tags))
		card.tags = input('tags: ').split()
		lines = 1
		rl.set_startup_hook()
	elif cards:
		tags_add = input('tags to add: ').split()
		tags_remove = input('tags to remove: ').split()
		lines = 2
		for tag in tags_add:
			add_tag(card = card, cards = cards, tag = tag)
		for tag in tags_remove:
			remove_tag(cards = cards, tag = tag)
	
	rl.set_completer()

	if scrollback:
		ansi.up_line(lines)


CMD_DICT = {'r': review, 'R': review,
	    's': statistics, 'S': advanced_statistics,
	    'x': delete, 'X': delete,
	    'e': edit, 'E': edit_metadata,
	    't': edit_tags, 'T': edit_tags}
@subcommand(arg('--cards',nargs='*',type=card_type,default=filter.filter(ALL_CARDS)), arg('-t','--default_tags', nargs='+', default=[]), alias='b')
def browse(card, cards, reviewing = False):
	''' Use J and K to move up and down. In general a lowercase letter will act on the selected card while a capital letter will act upon all cards. Use the following hotkeys in browse mode: r, x, s, e, t'''
	if not cards:
		print('no cards')
		return
	N = len(cards)
	FRAME_WIDTH = 10  # TODO better width?
	STATUS_BAR = N > FRAME_WIDTH
	VISIBLE_LINES = min(N, FRAME_WIDTH) + STATUS_BAR
	# TODO max frame of ten cards
	sel = 0

	def draw_browser(frame):
		ansi.hide_cursor()
		ansi.line_wrap_off()

		if STATUS_BAR:
			ansi.light()
			print(f'{sel+1} of {len(cards)}')
			ansi.reset()
		for i, card in enumerate(cards[frame:frame+FRAME_WIDTH], start=frame):
			if card.due_as_of(TODAY):
				ansi.bold()
				ansi.blue()
			if card.deleted:
				ansi.crossout()
				ansi.red()
			if i==sel:
				ansi.highlight()
			print(card)
			ansi.reset()
		ansi.line_wrap_on()
	def clear_browser(frame):
		ansi.up_line(VISIBLE_LINES)
		ansi.clear_to_end()
	def quit():
		clear_browser(frame)
		ansi.show_cursor()
		exit()
	def redraw_browser(frame):
		clear_browser(frame)
		draw_browser(frame)
		
	frame = 0
	draw_browser(0)
	while True:

		k = 'R' if reviewing else readchar.readkey()

		sel += (k=='j' or k==readchar.key.DOWN) and sel < len(cards)-1
		sel -= (k=='k' or k==readchar.key.UP) and sel > 0


		if k in QUIT_KEYS:
				quit()
		if k in CMD_DICT:
			ansi.show_cursor()
			card = cards[sel] if k in ('x','s','r','R','e','E', 't') else None
			if k == 'e':
				edit(card)
			else:
				CMD_DICT[k](card, cards)
			ansi.hide_cursor()
			reviewing = (k == 'R' and cards[sel].last_grade != 'exit')
			if reviewing and sel == N - 1:
				quit()
			elif reviewing and sel < N - 1:
				sel += 1 
		if k in GENERATORS_DICT:
			ansi.show_cursor()
			new_cards = generate(generator = GENERATORS_DICT[k])
			cards[sel:sel] = new_cards
			N = len(cards)
			STATUS_BAR = N > FRAME_WIDTH
			_VISIBLE_LINES = min(N, FRAME_WIDTH) + STATUS_BAR
			new_lines = _VISIBLE_LINES - VISIBLE_LINES 
			VISIBLE_LINES = _VISIBLE_LINES
			ansi.down_line(new_lines)
			ansi.hide_cursor()

		frame += (frame + FRAME_WIDTH == sel)  # scroll down if we are off the screen
		frame -= (frame - 1 == sel) # scroll up if we are off the screen
		if k not in ('s','S'):
			redraw_browser(frame)
			

@subcommand(arg('pattern',nargs='?',default=''),
	arg('-v','--invert',action='store_true'),
	arg('-i','--id_only',action='store_true'),
	arg('--cards',nargs='*',type=card_type, default=ALL_CARDS),
	arg('--tags_include',nargs='*', metavar='TAGS', default=[]),
	arg('--tags_exclude',nargs='*', metavar='TAGS', default=[]),
	arg('--create_date_min',type=date_type, metavar='DATE'),
	arg('--create_date_max',type=date_type, metavar='DATE'),
	arg('--seen_date_min',type=date_type, metavar='DATE'),
	arg('--seen_date_max',type=date_type, metavar='DATE'),
	arg('--due_date_min',type=date_type, metavar='DATE'),
	arg('--due_date_max',type=date_type, metavar='DATE'),
	arg('--due_only',action='store_true'),
	arg('--editor', type=str),
	arg('--reviewer', type=str),
	arg('--scheduler', type=str),
	arg('--deleted_only',action='store_true'),
	arg('--new_only',action='store_true'),
	alias='f', name='filter')
def display_filter(pattern, invert, id_only, cards,
		   tags_include, tags_exclude, create_date_min, create_date_max,
		   seen_date_min, seen_date_max, due_date_min, due_date_max,
		   due_only, deleted_only, new_only,
		   editor, reviewer, scheduler):
	''' Filter a set of cards using a variety of parameters.
	It is often helpful to pipe this command to another one.'''

	options = locals()

	# get a list of the filter parameters
	parameters = inspect.signature(filter.filter).parameters
	# pass the list of options this function received on to the filtering function
	matches = filter.filter(**{p : options[p] for p in parameters})
	
	if PIPE_OUT:
		print(*[card.id for card in matches], sep='\n', end='')
		exit()
	if len(matches) > 10:
		ansi.light()
		print(f'10 of {len(matches)}')
		ansi.reset()
	ansi.line_wrap_off()
	for card in matches[:10]:
		if card.due_as_of(TODAY):
			ansi.bold(); ansi.blue()
		if card.deleted:
			ansi.crossout(); ansi.red()
		print(card.id, card, sep='\t')
		ansi.reset()
	
@subcommand()
def purge():
	''' Permanently delete all cards marked for deletion. '''
	deleted_cards = filter.filter(ALL_CARDS, deleted_only=True)
	if not deleted_cards:
		print('no cards are marked for deletion.')
		return
	print(f'delete {len(deleted_cards)} cards? (y/n)')
	if (confirmation := readchar.readchar()) == 'y':
		for card in deleted_cards:
			rmtree(card.path)

@subcommand(arg('backup_path',type=Path), CARDS, name='export')
def exp(cards, backup_path):
	''' Save the collection of cards to a new folder. '''
	for card in cards:
		copytree(card.path, backup_path / str(card.id))

@subcommand(arg('import_path',type=Path), arg('-o','--overwrite', action='store_true'), name='import')
def imp(import_path, overwrite = False):
	''' Import a collection of cards. Specify the folder in which these cards are located. '''
	if overwrite:
		rmtree(cards_path)
		copytree(import_path, cards_path)
		return
	old_ids = [card.id for card in ALL_CARDS]
	for new_id,card_path in enumerate(import_path.iterdir(), max(old_ids, default=1) + 1):
		copytree(card_path, cards_path / str(new_id))



for alias, generator in GENERATORS_DICT.items():
	p = subparsers.add_parser(generator, aliases=[alias], help='')
	p.add_argument('-t','--default_tags',nargs='*',default=[])
	p.set_defaults(func = generate, generator = generator)

# parse the command line arguments
parser.add_argument('-V','--version',action='version',version=str(VERSION))
parser.set_defaults(cards = [], func = lambda: parser.print_help(), card = None)
# simplifiy the help message
parser._action_groups[0].title = 'commands'
parser._action_groups.pop()
args = parser.parse_args()
# accept a file of newline separated card ids
if PIPE_IN:
	ids = [int(line.strip().split()[0]) for line in sys.stdin]
	args.cards = [Card(id) for id in ids]
	sys.stdin = open('/dev/tty')  

# from args pass to the function the parameters which it requires.
# get filter parameters as a list of strings
parameters = inspect.signature(args.func).parameters.values()
specified_parameters = [p.name for p in parameters if hasattr(args, p.name)]
required_parameters = [p.name for p in parameters if p.default is inspect._empty]
assert all(p in specified_parameters for p in required_parameters)
args.func(**{p : getattr(args, p) for p in specified_parameters})
