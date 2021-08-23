import requests, json, sys, re
from xml.dom import minidom

class Finder:
	"""
	Main class
	"""
	def __init__(self, output_file="results.tsv", any_case=False):
		self.url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/searchPOST'
		self.pageSize = 25
		self.clean_re = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
		self.file_writer = open(output_file, 'w')
		self.any_case = any_case
		self.file_writer.write("\tRESIDUE\tPAPER_ID\tSOURCE\tPHRASE\tNEXT_CURSOR")

	def __minePMC(self, pmc_id):
		"""
		Private method to read and parse a full text article
		"""
		patterns = []
		url = "https://www.ebi.ac.uk/europepmc/webservices/rest/%s/fullTextXML" % pmc_id
		raw_data = requests.get(url)
		xmldoc = minidom.parseString(raw_data.text)
		for node in xmldoc.getElementsByTagName('p'):
			clean_text = re.sub(self.clean_re,'',node.toxml())
			patterns += self.__mineText(clean_text)
		return patterns

	def __mineText(self, text):
		"""
		Private method to find and extract the matching phrase in the text
		"""
		regex = '[^.]* (?:Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)\d+[^.]*\.'
		if self.any_case:
			regex = '(?i)' + regex
		patterns = re.findall(regex, text)
		return patterns

	def __extractResidues(self, text):
		"""
		Private method to extract the residues from the text
		"""
		regex = '(?:Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)\d+'
		if self.any_case:
			regex = '(?i)' + regex
		patterns = re.findall(regex, text)
		return patterns

	def __crawl(self, post_data):
		"""
		Execute crawler
		"""
		i = 1
		read = 0
		while True:
			raw_data = requests.post(self.url, data = post_data)
			data = json.loads(raw_data.text)
			nextCursor = data['nextCursorMark'] if 'nextCursorMark' in data else ''
			hitCount = data['hitCount'] if 'hitCount' in data else 0
			read += self.pageSize if self.pageSize < hitCount else hitCount
			read = hitCount if nextCursor == '' else read
			print(f'Reading {read} of {hitCount}: Next cursor is: {nextCursor}')

			if hitCount > 0:
				result = data['resultList']['result']

				if len(result) == 0:
					break

				for result in result:
					pubid = result['id']
					source = result['source']
					open_access = True if result['isOpenAccess'] == 'Y' else False
					if open_access and 'pmcid' in result:
						pmcid = result['pmcid']
						for element in self.__minePMC(pmcid):
							element = element.replace("\n"," ")
							residues = self.__extractResidues(element)
							for residue in residues:
								row = f"{residue}\t{pmcid}\tPMC\t{element}\t{nextCursor}"
								self.file_writer.write(row + "\n")
								self.file_writer.flush()
								#print(row)
					else:
						#Mine abstract
						abstract = result['abstractText'] if 'abstractText' in result else ''
						for element in self.__mineText(abstract):
							element = element.replace("\n"," ")
							residues = self.__extractResidues(element)
							for residue in residues:
								row = f"{residue}\t{pubid}\t{source}\t{element}\t{nextCursor}"
								self.file_writer.write(row + "\n")
								self.file_writer.flush()
								#print(row)
			else:
				break

			if nextCursor == '' or hitCount == 0:
				break
			else:
				post_data['cursorMark'] = nextCursor
				i+=1

	def search(self, idt, database="", min_year=None, cursor=None):
		"""
		Search by UniProt id
		"""
		database = database.lower()

		if database == "uniprot":
			query = f"UNIPROT_PUBS:{idt}"
		elif database == "pdb":
			query = f"PDB_PUBS:{idt}"
		elif database == "interpro":
			query = f"INTERPRO_PUBS:{idt}"
		elif database == "chebi":
			query = f"CHEBI_PUBS:{idt}"
		elif database == "chembl":
			query = f"CHEMBL_PUBS:{idt}"
		elif database == "pfam":
			query = f"ACCESSION_ID:{idt} AND ACCESSION_TYPE:pfam"
		elif database == "go":
			query = f'ACCESSION_ID:"{idt}" AND ACCESSION_TYPE:go'
		else:
			query = idt

		if min_year:
			query += f" AND PUB_YEAR:[{min_year} TO *]"

		data = {
			'query': query,
			'format': 'json',
			'resultType': 'core',
			'pageSize' : self.pageSize,
		}

		if cursor:
			data['cursorMark'] = cursor

		self.__crawl(data)




