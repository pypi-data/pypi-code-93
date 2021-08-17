from shapash.explainer.smart_explainer import SmartExplainer
import pandas as pd

class Model_Explanation():
    def __init__(self):
        pass

    def model_explain(self,X_train,final_model):
        c1=X_train.columns
        c2=X_train.columns
        feature=dict(zip(c1,c2))
        y_pred=final_model.predict(X_train)
        y_pred=pd.Series(y_pred)
        xpl=SmartExplainer(features_dict=feature)
        xpl.compile(X_train,final_model,y_pred=y_pred)
        final_output_df=xpl.to_pandas(proba=True)
        return xpl,final_output_df
