import sys
import os
import easypython



init_exists=os.path.exists('/sdcard/pydroid/pysql/__init__.py')
if not init_exists:
	os.mknod('/sdcard/pydroid/pysql/__init__.py')
	
	

class BetterSql:
	
	
	
	def __init__(self,name):
		name=name.replace(' ','')
		if name=='':
			print('文件名不能为空')
			sys.exit(0)
		self.pyrootPath='/sdcard/pydroid/pysql/'
		self.sqlsName=name
		self.sqlName=None
		self.sqlData={}
		self.sqlsPath=self.pyrootPath+self.sqlsName+'/'
		if not os.path.exists(self.sqlsPath):
			os.mkdir(self.sqlsPath)
			
			
			
	def access(self,name):
		self.sqlName=None
		if self.sqlsName==None:
			print('未连接到数据库集')
			sys.exit(0)
		name=name.replace(' ','')
		if name=='':
			print('文件名不能为空')
			sys.exit(0)
		self.sqlPath=self.sqlsPath+name+'.py'
		sql_exists=os.path.exists(self.sqlPath)
		if not sql_exists:
			with open(self.sqlPath,'w')as f:
				f.write('{}')
		init_exists=os.path.exists(self.sqlsPath+'__init__.py')
		if not init_exists:
			os.mknod(self.sqlsPath+'__init__.py')
		self.sqlName=name
		with open (self.sqlPath,'r')as f:
			data=f.read()
		function='self.sqlData='+data.replace('/n','\\n')
		exec(function)
		
		
		
	def refresh(self):
		with open(self.sqlPath,'r')as f:
			data=f.read()
		function='self.sqlData='+data.replace('/n','\\n')
		exec(function)		
		
			
			
			
	def newData(self,key,value,id=-1):
		if self.sqlName==None:
			print('未连接到数据库')
			sys.exit(0)
		for data in self.sqlData.items():
			if data[1][0]==key:
				self.sqlData[data[0]][1]=value
				return 'edited'
		if id==-1:
			id=1
			for digit in self.sqlData.keys():
				if id==digit:
					id+=1
				else:
					break
		self.sqlData[id]=[key,value]
		self.sqlData=easypython.dictSort(self.sqlData)
		
	
	
	def save(self):
		string='{'
		sqlLen=len(self.sqlData)
		digit=1
		for data in self.sqlData.items():
			string+=str(data[0])
			string+=':['
			if isinstance(data[1][0],str):
				string+='\''
				string+=data[1][0]
				string+='\''
			else:
				string+=str(data[1][0])
			string+=','
			if isinstance(data[1][1],str):
				string+='\''
				string+=data[1][1]
				string+='\''
			else:
				string+=str(data[1][1])
			string+=']'
			if digit!=sqlLen:
				string+=','
			digit+=1
		string+='}'
		string=string.replace('\n','/n')
		with open(self.sqlPath,'w') as f:
			f.write(string)
	
			
					
	def getSql(self):
		if self.sqlName==None:
			print('未连接到数据库')
			sys.exit(0)
		return self.sqlData		
	
	
	def data(self,kv,id=None,reverse=False):
		if id!=None and reverse==True:
			print('函数设置冲突:id=%d,reverse=True'%id)
			sys.exit(0)
		if not isinstance(id,int)and id!=None:
			print('id 必须是int')
			sys.exit(0)
		if not isinstance(reverse,bool):
			print('reverse必须是bool')
			sys.exit(0)
		if self.sqlName==None:
			print('未连接到数据库')
			sys.exit(0)
		if id!=None:
			return self.sqlData[id]
		keys=[]
		for data in self.sqlData.items():
			if not reverse:
				if data[1][0]==kv:
					return data[1][1]
			else:
				if data[1][1]==kv:
					keys.append(data[1][0])
		if keys==[]:
			keys=None
		return keys
		
		
		
	def sqlSize(self):
		if self.sqlName==None:
			print('未连接到数据库')
			sys.exit(0)
		return len(self.sqlData)
		
		
		
	def autoArrange(self):
		if self.sqlName==None:
			print('未连接到数据库')
			sys.exit(0)
		digit=1
		newSql={}
		for data in self.sqlData.items():
			kv=[data[1][0],data[1][1]]
			newSql[str(digit)]=kv
			digit+=1
		self.sqlData=newSql	
	
			
				
	def delete(self,IOKs,mode='key'):
		if self.sqlName==None:
			print('未连接到数据库')
			sys.exit(0)
		if mode=='key':
			if isinstance(IOKs,str) or isinstance(IOKs,int):
				for key in self.sqlData.items():
					if key[1][0]==IOKs:
						del self.sqlData[key[0]]
						return 
			elif isinstance(IOKs,list):
				for key in self.sqlData.items():
					if key[1][0] in IOKs:
						del self.sqlData[key[0]]
						return 
			else:
				return 'Error'
		elif mode=='value':
			if isinstance(IOKs,str)or isinstance(IOKs,int):
				for key in self.sqlData.items():
					if key[1][1]==IOKs:
						del self.sqlData[key[0]]	
			elif isinstance(IOKs,list):
				for key in self.sqlData.items():
					if key[1][1] in IOKs:
						del self.sqlData[key[0]]
			else:
				return 'Error'
		elif mode=='id':
			if isinstance(IOKs,int):
				for key in self.sqlData:
					if key==IOKs:
						del self.sqlData[key]
						return
			elif isinstance(IOKs,list):
				for key in self.sqlData:
					if key in IOKs:
						del self.sqlData[key]