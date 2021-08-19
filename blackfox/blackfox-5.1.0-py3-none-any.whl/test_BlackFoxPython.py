
from blackfox import BlackFox
from blackfox import AnnOptimizationConfig, RandomForestOptimizationConfig, XGBoostOptimizationConfig
from blackfox_extras import prepare_input_data, scale_output_data
from blackfox import InputConfig, Encoding

blackfox_url = 'http://localhost:5000'
bf = BlackFox(blackfox_url)




# Importing libraries
import numpy as np
import pandas as pd

# Import data
df = pd.read_csv('F:\\.spyder-py3\\projekti\\Vodena_Primeri\\ANN\\Churn\\Churn_Modelling.csv')

df_X = df.iloc[:, 3:13]
y = df.iloc[:, 13:14].values

df_X = pd.concat(
    [
     pd.get_dummies(df_X['Geography'], drop_first = True),
     pd.get_dummies(df_X['Gender'], drop_first = True),
     df_X.drop(['Geography', 'Gender'], axis=1),
     ], axis=1)
X = df_X.iloc[:, :].values


from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)


c = AnnOptimizationConfig(
    problem_type = 'BinaryClassification',
    binary_optimization_metric = 'ROC_AUC',
    # # validation_split = 0.2,
    # inputs=[
    #     InputConfig(encoding=["None"]),
    #     InputConfig(encoding=["None", "OneHot", "Dummy", "Target", "Effect", "CountOfFrequency", "OrderInteger"]),
    #     InputConfig(encoding=["None", "OneHot", "Dummy", "Target", "Effect", "CountOfFrequency", "OrderInteger"]),
    #     InputConfig(encoding=["None"]),
    #     InputConfig(encoding=["None"]),
    #     InputConfig(encoding=["None"]),
    #     InputConfig(encoding=["None"]),
    #     InputConfig(encoding=["None"]),
    #     InputConfig(encoding=["None"]),
    #     InputConfig(encoding=["None"]),
    #     InputConfig(encoding=["None"])
    # ]
    )

# Use CTRL + C to stop optimization
(ann_io, ann_info, ann_metadata) = bf.optimize_ann(
    input_set = X_train,
    output_set = y_train,
    config = c,
    model_path = 'bf_model_churn.h5',
    delete_on_finish = False
)

print('\nann info:')
print(ann_info)

print('\nann metadata:')
print(ann_metadata)






