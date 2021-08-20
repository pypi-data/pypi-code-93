import os
import joblib

def asiva_model():
    path = os.path.dirname(os.path.realpath(__file__))
    clf = joblib.load(f"{path}/asiva_model.joblib")
    return clf

def asiva_cm():
    path = os.path.dirname(os.path.realpath(__file__))
    return open(f"{path}/asiva_cm.png", "rb").read()