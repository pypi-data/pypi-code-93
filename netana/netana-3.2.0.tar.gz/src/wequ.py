#! /usr/bin/env python3

NBCOL = 3  # number of columns in 'net' data file

def wequ(fn):
	""" This module will read a net file "fn" containing
	components and node connection specifications. It will
	output the matrix node equations. Format of the 'net'
	data file example of one line:
		c1+y1+A*ya,3,4   equation, node 3, mutual (adjacent node 4
		A zero in the third column refers to common or ground.
	input: fn = filename of net file (connection list)
	output: square matrix (list of lists) of size equal number of
	voltage nodes."""

	with open(fn, 'r') as equfile:
		nbnodes = 0
		nodedict = {}
		mdict ={}
		for line in equfile:
			if line == '\n' or line[0] == "#" or line == "" : continue
			line = line[:line.find("#")]	# remove any eol comments
			line = line.strip()
			line = line.upper()
			print( "line = ", line)
			# comp equ,common node, mutual node
			c,n,m = line.split(',',NBCOL)

			# Count numer of nodes
			i = int(n)
			if i > nbnodes : nbnodes = i

			# Build the node dict for common node components
			if not int(m): # only collect common node data
				if n in nodedict :  # old node
					nodedict[n] += ' + ' + c
				else:  # new node
					nodedict[n] = c

			# Build the mdict for mutual node components
			if int(m)  : # only collect mutual node data
				if n in mdict :
					nn = len(mdict[n])-1
					if mdict[n][nn][1] == m :  # same mutual node
						mdict[n][nn][0] += '+' + c
					else:
						mdict[n].append([c,m])
				else: # new common node
					mdict[n] = [[c,m]]

	# Start by building ascii zero filled matrix
	mat = [['0']*nbnodes]*nbnodes

	# Fill "mat" with the common node terms
	for key in nodedict:
		i = int(key)-1
		mat[i][i] = nodedict[key]

	# Fill "mat" with the mutual node terms
	for key in mdict:
		lst = mdict[key]
		for row in lst:
			mr = int(key)-1
			mc = int(row[1])-1
			mat[mr][mc] = '-(' + row[0] + ')'


	return mat

if __name__ == "__main__":

	mat = wequ("examples/BainterFilter.net")
	print("mat = ", mat)




