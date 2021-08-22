from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from datetime import datetime
currentime = str(datetime.now())

class nzxvirtualtrader():
    __version__ = '0.0.1'

    username = ''
    password = ''

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_tickers(self):
        """ returns list of dictionary's of available stocks, bid and ask price, ticker and company name"""
        # Run with Chrome window Hidden
        options = Options()
        options.headless = True
        options.add_argument("--window-size=1920,1200")
        DRIVER_PATH = 'C:/Users/hazza/Documents/Programming/WebDriver/chromedriver'
        driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
        driver.get("https://virtualtrading.nzx.com/")

        # Run with Chrome window visible
        # DRIVER_PATH = 'C:/Users/hazza/Documents/Programming/WebDriver/chromedriver'
        # driver = webdriver.Chrome(executable_path=DRIVER_PATH)
        # driver.get("https://virtualtrading.nzx.com/")

        # Get To the Trading Page
        LoginButton = driver.find_element_by_xpath(
            '//*[@id="nav"]/div[2]/a').click()
        UsernameInput = driver.find_element_by_xpath(
            '//*[@id="registered_customers"]/form/table/tbody/tr[1]/td[2]/input').send_keys(self.username)
        PasswordInput = driver.find_element_by_xpath(
            '//*[@id="registered_customers"]/form/table/tbody/tr[2]/td[2]/input').send_keys(self.password)
        LoginButton = driver.find_element_by_xpath(
            '//*[@id="registered_customers"]/form/table/tbody/tr[4]/td/div/input').click()
        TradeEquitiesButton = driver.find_element_by_xpath(
            '//*[@id="sub_nav"]/li[3]/a').click()

        # Class Properties
        Tickers = driver.find_elements_by_class_name('c-sym')
        Company = driver.find_elements_by_class_name('c-description')
        Bid = driver.find_elements_by_class_name('c-bid')
        Ask = driver.find_elements_by_class_name('c-ask')

        RawStockData = []
        for i in range(0, len(Tickers)):
            stock = {
                'Ticker': str(Tickers[i].text).strip(),
                'Company': str(Company[i].text).strip(),
                'Bid': str(Bid[i].text).strip(),
                'Ask': str(Ask[i].text).strip(),
                'Time': str(currentime).strip()
            }
            RawStockData.append(stock)
        # print(driver.page_source)
        driver.quit()
        return RawStockData

    #print(*Scrape(), sep = "\n")

    #Order Virtual Stock: OrderStock('AIR', '1', 'Buy')
    def order(self, symbol, quantity, buy=True, duration=True, price_action='Market', section1=None, section2=None):
        """
        param:
            symbol: stock ticker
            quantity: number of stocks to buy or sell
            Buy: True=Buy or False=Sell
            duration: True=Good Until Cancelled or False=Good For Day
            price_action: Market, Limit, Stop or Stop Limit. refer to https://virtualtrading.nzx.com/virtual/order/stock/#help-select-price
            section1: str, if priceaction takes top input, input here or leave blank
            section2: str, if priceaction takes bottom input, input here or leave blank
        """
        # Run with Chrome window Hidden
        options = Options()
        options.headless = True
        options.add_argument("--window-size=1920,1200")
        DRIVER_PATH = 'C:/Users/hazza/Documents/Programming/WebDriver/chromedriver'
        driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
        driver.get("https://virtualtrading.nzx.com/")

        # Run with Chrome window visible
        # DRIVER_PATH = 'C:/Users/hazza/Documents/Programming/WebDriver/chromedriver'
        # driver = webdriver.Chrome(executable_path=DRIVER_PATH)
        # driver.get("https://virtualtrading.nzx.com/")

        # Login
        LoginButton = driver.find_element_by_xpath(
            '//*[@id="nav"]/div[2]/a').click()
        UsernameInput = driver.find_element_by_xpath(
            '//*[@id="registered_customers"]/form/table/tbody/tr[1]/td[2]/input').send_keys(self.username)
        PasswordInput = driver.find_element_by_xpath(
            '//*[@id="registered_customers"]/form/table/tbody/tr[2]/td[2]/input').send_keys(self.password)
        LoginButton = driver.find_element_by_xpath(
            '//*[@id="registered_customers"]/form/table/tbody/tr[4]/td/div/input').click()
        # get to trade equites page
        TradeEquitiesButton = driver.find_element_by_xpath(
            '//*[@id="sub_nav"]/li[3]/a ').click()
        # input symbol
        SymbolInput = driver.find_element_by_xpath(
            '//*[@id="formtools_security"]').send_keys(symbol)
        #input quantity
        QuantityInput = driver.find_element_by_xpath(
            '//*[@id="formtools_quantity"]').send_keys(quantity)
        #select buy or sell
        SelectAction = driver.find_element_by_xpath(
            '//*[@id="formtools_action"]')
        if buy:  # buy
            BuySelectButton = driver.find_element_by_xpath(
                '//*[@id="formtools_action"]/option[2]').click()
        elif not buy:  # sell
            AskSelectButton = driver.find_element_by_xpath(
                '//*[@id="formtools_action"]/option[3]').click()
        # select duration
        if not duration:
            SelectDuration = driver.find_element_by_xpath(
            '/html/body/div/div[1]/div[4]/div[1]/div[2]/form/div[1]/select[2]')
            SelectDuration = driver.find_element_by_xpath(
            '/html/body/div/div[1]/div[4]/div[1]/div[2]/form/div[1]/select[2]/option[2]').click()
        # Select Price Action
        if price_action != 'Market':
            if price_action == 'Limit':
                SelectDuration = driver.find_element_by_xpath(
                '/html/body/div/div[1]/div[4]/div[1]/div[2]/form/div[2]/ul/li[2]/input[1]').click()
            elif price_action == 'Stop':
                SelectDuration = driver.find_element_by_xpath(
                '/html/body/div/div[1]/div[4]/div[1]/div[2]/form/div[2]/ul/li[3]/input[1]').click()
            elif price_action == 'Stop Limit':
                SelectDuration = driver.find_element_by_xpath(
                '/html/body/div/div[1]/div[4]/div[1]/div[2]/form/div[2]/ul/li[4]/input').click()
        # Input Price inputs
        if section1:
            SectionInput = driver.find_element_by_xpath(
                '/html/body/div/div[1]/div[4]/div[1]/div[2]/form/div[2]/ul/li[2]/input[2]').send_keys(section1)
        if section2:
            SectionInput = driver.find_element_by_xpath(
                '/html/body/div/div[1]/div[4]/div[1]/div[2]/form/div[2]/ul/li[3]/input[2]').send_keys(section2)

        PreveiwTrade = driver.find_element_by_xpath(
            '//*[@id="order-preview"]').click()
        PlaceTrade = driver.find_element_by_xpath(
            '//*[@id="left_and_middle_col"]/form[2]/p/input').click()
            
        driver.quit()

