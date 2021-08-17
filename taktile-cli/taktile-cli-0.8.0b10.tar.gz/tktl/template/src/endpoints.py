import joblib
import pandas as pd

from tktl import Tktl

# instantiate client
tktl = Tktl()

# load model
model = joblib.load("assets/model.joblib")

# load reference data
data = pd.read_parquet("assets/loans_test.pqt")
label = "Repaid"
X = data.drop(columns=label)
y = data[label]


# specify transformation
@tktl.endpoint(kind="binary", X=X, y=y)
def repayment(df):
    pred = model.predict_proba(df)[:, 1]
    return pred
