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



def restVoiceRoid(intext):
  reqtext=intext

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
  lists = lists.replace("['","")
  lists = lists.replace("',","")
  lists = lists.replace("']","")
  lists = lists.replace(" '","")

  talkVOICEROID2(lists)

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

'''
import pywinauto

def search_child_byclassname(class_name, uiaElementInfo, target_all = False):
    target = []
    # 全ての子要素検索
    for childElement in uiaElementInfo.children():
        # ClassNameの一致確認
        if childElement.class_name == class_name:
            if target_all == False:
                return childElement
            else:
                target.append(childElement)
    if target_all == False:
        # 無かったらFalse
        return False
    else:
        return target


def search_child_byname(name, uiaElementInfo):
    # 全ての子要素検索
    for childElement in uiaElementInfo.children():
        # Nameの一致確認
        if childElement.name == name:
            return childElement
    # 無かったらFalse
    return False

def talkVOICEROID2(speakPhrase):
    # デスクトップのエレメント
    parentUIAElement = pywinauto.uia_element_info.UIAElementInfo()
    # voiceroidを捜索する
    voiceroid2 = search_child_byname("VOICEROID2",parentUIAElement)
    # *がついている場合
    if voiceroid2 == False:
        voiceroid2 = search_child_byname("VOICEROID2*",parentUIAElement)

    # テキスト要素のElementInfoを取得
    TextEditViewEle = search_child_byclassname("TextEditView",voiceroid2)
    textBoxEle      = search_child_byclassname("TextBox",TextEditViewEle)

    # コントロール取得
    textBoxEditControl = pywinauto.controls.uia_controls.EditWrapper(textBoxEle)

    # テキスト登録
    textBoxEditControl.set_edit_text(speakPhrase)


    # ボタン取得
    buttonsEle = search_child_byclassname("Button",TextEditViewEle,target_all = True)
    # 再生ボタンを探す
    playButtonEle = ""
    for buttonEle in buttonsEle:
        # テキストブロックを捜索
        textBlockEle = search_child_byclassname("TextBlock",buttonEle)
        if textBlockEle.name == "再生":
            playButtonEle = buttonEle
            break

    # ボタンコントロール取得
    playButtonControl = pywinauto.controls.uia_controls.ButtonWrapper(playButtonEle)

    # 再生ボタン押下
    playButtonControl.click()
'''

def main():
  restVoiceRoid("こんにちわ")

if __name__ == '__main__':
    main()
'''