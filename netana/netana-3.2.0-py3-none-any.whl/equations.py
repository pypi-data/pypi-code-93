from griddialog import *
from wequ import wequ
import pickle
from tkinter.messagebox import showerror

class Equations():

	def cleanup(self,dig):
		if dig.status == "Save":
			self.Mat = dig.get()
			self.SaveEquations()
		if dig.top:	dig.top.destroy()

	def SaveEquations(self):
		# Save Mat Equations to file
		if len(self.Mat) > 1:	# if it has been defined
			pickle.dump(self.Mat, open(self.EquFileName ,'wb'))

	def RestoreEquations(self):
		if os.path.exists(self.EquFileName):
			self.Mat=pickle.load(open(self.EquFileName,'rb'))


	def getequ(self):
		# Build Grid Table and get Equations
		if os.path.exists(self.EquFileName):
			self.RestoreEquations()
			dig = GridDialog(self.parent,self.Mat,collab=self.AnalType)
			self.cleanup(dig)
		elif os.path.exists(self.NetFileName):
			self.Mat = wequ(self.NetFileName)
			dig = GridDialog(self.parent,self.Mat,collab=self.AnalType)
			self.cleanup(dig)
		else:
			dig = GridDialog(self.parent,size=self.Nodes,collab=self.AnalType)
			self.cleanup(dig)



if __name__ == "__main__":

	import os,pickle
	from tkinter import *

	root = Tk()

	os.chdir('/home/jim/test')


	eq = Equations(root)
	eq.Mat = [[1,2,3,4],
			[5,6,7,8],
			[9,10,11,12],
			[13,14,15,16]]

	eq.AnalType = "Node"
	eq.Nodes=4
	eq.EquFileName = "/home/jim/test/Wein_Bridge.equ"
	#eq.NetFileName = "/home/jim/test/BainterFilter.net"
	eq.EquFileName=""
	#eq.NetFileName=""
	eq.getequ()

	print('Mat = {}'.format(eq.Mat))

	root.mainloop()
