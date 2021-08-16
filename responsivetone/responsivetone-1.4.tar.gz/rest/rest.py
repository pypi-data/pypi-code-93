#import rest
import argparse
import requests
import json
import time


'''
def main():
    parser = argparse.ArgumentParser()
    #parser.add_argument('--name', choices=['intext'], default='名前は？')
    parser.add_argument('arg1', help='InputText')  
    
    args = parser.parse_args()

    intext = args.arg1
    intext = str(intext)
    result = rest(intext)
    print(result)
'''

def rest(intext):
  print("input Japanese text>")
  #reqtext=input()
  reqtext=intext
  print("Mode: Language==Japanese , Dialect==(Tokyo,Osaka)")
  print('\033[32m'+"ContactMe: osawa_yuto@yahoo.co.jp (e-mail)"+'\033[0m')
  time.sleep(1)
  print("Artificial intelligence is calculating. Please wait...")
  time.sleep(1)
  print("Artificial intelligence is calculating. Please wait......")
  time.sleep(1)
  print("Artificial intelligence is calculating. Please wait.........")
  # エンドポイント
  url = 'https://yutoosawa.ngrok.io/message/'

  url+=reqtext
  # リクエスト
  res = requests.get(url)
  # 取得したjsonをlists変数に格納
  lists = res.text
  lists = "".join(lists)
  lists = str(lists)
  #print(lists)
  return lists
'''
def ToneEnc(intext):
  print("input Japanese text>")
  #reqtext=input()
  reqtext=intext
  print("Mode: Language==Japanese , Dialect==(Tokyo,Osaka)")
  time.sleep(1)
  print("Artificial intelligence is calculating. Please wait...")
  time.sleep(1)
  print("Artificial intelligence is calculating. Please wait......")
  time.sleep(1)
  print("Artificial intelligence is calculating. Please wait.........")
  # エンドポイント
  url = 'https://yutoosawa.ngrok.io/message/'

  url+=reqtext
  # リクエスト
  res = requests.get(url)
  # 取得したjsonをlists変数に格納
  lists = res.text
  lists = "".join(lists)
  #print(lists)
  return lists



if __name__ == '__main__':
    main()
'''