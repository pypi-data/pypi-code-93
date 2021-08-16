# coding=utf-8
import re
from collections import defaultdict


def match(abnex_str, to_match):
	regex = parse(abnex_str)
	return re.match(regex, to_match)


def holds(abnex_str, to_match):
	return bool(match(abnex_str, to_match))


def contains(abnex_str, to_match):
	return bool(all(abnex_str, to_match))


def all(abnex_str, to_match):
	regex = parse(abnex_str)
	return re.findall(regex, to_match)


def split(abnex_str, to_match, max_split=0):
	regex = parse(abnex_str)
	if max_split:
		return re.split(regex, to_match, max_split)
	return re.split(regex, to_match)


def replace(abnex_str, to_match, replacement, count=0):
	regex = parse(abnex_str)
	return re.sub(regex, replacement, to_match, count)


def replace_count(abnex_str, to_match, replacement):
	regex = parse(abnex_str)
	return re.subn(regex, replacement, to_match)


def first(abnex_str, to_match):
	regex = parse(abnex_str)
	return re.search(regex, to_match)


def last(abnex_str, to_match):
	regex = parse(abnex_str)
	return re.findall(regex, to_match)[-1]


def escape(txt):
	escaped = ''

	for char in txt:
		prefix = ''
		if char in ['.', '$', '*', '+', '?', '(', ')', '[', '{', '\\', '-']:
			prefix = '\\'
		escaped += prefix + char

	return escaped


def get_chars():
	return {
		'(': '{',
		')': '}',
		'{': '(',
		'}': ')',
		'd': '\\d',
		'*': '.',
		'w': '\\w',
		'_': '\\s',
		':': '\\b',
		'->': '^',
		'<-': '$',
		's>': '\\A',
		'<s': '\\Z',
		'w>': '\\<',
		'<w': '\\>',
		'!': '^',
		'0++': '*',
		'1++': '+',
		'0+': '?',
		'c': '\\c',
		'x': '\\x',
		'o': '\\o',
	}


def transpile(char, is_not):
	chars = get_chars()
	translation = defaultdict(lambda: char, chars)[char]
	return translation if not is_not else translation.upper()


def parse(expr):
	regex = ''
	tmp = ''

	is_exact = False
	is_skip = False
	is_not = False
	is_quantifier = False
	tmp_range = ''
	tmp_range_ends_next = False

	for index, char in enumerate(expr):
		if tmp_range_ends_next:
			tmp_range += char
			regex += tmp_range

			tmp_range_ends_next = False
			tmp_range = ''
			continue

		if tmp_range and char in ['-']:
			tmp_range += char
			tmp_range_ends_next = True
		elif is_quantifier:
			tmp += char
			try:
				check = expr[index + 1] != '+'
			except IndexError:
				check = True

			if check:
				regex += transpile(tmp, is_not)
				tmp = ''
				is_quantifier = False
		elif is_skip:
			is_skip = False
		elif is_exact:
			if char in ['"', "'"]:
				is_exact = False
				tmp = escape(tmp)
				regex += tmp
				tmp = ''
			else:
				tmp += char
		elif char not in [' ', '\n', '\t']:
			if char in ['"', "'"]:
				is_exact = True
			elif char == '!' and expr[index - 1] != '[':
				is_not = True
			elif char in ['0', '1'] and expr[index + 1] == '+':
				is_quantifier = True
				tmp = char
			elif char in ['a', '0']:
				tmp_range = char
			else:
				if index < len(expr) - 1:
					next_up = expr[index + 1]
					if char in ['-', 's', 'w'] and next_up == '>' or char == '<' and next_up in ['-', 's', 'w']:
						is_skip = True
						regex += transpile(char + next_up, is_not)
					else:
						regex += transpile(char, is_not)
				else:
					regex += transpile(char, is_not)

	return regex
