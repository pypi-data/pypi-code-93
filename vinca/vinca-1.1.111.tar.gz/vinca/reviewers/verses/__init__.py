from vinca.lib.terminal import AlternateScreen
import readchar

def review(card):

	with AlternateScreen():

		lines = (card.path / 'lines').read_text().splitlines()
		print(lines.pop(0))  # print the first line
		for line in lines:
			readchar.readchar()  # press any key to continue
			# TODO abort
			print(line)
		print('\n(end)')

		# grade the card
		char = readchar.readchar()
	
	return char

def make_string(card):
	return (card.path / 'lines').read_text().replace('\n',' / ')
