#TODO <ESC> and <UP>
#TODO d2w not just 2dw
from vinca.lib import ansi
from vinca.lib.terminal import COLUMNS
from vinca.lib import readchar
from vinca.lib.readchar import ESC, BACK
import string
import re
NUMBERS = string.digits
OPERATORS = ['d','c','y','~','z']
MOTIONS = ['w','e','b','f','t','F','T',';',',','h','l','(',')','0','$','_','^']  # TODO capital letters
EXCLUSIVE_MOTIONS = ['w','l']
ACTIONS = ['s','S','r','u','.','x','X','D','C','p','P','Y','a','i','A','I','j','k']

BOW = re.compile(	# BEGINNING OF WORD
	'((?<=\s)|^)'	# pattern is preceded by whitespace or the beginning of the line
	'\w')		# the beginning of the word is any alphanumeric character.
EOW = re.compile(	# END OF WORD
	'\w'		# any alphanumeric character
	'(\s|$)')	# succeeded by whitespace or the end of the line.
EOS = re.compile('[.!?]')  # EDGE OF SENTENCE

def idx(pattern, text, pos, direction = 'forwards'):
	'''Return the index of a match of the pattern in the text.
	direction=1 means we are looking for the first match *after* pos
	direction=-1 means we are looking for the first match *before* pos
	If we find no match we return pos.'''
	indices = [m.start() for m in re.finditer(pattern, text)]  # list of matching indices
	if direction == 'forwards':
		return min([i for i in indices if i > pos], default = pos)
	elif direction == 'backwards':
		return max([i for i in indices if i < pos], default = pos)

def vi_operator(op, text, start, end):
	mode = 'normal'
	if op in ('d','c'):
		text = text[:start] + text[end+1:]  # exception for exclusive dw and dl
		if op == 'c':
			mode =='insert'
	if op == 'y':
		raise NotImplementedError
	if op == '~':
		text = text[:start] + text[start:end].upper() + text[end+1:]
	if op == 'z':
		text = text[:start] + '_'*(end - start) + text[end+1:]
	return mode, text
		
	
def vi_motion(m, text, pos):
	# TODO refactor using the match / case syntax
	N = len(text)
	if m == 'w':
		pos = idx(BOW, text, pos)
	if m == 'e':
		pos = idx(EOW, text, pos)
	if m == 'b':
		pos = idx(BOW, text, pos, direction = 'backwards')
	if m == 'f':
		search_char = readchar.readchar()
		pat = re.compile(search_char)
		pos = idx(pat, text, pos)
	if m == 'F':
		search_char = readchar.readchar()
		pat = re.compile(search_char)
		pos = idx(pat, text, pos, direction = 'backwards')
	if m == 't':
		search_char = readchar.readchar()
		pat = re.compile(f'.(?={search_char})')
		pos = idx(pat, text, pos)
	if m == 'T':
		search_char = readchar.readchar()
		pat = re.compile(f'(?<={search_char}).')
		pos = idx(pat, text, pos, direction = 'backwards')
	if m in (';',','):
		raise NotImplementedError
	if m == 'h':
		pos -= 1*(pos > 0)
	if m == 'l':
		pos += 1*(pos < N)
	if m == ')':
		pos = idx(EOS, text, pos)
	if m == '(':
		pos = idx(EOS, text, pos, direction = 'backwards')
	if m in ('0','^','_'):
		pos = 0
	if m == '$':
		pos = N
	return pos
def vi_action(a, text, pos) -> (str, str, int): 
	N = len(text)
	mode = 'normal'
	if a in ('s','S','C'):
		if a == 's':
			text = text[:pos] + text[pos+1]
			mode = 'insert'
		if a == 'S':
			text = ''
			pos = 0
			mode = 'insert'
		if a == 'C':
			text = text[:pos]
			mode = 'insert'
	if a in ('u','.'):
		raise NotImplementedError
	if a in ('x','X','D'):
		if a == 'x':
			text = text[:pos] + text[pos+1:]
		if a == 'X':
			text = text[:pos-1] + text[pos:]
			pos -= 1
		if a == 'D':
			text = text[:pos]
	if a in ('p','P','Y'):
		raise NotImplementedError
	if a in ('a','A','i','I'):
		mode = 'insert'
		if a == 'I':
			pos = 0
		if a == 'a':
			pos += 1
		if a == 'A':
			pos = len(text)
	if a in ('j','k'):
		raise NotImplementedError
	pos = max(0, pos)
	pos = min(N, pos)
	return mode, text, pos
	

def input(vi_mode = False, starting_mode = 'insert', multiline = False, prompt = '', text = '', completions = None):
	normal_prompt = f'{ansi.codes["red"]}[N]{ansi.codes["reset"]} '
	insert_prompt = f'{ansi.codes["green"]}[I]{ansi.codes["reset"]} '
	if not completions:
		completions = []
	mode = starting_mode
	multiplier = 1
	pos = len(text)
	ansi.hide_cursor()
	while True:
		prefix = (normal_prompt if mode == 'normal' else insert_prompt) * vi_mode
		display_text = text[:pos] + ansi.codes['reverse'] + (text[pos] if pos<len(text) else ' ') + ansi.codes['reset'] + text[pos+1:] + ' '
		w = (len(display_text) // COLUMNS + 1) * COLUMNS
		print('\r', f'{prefix+display_text:<{w}}', end='', sep='', flush=True)

		c = readchar.readchar()

		if mode == 'insert':
			if c in ('\n','\r'):
				break
			elif c == ESC:
				mode = 'normal'
			elif c in ('\b',BACK):
				text = text[:pos - 1] + text[pos:]
				pos -= 1
				pos = max(pos, 0)
			else:
				assert c in string.printable
				text = text[:pos] + c + text[pos:]
				pos += 1
		elif mode == 'normal':
			if c in ('\n','\r','q', ESC):
				break

			# numbers are built up to make a multiplier
			if c in NUMBERS:
				multiplier *= 10
				multiplier += int(c)
			multiplier = multiplier if multiplier else 1

			# operations motions and actions
			if c in OPERATORS:
				m = readchar.readchar()
				# TODO allow for d2w not just 2dw
				assert m in MOTIONS
				while multiplier:
					multiplier -= 1
					start = pos
					end = vi_motion(m, text, pos) - (m in EXCLUSIVE_MOTIONS)
					mode, text = vi_operator(c, text, start, end)
			if c in MOTIONS:
				while multiplier:
					multiplier -= 1
					pos = vi_motion(c, text, pos)
			if c in ACTIONS:
				while multiplier:
					multiplier -= 1
					mode, text, pos = vi_action(c, text, pos)
	ansi.show_cursor()
	return text
