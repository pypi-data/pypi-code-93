#####################################################################
#   THE OSCARSCRAPPER, by YANN AUBINEAU AND SAMUEL BOZON            #
#   yann.aubineau@gmail.com         @samuel.bozon@gmail.com         #
#   2021                                                            #
#####################################################################


import time
import requests
from scrapy import Selector
from tqdm import tqdm
import pandas as pd
import re  # text processing
import numpy as np
import json
import jellyfish
from urllib.parse import quote
import os 
import sys # to use exit()
from tkinter import * # Window
from pathlib import Path


os.chdir(os.path.dirname(os.path.abspath(__file__))) # This changes the working directory to be the same as where the python script is. FOR EXECUTABLE

class Oscar_Scraper:
    
    
    def __init__(self):
        """
        Initialization method.
        Initializes most lists used to select and store data.
        It endes by calling the Imput method to start the program.
        """

        # * List of the content of every oscars.org pages used
        self.links = {
            'oscars':[],
            'path': [os.path.join("data", "corrections")]
        }

        
        

        # * Lists of different names for same categories
        self.categories_dictionary = {
                    "Actor in a Leading Role": ['Actor', 'Actor in a Leading Role'],
                    "Actress in a Leading Role": ['Actress', 'Actress in a Leading Role'],
                    "Directing": ["Directing"],
                    "Best Picture": ['Outstanding Picture', 'Outstanding Production','Best Motion Picture', 'Best Picture']
                    }
        
        # * List of categories related to individuals.

        self.categories_individuals = ['Directing', 'Actor', 'Actor in a Leading Role', 'Actress', 'Actress in a Leading Role']

        self.categories_films = ['Outstanding Picture', 'Outstanding Production','Best Motion Picture', 'Best Picture']

        # * Stores the user's selected categories to fetch
        self.selected_categories = []
        
        # *  Defining lists containing the future raw data
        self.list_names = []
        self.list_year = []
        self.list_category = []
        self.list_films = []
        self.list_results = [] 
        self.list_id_movie = []
        self.list_birthday = []
        self.list_gender = []
        self.list_id_indiv = []
        self.list_names_right = []
        self.list_films_right = []
        self.list_names_wrong = []
        self.list_films_wrong = []
        self.list_originallanguage = []
        self.list_genreids = []
    
                 
        # * Initialize the lists containing the future cleaned data
        self.data = {
                'category':[],
                'film':[],
                'year':[],
                'name':[],
                'gender':[],
                'result':[],
                'birthdate':[],
                'id_movie':[]
                
            }

        # * End of the initialization, fetching for user's imput.
        self.Imput()

    def Imput(self):
        """
        Main method.
        It creates a user interface to interact with the program.
        It asks for categories of interest, time period and how to proceed (autorun or manual run).
        Returns nothing.
        
        """
        window = Tk()
        window.geometry("400x500")
        window.title('Which categories do you want to compile ?')
        
        Title_frontend = Label(window,
                    text = "The Oscar Scapper, by Yann Aubineau and Samuel Bozon",
                    font = ("Times New Roman", 10), 
                    padx = 10, pady = 10)
        Title_frontend.pack()
        
        Label(window, text="From:").pack(pady = 2)
        From_user = Entry(window)
        From_user.pack(pady=2)
        From_user.insert(END, '1930')

        Label(window, text="To:").pack(pady = 2)
        To_user = Entry(window)
        To_user.pack(pady=2)
        To_user.insert(END, '2021')
        
        # for scrolling vertically
        yscrollbar = Scrollbar(window)
        yscrollbar.pack(side = RIGHT, fill = Y)
        
        Informations = Label(window,
                    text = "Which categories do you want to compile ?\n Select the categories below :  ",
                    font = ("Times New Roman", 10), 
                    padx = 10, pady = 10)
        Informations.pack()
        list_selection = Listbox(window, selectmode = "multiple", yscrollcommand = yscrollbar.set)

        list_selection.pack(padx = 2, pady = 2, expand = NO, fill = X)
        
        list_categories_possible = [item for item in list(self.categories_dictionary.keys())]


        for each_item in range(len(list_categories_possible)):
            list_selection.insert(END, list_categories_possible[each_item])
            list_selection.itemconfig(each_item, bg = "white")

        self.user_imput = IntVar() #Basically Links Any Radiobutton With The Variable=i.
        r1 = Radiobutton(window, text="Autorun (recommended)", value=1, variable=self.user_imput)
        r1.pack(pady = 10, padx= 5)
        r2 = Radiobutton(window, text="Manual run", value=2, variable=self.user_imput)
        r2.pack(pady = 2, padx= 2)
        exit_button = Button(window, text="Done", command= lambda:[fCategories(),fPopup(),fDates(), fExit()])
        exit_button.pack(pady=20)
        

        def fCategories():

            # * Stores the index of the selected categories after the exit_button press.

            self.input_selected = []
            for number_selected in list_selection.curselection():
                self.input_selected.append(list_selection.get(number_selected)) 
            # * From the index of the selected categories to the selected categories.
            for input_categories in self.input_selected:
                if input_categories in self.categories_dictionary.get(input_categories):
                    for number_name in range(len(self.categories_dictionary.get(input_categories))):
                        self.selected_categories.append(self.categories_dictionary.get(input_categories)[number_name])

        def fDates():

                self.from_time = int(From_user.get())
                self.to_time = int(To_user.get())
                self.time_period = range(self.from_time, self.to_time + 1)

        def fPopup():
            self.popup = FALSE
            if self.input_selected == []:
                text = "You must select at least one category"
                self.popup = TRUE

            if self.user_imput.get() == 0: 
                text = "You must choose how to use the program"
                self.popup = TRUE

            if not To_user.get().isdigit() or not From_user.get().isdigit():
                text = "You must enter valid dates."
                self.popup = TRUE
            if To_user.get().isdigit() and From_user.get().isdigit():
                if  int(From_user.get()) < 1930:
                    text = "The Academy Awards ceremony starts in 1929 but the categories are standardized in the 1930's ceremony. Please pick between 1930 and 2021."
                    self.popup = TRUE

                if  int(To_user.get()) > 2021:
                    text = "This program supports Academy Awards ceremonies until 2021. Please pick between 1930 and 2021."
                    self.popup = TRUE

                if int(From_user.get()) > int(To_user.get()):
                    text = "You must enter a valid range of dates."
                    self.popup = TRUE

            if self.popup == TRUE:
                fInfos = Toplevel()		  # Popup -> Toplevel()
                fInfos.title('Warning')
                Label(fInfos, text= text ).pack(pady = 10, padx = 10)
                Button(fInfos, text='OK', command=fInfos.destroy).pack(padx=10, pady=10)
                fInfos.transient(window) 	  # Réduction popup impossible 
                fInfos.grab_set()		  # Interaction avec fenetre jeu impossible
                window.wait_window(fInfos)   # Arrêt script principal

            
        
        def fExit():
            if self.popup == FALSE:
                window.destroy()
                self.Run()
            else:
                self.popup = FALSE # Reinitialization

        window.mainloop()

        
        
        
 
        

    def getHTML(self):

        """"
        Main method.
        Used to extract the content of the oscar.org webpage for each ceremonies included in the time period chose by the utilisator.
        It stocks them in self.links['oscars']
        Returns nothing
        """

        print("Getting the content of oscars.org webpages ...")
        
        for number_year in tqdm(self.time_period):
            try:
                #time.sleep(10) # Crawlerdelay
                url = "https://www.oscars.org/oscars/ceremonies/{}".format(number_year)
                response_oscars = requests.get(url)
                sel = Selector(text = response_oscars.text)   # Scrapy chose over BeautifulSoup for selector CSS
                self.links['oscars'].append(sel)
            except requests.exceptions.RequestException as e:  
                print("There was an error while requesting oscars.org website. Please retry or check your connection or the status of the website. See next the error message: ", e)
                raise SystemExit(e)

    def getNominees(self, years, number_categories, category, number_nominees, number_winners):

        """
        Sub-method.
        It takes itself, the index of which year it is, the index of which category it is, the category, the number of nominees and the number of winners
        It extracts and stock the name of the nominees and the film nominated
        Returns nothing.
        """

        for number_people_nominated in range(number_nominees):   
            if number_winners == 1:
                # NAME
                path_name = "#quicktabs-tabpage-honorees-0 > div > div.view-content > div:nth-child({}) > div.view-grouping-content > div:nth-child({}) > div.views-field.views-field-field-actor-name > h4::text".format(number_categories+1, 4 + number_people_nominated)
                nominee_name = ''.join(self.links['oscars'][years].css(path_name).extract()) # ''.join() transforms the list produced by the selector into a string
            if number_winners == 2:
                 # NAME
                path_name = "#quicktabs-tabpage-honorees-0 > div > div.view-content > div:nth-child({}) > div.view-grouping-content > div:nth-child({}) > div.views-field.views-field-field-actor-name > h4::text".format(number_categories+1, 5 + number_people_nominated)
                nominee_name = ''.join(self.links['oscars'][years].css(path_name).extract()) # ''.join() transforms the list produced by the selector into a string
            
            if category == "Directing" or category in self.categories_films: # For Directing, titles and names are swapped on the website
                self.list_films.append(nominee_name)
            else:
                self.list_names.append(nominee_name)

            # FILM
            if number_winners == 1:
                path_film = "#quicktabs-tabpage-honorees-0 > div > div.view-content > div:nth-child({}) > div.view-grouping-content > div:nth-child({}) > div.views-field.views-field-title > span::text".format(number_categories+1, 4 + number_people_nominated)
                nominee_film = ''.join(self.links['oscars'][years].css(path_film).extract()) # ''.join() transforms the list produced by the selector into a string
                nominee_film = nominee_film.replace("\n", "") # Cleaning up the string
            if number_winners == 2:
                path_film = "#quicktabs-tabpage-honorees-0 > div > div.view-content > div:nth-child({}) > div.view-grouping-content > div:nth-child({}) > div.views-field.views-field-title > span::text".format(number_categories+1, 5 + number_people_nominated)
                nominee_film = ''.join(self.links['oscars'][years].css(path_film).extract()) # ''.join() transforms the list produced by the selector into a string
                nominee_film = nominee_film.replace("\n", "") # Cleaning up the string
            if category == "Directing" or category in self.categories_films: # For Directing, titles and names are swapped on the website
                self.list_names.append(nominee_film)
            else:
                self.list_films.append(nominee_film)
            
            self.list_year.append(self.from_time + years)         
            self.list_category.append(category)
            self.list_results.append("Nominee")

    def getWinners(self, years, number_categories, category, number_winners):
        """
        Sub-method.
        It takes itself, the index of which year it is, the index of which category it is, the category and the number of winners
        It extracts and stock the name of the winners and the film winning.
        Returns nothing.       
        """

        if number_winners == 1: # 1 Winner
        # NAME
            path_name = "#quicktabs-tabpage-honorees-0 > div > div.view-content > div:nth-child({}) > div.view-grouping-content > div.views-row.views-row-1.views-row-odd.views-row-first.views-row-last > div.views-field.views-field-field-actor-name > h4::text".format(number_categories+1)
            nominee_name = ''.join(self.links['oscars'][years].css(path_name).extract()) # ''.join() transforms the list produced by the selector into a string

            if category == "Directing" or category in self.categories_films: # For Directing, titles and names are swapped on the website
                self.list_films.append(nominee_name)
            else:
                self.list_names.append(nominee_name)
            
        
            # FIlM
            path_film = '#quicktabs-tabpage-honorees-0 > div > div.view-content > div:nth-child({}) > div.view-grouping-content > div.views-row.views-row-1.views-row-odd.views-row-first.views-row-last > div.views-field.views-field-title > span::text'.format(number_categories+1)
            nominee_film = ''.join(self.links['oscars'][years].css(path_film).extract()) # ''.join() transforms the list produced by the selector into a string
            nominee_film = nominee_film.replace("\n", "") # Cleaning up the string

            if category == "Directing" or category in self.categories_films:# For Directing, titles and names are swapped on the website
                self.list_names.append(nominee_film)
            else:
                self.list_films.append(nominee_film)
           
            self.list_year.append(self.from_time + years)
            self.list_category.append(category)
            self.list_results.append("Winner")


        if number_winners == 2: # 2 Winners

            # NAME 1st Winner 
            path_name = "#quicktabs-tabpage-honorees-0 > div > div.view-content > div:nth-child({}) > div.view-grouping-content > div:nth-child(2) > div.views-field.views-field-field-actor-name > h4::text".format(number_categories+1)
            nominee_name = ''.join(self.links['oscars'][years].css(path_name).extract()) # ''.join() transforms the list produced by the selector into a string4

            # For Directing, titles and names are swapped on the website
            if category == "Directing" or category in self.categories_films:
                self.list_films.append(nominee_name)
            else:
                self.list_names.append(nominee_name)

            self.list_year.append(self.from_time + years)
            self.list_category.append(category)
            self.list_results.append("Tie-winner")

            # NAME 2st Winner 
            path_name = "#quicktabs-tabpage-honorees-0 > div > div.view-content > div:nth-child({}) > div.view-grouping-content > div:nth-child(3) > div.views-field.views-field-field-actor-name > h4::text".format(number_categories+1)
            nominee_name = ''.join(self.links['oscars'][years].css(path_name).extract()) # ''.join() transforms the list produced by the selector into a string4

            # For Directing, titles and names are swapped on the website
            if category == "Directing" or category in self.categories_films:
                self.list_films.append(nominee_name)
            else:
                self.list_names.append(nominee_name)

            self.list_year.append(self.from_time + years)
            self.list_category.append(category)
            self.list_results.append("Tie-winner")

            # FILM
            path_film1 = '#quicktabs-tabpage-honorees-0 > div > div.view-content > div:nth-child({}) > div.view-grouping-content > div:nth-child(2) > div.views-field.views-field-title > span::text'.format(number_categories+1)
            path_film2 = '#quicktabs-tabpage-honorees-0 > div > div.view-content > div:nth-child({}) > div.view-grouping-content > div:nth-child(3) > div.views-field.views-field-title > span::text'.format(number_categories+1)

            winner1_film = ''.join(self.links['oscars'][years].css(path_film1).extract()) # ''.join() transforms the list produced by the selector into a string
            winner1_film = winner1_film.replace("\n", "") # Cleaning up the string

            # For Directing, titles and names are swapped on the website
            if category == "Directing" or category in self.categories_films:
                self.list_names.append(winner1_film)
            else:
                self.list_films.append(winner1_film)

            winner2_film = ''.join(self.links['oscars'][years].css(path_film2).extract()) # ''.join() transforms the list produced by the selector into a string
            winner2_film = winner2_film.replace("\n", "") # Cleaning up the string

            # For Directing, titles and names are swapped on the website
            if category == "Directing" or category in self.categories_films:
                self.list_names.append(winner2_film)
            else:
                self.list_films.append(winner2_film)        



    def getDATA(self): 

        """
        Main method:
        Using the content of each oscar.org webpage per year to identify the number of winners and nominated of each category in the list, then through two sub-methods it identifies the result, year, name of the winner/nominee,
        title of the movie and category, and save them in a dictionnary of list.
        Then it calls a sub-method to proceed some corrections on these lists, as some errors exist in the oscar.org website.
        Returns nothing
        """

        print("Extracting the data of the website ...")    
        for years in tqdm(range(len(self.links['oscars']))):
            categories = self.links['oscars'][years].css('#quicktabs-tabpage-honorees-0 > div > div.view-content > div.view-grouping > div.view-grouping-header > h2::text').extract()    
            for number_categories in range(len(categories)):
                
                if categories[number_categories] in self.selected_categories:
                    
                    # Need the number of winners (might be ties) and nominated          
                    path_nominated = "#quicktabs-tabpage-honorees-0 > div > div.view-content > div:nth-child({}) > div.view-grouping-content > div:last-child".format(number_categories+1)
                    number_of_film_nominated = int(''.join(self.links['oscars'][years].css(path_nominated).extract()).split("views-row-")[1])

                    path_winner = "#quicktabs-tabpage-honorees-0 > div > div.view-content > div:nth-child({}) > div.view-grouping-content > div:nth-child(2)".format(number_categories+1)
                    trial = ''.join(self.links['oscars'][years].css(path_winner).extract()).split("views-row-first views-row-last") # If 1 winner then it splits the string into 1 list of 2 elements, if 2 winners, it does nothing
                    
                    if len(trial) == 2:
                        number_winners = 1
                    elif len(trial) == 1:
                        number_winners = 2

                    ## WINNERS                 
                    
                    self.getWinners(years, number_categories, categories[number_categories], number_winners)     
                    
                    ## NOMINEES
                    
                    self.getNominees(years, number_categories, categories[number_categories], number_of_film_nominated, number_winners)   

                    
        self.data = {
            'year': self.list_year,
            'category': self.list_category,
            'film': self.list_films,
            'name': self.list_names,
            'result':self.list_results
        }            

        # Process the corrections on the data scrapped
        self.Correction(0,True)
        


    def printINDIVIDUALS(self):
        df = pd.DataFrame(self.data)
        df = df.set_index(['year','category'])
        individuals = df.loc(axis = 0)[pd.IndexSlice[:, self.categories_individuals]]
        return(print(individuals))
    
    def saveINDIVIDUALS(self):
        df = pd.DataFrame(self.data)
        df = df.set_index(['year','category'])
        individuals = df.loc(axis = 0)[pd.IndexSlice[:, self.categories_individuals]]
        individuals.reset_index() # For some reasons the index is not saved with the rest so we make it back to two columns 
        
        # Creation of the csv file. We store each iteration of the dataframe separately
        downloads_path = str(Path.home() / "Downloads")
        number_of_files = 0
        while os.path.exists(downloads_path+"\Individuals%s.csv" % number_of_files):
            number_of_files += 1
        individuals.to_csv(downloads_path+"\Individuals%s.csv" % number_of_files)
        
        return(print("The dataframe was saved as Individuals%s.csv in your downloads directory." % number_of_files))
    
        
    def printFILMS(self):
        df = pd.DataFrame(self.data)
        df = df.set_index(['year','category'])
        films = df.loc(axis = 0)[pd.IndexSlice[:, self.categories_films]]
        return(print(films))

    def saveFILMS(self):
        df = pd.DataFrame(self.data)
        df = df.set_index(['year', 'category'])
        films = df.loc(axis=0)[pd.IndexSlice[:, self.categories_films]]
        films.reset_index() # For some reasons the index is not saved with the rest so we make it back to two columns
               
        # Creation of the csv file. We store each iteration of the dataframe separately
        downloads_path = str(Path.home() / "Downloads")
        number_of_files = 0
        while os.path.exists(downloads_path+"\Films%s.csv" % number_of_files):
            number_of_files += 1
        films.to_csv(downloads_path+"\Films%s.csv" % number_of_files)
        return(print("The dataframe was saved as Films%s.csv in your downloads directory." % number_of_files))


        
    def getAPI_TMDB(self):

        """
        Main method.
        From the title, it searches in an complete movie database for the movie, then we extract the matching individual and collect their birthdate and gender, for movie it collects their original language and genre.
        It uses the sub-method getTMDB
        Returns nothing
        
        """
        
        wrongfilms = []
        count_indiv_records = -1
        API_KEY_MDB = "a68690ebf69567801e68c26ee82d7787"
        URL_MDB_SEARCH = "https://api.themoviedb.org/3/search/movie?api_key={}&language=en-US&query={}&page={}&include_adult=false"
        URL_MDB_PERSON = "https://api.themoviedb.org/3/person/{}?api_key={}"

        print("Requesting TheMovieDataBase API for the gender, birthdays, original language and genres...")

        try:
            for film_number in tqdm(range(len(self.data['film']))):
                if self.data['category'][film_number] in self.categories_individuals:
                    self.list_originallanguage.append(np.nan)
                    self.list_genreids.append(np.nan)
                    count_indiv_records += 1
                    title_standard = quote(self.data['film'][film_number])
                    response_search = json.loads(requests.get(URL_MDB_SEARCH.format(API_KEY_MDB,title_standard,1)).text)
                    if response_search["total_results"] != 0:        
                        if self.TMDB_get(response_search, film_number) == True: # A movie-individual pair was found, we look for the individual data now

                            response_person = json.loads(requests.get(URL_MDB_PERSON.format(self.list_id_indiv[count_indiv_records],API_KEY_MDB)).text)
                            if response_person.get("success") != False: # Check if the API find a person

                                if response_person["birthday"] in (None,0):
                                    self.list_birthday.append(np.nan)
                                else:
                                    self.list_birthday.append(response_person["birthday"])
                                
                                if response_person["gender"] in (None,0):
                                    self.list_birthday.append(np.nan)
                                else:
                                    self.list_gender.append(response_person["gender"])

                        else: # Happens if not a single movie-actor pair was found in the first page (hence the 2)
                            response_search = json.loads(requests.get(URL_MDB_SEARCH.format(API_KEY_MDB,title_standard,2)).text)
                            if response_search["total_results"] != 0:        
                                if self.TMDB_get(response_search, film_number) == True: # A movie-individual pair was found, we look for the individual data now
                                    response_person = json.loads(requests.get(URL_MDB_PERSON.format(self.list_id_indiv[count_indiv_records],API_KEY_MDB)).text)
                                    if response_person.get("success") != False: # Check if the API find a person
                                        if response_person["birthday"] in (None,0):
                                            self.list_birthday.append(np.nan)
                                        else:
                                            self.list_birthday.append(response_person["birthday"])
                                        
                                        if response_person["gender"] in (None,0):
                                            self.list_birthday.append(np.nan)
                                        else:
                                            self.list_gender.append(response_person["gender"])
                                    
                                else:  # specific problems with some 1930's movies
                                    URL_MDB_SEARCH1930 = "https://api.themoviedb.org/3/search/movie?api_key={}&language=en-US&query={}&page={}&include_adult=false&year=1930"
                                    response_search = json.loads(requests.get(URL_MDB_SEARCH1930.format(API_KEY_MDB,title_standard,1)).text)
                                    
                                    if response_search["total_results"] != 0:        
                                        if self.TMDB_get(response_search, film_number) == True: # A movie-individual pair was found, we look for the individual data now
                                            response_person = json.loads(requests.get(URL_MDB_PERSON.format(self.list_id_indiv[count_indiv_records],API_KEY_MDB)).text)
                                            
                                            if response_person.get("success") != False: # Check if the API find a person
                                                
                                                if response_person["birthday"] in (None,0):
                                                    self.list_birthday.append(np.nan)
                                                else:
                                                   self.list_birthday.append(response_person["birthday"])
                                            
                                                if response_person["gender"] in (None,0):
                                                    self.list_birthday.append(np.nan)
                                                else:
                                                    self.list_gender.append(response_person["gender"])

                elif self.data['category'][film_number] in self.categories_films: # Special condition if we are not looking for the data on individual (winner of the award is a company for example)
                    title_standard = quote(self.data['film'][film_number])
                    response_search = json.loads(
                        requests.get(URL_MDB_SEARCH.format(API_KEY_MDB, title_standard, 1)).text)
                    try:
                        if response_search['total_results'] == 0:
                            wrongfilms.append(self.data["film"][film_number])
                            self.list_originallanguage.append('not found')
                            self.list_genreids.append('not found')
                            self.list_birthday.append(np.nan)
                            self.list_gender.append(np.nan)


                        else:
                            found = False
                            added = False
                            for number_results in range(len(response_search["results"])):
                                if jellyfish.damerau_levenshtein_distance(
                                        str(response_search["results"][number_results].get("title")),
                                        str(self.data["film"][film_number])) < 4 and found == False:
                                    if response_search["results"][number_results].get("release_date") not in (
                                            None, 0, ''):
                                        if (int(response_search["results"][number_results]["release_date"][0:4]) in (
                                                self.data["year"][film_number], self.data["year"][film_number] - 1,
                                                self.data["year"][film_number] - 2,
                                                self.data["year"][film_number] - 3)):

                                            self.list_originallanguage.append(
                                                response_search["results"][number_results].get("original_language"))

                                            self.list_genreids.append(
                                                response_search["results"][number_results].get("genre_ids"))
                                            self.list_birthday.append(np.nan)
                                            self.list_gender.append(np.nan)

                                            found = True

                            if found == False:
                                self.list_originallanguage.append('not found')
     
                                self.list_genreids.append('not found')
                                self.list_birthday.append(np.nan)
                                self.list_gender.append(np.nan)
                                wrongfilms.append(self.data["film"][film_number])

                                found = True


                    except KeyError:
                        print('Key Error' + '--' + str(self.data["film"][film_number]))
                        print('rok' + str(self.data["year"][film_number]) + '---' + str(
                            print(self.data["category"][film_number])))
                        wrongfilms.append(self.data["film"][film_number])
                        self.list_originallanguage.append('not foundKeyError')
                        self.list_genreids.append('not foundKeyError')
                        self.list_birthday.append('n/a')
                        self.list_gender.append('n/a')
                else:
                    print(self.data['category'][film_number] + '---' + self.data['film'][film_number])
                    print('wrong category')
                    self.list_originallanguage.append('wrong category')
                    self.list_genreids.append('wrong category')
                    self.list_birthday.append(np.nan)
                    self.list_gender.append(np.nan)
            else:
                pass

        # Exception handling
        except requests.exceptions.RequestException as e:  
            print("There was an error while requesting the API of TheMovieDataBase website. Please retry or check your connection or the status of the website. See next the error message: ", e)
            raise SystemExit(e)
        
        # Transformation of the data
        for individuals in tqdm(range(len(self.data['film']))): 
            if self.list_gender[individuals] == 1:
                self.list_gender[individuals] = "Female"
            elif self.list_gender[individuals] == 2:
                self.list_gender[individuals] = "Male"
            elif self.list_gender[individuals] == 3:
                self.list_gender[individuals] = "Non-binary"

            if np.nan not in [self.list_birthday[individuals]]:
                self.list_birthday[individuals] = str(self.list_birthday[individuals][0:4]) # We keep only the year and transform from string to integer

    
        self.data['gender'] = self.list_gender
        self.data['birthday'] = self.list_birthday
        self.data['genreids'] = self.list_genreids
        self.data['original_language'] = self.list_originallanguage

        wfdf = pd.DataFrame(wrongfilms)
        wfdf.to_csv(os.path.join(self.links['path'][0],'wfdf.csv'))  # all the wrong names of the films in film categories
        
                                        
    def TMDB_get(self, response_search, film_number):
        """
        Sub-method.
        It takes itself, the content of the response of the API, the index number of the film in self.data["film"].
        Used by getAPI_tmdb to extract to confirm the right movie was picked (it contains the individual it is looking for)
        Returns True or False, True if the individual was present in the credits of the movie.
        """
        
        url_MDB_credit = "http://api.tmdb.org/3/movie/{}/credits?api_key={}"
        API_KEY_MDB = "a68690ebf69567801e68c26ee82d7787"
        found_individual = False
        try :
            for number_results in range(len(response_search["results"])):
                if found_individual == False:
                    if response_search["results"][number_results].get("release_date") not in (None,0,''): # There is a release date
                        if (int(response_search["results"][number_results]["release_date"][0:4]) in (self.data["year"][film_number],self.data["year"][film_number]-1, self.data["year"][film_number]-2, self.data["year"][film_number]-3)) and found_individual == False:
                            id_MDB = response_search["results"][number_results]["id"]
                            response_credit = json.loads(requests.get(url_MDB_credit.format(id_MDB,API_KEY_MDB)).text)
                            if response_credit.get("success") != False: # Check if the API find a person
                                if self.data["category"][film_number] == "Directing":
                                    for acteurs in range(len(response_credit["crew"])):
                                        if jellyfish.damerau_levenshtein_distance(response_credit["crew"][acteurs]["name"], self.data["name"][film_number]) < 2:
                                            self.list_id_indiv.append(response_credit["crew"][acteurs]["id"])
                                            found_individual = True
                                        
                                            break


                                    if not any(jellyfish.damerau_levenshtein_distance(response_credit["crew"][acteurs]["name"], self.data["name"][film_number]) < 2 for acteurs in range(len(response_credit["crew"]))):
                                        pass
                                        # self.Correction(film_number, False)
                                        
                                else:
                                    for acteurs in range(len(response_credit["cast"])):
                                        if jellyfish.damerau_levenshtein_distance(response_credit["cast"][acteurs]["name"], self.data["name"][film_number]) < 2:
                                            self.list_id_indiv.append(response_credit["cast"][acteurs]["id"])
                                            found_individual = True  # Empêche d'avoir plusieurs fois le même acteur si on l'a déjà trouvé
                                            break   
                                            
                                    if not any(jellyfish.damerau_levenshtein_distance(response_credit["cast"][acteurs]["name"], self.data["name"][film_number]) < 2 for acteurs in range(len(response_credit["cast"]))):
                                        pass
                                        # self.Correction(film_number, False)
                                        

        # Error handling      
        except requests.exceptions.RequestException as e:  
            print("There was an error while requesting oscars.org website. Please retry or check your connection or the status of the website. See next the error message: ", e)
            raise SystemExit(e)
        
        # Return False if no movie-individual pair was found, and True if it was found
        return(found_individual)
                                

    def Correction(self,film_number, corrected):
        """
        Sub-method.
        Used in two ways:
        1) It was used to manually identify and correct mistakes hidden in the oscar.org website, stocking them in a dataframe to use at each iteration of the script. It has been disabled once every mistake was corrected.
        2) It loads the dataframes precedently created, then correct them 
        Returns nothing.
        """
        if corrected == False: # Part used to debug
            question = input("Film (f) or Name (n) or Both (b) or Pass (p)?")
            if question == "f":
                answer = input("Correct title ?")
                self.list_films_wrong.append(self.data["film"][film_number])
                self.list_films_right.append(answer)
                self.data["film"][film_number] = answer
                pd.DataFrame(self.list_films_right).to_csv(os.path.join(self.links['path'][0],'list_films_right.csv'),index=False) 
                pd.DataFrame(self.list_films_wrong).to_csv(os.path.join(self.links['path'][0],'list_films_wrong.csv'),index=False) 
            if question == "n":
                answer = input("Correct name ?")
                self.list_names_wrong.append(self.data["name"][film_number])
                self.list_names_right.append(answer)           
                self.data["name"][film_number] = answer
                pd.DataFrame(self.list_names_right).to_csv(os.path.join(self.links['path'][0],'list_names_right.csv'),index=False) 
                pd.DataFrame(self.list_names_wrong).to_csv(os.path.join(self.links['path'][0],'list_names_wrong.csv'),index=False) 
            if question == "b":
                answer1 = input("Correct title ?")
                answer2 = input("Cprrect name ?")
                self.list_films_wrong.append(self.data["film"][film_number])
                self.list_names_wrong.append(self.data["name"][film_number])
                self.list_films_right.append(answer1)
                self.list_names_right.append(answer2)
                self.data["film"][film_number] = answer1
                self.data["name"][film_number] = answer2
                pd.DataFrame(self.list_names_right).to_csv(os.path.join(self.links['path'][0],'list_names_right.csv'),index=False) 
                pd.DataFrame(self.list_names_wrong).to_csv(os.path.join(self.links['path'][0],'list_names_wrong.csv'),index=False)
                pd.DataFrame(self.list_films_right).to_csv(os.path.join(self.links['path'][0],'list_films_right.csv'),index=False) 
                pd.DataFrame(self.list_films_wrong).to_csv(os.path.join(self.links['path'][0],'list_films_wrong.csv'),index=False) 
            if question == "p":
                pass

        if corrected == True: # Part actually used to load the corrections
            list_films_right = pd.read_csv(os.path.join(self.links['path'][0],"list_films_right.csv"))
            list_films_wrong = pd.read_csv(os.path.join(self.links['path'][0],"list_films_wrong.csv"))
            list_names_right = pd.read_csv(os.path.join(self.links['path'][0],"list_names_right.csv"))
            list_names_wrong = pd.read_csv(os.path.join(self.links['path'][0],"list_names_wrong.csv"))
            l_films = len(list_films_right)
            l_names = len(list_names_right)
            l_data = len(self.data["film"])
            
            # Attribute the correction to the... correct film or individual
            for max_length_correction in range(max(l_films,l_names)):
                if max_length_correction < l_names:
                    self.list_names_right.append(list_names_right.values.tolist()[max_length_correction][0])
                    self.list_names_wrong.append(list_names_wrong.values.tolist()[max_length_correction][0])
                if max_length_correction < l_films:
                    self.list_films_right.append(list_films_right.values.tolist()[max_length_correction][0])
                    self.list_films_wrong.append(list_films_wrong.values.tolist()[max_length_correction][0])
                    
            for max_length_data in range(l_data):
                for max_length_correction in range(max(l_films,l_names)):
                    if max_length_correction < l_films:
                        if self.data['film'][max_length_data] == self.list_films_wrong[max_length_correction]:
                            self.data['film'][max_length_data] = self.list_films_right[max_length_correction]
                    if max_length_correction < l_names:       
                        if self.data['name'][max_length_data] == self.list_names_wrong[max_length_correction]:
                            self.data['name'][max_length_data] = self.list_names_right[max_length_correction]

   
    def Run(self):
        if self.user_imput.get() == 1: # Autorun
            self.getHTML()
            self.getDATA()
            self.getAPI_TMDB()
            if any(self.selected_categories[number_categories] in self.categories_individuals for number_categories in range(len(self.selected_categories))):
                self.printINDIVIDUALS()
                self.saveINDIVIDUALS()
            if any(self.selected_categories[number_categories] in self.categories_films for number_categories in range(len(self.selected_categories))):
                self.printFILMS()
                self.saveFILMS()
            input("Press any key to exit:")
            
            
            
if __name__ == "__main__": # execute only if run as a script
    Scrapper = Oscar_Scraper()




