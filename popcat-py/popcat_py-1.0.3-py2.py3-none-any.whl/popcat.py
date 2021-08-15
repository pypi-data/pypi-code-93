from selenium import webdriver

fp = webdriver.FirefoxProfile()
fp.set_preference("media.volume_scale", "0.0")

driver = webdriver.Firefox(fp)
driver.get("https://popcat.click/")
button_element = driver.find_element_by_id("app")
while 1:
    button_element.click()
