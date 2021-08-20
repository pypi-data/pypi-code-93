#!/usr/bin/python3

class InvalidConfig(Exception):
	def __init__(self):
		self.message = "INVALID CONFIG DATA"
		super().__init__(self.message)