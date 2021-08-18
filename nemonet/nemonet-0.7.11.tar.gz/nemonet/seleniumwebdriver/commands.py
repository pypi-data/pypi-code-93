'''
Created on 13 feb. 2018

@author: ex03210
'''
import logging

from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import ElementNotVisibleException

from nemonet.seleniumwebdriver.page_capture import PageCapturing
from nemonet.engines.cache_store import KeyValueStore

import random
import string
import time

from nemonet.cvision.computer_vision import ComputerVision


class Command(object):
    """
        All kind of selenium actions
    """


    def __init__(self, driver=None):
        """Constructor"""
        self.driver = driver
        self._wait = WebDriverWait(self.driver, 60)
        self.logger = logging.getLogger('vision_logger')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('vision.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def add_browser_tabs(self, nbr_of_tabs=1):
        self.logger.debug(self.driver.current_window_handle)
        for nbr in range(nbr_of_tabs):
            tab_name = "TAB_" + str(nbr)
            self.driver.execute_script("window.open('about:blank', '%s');" % ( tab_name ) )
            time.sleep(0.5)
            self.driver.switch_to.window(tab_name)
            self.logger.debug(self.driver.current_window_handle)

    def goto_browser_tab(self, tab_nbr=1):
        handles = self.driver.window_handles
        self.logger.debug(handles)
        self.driver.switch_to.window( handles[tab_nbr] )

    def goto_current_browser_tab(self):
        self.driver.switch_to.window( self.driver.current_window_handle )

    def goto_frame(self, frame_nbr):
        self.driver.switch_to.frame(int(frame_nbr))

    def log_current_url(self):
        self.logger.debug(self.driver.current_url)

    def openurl(self, url ):
        self.driver.get(str(url))

    def screenshot(self, filename):
        capture = PageCapturing(self.driver)
        capture.capture_save(file_name_cpatured=filename)

    def element(self, locator):
        element = self._wait.until(ec.element_to_be_clickable(locator), message='Cannot locate {}'.format(locator))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        return element

    def click(self, locator):
        self.element(locator).click()



    def select_drop_down_by_value(self, select_locator, value):
        Select(self.element(select_locator)).select_by_value(value)

    def select_drop_down_by_text(self, select_locator, text):
        Select(self.element(select_locator)).select_by_visible_text(text)

    def find_element_xpath(self, xpath_str):
        return self._wait.until(ec.visibility_of_element_located((By.XPATH, xpath_str)))

    def find_elements_xpath(self, xpath_str):
        return self._wait.until(ec.visibility_of_all_elements_located((By.XPATH, xpath_str)))

    def fill_in_text(self, xpath_str, text):
        # element = WebDriverWait(self.driver, 60 ).until(EC.presence_of_element_located(( By.XPATH, xpathStr )))
        element = self._wait.until(ec.visibility_of_element_located((By.XPATH, xpath_str)))
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        actions.click()
        actions.send_keys(text)
        actions.perform()

    def fill_in_text_no_action_chain(self, xpath_str, text):
        element = self._wait.until(ec.visibility_of_element_located((By.XPATH, xpath_str)))
        element.send_keys(text)

    def element_fill_in_text(self, element, text):
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        actions.click()
        actions.send_keys(text)
        actions.perform()

    def enter_text_current_position(self, text=""):
        actions = ActionChains(self.driver)
        actions.send_keys(text)
        actions.perform()

    def enter_text_current_position_stamp(self, text=""):
        actions = ActionChains(self.driver)
        text = text + " " + ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        actions.send_keys(text)
        actions.perform()

    def enter_tab_current_position(self):
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.TAB)
        actions.perform()

    def fill_in_text_enter(self, xpath_str, text):
        element = self._wait.until(ec.visibility_of_element_located((By.XPATH, xpath_str)))
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        actions.click()
        actions.send_keys(text)
        actions.send_keys(Keys.RETURN).perform()

    def clear_fill_in_text(self, xpath_str, text):
        element = self._wait.until(ec.visibility_of_element_located((By.XPATH, xpath_str)))
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        time.sleep(0.25)
        actions = ActionChains(self.driver)
        element.clear()
        actions.move_to_element(element).perform()
        actions.click()
        actions.send_keys(text)
        actions.perform()

    def clear_fill_in_text_tab(self, xpath_str, text):
        element = self._wait.until(ec.visibility_of_element_located((By.XPATH, xpath_str)))
        actions = ActionChains(self.driver)
        element.clear()
        actions.move_to_element(element).perform()
        actions.click()
        actions.send_keys(text)
        actions.send_keys(Keys.TAB)
        actions.perform()


    def click_xpath(self, xpath_str):
        element = self._wait.until(ec.visibility_of_element_located((By.XPATH, xpath_str)))
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        actions.click()
        actions.perform()

    def right_click_xpath(self, xpath_str):
        element = self._wait.until(ec.visibility_of_element_located((By.XPATH, xpath_str)))
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        actions.context_click(element)
        actions.perform()

    def click_css(self, css_str):
        element = self._wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, css_str)))
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        actions.click()
        actions.perform()

    def click_element_in_list(self, xpath_str, index):
        element = self._wait.until(ec.visibility_of_all_elements_located((By.XPATH, xpath_str)))
        actions = ActionChains(self.driver)
        actions.move_to_element(element[index]).perform()
        actions.click()
        actions.perform()

    def element_click(self, element):
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        actions.click()
        actions.perform()

    def double_click_xpath(self, xpath_str):
        element = self._wait.until(ec.visibility_of_element_located((By.XPATH, xpath_str)))
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        actions.double_click(element)
        actions.perform()

    def drag_and_drop_mouse_xpath(self, xpath_from, xpath_to):
        element_from = self._wait.until(ec.visibility_of_element_located((By.XPATH, xpath_from)))
        element_to = self._wait.until(ec.visibility_of_element_located((By.XPATH, xpath_to)))
        actions = ActionChains(self.driver)
        actions.click(element_from).perform()
        time.sleep(0.25)
        actions.click_and_hold(element_from)
        actions.move_to_element(element_to).perform()
        time.sleep(0.25)
        actions.release()
        time.sleep(0.25)
        actions.perform()

    def drag_and_drop_xpath(self, xpath_from, xpath_to):
        element_from = self._wait.until(ec.visibility_of_element_located((By.XPATH, xpath_from)))
        element_to = self._wait.until(ec.visibility_of_element_located((By.XPATH, xpath_to)))
        actions = ActionChains(self.driver)
        actions.move_to_element(element_from).perform()
        actions.drag_and_drop(element_from,element_to)
        actions.perform()

    def drag_and_drop_offset_xpath(self, xpath_from, offset_x, offset_y):
        element_from = self._wait.until(ec.visibility_of_element_located((By.XPATH, xpath_from)))
        actions = ActionChains(self.driver)
        actions.move_to_element(element_from).perform()
        time.sleep(0.25)
        actions.drag_and_drop_by_offset( element_from, offset_x, offset_y)
        time.sleep(0.25)
        actions.perform()

    def remove_html_element(self, css_selector):
        element_css_selector = self._wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        time.sleep(0.25)
        self.driver.execute_script("arguments[0].scrollIntoView();", element_css_selector)
        time.sleep(0.25)
        self.driver.execute_script("arguments[0].parentNode.removeChild(arguments[0]);",element_css_selector)


    def __movedDownEnter__(self, xpStr, nbrofMoves):
        element = self._wait.until(ec.visibility_of_element_located((By.XPATH, xpStr)))
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        actions.click().perform()
        for i in range(nbrofMoves):
            actions.send_keys(Keys.DOWN)
        actions.perform()
        actions.send_keys(Keys.RETURN).perform()

    def __scrollToTop__(self):
        element = self.driver.find_element_by_tag_name("head")
        self.driver.execute_script("return arguments[0].scrollIntoView(true);", element)

    def scroll_to_element(self, xpath_str):
        element = WebDriverWait(self.driver, 120).until(ec.visibility_of_element_located((By.XPATH, xpath_str)))
        self.driver.execute_script("return arguments[0].scrollIntoView(true);", element)

    def __findTextAndClick__(self, text):
        self.driver.find_element_by_xpath("//*[contains(text(), '%s')]" % (text)).click()

    def get_text_xpath(self, xpath_str):
        element = self._wait.until(ec.visibility_of_element_located((By.XPATH, xpath_str)))
        return element.text

    def get_text_from_element(self, element):
        return element.text

    def __selectFromDropDown__(self, xpathStr, text):
        element = WebDriverWait(self.driver, 120).until(ec.visibility_of_element_located((By.XPATH, xpathStr)))
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        actions.click()
        actions.send_keys(text)
        actions.click()
        actions.perform()

    def select_drop_down_enter(self, xpath_str, text):
        element = self._wait.until(ec.visibility_of_element_located((By.XPATH, xpath_str)))
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        actions.click()
        actions.send_keys(text)
        actions.click()
        actions.send_keys(Keys.RETURN)
        actions.perform()

    def __selectFromDropDownByValue__(self, xpathStr, value):
        element = Select(WebDriverWait(self.driver, 120).until(ec.visibility_of_element_located((By.XPATH, xpathStr))))
        element.select_by_value(value)

    def wait(self, number_of_seconds):
        time.sleep(number_of_seconds)

    def split_stored_url(self, url_key):
        kv_store = KeyValueStore()
        url = kv_store.get_value_as_str(url_key)
        split_url = url.split('//')[1].split('/')
        counter = 1
        for section in split_url:
            if len(section) > 0:
                url_key_nbr = url_key + "_" + str(counter)
                counter += 1
                kv_store.add(url_key_nbr, section )
        kv_store.close()

    def split_url_and_store(self, key_prefix, value):
        split_url = value.split('//')[1].split('/')
        kv_store = KeyValueStore()
        counter = 1
        for section in split_url:
            if len(section) > 0:
                url_key_nbr = key_prefix + "_" + str(counter)
                counter += 1
                kv_store.add(url_key_nbr, section)
        kv_store.close()


    def format_string_and_store(self, key, value):
        kv_store = KeyValueStore()
        reformated_str = kv_store.replace_formated_key(value)
        kv_store.add(key, reformated_str)
        kv_store.close()

    def store_string(self, key, value):
        kv_store = KeyValueStore()
        kv_store.add(key,value)
        kv_store.close()

    def executeSequences(self, seq, g):

        for step in g.getSetup():
            self.execute_action(step.getAction())

        pa = seq.get()
        for l in pa:
            #logger.info("Excute sequence=%s" % (str(l)))
            for el in l:
                a = g.getVertex(el).getAction()
                self.execute_action(a)

    def execute_action(self, a):
        """
        TODO : error handling
        :param a:
        :return:
        """
        command_type = a.getElementType()
        if command_type == 'CLICKABLE':
            self.click_xpath(a.getXpathStr())
        elif command_type == 'TEXTABLE':
            if a.getValue() == None:
                rStr = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
            else:
                rStr = a.getValue()
            self.fill_in_text(a.getXpathStr(), rStr)
        elif command_type == 'JSexec':
            self.driver.execute_script(a.getXpathStr())
        elif command_type == 'SELECTABLE':
            self.click_element_in_list(a.getXpathStr(), 2)
        elif command_type == 'OPENURL':
            self.openurl(a.getValue())
        elif command_type == 'SCREENSHOT':
            self.screenshot(a.getValue())
        elif command_type == 'CLEARTEXTABLE':
            if a.getValue() == None:
                rStr = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
            else:
                rStr = a.getValue()
            self.clear_fill_in_text(a.getXpathStr(), rStr)
        elif command_type == 'CLEARTEXTABLETAB':
            if a.getValue() == None:
                rStr = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
            else:
                rStr = a.getValue()
            self.clear_fill_in_text_tab(a.getXpathStr(), rStr)
        elif command_type == 'TEXTABLE-ENTER':
            if a.getValue() == None:
                rStr = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
            else:
                rStr = a.getValue()
            self.fill_in_text_enter(a.getXpathStr(), rStr)
        elif command_type == 'COMPAREPNG':
            arguments = eval(a.getValue())
            filenameA = arguments[0]
            filenameB = arguments[1]
            cv = ComputerVision()
            result = cv.diff(filenameA, filenameB)
            assert result, 'Difference between %s and %s' % (filenameA, filenameB)
        elif command_type == 'COMPAREPNGPHASH':
            arguments = eval(a.getValue())
            filenameA = arguments[0]
            filenameB = arguments[1]
            cv = ComputerVision()
            result = cv.diff_with_phash_image_hash(filenameA, filenameB)
            assert result, 'Difference between %s and %s' % (filenameA, filenameB)
        elif command_type == 'WAIT':
            time.sleep(int(a.getValue()))
        elif command_type == 'SCROLLTOP':
            self.driver.execute_script("window.scrollTo(0,0);")
        elif command_type == 'SCROLLBOTTOM':
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        elif command_type == 'DUMMY':
            #command for testing purposes
            pass
        elif command_type == 'BROWSER_TABS_ADD':
            nbr_of_tabs = int(a.getValue())
            self.add_browser_tabs(nbr_of_tabs)
        elif command_type == 'BROWSER_TABS_GOTO':
            tab_nbr = int(a.getValue())
            self.goto_browser_tab( tab_nbr )
        elif command_type == 'BROWSER_TABS_GOTO_CURRENT':
            self.goto_current_browser_tab()
        elif command_type == "TEXT_CURRENT_POSITION":
            text = a.getValue()
            self.enter_text_current_position( text )
        elif command_type == "TEXT_CURRENT_POSITION_STAMP":
            text = a.getValue()
            self.enter_text_current_position_stamp( text )
        elif command_type == "TAB":
            text = a.getValue()
            self.enter_tab_current_position()
        elif command_type == "LOG_CURRENT_URL":
            self.log_current_url()
        elif command_type == "CLICKABLE_RIGHT":
            self.right_click_xpath(a.getXpathStr())
        elif command_type == "CLICKABLE_DOUBLE":
            self.double_click_xpath(a.getXpathStr())
        elif command_type == "DRAG_AND_DROP":
            from_xpath = a.getXpathStr()
            to_xpath = a.getValue()
            self.drag_and_drop_xpath( from_xpath, to_xpath )
        elif command_type == "DRAG_AND_DROP_MOUSE":
            from_xpath = a.getXpathStr()
            to_xpath = a.getValue()
            self.drag_and_drop_mouse_xpath(from_xpath, to_xpath)
        elif command_type == "GOTO_FRAME":
            self.goto_frame(a.getValue())
        elif command_type == "DRAG_AND_DROP_WITH_OFFSET":
            from_xpath = a.getXpathStr()
            offsets=a.getValue()
            offsets = offsets.split(',')
            self.drag_and_drop_offset_xpath( from_xpath, offsets[0], offsets[1])
        elif command_type == "SWITCH_TO_ALERT_AND_CONFIRM":
            the_alert = self.driver.switch_to.alert
            the_alert.accept()
        elif command_type == "REMOVE_HTML_ELEMENT":
            css_selector = a.getValue()
            self.remove_html_element(css_selector)
        elif command_type == "SAVE_CURRENT_URL":
            kv_store = KeyValueStore()
            kv_store.add( a.get_key(), self.driver.current_url )
            kv_store.close()
        elif command_type == "SPLIT_STORED_URL":
            self.split_stored_url( a.get_key() )
        elif command_type == "FORMAT_STRINGS":
            string_to_format = a.getValue()
            key_for_store = a.get_key()
            self.format_string_and_store(key_for_store, string_to_format)
        elif command_type == "STORE_STRING":
            string_to_store = a.getValue()
            key_for_store = a.get_key()
            self.store_string(key_for_store, string_to_store)
        elif command_type == "SPLIT_URL_AND_STORE":
            string_to_split = a.getValue()
            key_for_store = a.get_key()
            self.split_url_and_store(key_for_store, string_to_split)
        elif command_type == "OPEN_STORED_URL":
            kv_store = KeyValueStore()
            stored_key = a.get_key()
            url = kv_store.get_value_as_str(stored_key)
            self.logger.debug(url)
            self.openurl(url)
        elif command_type == "SELECT_FROM_DROP_DOWN":
            select_xpath = a.getXpathStr()
            some_text = a.getValue()
            self.select_drop_down_by_text((By.XPATH, select_xpath), some_text)
        else:
            assert False, "unknown command"
        waiting_time = a.get_wait_after()
        time.sleep(waiting_time)

class AbstractPage(Command):

    def __init__(self, driver, sleepTime=20, pollFrequency=1):
        super(AbstractPage, self).__init__(driver)
        self.sleepTime = sleepTime
        self.pollFrequency = pollFrequency

    def WaitUntilLoaded(self):
        aList = self.xPathWaitForList()
        for item in aList:
            wait = WebDriverWait(self.driver, self.sleepTime, poll_frequency=self.pollFrequency,
                                 ignored_exceptions=[ElementNotVisibleException])
            element = wait.until(ec.presence_of_all_elements_located((By.XPATH, item)))
            time.sleep(self.sleepTime)
        return True

    def xPathWaitForList(self):
        raise NotImplementedError()

    def __fillInTextAtIndex__(self, xpathStr, text, index=0):
        element = WebDriverWait(self.driver, 120).until(ec.visibility_of_all_elements_located((By.XPATH, xpathStr)))
        actions = ActionChains(self.driver)
        actions.move_to_element(element[index]).perform()
        actions.click()
        actions.send_keys(text)
        actions.perform()
