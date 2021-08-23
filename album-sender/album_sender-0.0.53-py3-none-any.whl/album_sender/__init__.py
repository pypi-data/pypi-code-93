#!/usr/bin/env python3
# -*- coding: utf-8 -*-

name = 'album_sender'

from PIL import Image
from telegram import InputMediaPhoto, InputMediaVideo
import cached_url
import pic_cut
from telegram_util import cutCaption, isUrl, cutCaptionHtml
import os
import time

next_send_time = {}
def waitSend(chat_id, media_group_size):
	wait = next_send_time.get(chat_id, 0) + media_group_size ** 2 + media_group_size * 10 - time.time()
	next_send_time[chat_id] = time.time() + media_group_size ** 2 + media_group_size * 10
	if wait > 0:
		time.sleep(wait)
	
def properSize(fn):
	size = os.stat(fn).st_size
	if fn.endswith('mp4'):
		return 0 < size and size < (1 << 25)
	return 0 < size and size < (1 << 23)

def getCap(result, limit):
	if result.cap_html_v2:
		if not result.url:
			return cutCaptionHtml(result.cap_html_v2, limit)
		return (cutCaptionHtml(result.cap_html_v2, limit) + 
			' <a href="%s">source</a>' % result.url).strip()
	if result.getParseMode() == 'HTML':
		# currently, the only use case is repost the telegram post
		# later on, this part might need expansion
		return result.cap_html
	if result.url:
		suffix = '[source](%s)' % result.url
	else:
		suffix = ''
	return cutCaption(result.cap, suffix, limit)

def sendVideo(chat, result):
	os.system('mkdir tmp > /dev/null 2>&1')
	with open('tmp/video.mp4', 'wb') as f:
		f.write(cached_url.get(result.video, force_cache=True, mode='b'))
	if os.stat('tmp/video.mp4').st_size > 50 * 1024 * 1024:
		return []
	group = [InputMediaVideo(open('tmp/video.mp4', 'rb'), 
		caption=getCap(result, 1000), parse_mode=result.getParseMode())]
	return chat.bot.send_media_group(chat.id, group, timeout = 20*60)

def imgRotate(img_path, rotate):
	if img_path.endswith('mp4'):
		return
	if not rotate:
		return
	if rotate == True:
		rotate = 180
	img = Image.open(img_path)
	img = img.rotate(rotate, expand=True)
	img.save(img_path)

def getMedia(fn, result = None):
	# see if animated gif still work or not
	if pic_cut.isAnimated(fn):
		tag = InputMediaVideo
	else:
		tag = InputMediaPhoto
	return tag(open(fn, 'rb'), 
		caption=result and getCap(result, 1000),
		parse_mode=result and result.getParseMode())

def getMediaGroup(imgs, result):
	return [getMedia(imgs[0], result)] + [getMedia(img) for img in imgs[1:]]

def getImage(img):
	cached_url.get(img, force_cache=True, mode='b')
	return cached_url.getFilePath(img)

def send_v2(chat, result, rotate=0, send_all=False, no_cut=False, size_factor = None, rotate_detail = {}):
	# todo: cached_url may want to make sure the video fn ends with mp4...	
	if result.video:
		try:
			return sendVideo(chat, result)
		except Exception as e:
			if not result.imgs:
				raise e

	img_limit = 100 if send_all else 10
	if no_cut:
		imgs = [getImage(img) for img in result.imgs]
	else:
		args = {}
		if size_factor:
			args['size_factor'] = size_factor
		imgs = pic_cut.getCutImages(result.imgs, img_limit, **args)	
	imgs = [x for x in imgs if properSize(x)]
	print(len(imgs), imgs)
	[imgRotate(x, rotate) for x in imgs]
	for index, rotate_single in rotate_detail.items():
		imgRotate(imgs[index], rotate_single)
	
	if imgs:
		return_result = []
		for page in range(1 + int((len(imgs) - 1) / 10)):
			group = getMediaGroup(imgs[page * 10: page * 10 + 10], result)
			waitSend(chat.id, len(group))
			return_result += chat.bot.send_media_group(chat.id, group, timeout = 20*60)
		return return_result

	if result.cap or result.cap_html or result.cap_html_v2:
		waitSend(chat.id, 1)
		return [chat.send_message(getCap(result, 4000), 
			parse_mode=result.getParseMode(), timeout = 20*60, 
			disable_web_page_preview = (not isUrl(result.cap)))]

def send(chat, url, result, rotate=0, send_all=False):
	result.url = url
	send_v2(chat, result, rotate=rotate, send_all=send_all)