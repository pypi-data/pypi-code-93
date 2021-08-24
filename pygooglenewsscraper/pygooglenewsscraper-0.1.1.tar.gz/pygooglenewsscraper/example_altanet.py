
from pygooglenewsscraper import GoogleNews
from pygooglenewsscraper import NewsArticle
from database import MongoDatabase
from datetime import datetime

import logging
import time

def get_raw_googlenews():


	# define search keywords
	search_keywords = ['macroalgae', 'seaweed', 'echinoderms', 'sea urchins' ,'sea cucumbers', 'molluscs', 'oysters', 'mussels', 'crustaceans', 'integrated multi-trophic aquaculture']

	# create db object
	db = MongoDatabase()

	# process each keyword
	for i, w in enumerate(search_keywords):

		logging.debug(f'Processing keyword {w} {i}/{len(search_keywords)}')

		# create a google news 
		googlenews = GoogleNews(keyword = w)
			
		# get html object trough request
		html = googlenews.get_raw_news()

		# check if response is ok
		if html.status_code == 200:

			# create document to insert into database
			new_doc = {	'keyword' : w,
						'encoding' : html.encoding,
						'status_code' : html.status_code,
						'processed' : False,
						'datetime' : datetime.now(),
						'text' : html.text,
						'url' : googlenews.url}

			db.insert_collection(collection = 'raw_googlenews', document = new_doc)

		# wait some time for the next call
		time.sleep(5)

def parse_raw_googlenews():

	logging.info('Start parsing raw google news')

	# get database object
	db = MongoDatabase()

	# read already processed urls
	processed_urls = set([x['url'] for x in db.read_collection(collection = 'parsed_googlenews', projection = {'url' : 1})])

	# read raw google news that need to be parsed
	D, count = db.read_collection(collection = 'raw_googlenews', query = {'processed' : False}, return_count = True)

	# trackers for number of inserts and duplicates
	inserts, duplicates = 0, 0

	# process each document
	for i, d in enumerate(D):

		logging.info(f'Processing {i}/{count}')

		# create a google news object
		googlenews = GoogleNews(keyword = d['keyword'])

		# parse out news items from raw html content
		news_items = googlenews.parse_news(html= d['text'])

		# store each item to database
		for n in news_items.values():

			# check if news url already part of database
			if n['url'] not in processed_urls:

				# new dictinary to store to database
				new_doc = {'processed' : False,
							**n}

				db.insert_collection(collection = 'parsed_googlenews', document = new_doc)
				inserts +=1
			else:
				logging.debug(f"news already processed: {n['url']}")
				duplicates +=1

		# set raw google news collection to processed so we can skip it next time
		db.update_collection(collection = 'raw_googlenews', doc_id = d['_id'], field = 'processed', new_value = True)

	logging.info(f'Number of documents processed : {count}')
	logging.info(f'Documents inserted: {inserts}')
	logging.info(f'Documents duplicated (not inserted): {duplicates}')

def parse_raw_news():

	db = MongoDatabase()
	
	# read raw google news that need to be parsed
	D, count = db.read_collection(collection = 'parsed_googlenews', query = {'processed' : False}, return_count = True)

	for i, d in enumerate(D):

		logging.info(f'Processing {i}/{count}')
		logging.info(f"--- URL : {d['url']}")

		# instantiate news article object
		news = NewsArticle(url = d['url'])

		# extract content
		news_content = news.parse_main_content()

		new_doc = {**d, 
					**news_content, 
					'processed' : False,
					}

		# remove ID
		del new_doc['_id']

		# add to database
		db.insert_collection(collection = 'parsed_news', document = new_doc)
		
		# update status
		db.update_collection(collection = 'parsed_googlenews', doc_id = d['_id'], field = 'processed', new_value = True)


def main():

	# get_raw_googlenews()

	# parse_raw_googlenews()

	parse_raw_news()

if __name__ == '__main__':

	logging.basicConfig(level=logging.DEBUG)

	main()

