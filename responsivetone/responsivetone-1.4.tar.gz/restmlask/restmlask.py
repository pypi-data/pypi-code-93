#import rest
import argparse
import requests
import json
import time



def restmlask(intext):

  reqtext=intext

  url = 'https://mikokuro.jp.ngrok.io/RestMlask/'

  url+=reqtext
  # リクエスト
  res = requests.get(url)
  # 取得したjsonをlists変数に格納
  lists = res.text
  lists = "".join(lists)
  #print(lists)
  return lists
