from .message_sender import MessageSender
import datetime
import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By

class ImageMessageSender(MessageSender):

    def __init__(self):
        super(ImageMessageSender, self).__init__()

        driver_path = '/tool/chromedriver'
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--hide-scrollbars')
        self.driver = webdriver.Chrome(executable_path=driver_path, options=options)
        width = 600
        height = 1150
        self.driver.set_window_size(width, height)
        self.driver.implicitly_wait(10)

    def capture_webpage(self, webpage_url):
        self.driver.get(webpage_url)
        time.sleep(1)
        # WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'tab-MONTH1')))
        filename = f'/tmp/{webpage_url.split("/")[-1]}.png'
        self.driver.save_screenshot(filename)
        return filename

    def send(self, msg_to, msg_content):
        # Send snapshot of webpage and url
        # doc: https://open.work.weixin.qq.com/api/doc/90000/90135/90236
        access_token = self.get_access_token()
        target_url = f'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}'


        filename = self.capture_webpage(msg_content)
        files = {'file': ('snapshot.png', open(filename, 'rb'), 'image/png', {'Expires': '0'})}

        # upload image and get media_id
        # doc: https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/New_temporary_materials.html
        upload_url = f'https://api.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type=image'
        res = requests.post(url=upload_url, files=files, timeout=30)
        data = json.loads(res.text)
        if 'errcode' in data:
            print(f'Failed to upload image, errmsg: {data["errmsg"]}')
            return
        media_id = data['media_id']

        # Send image
        message = {
            'touser': '|'.join(msg_to) if type(msg_to) is list else msg_to,
            'msgtype': 'image',
            'image' : {'media_id' : media_id}
        }
        res = requests.post(url=target_url, data=json.dumps(message), timeout=20)

        print(f'msg: {message} {datetime.datetime.now()}')
