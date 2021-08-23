
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId


class MongoDatabase:

	def __init__(self, db = 'altanet_crawler'):

		self.client = MongoClient()
		self.db = self.client[db]

	def read_collection(self, collection, query = {}, projection = None, no_cursor_timeout = False, return_count = False):
		"""Read all documents in a certain collection"""

		try:
			if projection is None:
				result = self.db[collection].find(query, no_cursor_timeout = no_cursor_timeout)
			else:
				result = self.db[collection].find(query, projection, no_cursor_timeout = no_cursor_timeout)

			# return results with or without count
			if return_count:
				count = self.db[collection].count_documents(query)
				return result, count
			else:
				return result

		except Exception as e:
			logging.error(e)
			return None

	def insert_collection(self, collection, document):
		"""Insert one document to a collection"""

		try:
			self.db[collection].insert_one(document)
		except Exception as e:
			logging.error(e)
			return False

	def update_collection(self, collection, doc_id, field, new_value):
		""" Update a field of a collection """

		try:
			self.db[collection].update({'_id' : ObjectId(doc_id)}, 
									{"$set": 
										{field : new_value}
									}, upsert=False)
		except Exception as e:
			logging.error(e)
			return False



	# def insertManyToCollection(self, collection, document_array):

	# 	"""
	# 		Insert one document to a collection
	# 	"""

	# 	try:
	# 		self.db[collection].insert_many(document_array)
	# 	except Exception, e:
	# 		logging.error("Error adding document to collection {}: {}".format(collection, str(e)))

	# def updateOneToCollection(self, collection, doc_id, field, new_value):

	# 	""" 
	# 		Update a field of a collection
	# 	"""

	# 	try:
	# 		self.db[collection].update({'_id' : ObjectId(doc_id)}, 
	# 								{"$set": 
	# 									{field : new_value}
	# 								}, upsert=False)
	# 	except Exception, e:
	# 		logging.error("Error updating collection: {}".format(str(e)))


	# def removeOneFromCollection(self, collection, document_id):

	# 	"""
	# 		Remove one record from collection
	# 	"""

	# 	try:
	# 		self.db[collection].remove({'_id' : ObjectId(document_id)})
	# 	except Exception, e:
	# 		logging.error("Error removing document: {}, {}".format(document_id, str(e)))


	# def updatePublicationTokens(self, doc, collection = 'publications'):

	# 	""" 
	# 		Update a field of a collection
	# 	"""

	# 	try:
	# 		self.db[collection].update({'_id' : ObjectId(doc['_id'])}, 
	# 								{"$set": 
	# 									{ 	'unigrams' : doc['unigrams'],
	# 										'bigrams' : doc['bigrams'],
	# 										'entities' : doc['entities'],}
	# 								}, upsert=False)
	# 	except Exception, e:
	# 		logging.error("Error updating collection: {}".format(str(e)))