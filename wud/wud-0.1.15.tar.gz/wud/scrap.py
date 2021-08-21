#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 08:37:37 2021

@author: nattawoot
"""
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

def open_browser(driver_path, url):
    
    loaded = False

    while not loaded:
        try:

            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('disable-notifications')
            
            driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
            start = datetime.now()
            driver.set_page_load_timeout(60)
            driver.get(url)

            loaded = True

            return driver, start, [""] * 10
        except Exception as e:
            print(e.__class__.__name__)


def refresh_ssl(driver_path):
    
    try_count = 1
    while try_count<10:
        print(f"try refresh ssl - {try_count}")

        try:
            driver = webdriver.Chrome(executable_path=driver_path)
            driver.get( "http://www.google.com")
            time.sleep(10)
            driver.find_element_by_id("user").send_keys(os.environ['PTTLNG_USER'])
            driver.find_element_by_name("passwd").send_keys(os.environ['PTTLNG_PWD'])
            driver.find_element_by_id("submit").click()        
            driver.quit()
            print("refresh ssl success.")
            break
        
        except NoSuchElementException:
            try_count = try_count + 1
            
