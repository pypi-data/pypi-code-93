# from os import path
import pandas as pd

class Data:
    # constructor
    def __init__ (self, file_name):
        self.file_name = file_name

    # import et transformation du fichier en dataframe (lien url pour compatibilité avec Docker)
    def get_data(self):
        return pd.read_csv(f"https://raw.githubusercontent.com/Adriengith/titanicazertyui/master/titanicazertyui/data/{self.file_name}.csv")
