import os
from tkinter.messagebox import showerror
from equations import Equations
from mkreport import MkReport


class AnalizeSpec():

	MashNodeError = "Mashs or Nodes must be defined"

	def __init__(self):
		pass

	def analize(self):   # Collect & Evaluate file spec data
		# Get number of Mashs/Nodes if not defined
		with open(self.FileName) as specfile:
			lines = specfile.readlines()
			for line in lines:
				exec(line.upper(),{},self.NetDict)
		try:
			if 'NODES' in self.NetDict:
				self.Nodes = self.NetDict['NODES']
				self.AnalType='Node'
			elif 'MASHS' in self.NetDict:
				self.Nodes = self.NetDict['MASHS']
				self.AnalType='Mash'
			else:
				raise MashNodeError

		except MashNodeError:
			showerror('Error','Mashs or Nodes must be defined')


		if self.Nodes < 2:
			showerror('Error', 'Enter Number of Mashs or Nodes.\nMust be 2 or higher.', 'Net Size', '2')

