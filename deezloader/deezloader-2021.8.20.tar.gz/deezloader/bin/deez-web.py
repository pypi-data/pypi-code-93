#!/usr/bin/python3

from sys import argv
from pathlib import Path
from shutil import rmtree
from urllib.parse import quote_plus
from uvicorn import run as run_server
from json.decoder import JSONDecodeError
from deezloader_lite.KThread import KThread
from fastapi.responses import StreamingResponse

from os import (
	remove, listdir, rmdir
)

from fastapi import (
	FastAPI, Request, HTTPException
)

from deezloader_lite.google_webhook_utils import (
	check_user, hello_json,
	start_download_artist_top, start_download_playlist,
	start_download_track, play,
	not_found_json, output
)

try:
	ngrok_url= argv[1]
except IndexError:
	print("Ngrok url is missing")
	exit()

song_url = f"{ngrok_url}/download?path=%s"

app = FastAPI(
	docs_url = None,
	redoc_url = None,
	openapi_url = None
)

user_data = {}

def del_user(chat_id):
	songs = user_data[chat_id]['datas']

	for song in songs:
		path = song['path']

		try:
			remove(path)
		except FileNotFoundError:
			pass

		path_dir = Path(path).parent.absolute()

		try:
			list_dir = listdir(path_dir)

			if not list_dir:
				rmdir(path_dir)
		except FileNotFoundError:
			pass

def results(req):
	try:
		query = req['queryResult']
	except TypeError:
		return {
			"ciao": "sei bellissimo"
		}

	chat_id = req['originalDetectIntentRequest']['payload']['conversation']['conversationId']
	datas_users = check_user(user_data, chat_id)
	data_user = datas_users[chat_id]

	try:
		media_status = query['outputContexts'][-2]['parameters']['MEDIA_STATUS']['status']

		if media_status == "FAILED":
			data_user['playlist_index'] -= 1
	except KeyError:
		if query['queryText'] == "GOOGLE_ASSISTANT_WELCOME":
			return hello_json()

		infos = query['parameters']
		artist = infos['music-artist']
		genre = infos['music-genre']
		song = infos['song-name']
		keyword = None
		what = None

		if artist != "":
			keyword = artist
			what = "artist"
			target = start_download_artist_top

		if genre != "":
			keyword = genre
			what = "playlist"
			target = start_download_playlist

		if song != "":
			keyword = song
			what = "song"
			target = start_download_track

		if song != "" and artist != "":
			keyword = {
				"song": song,
				"artist": artist
			}

			what = "artist-song"
			target = start_download_track

		if not keyword:
			return hello_json()

		if data_user['thread']:
			try:
				data_user['thread'].kill()
				data_user['thread'].join()
			except RuntimeError:
				pass

			KThread(
				target = del_user, args = (chat_id, )
			).start()

		data = play(keyword, what)

		if not data:
			return not_found_json()

		datas, title, api_url = data

		t = KThread(
			target = target, args = (api_url, )
		)

		data_user['thread'] = t
		data_user['thread'].start()
		data_user['datas'] = datas
		data_user['title'] = title
		data_user['playlist_index'] = -1

	data_user['playlist_index'] += 1

	if data_user['playlist_index'] <= len(data_user['datas']) - 1:
		playlist_index = data_user['playlist_index']
		data = data_user['datas'][playlist_index]
		song = "La canzone {} - {} sta per essere riprodotta".format(data['song'], data['artist'])

		json = {
			"payload": {
				"google": {
					"expectUserResponse": True,
					"richResponse": {
						"items": [{
								"simpleResponse": {
									"textToSpeech": "<speak></speak>",
									"displayText": song
								}
							},
							{
								"mediaResponse": {
									"mediaType": "AUDIO",
									"optionalMediaControls": [
									"PAUSED",
									"STOPPED"
									],
									"mediaObjects": [
										{
											"contentUrl": song_url % quote_plus(data['path']),
											"description": data['artist'],
											"icon": {
												"url": data['image'],
												"accessibilityText": data['album_name']
											},
											"name": data['song']
										}
									]
								}
							}
						],
						"suggestions": [
							{
								"title": "start over"
							},
							{
								"title": "pause"
							},
							{
								"title": "play"
							},
							{
								"title": "next"
							}
						]
					}
				}
			}
		}
	else:
		json = {
			"payload": {
				"google": {
					"expectUserResponse": True,
					"richResponse": {
						"items": [{
							"simpleResponse": {
								"textToSpeech": "<speak>La playlist è finita</speak>",
								"displayText": "La playlist è finita"
							}
						}]
					}
				}
			}
		}

	return json

@app.get("/delall/")
def delall():
	for a in listdir(output):
		try:
			rmtree(output + a)
		except NotADirectoryError:
			remove(output + a)
		except OSError:
			pass

	json = {
		"success": True
	}

	return json

@app.get("/download/")
async def download(path: Path):
	try:
		file_like = open(path, "rb")
	except FileNotFoundError:
		json = {
			"error": "PATH NOT FOUND"
		}

		raise HTTPException(
			status_code = 404,
			detail = json
		)

	return StreamingResponse(file_like, media_type = "audio/mp3")

@app.post("/deez_webhook/")
async def deez_webhook(request: Request):
	try:
		json = await request.json()
	except JSONDecodeError:
		json = {
			"error": "NO JSON"
		}

		raise HTTPException(
			status_code = 406,
			detail = json
		)

	return results(json)

if __name__ == "__main__":
	run_server(
		app,
		host = "0.0.0.0",
		port = 8000
	)