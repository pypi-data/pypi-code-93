# linear editor for lyrics, poetry, oratory, etc.
import subprocess
from pathlib import Path
import shutil

vinca_path = Path(__file__).parent.parent.parent # I counted right
tags_path = vinca_path / 'data' / 'tags.txt'

path = Path(__file__).parent
vimrc_path = path / 'vimrc'

def edit(card):
	# we are going to run vim...
	vim_cmd = ['vim']
	vim_cmd += [card.path/'lines']
	# specify custom vimrc
	vim_cmd += ['-Nu', vimrc_path]
	# launch
	subprocess.run(vim_cmd)
