from lxml import objectify as xml, etree

class MicrovixAuthentication:


	def __init__(self, user, password, key, cnpj):

		self.__user = user 
		self.__password= password
		self.__key = key
		self.__cnpj = cnpj

		E = xml.ElementMaker(annotate=False)

		self.__parameters = E.Parameters()

		self.chave = key
		self.cnpjEmp = cnpj

		self.__command = E.Command()

		authentication = E.Authentication()
		authentication.set('user', user)
		authentication.set('password', password)

		self.__linxMicrovix = E.LinxMicrovix()
		self.__linxMicrovix.append(authentication)
		self.__linxMicrovix.append(self.__command)


	def setCommandName(self, name):
		self.__command.Name = xml.DataElement(name, nsmap='', _pytype='')


	def __str__(self):
		self.__command.append(self.__parameters)
		string =  etree.tostring(self.__linxMicrovix, pretty_print=True, xml_declaration=True,encoding='utf-8').decode()
		return string 


	def __setattr__(self, name, value):
		classname = f'_{MicrovixAuthentication.__name__}'

		if name in self.__dict__ or name.startswith(classname):
			self.__dict__[name] = value
			return

		parameter = xml.StringElement(str(value) if value else 'NULL')
		parameter.set('id', name)

		self.__parameters.addattr('Parameter', parameter)


	def copy(self):
		return MicrovixAuthentication(
			self.__user,
			self.__password,
			self.__key,
			self.__cnpj
		)
