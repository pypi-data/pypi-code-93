import requests

from taskhub.server import serve
from retry import retry
from loger import log
import traceback


def sync(task):

    back_end_url = "http://127.0.0.1/api/"
    @retry(tries=5, delay=1, backoff=1)
    def req(task):
        print(task)
        r = requests.post(back_end_url, json=task.get_dict())
        r.raise_for_status
        return r.json()

    log("syncing...")
    try:
        r_data = req(task)
    except:
        log("sync: req 时发生异常：{}".format(traceback.format_exc()), 1)
        return False
    else:
        if r_data.get("code") == 200:
            log("synced!", 4)
            return True
        else:
            log("sync: 返回状态异常：{}".format(r_data))
            return False



if __name__ == "__main__":
    serve(
        port=2333, 
        passwd="1qaz2wsx", 
      sync=sync)
