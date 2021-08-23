from imblearn.over_sampling import SVMSMOTE
from sklearn.decomposition import PCA
from sklearn import svm
from tqdm import tqdm
import pandas as pd
import numpy as np
import string
import re


class ContentExtractor:

    def __init__(self, w2v_model):
        self.w2v_model = w2v_model
        self.train_paragraph_df = None
        self.target_text_df = None
        self.model_pred = None
        self.data_max = None
        self.data_min = None
        self.n_label_1 = None
        self.pca = None

    def train_model(self, train_df, train_additional_features=None, y_name="label", text_name="text", use_pca=False, gamma=0.1, C=1):

        self.n_label_1 = train_df[train_df[y_name] == 1].shape[0]
        self.train_paragraph_df = build_features_df(train_df, self.w2v_model, text_name=text_name)
        if train_additional_features is not None:
            self.train_paragraph_df = pd.concat([self.train_paragraph_df, train_additional_features], axis=1)

        x = self.train_paragraph_df.iloc[:, 2:]
        self.data_min = x.min()
        self.data_max = x.max()
        df_scaled = min_max_rescale(x, self.data_min, self.data_max)
        df_scaled.fillna(0, inplace=True)

        if use_pca:
            self.pca = PCA(.95)
            df_scaled = self.pca.fit_transform(df_scaled)

        model_pred = svm.SVC(kernel="rbf", gamma=gamma, C=C)
        x_resampled, y_resampled = SVMSMOTE().fit_resample(df_scaled, self.train_paragraph_df[y_name])
        model_pred.fit(x_resampled, y_resampled)
        self.model_pred = model_pred

    def extract_content(self, target_df, target_additional_features=None, text_name="text"):

        self.target_text_df = build_features_df(target_df, self.w2v_model, text_name=text_name)
        if target_additional_features is not None:
            self.target_text_df = pd.concat([self.target_text_df, target_additional_features], axis=1)

        self.target_text_df.fillna(0, inplace=True)
        x = self.target_text_df.iloc[:, 1:]
        df_scaled = min_max_rescale(x, self.data_min, self.data_max)
        df_scaled.fillna(0, inplace=True)
        df_scaled = df_scaled.replace([np.inf, -np.inf], 0)

        if self.pca is not None:
            df_scaled = self.pca.transform(df_scaled)

        print("Predicting content")
        self.target_text_df["predicted_label"] = self.model_pred.predict(df_scaled)
        wanted_content = self.target_text_df[self.target_text_df["predicted_label"] == 1][text_name].tolist()

        return wanted_content


def build_features_df(text_df, w2v_model, text_name="text"):
    dict_list = []
    print("Extracting Sherlock Features")
    for par in tqdm(text_df[text_name]):
        if not isinstance(par, str):
            par = str(par)

        features_dict = {}

        spec_reg = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\t\n\r\x0b\x0c'

        characters_to_check = (
            [c for c in string.printable if c not in spec_reg + " "]
        )

        for c in characters_to_check:
            features_dict['n_[{}]'.format(c)] = par.count(c)

        def hasNumbers(inputString):
            return any(char.isdigit() for char in inputString)

        # Fraction of words with special characters

        def hasSpecialChar(inputString):
            return any(char in spec_reg for char in inputString)

        num_count = 0
        specialchar_count = 0
        text_count = 0
        n_val = len(par)
        for char in par:
            if hasNumbers(char):
                num_count += 1
            elif hasSpecialChar(char):
                specialchar_count += 1
            else:
                text_count += 1
        if n_val > 0:

            features_dict['frac_numcells'] = num_count / n_val
            features_dict['frac_textcells'] = text_count / n_val
            features_dict['frac_speccells'] = specialchar_count / n_val
        else:
            features_dict['frac_numcells'] = 0
            features_dict['frac_textcells'] = 0
            features_dict['frac_speccells'] = 0

        clean_text = re.sub('[^A-Za-z0-9]+', ' ', par).strip()
        if len(clean_text) != 0:
            row_len = len(clean_text.replace(" ", ""))
            num_words = len(clean_text.split())
            features_dict["num_words"] = num_words
            features_dict["row_len"] = row_len
            features_dict["upper_perc"] = sum(1 for c in clean_text.replace(" ", "") if c.isupper()) / row_len
            features_dict["starting_upper_perc"] = sum(1 for c in clean_text.split() if c[0].isupper()) / num_words

        dict_list.append(features_dict)

    paragraph_df = pd.DataFrame(dict_list)

    print("Extracting Word Embedding Features")
    row_list = []
    for obj in tqdm(text_df[text_name]):
        try:
            words = [w for w in obj.lower().split() if w in w2v_model]
            input_vector = np.mean(w2v_model[words], axis=0)
            row_list.append(input_vector)
        except:
            row_list.append(np.zeros(300))

    wb_df = pd.DataFrame(row_list)
    paragraph_df = pd.concat([text_df, paragraph_df, wb_df], axis=1)

    return paragraph_df


def min_max_rescale(data, data_min, data_max):
    """Rescale the data to be within the range [new_min, new_max]"""

    return (data - data_min) / (data_max - data_min)
