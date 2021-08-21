#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 08:28:49 2021

@author: nattawoot
"""

import os 
from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)

from linebot.models import (
 MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, 
 SourceUser, SourceGroup, SourceRoom,
 TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
 ButtonsTemplate, URITemplateAction, PostbackTemplateAction, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
 CarouselTemplate, CarouselColumn, PostbackEvent,
 StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
 ImageMessage, VideoMessage, AudioMessage, FlexSendMessage, 
 UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
 FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
 TextComponent, IconComponent, ButtonComponent,
 SeparatorComponent, QuickReply, QuickReplyButton, PostbackAction,MessageAction, CarouselContainer

)
from loguru import logger

line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))


#%% line notify
def lineNotify(token, message):
    payload = {'message':message}
    return _lineNotify(token, payload)

def notifyFile(token, filename):
    file = {'imageFile':open(filename,'rb')}
    payload = {'message': 'test'}
    return _lineNotify(token, payload,file)

def notifyPicture(token, url):
    payload = {'message':" ",'imageThumbnail':url,'imageFullsize':url}
    return _lineNotify(token, payload)

def notifySticker(token, stickerID,stickerPackageID):
    payload = {'message':" ",'stickerPackageId':stickerPackageID,'stickerId':stickerID}
    return _lineNotify(token, payload)

def _lineNotify(token, payload,file=None):
    import requests
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization':'Bearer '+token}
    return requests.post(url, headers=headers , data = payload, files=file)

#%% line send message
def send_message(messenger, messenger_id, message):

    if messenger == 'line':
        try:
            line_bot_api.push_message(
                messenger_id,
                TextSendMessage(text=message),
            )
        except LineBotApiError as e:
            logger.warning(f"error send to {messenger_id} fail{e.status_code},{e.error.message},{e.error.details}")

    if messenger == 'fb':
        response = fb_bot.send_text_message(messenger_id, message)
        if ('error' in response):
            logger.debug(f"{messenger_id}-{response}")
    if messenger == 'line_notify':
        response = lineNotify(messenger_id, message)
        if ('error' in response):
            logger.debug(f"{messenger_id}-{response}")
def send_image(messenger, messenger_id, image_link):

    if messenger == 'line':
        try:
            line_bot_api.push_message(
                messenger_id,
                ImageSendMessage(
                    original_content_url=image_link,
                    preview_image_url=image_link,
                ),
            )
            print("sent to-" + messenger_id)
        except LineBotApiError as e:
            logger.warning(f"error send to {messenger_id} fail{e.status_code},{e.error.message},{e.error.details}")
                
    if messenger == 'fb':
        response = fb_bot.send_image_url(messenger_id, image_link)
        if ('error' in response):
            logger.debug(f"{messenger_id}-{response}")

    if messenger == 'line_notify':
        response = notifyPicture(messenger_id, image_link)
        if ('error' in response):
            logger.debug(f"{messenger_id}-{response}")

def send_carousel_flex(messenger_id, json_contents_list, alt_text='flex message'):
    containers = CarouselContainer(
       contents=json_contents_list
    )
    
    message = FlexSendMessage(alt_text=alt_text, contents=containers)
    line_bot_api.push_message(
    messenger_id,
    message
    )

