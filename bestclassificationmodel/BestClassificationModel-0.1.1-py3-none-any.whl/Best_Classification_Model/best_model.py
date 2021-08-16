from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

def bestClassificationModel(X, Y):
    '''
    Select the best model for the given dataset
    :param X: features
    :param Y: labels
    :return: the name and the accuracy of the model for the given dataset
    '''
    # split data
    Xtrain, Xtest, ytrain, ytest = train_test_split(X, Y)

    # Dictionary to store accuracy score of each model
    clf_acc = {}
    '''Logistic Regression'''
    logistic_regression = LogisticRegression()

    # Fit model
    logistic_regression.fit(Xtrain, ytrain)

    # predict
    ypred = logistic_regression.predict(Xtest)

    # Accuracy
    logistic_regression_acc = accuracy_score(ypred, ytest)
    clf_acc['Logistic_Regression'] = logistic_regression_acc

    '''Naive Bayes'''
    naive_bayes_clf = GaussianNB()

    # Fit model
    naive_bayes_clf.fit(Xtrain, ytrain)

    # predict
    ypred = naive_bayes_clf.predict(Xtest)

    # Accuracy
    naive_bayes_clf_acc = accuracy_score(ypred, ytest)
    clf_acc['Naive_Bayes_Clf'] = naive_bayes_clf_acc

    '''Stochastic Gradient Classifier'''
    sgclassifier = SGDClassifier()

    # Fit model
    sgclassifier.fit(Xtrain, ytrain)

    # predict
    ypred = sgclassifier.predict(Xtest)

    # Accuracy
    sgclassifier_acc = accuracy_score(ypred, ytest)
    clf_acc['Stochastic_Clf'] = sgclassifier_acc

    '''K Neighbors Classifier'''
    knn_clf = KNeighborsClassifier()

    # Fit model
    knn_clf.fit(Xtrain, ytrain)

    # predict
    ypred = knn_clf.predict(Xtest)

    # Accuracy
    knn_clf_acc = accuracy_score(ypred, ytest)
    clf_acc['K-Neighbors-Classifier'] = knn_clf_acc

    '''Decision Tree Classifier'''
    decision_tree_clf = DecisionTreeClassifier()

    # Fit model
    decision_tree_clf.fit(Xtrain, ytrain)

    # predict
    ypred = decision_tree_clf.predict(Xtest)

    # Accuracy
    decision_tree_clf_acc = accuracy_score(ypred, ytest)
    clf_acc['Decision_Tree_Clf'] = decision_tree_clf_acc

    '''Random Forest Classifier'''
    random_forest_clf = RandomForestClassifier()

    # Fit model
    random_forest_clf.fit(Xtrain, ytrain)

    # predict
    ypred = random_forest_clf.predict(Xtest)

    # Accuracy
    random_forest_clf_acc = accuracy_score(ypred, ytest)
    clf_acc['Random_Forest_Clf'] = random_forest_clf_acc

    '''Support Vector Machine'''
    svm_clf = SVC()

    # Fit model
    svm_clf.fit(Xtrain, ytrain)

    # predict
    ypred = svm_clf.predict(Xtest)

    # Accuracy
    svm_clf_acc = accuracy_score(ypred, ytest)
    clf_acc['SVM_Clf'] = svm_clf_acc

    # Finding key with maximum accuracy value
    best_model = max(clf_acc, key=clf_acc.get)
    return best_model, clf_acc[best_model]



