import random
import sys
import argparse
from time import time as now

from .alphabets import GREEK
from .names import NAMES
from .adjectives import ADJECTIVES


def get_full_name(sep='_'):
    r = random.SystemRandom()
    name = '%s%s%s' % (r.choice(ADJECTIVES), sep, r.choice(NAMES))
    return name

def get_greek_name(sep='_'):
    r = random.SystemRandom()
    name = '%s%s%s' % (r.choice(GREEK), sep, number_suffix(''))
    return name

def number_suffix(sep="_"):
	return sep + "%.8d" % random.randint(0,1e8)

def ts_suffix(sep="_"):
	return sep + str(now()).replace(".", "")

def empty_suffix(sep="_"):
	return ""

def generate_name(sep="_", lang="english", suffix=None):

	name_gen_func = (get_full_name if lang == "english" else (get_greek_name if lang == "greek" else get_full_name))
	suffix_func = { "ts": ts_suffix, "num": number_suffix}.get(suffix) or empty_suffix

	return name_gen_func(sep) + suffix_func(sep)
	

def __argparser():
	import argparse

	parser = argparse.ArgumentParser(prog="namegenerator", description='Random name generator.')
	parser.add_argument("-n", metavar="NUMBER_OF_NAMES", required=False, default=1, type=int)
	parser.add_argument("--sep", metavar="NAME_SEPARATOR", required=False, default="_", type=str)
	group = parser.add_mutually_exclusive_group()
	group.add_argument("--english", action="store_true")
	group.add_argument("--greek", action="store_true")
	parser.add_argument("--suffix", choices=["ts", "num"])

	return vars(parser.parse_args())


if __name__ == '__main__':
	args = __argparser()

	name_gen_func = (get_full_name if args["english"] else (get_greek_name if args["greek"] else get_full_name))
	suffix_func = { "ts": ts_suffix, "num": number_suffix}.get(args["suffix"]) or empty_suffix

	for n in range(args["n"]):
		sys.stdout.write(name_gen_func(args["sep"]) + suffix_func(args["sep"]))
		sys.stdout.write("\n")
