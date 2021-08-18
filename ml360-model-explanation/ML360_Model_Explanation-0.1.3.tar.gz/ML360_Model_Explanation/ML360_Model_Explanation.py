from shapash.explainer.smart_explainer import SmartExplainer
import pandas as pd

class ML360_Model_Explanation():
    global xp
    def __init__(self):
        pass

    def model_explain(self,X_train,final_model):
        c1=X_train.columns
        c2=X_train.columns
        feature=dict(zip(c1,c2))
        y_pred=final_model.predict(X_train)
        y_pred=pd.Series(y_pred)
        xp=SmartExplainer(features_dict=feature)
        xp.compile(X_train,final_model,y_pred=y_pred)
        return xp

    def Final_Pandas_Df_for_Classification(self,xp):
        final_output_df=xp.to_pandas(proba=True)
        return final_output_df
    
    def Final_Pandas_Df_for_Regression(self,xp):
        final_output_df=xp.to_pandas(proba=False)
        return final_output_df
    
    def Model_Features_Importance(self,xp):
        return xp.plot.features_importance()
        
    def Contribution_polt(self,xp,col,label=None):
        return xp.plot.contribution_plot(col=col,label=label)
    
    def Local_plot(self,xp,index=1):
        return xp.plot.local_plot(index=index)
    
    def Local_prediction(self,xp,index=1,label=0):
        return xp.plot.local_pred(index=index,label=label)