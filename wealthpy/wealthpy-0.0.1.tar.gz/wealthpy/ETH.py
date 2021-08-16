import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from .Asset import Asset


class ETH(Asset):
    def __init__(self, csv_path, provider = "Coindesk"):
        self.df = pd.read_csv(csv_path)
        
    def draw(self):
        return self.df.plot.line()