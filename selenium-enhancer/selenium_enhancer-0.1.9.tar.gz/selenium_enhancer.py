#!/usr/bin/env python
import os
import contextlib
from selenium import webdriver
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


class SeleniumEnhancer(object):
    """
        Parent class that assists with Selenium testing and automation.

        This class is built to be inherited by classes that will benefit 
        from the enhanced Selenium web driver functionality within.

        Methods are arranged alphabetically for value.
    """


    def accept_simple_alert(self):
        """ Method clicks the OK button in a pop-up alert. 
        
            Only use this when *sure* of an alert, otherwise it will 
            loop infinitiely looking for one.
        """
        while True:
            try:
                alert = self.driver.switch_to.alert
                alert.accept()
                break
            except NoAlertPresentException:
                continue 


    def attach_image_file_to_input(self, input_id, img_path):
        """ Method to attach an image file to input with type="file".

            Requires two strings: a partial/unique id of an input element
            and the path of an image file (relative to working directory).
        """
        self.driver.find_element_by_xpath(
            f"//input[contains(@id, '{input_id}')]"
        ).send_keys(os.getcwd()+img_path)


    def check_box(self, checkbox_id, uncheck=False, return_status=False):
        """ Method's default behavior is to check unchecked boxes.

            Requires a string equal to a partial/unique id or XPath.

            * Optional arguments/behavior *
            uncheck=True -- will instead uncheck a checked box.
            return_status=True -- instead returns checked status
        """
        try:
            element = self.driver.find_element_by_xpath(
                f"//*[contains(@id, '{checkbox_id}')]"
            )
        except NoSuchElementException:
            element = self.driver.find_element_by_xpath(checkbox_id)
        
        if return_status:
            if element.is_selected():
                return True
            else:
                return False

        if not uncheck: # make sure specified element is checked
            if not element.is_selected():
                element.click()
        else: # if uncheck=True, make sure specified element is unchecked
            if element.is_selected():
                element.click()


    def check_for_presence_of_element(self, element_id):
        """ Method returns True if element exists or False if not.

            Takes partial but unique ID, XPath, or CSS selector.
        """

        try:
            self.driver.find_element_by_xpath(
                f"//*[contains(@id, '{element_id}')]"
            )
        except NoSuchElementException:
            try:
                self.driver.find_element_by_xpath(element_id)
            except NoSuchElementException:
                try:
                    self.driver.find_element_by_css_selector(element_id)
                except NoSuchElementException:
                    return False
        return True


    def clear_input_element(self, element_id):
        """ Method to clear an input element.

            Requires a string equal to a partial/unique id or XPath.
        """
        try:
            self.driver.find_element_by_xpath(
                f"//*[contains(@id, '{element_id}')]"
            ).clear()
        except NoSuchElementException:
            self.driver.find_element_by_xpath(element_id).clear()


    def click_button(self, identifier, dbl_click=False, no_js=False):
        """ Method to click an element (with JavaScript by default).

            Requires a string identifier that can be a partial/unique
            id, CSS selector, or XPath.

            * Optional arguments/behavior *
            dbl_click=True --  double clicks the element.
            no_js=True -- mimic user click rather than click with JS
        """
        attempts = 0
        while True:
            try:
                element = self.driver.find_element_by_xpath(
                    f"//*[contains(@id, '{identifier}')]"
                )
            except StaleElementReferenceException:
                attempts += 1
                if attempts > 5:
                    print(f"Match for \"{identifier}\" can't be found!")
                    break
                continue
            except NoSuchElementException:
                try: # try to find the element by CSS selector
                    element = self.driver.find_element_by_css_selector(
                        f"{identifier}"
                    )
                except NoSuchElementException:
                    try: # try to find element by xpath
                        element = self.driver.find_element_by_xpath(
                            f"{identifier}"
                        )
                    except NoSuchElementException:
                        attempts += 1
                        if attempts > 5:
                            print(
                                "Cannot find element by ID, CSS selector, or "
                                f"XPath:\n\n\t{identifier}\n\nPlease send a "
                                "valid selection string of one of these types."
                            )
                            break
            if dbl_click:
                action = ActionChains(self.driver)
                action.double_click(element).perform()
            elif no_js: # for use cases where one wants to explicitly ignore JS
                action = ActionChains(self.driver)
                action.move_to_element(element).click(element).perform()
            else: # default case
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                except UnboundLocalError: # Try a no JS click as a fail case
                    action = ActionChains(self.driver)
                    action.move_to_element(element).click(element).perform()
            break


    def get_text_of_current_selection(self, element_id):
        """ Method returns selected text from a select element.

            Takes an id only (for now).
        """

        try:
            select_element = Select(self.driver.find_element_by_id(element_id))
        except NoSuchElementException:
            return ""
        else:
            return select_element.first_selected_option.text


    def get_text_from_element(self, element_id, input=False):
        """ Method returns text from an element.

            Requires a string identifier that can be a partial/unique
            id, CSS selector, or XPath.

            If trying to get the current text/value from an input
            element, include `input=True` to do so.
        """
        try: # returns by exact match of ID
            element = self.driver.find_element_by_id(element_id)
        except NoSuchElementException:
            try: # returns by partial but unique ID
                element = self.driver.find_element_by_xpath(
                    f"//*[contains(@id, '{element_id}')]"
                )
            except NoSuchElementException: # returns by full xpath
                try:
                    element = self.driver.find_element_by_xpath(element_id)
                except NoSuchElementException: # returns by CSS selector
                    element = self.driver.find_element_by_css_selector(
                        element_id
                    )
        finally:
            if input:
                return element.get_property("value")
            else:
                return element.text


    def set_input_elements(self, data, clear=False):
        """ Method to set any number of text input elements on a page.

            Requires a dictionary with at least one key-value pair but
            can be any size. Keys must be an identifier that can be a
            partial/unique id or XPath. Values should be the desired
            text corresponding to each identifier.

            clear=True will clear the elements first
        """
        for key, value in data.items():
            # Select each input and textarea element
            try: # partial but unique ids are easiest
                element = self.driver.find_element_by_xpath(
                    f"//*[contains(@id, '{key}')]"
                )

            except NoSuchElementException:

                try: # xpaths are allowed for inputs without id attributes
                    element = self.driver.find_element_by_xpath(key)
                except NoSuchElementException:
                    print(f"Element matching {key} can't be found!")

            except ElementNotInteractableException:
                # the csc field (only) on the payment page requires this ...?
                element = self.driver.find_element_by_xpath(
                    f"//input[contains(@name, '{key}')]"
                )
            
            # If specified, clear input element first
            if clear:
                element.clear()

            # Finally, send the value
            element.send_keys(value)


    def set_select_elements(self, data):
        """ Method to choose any number of select elements on a page.

            Requires a dictionary with at least one key-value pair but
            can be any size. Keys must be an identifier that can be a
            partial/unique ~name~ or ID. Values should be the text of 
            the desired option to select.
        """

        type_ = ""
        for key, value in data.items():
            # Select each <select> element
            try:
                element = Select(self.driver.find_element_by_xpath(
                    f"//select[contains(@name, '{key}')]"
                ))
                type_ = "name"
            except NoSuchElementException:
                try:
                    element = Select(self.driver.find_element_by_xpath(
                        f"//select[contains(@id, '{key}')]"
                    ))
                    type_ = "id"
                except NoSuchElementException:
                    print(f"Element matching \"{key}\" cannot be found!")


            # Try by full text
            try:
                element.select_by_visible_text(value)

            except NoSuchElementException:
                try:
                    self.driver.find_element_by_xpath(
                        f"//select[contains(@{type_}, '{key}')]"
                        f"/option[contains(., '{value}')]"
                    ).click()
                except:
                    print(f"Option matching {value} not found!")




    def start_chrome_driver(self, 
                            detach=False, 
                            headless=False,
                            ga_debug=False):
        """ Method to start the Chrome driver with specified options. 
        
            This is where I do most of my work and thus has the most
            extensive option list. 
        """

        # must set environment variable CHROME_DRIVER equal to local path
        CHROME_PATH = os.environ['CHROME_DRIVER']
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-infobars")

        # Supress unwanted DevTools messages
        chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-logging"]
        )

        # If desired, the next option detaches the browser from driver
        # Thus allowing the browser to stay open after driver closes
        # The downside is the requirement to manually close browsers
        if detach:
            chrome_options.add_experimental_option("detach", True)

        # This causes Chrome to run in the background.
        if headless:
            chrome_options.add_argument("--headless")

        # Use this option to include the Google Analytics debugger
        # Will still need to activate with a coordinates click
        if ga_debug:
            extension_path = (
                os.path.dirname(os.path.abspath(__file__)) +
                "/data/Google-Analytics-Debugger_v2.8.crx.crx"
            )
            chrome_options.add_extension(extension_path)

        self.driver = webdriver.Chrome(
            options=chrome_options,
            executable_path=CHROME_PATH
        )
        self.driver.implicitly_wait(1)
        self.driverwait = WebDriverWait(self.driver, 10)


    def start_ie_driver(self):
        """ Method to start the Internet Explorer driver. """

        IE_PATH = os.environ['IE_DRIVER']
        # must set environment variable IE_DRIVER equal to local path
        self.driver = webdriver.Ie(executable_path=IE_PATH)
        self.driver.implicitly_wait(1)


    def start_firefox_driver(self):
        """ Method to start the Firefox driver with specified optons. """

        FIREFOX_PATH = os.environ['FIREFOX_DRIVER']
        # must set environment variable FIREFOX_DRIVER equal to local path
        self.options = webdriver.FirefoxOptions()
        self.driver = webdriver.Firefox(executable_path=FIREFOX_PATH)
        self.driver.find_element_by_xpath('/html/body').send_keys(Keys.F11)
        # self.driver.implicitly_wait(1)


    def switch_to_iframe(self, iframe_id):
        """ Method to switch to an iframe on a page.

            Requires a string identifier that can be a partial/unique
            id or Xpath.
        """
        try:
            WebDriverWait(self.driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it(
                    self.driver.find_element_by_xpath(
                        f"//iframe[@id='{iframe_id}']"
                    )
                )
            )
        except InvalidSelectorException:
            WebDriverWait(self.driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it(
                    self.driver.find_element_by_xpath(iframe_id)
                )
            )


    @contextlib.contextmanager
    def wait_for_page_load(self, timeout=10):
        """ Method to wait for page to load before continuing.

            This method checks for the staleness of the old page
            (i.e., that the new page has loaded) prior to moving
            forward with further actions. Therefore, it only
            works in situations where the URL changes between
            page loads. 

            Usage:

            with self.wait_for_page_load():
                # click a button or do whatever
            # do the next thing that was failing before using this

            Thanks to ObeyTheTestingGoat for this delightfully
            borrowed method!
        """
        old_page = self.driver.find_element_by_tag_name('html')
        yield
        WebDriverWait(self.driver, timeout).until(staleness_of(old_page))
