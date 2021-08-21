from selenium import webdriver
import time

def get_time(time_format="standard"):
    """
    Returns the current local time in a given format.

    Kwargs:
        time_format='standard' -> returns format: '2021-03-21 06:24:14'
        time_format='numeric'  -> returns format: '202103210624'

    """
    if time_format == "numeric":
        # 12 digit, all numeric.  Useful as a concise timestamp
        return time.strftime("%Y%m%d%H%M", time.localtime())
    else:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def disable_logging(**kwargs):
    """ Experimental: run selenium in silent mode """
    options = webdriver.ChromeOptions()
    options.headless = kwargs.get("headless")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return options

class Login_to:
    """
    A collection of common login functions for a variety of websites.
    Each receives a (CleverSession) object (self) as its argument, typically
    comprising:

    .browser : a selenium webbrowswer object that has already been initialised
    .username : typically derived from CleverSession and keyring
    .password : typically a CleverSession @property based on keyring
    .login_url : URL to provide login credentials to

    the .add_current_browser() method appends the current (login) browser to
    self.browsers list.
    """

    @staticmethod
    def hackerrank(self, **kwargs):
        """ Use selenium and CleverSession credentials to login to HackerRank """
        self.login_url = r"https://www.hackerrank.com/auth/login?h_l=body_middle_left_button&h_r=login"
        self.browser.get(self.login_url)
        self.browser.find_element_by_id("input-1").send_keys(self.username)
        self.browser.find_element_by_id("input-2").send_keys(self.password)
        self.browser.find_element_by_xpath('//*[@id="tab-1-content-1"]/div[1]/form/div[4]/button').click()
        self.add_current_browser()

    @staticmethod
    def fb_marketplace(self, **kwargs):
        """ Use selenium and CleverSession credentials to login to Github """
        self.browser.get(self.login_url)
        xpath = '//*[@id="facebook"]/body/div[2]/div[1]/div/div[2]/div/div/div/div/div[1]/div/div[3]/div/div[1]/div[1]/div/div[1]/div/span/span'
        self.browser.find_element_by_xpath(xpath).click()
        xpath = '//*[@id="login_form"]/div[2]/div[3]/div/div/div[1]/div/span/span'
        self.browser.find_element_by_xpath(xpath).click()
        self.browser.find_element_by_id("email").send_keys(self.username)
        self.browser.find_element_by_id("pass").send_keys(self.password)
        self.browser.find_element_by_name("login").click()
        xpath = '//*[@id="facebook"]/body/div[2]/div[1]/div/div[2]/div/div/div/div/div[1]/div/div[3]/div/div[1]/div[1]/div/div[1]/div/span/span'
        self.browser.find_element_by_xpath(xpath).click()
        self.add_current_browser()
        def search(search_string):
            xpath = '//*[@id="mount_0_0_lY"]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[1]/div/div[2]/div/span/div/div/div/div/label/input'
            search_box = self.browser.find_element_by_xpath(xpath)
            search_box.send_keys(Keys.SHIFT+Keys.HOME+Keys.DELETE)
            search_box.send_keys(search_string)
            search_box.send_keys(Keys.RETURN)
        setattr(self, "search", search)


    @staticmethod
    def github(self, **kwargs):
        """ Use selenium and CleverSession credentials to login to Github """
        self.browser.get(self.login_url)
        self.browser.find_element_by_id("login_field").send_keys(self.username)
        self.browser.find_element_by_id("password").send_keys(self.password)
        self.browser.find_element_by_name("commit").click()
        self.add_current_browser()

    @staticmethod
    def twitter(self, **kwargs):
        """ Use selenium and CleverSession credentials to login to Github """
        self.browser.get(self.login_url)
        self.browser.find_element_by_name("session[username_or_email]").send_keys(self.username)
        self.browser.find_element_by_name("session[password]").send_keys(self.password)
        span = self.browser.find_elements_by_tag_name("span")
        [x for x in span if x.text=="Log in"][0].click()
        self.add_current_browser()

    @staticmethod
    def office365(self, **kwargs):
        """ Use selenium and CleverSession credentials to login to Office365 """
        self.browser.get(self.login_url)
        self.browser.find_element_by_id("i0116").send_keys(self.username)
        self.browser.find_element_by_id("idSIButton9").click()
        self.browser.find_element_by_id("i0118").send_keys(self.password)
        time.sleep(2)
        self.browser.find_element_by_id("idSIButton9").click()
        self.add_current_browser()


    @staticmethod
    def satchelone(self, **kwargs):
        """ Use selenium and CleverSession credentials to login to SatchelOne
        """
        # from satchelone_config import userid, pw
        self.browser.get(self.login_url)
        main_window = self.browser.window_handles[0]
        span = self.browser.find_elements_by_tag_name("span")
        [x for x in span if x.text=="Sign in with Office 365"][0].click()
        popup_window = self.browser.window_handles[1]
        self.browser.switch_to.window(popup_window)
        Login_to.office365()
        self.browser.switch_to.window(main_window)
        print("\n ⓘ  Waiting for SatchelOne dashboard to appear...")
        while self.browser.current_url != 'https://www.satchelone.com/dashboard':
            continue
        print("\n ✓  OK we're in!\n")
        self.add_current_browser()
