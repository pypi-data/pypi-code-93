#!/usr/bin/python3

from tkinter import *
from netana import *

def main():
	root = Tk()
	root.title('NetAna')
	root.geometry('+100+200')
	app = NetAna(root)
	root.mainloop()
   
if __name__ == "__main__" :
	print("Starting Netana")
	main()
	print("Exiting Netana")
