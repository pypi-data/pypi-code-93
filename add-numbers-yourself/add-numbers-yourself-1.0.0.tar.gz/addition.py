def addition():
	n = 1
	while n:
	    a,b = input('Enter 2 numbers:').split()
	    try:
		value1 = int(a)
		value2 = int(b)
		n = 0
	    except:
		raise ValueError(f'{a} and {b} are not numbers')
	sum = value1 + value2
	print('The sum of two numbers',a,'and',b,'is:',sum)
