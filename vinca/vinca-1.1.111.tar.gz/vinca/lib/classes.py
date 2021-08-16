import subprocess
import json
import datetime
TODAY = datetime.date.today()
from pathlib import Path

from vinca import reviewers, editors, schedulers 

vinca_path = Path(__file__).parent.parent  # /path/to/vinca
cards_path = Path.home() / 'cards'

class Card:
	# Card class can load without 
	default_metadata = {'editor': 'base', 'reviewer':'base', 'scheduler':'base',
			    'tags': [], 'history': [], 'deleted': False,
			    'due_date': TODAY, 'siblings': [], 'string': ''}

	def __init__(self, id=None, create=False):
		assert (id is not None) ^ create
		if not create:  # load an existing card
			assert type(id) is int
			self.id = id
			self.metadata_is_loaded = False
		elif create: # create a new card
			old_cids = [int(x.name) for x in cards_path.iterdir()]
			self.id = max(old_cids) + 1 if old_cids else 100 
			self.path.mkdir()
			self.metadata = Card.default_metadata
			self.metadata_is_loaded = True
			self.save_metadata()

	@property
	def path(self):
		return cards_path/str(self.id)
		# assert p.exists(), f'Bad Card ID {self.id}; DOES NOT EXIST.'

	@property
	def metadata_path(self):
		return self.path / 'metadata.json'

	def load_metadata(self):
		self.metadata = json.load(self.metadata_path.open())
		# dates must be serialized into strings for json
		# I unpack them here
		str_to_date = lambda date: datetime.datetime.strptime(date, '%Y-%m-%d').date()
		self.metadata['history'] = [[str_to_date(date), grade,
					    time] for date, grade, time in self.metadata['history']]
		self.metadata['due_date'] = str_to_date(self.metadata['due_date'])
		self.metadata_is_loaded = True

	def save_metadata(self):
		json.dump(self.metadata, self.metadata_path.open('w'), default=str, indent=2)

	for m in default_metadata.keys():
		# create getter and setter methods for everything in the metadata dictionary
		exec(f'''
@property
def {m}(self):
	if not self.metadata_is_loaded:
		self.load_metadata()
	return self.metadata["{m}"]''')
		exec(f'''
@{m}.setter
def {m}(self, new_val):
	if not self.metadata_is_loaded:
		self.load_metadata()
	self.metadata["{m}"] = new_val
	self.save_metadata()''')	

	def __str__(self):
		return self.string

	def add_history(self, date, time, grade):
		self.history = self.history + [[date, time, grade]]
	def undo_history(self):
		self.history = self.history[:-1]
			
	def review(self): reviewers.review(self)
	def make_string(self): self.string = reviewers.make_string(self)
	def edit(self):
		editors.edit(self) 
		self.make_string()
	def edit_metadata(self):
		subprocess.run(['vim',self.path/'metadata.json'])
		self.load_metadata()
		self.make_string()
	def schedule(self): schedulers.schedule(self) 

	@property
	def create_date(self): return self.history[0][0] if self.history else None
	@property
	def seen_date(self): return self.history[-1][0] if self.history else None
	@property
	def last_grade(self): return self.history[-1][2] if self.history else None
	@property
	def last_interval(self): return self.history[-1][0] - self.history[-2][0] if len(self.history)>1 else None

	@property
	def new(self): return self.last_grade == 'create'

	def due_as_of(self, date):
		return self.due_date <= date

