from titanicpackagegna.get_data import Data
from titanicpackagegna.preprocessing import Preprocessing
from titanicpackagegna.model import Model
# from package_ml.response_json import Response_json
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


def controler():
    do = Data('titanic') 
    titanic_data = do.get_data()

    preproc = Preprocessing(titanic_data)
    preproc.drop('Cabin')
    preproc.mean_inputer('Age')
    preproc.mode_inputer('Embarked')
    preproc.encoding('Sex','Embarked')
    titanic_data = preproc.final_df()

    ml = Model(titanic_data)

    X = ml.X_features_drop(['PassengerId','Name','Ticket','Survived'])
    y = ml.y_target(['Survived'])
    X_train, X_test, y_train, y_test = ml.split(X,y,test_size=0.2,random_state=2)

    model = LogisticRegression()
    model.fit(X_train, y_train)
    X_train_prediction = model.predict(X_train)
    training_data_accuracy = accuracy_score(y_train, X_train_prediction)
    X_test_prediction = model.predict(X_test)
    test_data_accuracy = accuracy_score(y_test, X_test_prediction)
    return model, ml, X, y
