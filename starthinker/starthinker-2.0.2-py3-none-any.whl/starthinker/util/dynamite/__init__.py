import json
from urllib.request import Request, urlopen


def dynamite_write(room, key, token, text):
  url = 'https://chat.googleapis.com/v1/spaces/%s/messages?key=%s&token=%s' % (
      room, key, token)
  data = json.dumps({
      'sender': {
          'displayName':
              'StarThinker',
          'avatarUrl':
              'https://www.gstatic.com/images/icons/material/system/2x/chat_googblue_48dp.png'
      },
      'text': text
  })
  f = urlopen(
      urllib.request.Request(url, data, {
          'Content-Type': 'application/json',
          'Content-Length': len(data)
      }))
  response = f.read()
  f.close()
  return response
