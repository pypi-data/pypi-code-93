# WhirlData 1.0.0.0.0.0.0.0000.00.0 this many zeros...

import ast
def read(data):
	contents = {}
	for line in data.split("\n"):
		if line == "":
			continue
		elif line.isspace():
			continue
		elif line[0] == "~":
			continue
		else:
			line = line[:-1]+"<<LINE-END>>"
			line.replace("\\::","|$?1?$|")
			line.replace("\\[","|$?2?$|")
			line.replace("\\]","|$?3?$|")
			contents[line[:line.find("::")]] = line[line.find("[")+len("["):line.find("<<LINE-END>>")]
			TEMP = contents[line[:line.find("::")]].split("::")
			contents[line[:line.find("::")]] = []
			for i in TEMP:
				i = i.replace("|$?1?$|","::")
				i = i.replace("|$?2?$|","[")
				i = i.replace("|$?3?$|","]")
				t1 = ast.literal_eval(i)
				contents[line[:line.find("::")]].append(t1)
			continue
	return contents