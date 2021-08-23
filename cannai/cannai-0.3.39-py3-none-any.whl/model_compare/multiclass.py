import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import sklearn
from .base import *
import sys
import pandas as pd
import seaborn as sns
import math
import lightgbm
from .. import cannai_class

color_list = ["g", "r", "b", "y", "m", "c", "deeppink", "darkseagreen", "orengered", "darkslategray"]


def multiclass_base(C_mod, key_list, tl):
    tkl = type(key_list)
    if (key_list == None) or (key_list == "all"):
        if type(C_mod) == cannai_class.multi_Cmodel: key_list = C_mod.model_name_dict
        else: key_list = C_mod.model_name_list[tl]
    elif (tkl is str) or (tkl is int): key_list = [key_list]
    if len(key_list) > 10:
        raise ImportError("maximum number of keys inputs is 10, but " + str(len(key_list)) + " was input")
    try:
        if C_mod.iscannai != True:
            raise ImportError("C_mod.iscannai is not true")
    except AttributeError:
        raise ImportError("C_mod is not cannai classes")

    if key_list == []:
        raise ImportError("key_list is empty")

    return key_list


def get_labels(df):
    if type(df) is pd.core.series.Series:
        return df.name
    else:
        return df.columns


def add_labels(df, addi):
    if type(df) is pd.core.series.Series:
        df.name = df.name + addi
    else:
        dc = df.columns
        for ii in range(len(dc)):
            dc[ii] = dc[ii] + addi
        df.columns = dc
    return df


def get_line(df, l_name):
    if type(df) is pd.core.series.Series:
        if df.name != l_name and l_name != 0:
            raise IndexError(str(l_name) + "is not included in this data")
        else:
            return df
    else:
        return df[l_name]

class multiclass_lib:
    def __init__(self, parent):
        self.parent = parent

    def bar(self, key_list, target_line, score_list,target_label=None):
        multiclass_bar(self.parent, key_list, target_line, score_list,target_label)

    def scatter(self, key_list, target_line, explanatory_line_list,target_label=None):
        multiclass_scatter(self.parent, key_list, target_line, explanatory_line_list,target_label)

    def matrix(self, key_list,target_label=None):
        multiclass_matrix(self.parent, key_list,target_label)

    def rank(self, key_list, target_line ,score_type = "abs", comvert="default", show_range="top50",target_label=None):
        multiclass_rank(self.parent, key_list, target_line, score_type, comvert, show_range,target_label)

    def radarchart(self, key_list, target_line,target_label=None):
        multiclass_radarchart(self.parent, key_list, target_line,target_label)

    def f_importance(self, key_list,bar_type=None,target_label=None):
        multiclass_f_importance(self.parent, key_list,bar_type,target_label)

def check_multi_cmodel(C_mod, target_line, target_label):
    if type(C_mod) == cannai_class.multi_Cmodel:
        if target_label == None:
            raise IndexError(
                "please input target_label")
        elif target_line != None:
            raise IndexError(
                "please input target_line as None")
        elif type(target_label) != list:
            target_label = [target_label]

        C_mod.out_is_S = True
    elif target_line != None:
        target_label = [None]
        C_mod.out_is_S = True
    else:
        C_mod.out_is_S = False

    return target_label

def multiclass_bar(C_mod, key_list, target_line, score_list,target_label=None):
    """print bar graph for comparing models

    Parameters:
    ----------
    C_mod : cannai_model

    key_list : list of (int or str)
        key list of loading each model
    
    target_line : int or str or None
        label of column which wanted to use for plotting y
        if you are using multi_Cmodel, please set this None

    score_list : str or (list of str)
        list of evaluate score, what you want to display
        regression: MAE,MSE,RMSE,MSLE,RMSLE,R2
        binary classification(label): binary_accuracy,precision,recall,binary_f1,binary_f1_weighted,balanced_accuracy
        binary classification(rate_list): binary_cross_entropy(binary_logloss),binary_auc,auc_micro,average_precision
        multi classification(label): accuracy,cross_entropy(logloss),
        multi classification(rate_list): f1,f1_weighted,auc,auc_micro,auc_ovr,auc_ovo,auc_ovr_weighted,auc_ovo_weighted

    target_label : None or str or list
        if you are not using multi_Cmodel, do not set this input.
        you you are using it, each model group called by target_label.

    """

    target_label = check_multi_cmodel(C_mod, target_line, target_label)

    tsl = type(score_list)
    if (tsl is str) or (tsl is int): score_list = [score_list]



    len_score_l = len(score_list)

    for tl1 in target_label:
        key_list = multiclass_base(C_mod, key_list, tl1)
        print(key_list)
        len_key_l = len(key_list)
        fig = plt.figure(figsize=(8.0, 6.0))
        labels = C_mod.get_names(key_list, target_label=tl1)
        ax_list = []
        if tl1 != None: target_line = [tl1]
        for count in range(len_score_l):
            ax = fig.add_subplot(1, len_score_l, count + 1)
            e_score = score_list[count]
            score_out = C_mod.Cal_s.cal_score_multiple(key_list, target_line, e_score)
            left = np.array([ii + 1 for ii in range(len_key_l)])
            height = score_out
            ax.bar(left, height, tick_label=labels, color=color_list[:len_key_l], align="center")
            ax.set_title(e_score)
            ax.set_xlabel("models")
            ax.set_ylabel("score")
            ax.grid(True)
            ax_list.append(ax)
        plt.tight_layout()
        plt.show()


def multiclass_scatter(C_mod, key_list, target_line, explanatory_line_list,target_label=None):
    """ print scatter graph for comparing models

    Parameters:
    ----------
    C_mod : cannai_model

    key_list : list of (int or str)
        key list of loading each model

    target_line : int or str or None
        label of column which wanted to use for plotting y
        if you are using multi_Cmodel, please set this None

    explanatory_line_list : str or (list of str)
        labels of column which wanted to use for plotting x

    target_label : None or str or list
        if you are not using multi_Cmodel, do not set this input.
        you you are using it, each model group called by target_label.


    """
    target_label = check_multi_cmodel(C_mod, target_line, target_label)

    fig = plt.figure(figsize=(8.0, 12.0))

    ltl = len(target_label)

    for tl1 in target_label:
        if tl1 != None: target_line = [tl1]
        if explanatory_line_list is str: explanatory_line_list = [explanatory_line_list]
        key_list = multiclass_base(C_mod, key_list)
        labels = C_mod.get_names(key_list,target_label=tl1)

        len_key_l = len(key_list)
        len_exp_l = len(explanatory_line_list)

        out_l_list = C_mod.get_datas(key_list,target_label=tl1)

        inp_df = C_mod.get_input()
        ans_df = C_mod.get_answer(tl1,no_multiple_flag=True)

        target_name = C_mod.get_labelname(target_line,target_label=tl1)

        ans_li = get_line(ans_df, target_name)

        ax_list = []

        for count in range(len_exp_l):

            exp_name = explanatory_line_list[count]
            inp_li = get_line(inp_df, exp_name)


            for count2 in range(len_key_l):
                ax = fig.add_subplot(len_exp_l*len_key_l, 1, count * len_key_l + count2 + 1)
                out_l0 = out_l_list[count2]
                out_l = get_line(out_l0, target_line)
                sa_l = out_l - ans_li
                ax.bar(inp_li, out_l, label=labels[count], color=color_list[count], align="center")
                ax.set_xlabel(exp_name)
                ax.set_ylabel(target_name)
                ax.grid(True)
                ax_list.append(ax)
    plt.tight_layout()
    plt.legend(loc='upper left')
    plt.show()


def multiclass_matrix(C_mod, key_list,target_label):

    """print matrix graph for comparing models

    Parameters:
    ----------
    C_mod : cannai_model

    key_list : list of (int or str)
        key list of loading each model
    """

    key_list = multiclass_base(C_mod, key_list)
    labels = C_mod.get_names(key_list,target_label=target_label)

    len_key_l = len(key_list)

    fig = plt.figure(figsize=(8.0, 6.0))
    ax_list = []

    x_line = get_labels(C_mod.get_input())
    y_line = get_labels(C_mod.get_answer(target_label,no_multiple_flag=True))

    ax = fig.add_subplot(1, 1, 1)

    base_df = C_mod.get_input().var()
    base_df.name = "distribute"

    labels = C_mod.get_names(key_list,target_label=target_label)

    for count in range(len_key_l):
        comb_df0 = C_mod.Cal_s.combine_inout(count)
        comb_df1 = comb_df0.corr()
        comb_df2 = comb_df1.loc[y_line, x_line]
        comb_df2 = add_labels(comb_df2, "_(" + labels[count] + ")")
        base_df = pd.concat([base_df, comb_df2], axis=1)

    print(base_df)
    sns.heatmap(base_df.drop(columns="distribute"), annot=True, ax=ax)

    plt.tight_layout()
    plt.show()


def multiclass_rank(C_mod, key_list, target_line ,score_type = "abs", comvert="default", show_range="top50",target_label=None):
    """print ranking graph for comparing models
    Args:

        C_mod : cannai_model

        key_list : list of (int or str)
            key list of loading each model

        score_type : str(default: "abs")
            "abs": | pred_value - true_value |
            "rel": | 1 - (pred_value / true_value) |

        comvert: str(default: "default")
            y value conversion
            "default": no change
            "log": convert to log10 value

        show_range: str
            show top / bottom X datas
            (X must be int value)
            "topX": show X datas from top
            "botX": show X datas from bottom

    """
    target_label = check_multi_cmodel(C_mod, target_line, target_label)

    labels = C_mod.get_names(key_list,target_label=target_label)



    for tl1 in target_label:
        key_list = multiclass_base(C_mod, key_list, tl1)
        len_key_l = len(key_list)
        target_name = C_mod.get_labelname(target_line, target_label=target_label)
        fig = plt.figure(figsize=(8.0, 6.0))
        ax = fig.add_subplot(1, 1, 1)
        ax_list = []

        sa_lists = []

        for count in range(len_key_l):
            key = key_list[count]
            out_l, ans_l = C_mod.Cal_s.get_inout(key, target_line,target_label=target_label)

            if score_type == "abs":
                sa_l = out_l - ans_l
            elif score_type == "rel":
                sa_l = (out_l - ans_l) / ans_l
            else: raise IndexError("score_type must be diff or prod")

            sa2 = sa_l.values.tolist()
            for ss in sa2:
                if score_type == "abs": ss_b = abs(ss)
                elif score_type == "rel": ss_b = abs(ss)
                sa_lists.append([ss_b, count])

        sa_lists = sorted(sa_lists)
        l_sal = len(sa_lists)

        try:
            vv = int(show_range[3:])
        except ValueError:
            raise IndexError("show_range does not match topX or botX")

        if show_range[:3] == "top":
            if l_sal > vv: sa_lists = sa_lists[l_sal - vv:]
        elif show_range[:3] == "bot":
            if l_sal > vv: sa_lists = sa_lists[:vv]
        else: raise IndexError("show_range must be started from top or bot")

        l_sal = len(sa_lists)

        for count in range(len_key_l):

            v_list = []
            c_list = []
            for c2 in range(l_sal):
                c_list.append(c2)
                if sa_lists[c2][1] == count:
                    v_list.append(sa_lists[c2][0])
                else: v_list.append(0)

            if show_range[:3] == "top": c_list.reverse()

            if comvert == "log": ax.set_yscale('log')
            #ax.scatter(c_list, v_list, label=labels[count], color=color_list[count], s=8, alpha=0.4)
            ax.bar(c_list, v_list, label=labels[count], color=color_list[count], align="center")


        ax.set_ylabel(target_name + "_error")
        ax.grid(True)
        plt.tight_layout()
        if show_range[:3] == "top": plt.legend(loc='upper right')
        else: plt.legend(loc='upper left')
        plt.show()

def multiclass_radarchart(C_mod, key_list, target_line,target_label=None):
    """print radar chart for comparing models easily
    Args:

        C_mod : cannai_model

        key_list : list of (int or str)
            key list of loading each model

        target_line : int or str
            label of column which wanted to calculate

    """

    def log_change(in_num):
        if in_num >= 0: return math.log10(in_num)
        else: return -1.0 * math.log10(-1.0 * in_num)

    key_list = multiclass_base(C_mod, key_list)
    labels = C_mod.get_names(key_list,target_label=target_label)

    len_key_l = len(key_list)
    c_type = C_mod.class_type

    fig = plt.figure(figsize=(20.0, 15.0))
    ax_list = []

    if c_type == "b":
        e_score_list = ["accuracy", "precision", "recall", "logloss", "binary_auc"]
        e_title = ["accuracy", "precision", "recall", "logloss_inverse", "auc_inverse"]
        score_out = C_mod.Cal_s.cal_score_multiple_2d(key_list, target_line, e_score_list)

        for cc in range(len(score_out[0])):
            score_out[3][cc] = log_change(score_out[3][cc])
            score_out[4][cc] = log_change(score_out[4][cc])

        max_list = []
        min_list = []
        for so in score_out:
            max_list.append(max(so))
            min_list.append(min(so))

        for ii in range(5):
            if min_list[ii] > 0: min_list[ii] = 0

        for cc in range(len(score_out[0])):
            score_out[0][cc] /= max_list[0]
            score_out[1][cc] /= max_list[1]
            score_out[2][cc] /= max_list[2]
            score_out[3][cc] = (max_list[3] - score_out[3][cc]) / (max_list[3] - min_list[3])
            score_out[4][cc] = (max_list[4] - score_out[4][cc]) / (max_list[4] - min_list[4])

    elif c_type == "a":
        e_score_list = ["accuracy", "f1", "logloss", "auc"]
        e_title = ["accuracy", "f1", "logloss_inverse", "auc_inverse"]

        score_out = C_mod.Cal_s.cal_score_multiple_2d(key_list, target_line, e_score_list)

        for cc in range(len(score_out[0])):
            score_out[2][cc] = log_change(score_out[2][cc])
            score_out[3][cc] = log_change(score_out[3][cc])

        max_list = []
        min_list = []
        for so in score_out:
            max_list.append(max(so))
            min_list.append(min(so))

        for ii in range(4):
            if min_list[ii] > 0: min_list[ii] = 0

        for cc in range(len(score_out[0])):
            score_out[0][cc] /= max_list[0]
            score_out[1][cc] /= max_list[1]
            score_out[2][cc] = (max_list[2] - score_out[2][cc]) / (max_list[2] - min_list[2])
            score_out[3][cc] = (max_list[3] - score_out[3][cc]) / (max_list[3] - min_list[3])

    elif c_type == "r":
        e_score_list = ["rmse","r2","mae","rmsle"]
        e_title = ["rmse_inverse","r2_inverse","mae_inverse","rmsle_inverse"]

        score_out = C_mod.Cal_s.cal_score_multiple_2d(key_list, target_line, e_score_list)

        for cc in range(len(score_out[0])):
            score_out[0][cc] = log_change(score_out[0][cc])
            score_out[1][cc] = log_change(score_out[1][cc])
            score_out[2][cc] = log_change(score_out[2][cc])
            score_out[3][cc] = log_change(score_out[3][cc])

        max_list = []
        min_list = []
        for so in score_out:
            max_list.append(max(so))
            min_list.append(min(so))

        for ii in range(4):
            if min_list[ii] > 0: min_list[ii] = 0

        for cc in range(len(score_out[0])):
            score_out[0][cc] = (max_list[0] - score_out[0][cc]) / (max_list[0] - min_list[0])
            score_out[1][cc] = (max_list[1] - score_out[1][cc]) / (max_list[1] - min_list[1])
            score_out[2][cc] = (max_list[2] - score_out[2][cc]) / (max_list[2] - min_list[2])
            score_out[3][cc] = (max_list[3] - score_out[3][cc]) / (max_list[3] - min_list[3])

    val_list = list(zip(*score_out))

    ax = fig.add_subplot(len_key_l+1, 1, 1, polar=True)
    for count in range(len_key_l):
        vals = val_list[count]
        angles = np.linspace(0, 2 * np.pi, len(vals) + 1, endpoint=True)
        values = np.concatenate((vals, [vals[0]]))  # 閉じた多角形にする
        ax.plot(angles, values, 'o-', color=color_list[count])  # 外枠
        ax.set_thetagrids(angles[:-1] * 180 / np.pi, e_title)  # 軸ラベル
        ax.set_rlim(0, 1)
    ax.set_title(labels[count])
    ax_list.append(ax)

    for count in range(len_key_l):
        vals = val_list[count]
        ax = fig.add_subplot(len_key_l+1, 1, count + 2, polar=True)
        angles = np.linspace(0, 2 * np.pi, len(e_title) + 1, endpoint=True)
        values = np.concatenate((vals, [vals[0]]))  # 閉じた多角形にする
        print(values)
        ax.plot(angles, values, 'o-', color=color_list[count])  # 外枠
        ax.fill(angles, values, alpha=0.25, color=color_list[count])  # 塗りつぶし
        ax.set_thetagrids(angles[:-1] * 180 / np.pi, e_title)  # 軸ラベル
        ax.set_rlim(0, 1)
        ax.set_title(labels[count])
        ax_list.append(ax)
    plt.tight_layout()
    plt.show()

def multiclass_f_importance(C_mod, key_list, bar_type = None,target_label=None):
    """print bar chart about feature importance of models
    Args:

        C_mod : cannai_model

        key_list : list of (int or str)
            key list of loading each model

        bar_type: None or str
            None: show feature importance of each model
            "overlaid": make overlaid bar graph
            "lineup": sort label by score and show in one graph


    """

    def get_feature_importance(l_mod):
        #print(type(l_mod))
        if type(l_mod) == lightgbm.basic.Booster: return l_mod.feature_importance()
        else: return l_mod.feature_importances_

    le_ke = len(key_list)
    labels = C_mod.get_names(key_list,target_label=target_label)

    if bar_type == None:
        fig = plt.figure(figsize=(8.0, 6.0))
        ax_list = []
        for iii in range(le_ke):
            ax = fig.add_subplot(le_ke, 1, iii+1)
            l_mod = C_mod.get_model(key_list[iii],target_label=target_label)
            lbiii = labels[iii]
            fe_i = pd.DataFrame(get_feature_importance(l_mod), index=C_mod.get_input().columns, columns=[lbiii])
            fe_i = fe_i.sort_values(lbiii, ascending=True)
            labels_b = fe_i.index
            le_la = len(labels_b)
            left = np.array([ii + 1 for ii in range(le_la)])
            height = fe_i[lbiii]
            ax.barh(left, height, tick_label=labels_b, color=color_list[iii], align="center")
            ax.set_title(lbiii)
            ax.set_ylabel("labels")
            ax.grid(True)
            ax_list.append(ax)
        ax_list[-1].set_xlabel("importance")
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.7)
        plt.show()
    elif (bar_type == "overlaid") or (bar_type == "lineup"):
        fig = plt.figure(figsize=(8.0, 12.0))
        ax = fig.add_subplot(1, 1, 1)
        l_mod = C_mod.get_model(key_list[0])
        fei0 = get_feature_importance(l_mod)
        fe_i = pd.DataFrame(fei0/fei0.max(), index=C_mod.get_input().columns, columns=[labels[0]])
        for iii in range(1,le_ke):
            l_mod = C_mod.get_model(key_list[iii])
            lbiii = labels[iii]
            fei0 = get_feature_importance(l_mod)
            fe_i[lbiii] = fei0/fei0.max()

        fe_i["all_model_sum_akods"] = fe_i.sum(axis=1)
        fe_i = fe_i.sort_values("all_model_sum_akods", ascending=True)
        labels_b = fe_i.index
        le_la = len(labels_b)

        if bar_type == "overlaid":
            left = np.array([ii + 1 for ii in range(le_la)])
            print(left)
            sum_heig = [0 for jjj in range(le_la)]

            for iii in range(le_ke):
                height = fe_i.iloc[:,iii]
                ax.bar(left, height,bottom=sum_heig , color=color_list[iii], align="center", label=labels[iii])
                hvt = height.values.tolist()
                for iii2 in range(le_la):
                    sum_heig[iii2] += hvt[iii2]
            ax.set_ylabel("importance")
            ax.set_xlabel("labels")
            ax.set_xticks(left)
            ax.set_xticklabels(labels_b)
            ax.legend(loc="upper left")
            ax.grid(True)

        elif bar_type == "lineup":
            b_width = 0.8 / le_ke
            left = np.array([ii + 1 for ii in range(le_la)])
            for iii in range(le_ke):
                height = fe_i.iloc[:, iii]
                ax.bar(left + b_width*iii, height, width = b_width, color=color_list[iii], align="center", label=labels[iii])
            ax.set_ylabel("importance")
            ax.set_xlabel("labels")
            ax.set_xticks(left + b_width * 0.5 * (le_ke - 1))
            ax.set_xticklabels(labels_b)
            ax.legend(loc="upper left")
            ax.grid(True)

        plt.subplots_adjust(hspace=0.4)
        plt.tight_layout()
        plt.show()





