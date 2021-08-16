from sklearn.model_selection import train_test_split
import numpy as np

class Model:
    def __init__(self, df):
        self.df = df
        self.total_dead = 0
        self.total_alive = 0

    def X_features_drop(self, list_columns):
        return self.df.drop(columns = list_columns,axis=1)

    def y_target(self, column):
        return self.df[column]

    def split(self, X, y, test_size, random_state):
        return train_test_split(X,y, test_size=test_size, random_state=random_state)

    def prediction(self, model, pclass, sex, age, sibsp, parch, fare, embarked):
        input_data_as_numpy_array = np.asarray((pclass, sex, age, sibsp, parch, fare, embarked))
        input_data_reshaped = input_data_as_numpy_array.reshape(1,-1)
        prediction = model.predict(input_data_reshaped)
        if prediction[0]==0:
            self.total_dead += 1
            return "Cet individu n'aurait pas survécu"
        if prediction[0]==1:
            self.total_alive += 1
            return "Cet individu aurait survécu"

    def return_json_prediction(self):
        return [{"name":"Nombre de survivants de nos prédictions","pourcent":self.total_alive},{"name":"Nombre de morts de nos prédictions", "pourcent":self.total_dead}]







# input_data = (3,0,35,0,0,8.05,0)  # Note that these datas exclude the Survived data, as it is to be determined from the model itself

# input_data_as_numpy_array = np.asarray(input_data)

# input_data_reshaped = input_data_as_numpy_array.reshape(1,-1)

# prediction = model.predict(input_data_reshaped)
# #print(prediction)
# if prediction[0]==0:
#     print("Dead")
# if prediction[0]==1:
#     print("Alive")