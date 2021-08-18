import time
from bs4 import BeautifulSoup
from selenium import webdriver
from threading import *
import os,signal
import threading
import requests

class AmazonScraper:
    '''
    ### AmazonScraper an amazon scraper class.
    ### 1st param: which driver to use > options are 'chrome' and 'firefox'
    ### 2nd param: $PATH check > options are "DEFAULT", "GIVEN" , "PACKAGE"
    ### 3rd param: full path of webdriver necessary when 2nd param is "GIVEN"
    '''
    def __init__(self, which_driver = "chrome", full_path= None, url = "https://www.amazon.in/",):
        self.pwd = os.path.abspath(os.getcwd())
        self.which_driver = which_driver
        self.full_path = full_path
        self.amazonURL = url
        self.pageCount = 1
        self.web_driver = None
        self.soup_data = None
        self.data_list = dict()
        self.single_product_list = dict()
    
    def kill_process(self):
        try:
                
            # terminating process
            os.kill(int(self.web_driver.service.process.pid), signal.SIGKILL)
            print("Process Successfully terminated")
            
        except:
            print("Error Encountered while running script")
    
    def check_conn(self):
        timeout = 5
        try:
            request = requests.get(self.amazonURL, timeout=timeout)
            print("Connected to the Internet")
            return True
        except (requests.ConnectionError, requests.Timeout) as exception:
            print("No internet connection.")
            return False
    
    def load_mozila_driver(self, path, check = False):
        start_time = time.time()
        # Firefox
        try:
            opts = webdriver.FirefoxOptions()
            opts.headless = True
            self.web_driver = webdriver.Firefox(path, options=opts)
            print('Mozila open...')
            if check:
            # Calculate time
                print("--- %s seconds ---" % (time.time() - start_time))
            return True
        except Exception as e:
            return False

    def load_chrome_driver(self, path, check = False):
        start_time = time.time()
        # Chrome
        try:
            login = "amazon_web_scraper"
            chromeOptions = webdriver.ChromeOptions() 
            chromeOptions.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) 
            chromeOptions.add_argument("--no-sandbox") 
            chromeOptions.add_argument("--disable-setuid-sandbox") 
            chromeOptions.add_argument("--disable-dev-shm-using") 
            chromeOptions.add_argument("--disable-extensions") 
            chromeOptions.add_argument("start-maximized") 
            chromeOptions.add_argument("disable-infobars") 
            chromeOptions.add_argument("--headless") 
            chromeOptions.add_argument(r"user-data-dir=.\cookies\\" + login) 
            
            self.web_driver = webdriver.Chrome(executable_path=path, options=chromeOptions)
            print('Chrome open...')
            if check:
            # Calculate time
                print("--- %s seconds ---" % (time.time() - start_time))
            return True
        except Exception as e:
            print(path)
            print(e)
            return False

    def open_web_driver(self, check = False):
        # print(os.environ)
        start_time = time.time()
        if self.which_driver == "chrome":
            if self.full_path:
                path = self.full_path
            else:
                path = None
            try:
                return self.load_chrome_driver(path, check)
            except Exception:
                return False
        elif self.which_driver == "firefox":
            if self.full_path:
                path = self.full_path
            else:
                path = None
            try:
                return self.load_mozila_driver(path, check)
            except Exception:
                return False
        if check:
            # Calculate time
            print("--- %s seconds ---" % (time.time() - start_time))
        return True
    
    def close_web_driver(self, check = False):
        start_time = time.time()
        try:
            self.web_driver.close()
            print("Closing webdriver...")
            self.kill_process()
        except Exception as e:
            print(e)
        finally:
            if check:
            # Calculate time
                print("--- %s seconds ---" % (time.time() - start_time))
            return True

    def run_driver_set_data(self, url, check = False):
        if self.open_web_driver(check) is True:
            try:
                # fire get URL
                if check:
                    print(url)
                self.web_driver.get(url)
                
                # parse html data with bs4
                self.soup_data = BeautifulSoup(self.web_driver.page_source, 'html.parser')
                
            except Exception as e:
                print(e)
            finally:
                self.close_web_driver(check)
                return True
        else:
            return False

    def amazon_search_url(self, search_text):
        # generate url from search text
        search_text = search_text.replace(' ','+')
        if self.pageCount > 1:
            return "{}s?k={}&page={}".format(self.amazonURL, search_text.lower(), str(self.pageCount))
        else : 
            return "{}s?k={}".format(self.amazonURL, search_text.lower())

    def amazon_product_search(self, search_text, page= 1,check = False):
        start_time = time.time()
        self.pageCount = page
        # threads = list()
        url = self.amazon_search_url(search_text)
        if self.run_driver_set_data(url, check) is False:
            return False
        results =  self.soup_data.find_all('div', {'data-component-type' : 's-search-result'})
        if check:
            self.check_conn()
        count = 0
        for data in results:
            self.data_list[str(count)] = dict()
            try:
                T1_time = time.time()
                T1 = threading.Thread(target=self.get_product_search_name, args=(data,count,))
                T1.start()
                T2_time = time.time()
                T2 = threading.Thread(target=self.get_product_search_url, args=(data,count,))
                T2.start()
                T3_time = time.time()
                T3 = threading.Thread(target=self.get_product_search_price, args=(data,count,))
                T3.start()
                T4_time = time.time()
                T4 = threading.Thread(target=self.get_product_search_price_symbol, args=(data,count,))
                T4.start()
                T5_time = time.time()
                T5 = threading.Thread(target=self.get_product_search_whole_price, args=(data,count,))
                T5.start()
                T6_time = time.time()
                T6 = threading.Thread(target=self.get_product_search_image, args=(data,count,))
                T6.start()
                if check:
                    print("<<<<===========================>>>>>")
            except Exception as e:
                if check:
                    print(e)
                else:
                    pass
            finally:
                T1.join()
                if check:
                    print("T1--- %s seconds ---" % (time.time() - T1_time))
                T2.join()
                if check:
                    print("T2--- %s seconds ---" % (time.time() - T2_time))
                T3.join()
                if check:
                    print("T3--- %s seconds ---" % (time.time() - T3_time))
                T4.join()
                if check:
                    print("T4--- %s seconds ---" % (time.time() - T4_time))
                T5.join()
                if check:
                    print("T5--- %s seconds ---" % (time.time() - T5_time))
                T6.join()
                if check:
                    print("T6--- %s seconds ---" % (time.time() - T6_time))
                count+=1
        exs_time = time.time()
        if check:
            # Calculate time
            print("--- %s seconds ---" % (time.time() - start_time))
        print("EX--- %s seconds ---" % (time.time() - exs_time))
        return self.data_list

    def get_product_search_name(self, data, count):
        productNameHref = data.h2.a
        self.data_list[str(count)]['product_name'] = productNameHref.text.strip()
        return


    def get_product_search_url(self, data, count):
        productNameHref = data.h2.a
        self.data_list[str(count)]['product_url'] = self.amazonURL + productNameHref.get('href')
        return

    def get_product_search_price(self, data, count):
        price_with_symbol = "N/A"
        try:
            price_with_symbol = data.find('span', {'class' : 'a-price'}).find('span', {'class' : 'a-offscreen'}).text
        except Exception as e:
            pass
        finally:
            self.data_list[str(count)]['product_price'] = price_with_symbol
        return

    def get_product_search_price_symbol(self, data, count):
        price_symbol = "N/A"
        try:
            price_symbol = data.find('span', {'class' : 'a-price'}).find('span', {'class' : 'a-price-symbol'}).text
        except Exception as e:
            pass
        finally:
            self.data_list[str(count)]['product_price_symbol'] = price_symbol
        return

    def get_product_search_whole_price(self, data, count):
        price_whole = "N/A"
        try:
            price_whole = data.find('span', {'class' : 'a-price'}).find('span', {'class' : 'a-price-whole'}).text
        except Exception as e:
            pass
        finally:
            self.data_list[str(count)]['product_price_whole'] = price_whole
        return

    def get_product_search_image(self, data, count):
        product_image = data.find('img', {'class' : 's-image'})
        product_image_src = product_image.get('src')
        self.data_list[str(count)]['product_image_src'] = product_image_src
        return

    def get_single_product_details(self, url,check = False):
        start_time = time.time()
        if self.run_driver_set_data(url, check) is False:
            return False
        try:
            T1_time = time.time()
            T1 = threading.Thread(target=self.single_product_landing_img, args=(check,))
            T1.start()
            T2_time = time.time()
            T2 = threading.Thread(target=self.single_product_category, args=(check,))
            T2.start()
            T3_time = time.time()
            T3 = threading.Thread(target=self.single_product_title, args=(check,))
            T3.start()
            T4_time = time.time()
            T4 = threading.Thread(target=self.single_product_seller, args=(check,))
            T4.start()
            T5_time = time.time()
            T5 = threading.Thread(target=self.single_product_delivery_date, args=(check,))
            T5.start()
            T6_time = time.time()
            T6 = threading.Thread(target=self.single_product_price, args=(check,))
            T6.start()
            T7_time = time.time()
            T7 = threading.Thread(target=self.single_product_details, args=(check,))
            T7.start()
            T8_time = time.time()
            T8 = threading.Thread(target=self.single_product_price_only, args=(check,))
            T8.start()
        except Exception as e:
            pass
        finally:
            T1.join()
            if check:
                print("T1--- %s seconds ---" % (time.time() - T1_time))
            T2.join()
            if check:
                print("T2--- %s seconds ---" % (time.time() - T2_time))
            T3.join()
            if check:
                print("T3--- %s seconds ---" % (time.time() - T3_time))
            T4.join()
            if check:
                print("T4--- %s seconds ---" % (time.time() - T4_time))
            T5.join()
            if check:
                print("T5--- %s seconds ---" % (time.time() - T5_time))
            T6.join()
            if check:
                print("T6--- %s seconds ---" % (time.time() - T6_time))
            T7.join()
            if check:
                print("T7--- %s seconds ---" % (time.time() - T7_time))
            T8.join()
            if check:
                print("T8--- %s seconds ---" % (time.time() - T8_time))
            exs_time = time.time()
            if check:
                # Calculate time
                print("--- %s seconds ---" % (time.time() - start_time))
            print("EX--- %s seconds ---" % (time.time() - exs_time))
        return self.single_product_list

    def single_product_landing_img(self, check = False):
        try:
            landing_image = self.soup_data.find('img', {'data-a-image-name' : 'landingImage'}).get('src')
        except Exception as e:
            if check:
                print(e)
            else:
                pass
        finally:
            self.single_product_list['product_image'] = landing_image
        return

    def single_product_category(self, check = False):
        category_list = []
        try:
            categories = self.soup_data.find('div', {'id' : 'wayfinding-breadcrumbs_feature_div'}).find_all('a', {'class' : 'a-link-normal a-color-tertiary'})
            for a in categories:
                category_list.append(a.text.strip())
        except Exception as e:
            if check:
                print(e)
            else:
                pass
        finally:
            self.single_product_list['product_categories'] = category_list
        return

    def single_product_title(self, check = False):
        try:
            title = self.soup_data.find('span', {'id' : 'productTitle'}).text.strip()
        except Exception as e:
            if check:
                print(e)
            else:
                pass
        finally:
            self.single_product_list['product_title'] = title
        return

    def single_product_seller(self, check = False):
        try:
            seller = self.soup_data.find('a', {'id' : 'bylineInfo'}).text.strip()
        except Exception as e:
            if check:
                print(e)
            else:
                pass
        finally:
            self.single_product_list['product_seller'] = seller
        return

    def single_product_delivery_date(self, check = False):
        try:
            date = self.soup_data.find('div', {'id' : 'ddmDeliveryMessage'}).b.text.strip()
        except Exception as e:
            if check:
                print(e)
            else:
                pass
        finally:
            self.single_product_list['product_delivery'] = date
        return

    def single_product_price(self, check = False):
        sell_price = "₹0.00"
        try:
            sell_price = self.soup_data.find('span', {'id' : 'priceblock_ourprice'}).text.strip()
        except Exception as e:
            try:
                sell_price = self.soup_data.find('span', {'id' : 'currencyINR'}).text.strip()
            except Exception as e:
                try:
                    sell_price = self.soup_data.find('span', {'id' : 'priceblock_dealprice'}).text.strip()
                    pass
                except Exception as e:
                    if check:
                        print(e)
                if check:
                    print(e)
            if check:
                print(e)
            else:
                pass
        finally:
            self.single_product_list['product_price'] = sell_price
        return

    def single_product_price_only(self, check = False):
        sell_price = "₹0.00"
        try:
            sell_price = self.soup_data.find('span', {'id' : 'priceblock_ourprice'}).text.strip()
        except Exception as e:
            try:
                sell_price = self.soup_data.find('span', {'id' : 'currencyINR'}).text.strip()
            except Exception as e:
                if check:
                    print(e)
            if check:
                print(e)
            else:
                pass
        finally:
            self.single_product_list['product_price_only'] = sell_price[1:] if sell_price and len(sell_price) else ""
        return

    def single_product_details(self, check = False):
        try:
            try:
                top_details = self.soup_data.find('table', {'class' : 'a-normal a-spacing-micro'}).prettify()
            except Exception:
                top_details = ""
            try:
                bullet_details = self.soup_data.find('div', {'id' : 'feature-bullets'}).prettify()
            except Exception:
                bullet_details = ""
            try:
                product_details = self.soup_data.find('div', {'id' : 'prodDetails'}).prettify()
            except Exception:
                product_details = ""
        except Exception as e:
            if check:
                print(e)
            else:
                pass
        finally:
            self.single_product_list['product_details'] = top_details + bullet_details + product_details
        return

    

if __name__ == "__main__":
    full_path = os.path.abspath(os.getcwd()) + "/webdrivers/chromedriver_linux64/chromedriver"
    amazonSc = AmazonScraper("chrome", full_path)
    amazonSc.amazon_product_search("Mobile", 1, True)
    # url = "https://www.amazon.in/Redmi-9A-2GB-32GB-Storage/dp/B08696XB4B/ref=sr_1_3?dchild=1&keywords=mobile&qid=1629271762&sr=8-3"
    # amazonSc.get_single_product_details(url,True)
