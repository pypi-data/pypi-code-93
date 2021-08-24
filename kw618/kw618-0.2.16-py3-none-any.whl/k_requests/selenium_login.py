from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time



def get_cookies(browser):
    try:

        browser.get("http://price.ziroom.com/auth.html")

        username_input = browser.find_element_by_css_selector("#userAccount")
        username_input.send_keys("lvzc1")

        password_input = browser.find_element_by_css_selector("#password")
        password_input.send_keys("Lzc15168201914*")

        login_btn = browser.find_element_by_css_selector("#div-login > div > div:nth-child(4) > div > button")
        login_btn.send_keys(Keys.ENTER)

        wait = WebDriverWait(browser, 50)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "slimScrollDiv")))

        # print(browser.current_url)
        cookies = browser.get_cookies()

        for cookie_dict in cookies:
            if cookie_dict.get("name", 0) == "accessToken":
                TOKEN = cookie_dict.get("value")
        print("\n-------------------\n获取到最新的token：{0}\n\n".format(TOKEN))

    finally:
        print("done")
        # browser.close()
    if TOKEN:
        return TOKEN
    else:
        return "error"

# browser = webdriver.PhantomJS()
# 生成驱动对象是挺耗时的，所以如果要循环获得多个cookies时，不要马上close，等所有都获取完后，再关闭驱动对象！

def browser_loop(times):
    browser = webdriver.Chrome()
    for i in range(times):
        get_cookies(browser)
    browser.close()

def get_one_cookie():
    browser = webdriver.Chrome()
    TOKEN = get_cookies(browser)
    return TOKEN



def main():
    print("start!")

    # browser_loop(2)
    browser = webdriver.Chrome()
    browser.get("http://www.dianping.com/chongqing/ch50/g157r42p1")
    cookies = browser.get_cookies()
    print(cookies)

    print("end!")


if __name__ == '__main__':
    main()
