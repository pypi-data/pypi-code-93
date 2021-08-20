import os

import shap
import matplotlib.pyplot as plt
import base64
import pandas as pd


class ShapFeatureImportance:
    def __init__(self, sample_size: int = 100):
        self.sample_size = sample_size

    def calc_metrics(self, context):
        pipeline = context["pipeline"]
        model = pipeline.get_most_recent_final_model()
        data = pipeline.get_most_recent_data().get_X_data()

        def predict_proba(input_data):
            return model.predict_proba(pd.DataFrame(input_data, columns=data.columns))

        def predict(input_data):
            return model.predict(pd.DataFrame(input_data, columns=data.columns))

        if len(data) > self.sample_size:
            data = shap.sample(data, self.sample_size)

        if context["model_type"] == "classifier":
            explainer = shap.KernelExplainer(predict_proba, data)
        elif context["model_type"] == "regressor":
            explainer = shap.KernelExplainer(predict, data)

        shap_values = explainer.shap_values(data, l1_reg="aic")

        shap.summary_plot(shap_values, data, show=False)
        plt.savefig("global_interpretation.png", bbox_inches="tight")
        plt.close()

        with open("global_interpretation.png", "rb") as f:
            encoded_image = base64.b64encode(f.read())

        os.unlink("global_interpretation.png")

        return {"shap_feature_importance": encoded_image.decode()}
