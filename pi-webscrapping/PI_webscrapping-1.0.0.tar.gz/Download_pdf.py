from bs4 import BeautifulSoup
import requests
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import os.path
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import pdb
import os


class DownloaderBot():
    
    def __init__(self,  url, diretorio):
        self.__url = url #Atributo privado que recebe a url contendo a lista de links de PDF para download
        self.__diretorio = diretorio
        print("Downloader object initialezed!")
    

    def downloaderTcePiaui(self):
        diretorio = self.__diretorio
        html = self.__url
        proxima_pagina_existe = True
        
        cont = 0
        
        while proxima_pagina_existe:        

            html_page = requests.get(html)

            driver = webdriver.Chrome() 
            driver.get(html)

            select = Select(driver.find_element_by_id('tipo'))
            select.select_by_visible_text('CONTAS - CONTAS DE GOVERNO - CONTAS - CONTAS DE GOVERNO')

            select = Select(driver.find_element_by_id('exercicio'))
            select.select_by_visible_text('2018')                   

            element = driver.find_element_by_name("search")
            element.click()

            page_source = driver.page_source

            print(page_source)

            soup = BeautifulSoup(page_source,  "html.parser")

            driver.quit()

            x2 = 0

                        
            for link in soup.findAll("a"):
                print(link.get('href'))
                
                if link.get("href").find("2018") > 0:

                    li = os.listdir(diretorio)
                    #for i in li:
                    #    li.append(i.split('_')[0])
                    li = [i.split('_')[0] for i in li]
                    teste = link.get("href").split("=")
                    teste = teste[1].split("/")
                    if (teste[0] not in li):
                        cont = cont + 1

                        print("Link"+str(cont))
                        print(link.get("href"))
                        #webbrowser.open(link.get("href")) biblioteca nativa Python para abrir o browser padrão da máquina
                        #Vou passar a controlar o browser com o Selenium agora
                        #options = Options()
                        #options.headless = True

                        driver2 = webdriver.Chrome()
                        driver2.get(html+link.get("href"))

                        #pdb.set_trace()

                        element = driver2.find_element_by_partial_link_text("as do Processo")
                        baixar = element.get_attribute("href")

                        driver2.quit()

                        options = webdriver.ChromeOptions()

                        preferences = {
                            "download.default_directory": diretorio,
                            "download.prompt_for_download": False,
                            "download.directory_upgrade": True,
                            "safebrowsing.enabled": True
                        }
                        options.add_experimental_option("prefs", preferences)
                        options.add_argument("--headless")

                        driver3 = webdriver.Chrome(chrome_options=options)
                        driver3.get(baixar)

                        element = driver3.find_element_by_xpath("//*[@id = 'form:arvore:0_0:j_idt21']/span[2]")
                        element.click()

                        time.sleep(5)

                        url_do_pdf = driver3.current_url #pega a URL do PDF, que é o que queríamos desde o inicio!

                        print(url_do_pdf)


                        
            #testa botao proximo APÓS baixar todos os PDFs da primeira página!
            pagina_exibe_links_pdf_driver = webdriver.Chrome()
            pagina_exibe_links_pdf_driver.get(self.__url)
            
            try:
                botao_proximo = pagina_exibe_links_pdf_driver.find_element_by_link_text("Próximo →")
                #Necessidade de fazer downloads nas próximas páginas
                botao_proximo.click()                
                proxima_pagina = pagina_exibe_links_pdf_driver.current_url
                self.__url = proxima_pagina #Atualiza a página do link dos downloads no objeto!
                pagina_exibe_links_pdf_driver.quit() #Pode fechar o driver, pois já temos a proxima página para reiniciar o loop!
            except NoSuchElementException as exception: # Atingiu a última página da navegação! Acabou o trabalho!                
                proxima_pagina_existe = False #Não entrará na próxima iteração do loop!
