#In this I would like to write some of the sample programs to test.
# Print head of the dataset from the url given

__author__ = "Dara Ekanth"
__email__ = "daraekanth3@gmail.com"
__status__ = "developing"

import pandas as pd
#url = "https://raw.githubusercontent.com/cs109/2014_data/master/countries.csv"

#print(dataset.head())
class data_collection:
    '''
        class for the data collection. A valid url is expected to load the dataset.
    '''
    def __init__(self,url):
        '''
        creates a new instance of a data collection class
        :param url: str
            should be a valid url to retrieve data.
        '''
        self.url = url
        self.dataset = pd.read_csv(self.url)
    def print_head(self,rows = 5):
        '''

        :param rows: int
            The default value is 5. It will help to see the top rows from the dataset loaded.
        :return:
        '''
        print(self.dataset.head(rows))
    def print_tail(self,rows = 5):
        '''

        :param rows: int
            The default value is 5. It will help to see the last rows from the dataset loaded.
        :return:
        '''
        print(self.dataset.tail(rows))
    def print_correlation(self):
        '''
            No parameters required. It will print the pair wise correlation of all the columns in the dataset.
        :return:
        '''
        print(self.dataset.corr())
    def shape(self):
        '''
            No parameters required. It will print the shape of the datset.
        :return:
        '''
        print(self.dataset.shape)
class repeat:
    '''
    This is a class to repeat the string.
    '''
    def print_repeat(self,word = "hello",count = 100):
        '''
        :param word: str
               count: int
               It will print the input string for count number of times.
        '''
        print((word+" ")*count)

# if __name__ == "__main__":
#     r = repeat()
#     r.print_repeat()
#     d = data_collection("https://raw.githubusercontent.com/cs109/2014_data/master/countries.csv")
#     # d.print_head(3)
#     # d.print_tail()
#     d.print_correlation()
#     d.shape()
