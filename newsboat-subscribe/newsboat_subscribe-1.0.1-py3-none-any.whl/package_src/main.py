import requests
import bs4
import sys
import os

def main():

	if len(sys.argv) == 1:
		print('subscribe <youtube channel url> [<youtube channel url>...]')
		sys.exit(0)

	home_dir = os.environ['HOME']
	with open(f'{home_dir}/.newsboat/urls', 'a+') as urls_file:
		urls_file.seek(0)

		existing_channel_ids = set()
		for line in urls_file.readlines():
			line = line.rstrip()
			existing_channel_ids.add(line[52:76])

		for url in sys.argv[1:]:

			r = requests.get(url)
			html_source = r.text

			soup = bs4.BeautifulSoup(html_source, 'html.parser')
			
			channel_name = soup.find("meta", {"property":"og:title"})['content']

			links = soup.findAll('link', href=True)
			for link in links:
				if link['href'].startswith('https://www.youtube.com/channel/'):
					xml = 'https://www.youtube.com/feeds/videos.xml?channel_id='
					channel_id = link['href'][len('https://www.youtube.com/channel/'):]

					if channel_id in existing_channel_ids:
						print('You are already subscribed to ' + channel_name)
						break
					
					line_item = f'{xml}{channel_id} "~{channel_name}"'
					urls_file.write('\n' + line_item)
					existing_channel_ids.add(channel_id)
					print('Added to newsboat: ')
					print(line_item)
					break
			else:
				print('Channel ID not found. Unable to add to newsboat')

