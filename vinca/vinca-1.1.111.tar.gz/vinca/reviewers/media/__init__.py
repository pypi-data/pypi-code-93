# The default reviewer
# The parent module (reviewers/__init__.py) contatins some
# generic code used by all of the reviewers.
from vinca.lib import ansi
import readchar 

from vinca.lib.video import DisplayImage
from vinca.lib.audio import Recording
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
		tags_str = '    '.join(['['+t.replace('_',' ')+']' for t in card.tags])  # TODO show tags only if requested
		ansi.light()
		print(tags_str)
		ansi.reset()

		# front media
		with DisplayImage(card.path/'image_front'), Recording(card.path/'audio_front'):
			# card flip
			readchar.readchar() 

		back = '\n' + (card.path / 'back').read_text()
		print(back)

		with DisplayImage(card.path/'image_back'), Recording(card.path/'audio_back'):
			key = readchar.readchar()
	
	return key
