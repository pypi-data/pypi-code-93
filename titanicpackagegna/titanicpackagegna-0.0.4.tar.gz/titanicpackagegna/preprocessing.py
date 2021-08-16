class Preprocessing:
    def __init__(self, df):
        self.df = df

    def drop(self, column):
        self.df = self.df.drop(columns=column, axis=1)

    def mean_inputer(self, column):
        self.df[column].fillna(self.df[column].mean(), inplace=True)

    def mode_inputer(self, column):
        self.df[column].fillna(self.df[column].mode()[0], inplace=True)

    def encoding(self,column_1, column_2):
        self.df.replace({column_1:{'male':0,'female':1}, column_2:{'S':0,'C':1,'Q':2}}, inplace=True)

    # renvoie le df modifié
    def final_df(self):
        return self.df

