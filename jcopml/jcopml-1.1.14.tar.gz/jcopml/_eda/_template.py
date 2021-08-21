import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from ipywidgets import HBox, Tab, Output


class NumVsCat(HBox):
    def __init__(self, df, col, target_col=None):
        super().__init__()
        sns.set_palette(sns.color_palette("bright"))

        individual = Output()
        with individual:
            fig, ax = plt.subplots(2, 1, figsize=(8, 6), sharex=True, gridspec_kw={"height_ratios": (.15, .85)})
            fig.subplots_adjust(hspace=0.05)

            sns.boxplot(df[col].dropna(), ax=ax[0])
            ax[0].set_xlabel("")

            sns.distplot(df[col].dropna(), ax=ax[1])
            ax[1].set_xlabel(col, fontdict={"size": 14})
            plt.show(fig)

        if target_col is not None:
            correlation = Output()
            with correlation:
                _, bins = np.histogram(df[col].dropna())

                fig = sns.FacetGrid(df, height=5, aspect=7 / 5, hue=target_col)
                fig = fig.map(sns.distplot, col, bins=bins);
                fig.ax.set_xlabel(f"{col} vs {target_col}", fontdict={"size": 14})
                plt.legend()
                plt.show(fig)
            self.children = [individual, correlation]
        else:
            self.children = [individual]


class CatVsCat(HBox):
    def __init__(self, df, col, target_col=None):
        super().__init__()
        sns.set_palette(sns.color_palette("bright"))

        individual = Output()
        with individual:
            fig, ax = plt.subplots(1, 1, figsize=(8, 6))
            sns.countplot(df[col].dropna(), ax=ax)
            ax.set_xlabel(col, fontdict={"size": 14})
            plt.show(fig)

        if target_col is not None:
            correlation = Output()
            with correlation:
                fig, ax = plt.subplots(1, 1, figsize=(8, 6))
                sns.countplot(df[col].dropna(), ax=ax, hue=df[target_col])
                ax.set_xlabel(f"{col} vs {target_col}", fontdict={"size": 14})
                plt.show(fig)
            self.children = [individual, correlation]
        else:
            self.children = [individual]


class BoolVsCat(HBox):
    def __init__(self, df, col, target_col=None):
        super().__init__()
        individual = Output()
        with individual:
            percentage = df[col].value_counts()

            fig, ax = plt.subplots(1, 1, figsize=(5, 5))
            sns.set_palette(sns.color_palette("bright"))
            ax.pie(percentage.values, labels=percentage.index, autopct='%1.1f%%', textprops={"size": 14})
            plt.show(fig)

        if target_col is not None:
            correlation = Output()
            with correlation:
                fig, ax = plt.subplots(1, 1, figsize=(8, 6))
                df_count = df.dropna(subset=[target_col, col])
                df_count = df_count.groupby([target_col, col])[col].agg(count="count").reset_index()

                sns.barplot(col, "count", hue=target_col, data=df_count, ax=ax)
                ax.set_xlabel(f"{col} vs {target_col}", fontdict={"size": 14})
                plt.show(fig)
            self.children = [individual, correlation]
        else:
            self.children = [individual]


class OrdVsCat(HBox):
    def __init__(self, df, col, target_col=None):
        super().__init__()
        sns.set_palette(sns.color_palette("bright"))

        individual = Output()
        with individual:
            percentage = df[col].value_counts()

            fig, ax = plt.subplots(1, 1, figsize=(8, 6))
            sns.barplot(percentage.index, percentage.values, ax=ax)
            ax.set_xlabel(col, fontdict={"size": 14})
            plt.show(fig)

        if target_col is not None:
            correlation = Output()
            with correlation:
                fig, ax = plt.subplots(1, 1, figsize=(8, 6))
                df_count = df.dropna(subset=[target_col, col])
                df_count = df_count.groupby([target_col, col])[col].agg(count="count").reset_index()

                sns.barplot(col, "count", hue=target_col, data=df_count, ax=ax)
                ax.set_xlabel(f"{col} vs {target_col}", fontdict={"size": 14})
                plt.show(fig)
            self.children = [individual, correlation]
        else:
            self.children = [individual]


class NumVsNum(HBox):
    def __init__(self, df, col, target_col=None):
        super().__init__()
        sns.set_palette(sns.color_palette("bright"))

        individual = Output()
        with individual:
            fig, ax = plt.subplots(2, 1, figsize=(8, 6), sharex=True, gridspec_kw={"height_ratios": (.15, .85)})
            fig.subplots_adjust(hspace=0.05)

            sns.boxplot(df[col].dropna(), ax=ax[0])
            ax[0].set_xlabel("")

            sns.distplot(df[col].dropna(), ax=ax[1])
            ax[1].set_xlabel(col, fontdict={"size": 14})
            plt.show(fig)

        if target_col is not None:
            correlation = Output()
            with correlation:
                fig = sns.jointplot(col, target_col, data=df.dropna(subset=[col, target_col]), kind="reg", height=6)
                fig.set_axis_labels(xlabel=col, ylabel=target_col, fontsize=14)
                plt.show(fig)
            self.children = [individual, correlation]
        else:
            self.children = [individual]


class CatVsNum(HBox):
    def __init__(self, df, col, target_col=None):
        super().__init__()
        sns.set_palette(sns.color_palette("bright"))

        individual = Output()
        with individual:
            fig, ax = plt.subplots(1, 1, figsize=(8, 6))
            sns.countplot(df[col].dropna(), ax=ax)
            ax.set_xlabel(col, fontdict={"size": 14})
            plt.show(fig)

        if target_col is not None:
            correlation = Output()
            with correlation:
                fig, ax = plt.subplots(1, 1, figsize=(8, 6))
                sns.boxplot(col, target_col, ax=ax, data=df.dropna(subset=[col, target_col]))
                ax.set_xlabel(f"{col} vs {target_col}", fontdict={"size": 14})
                plt.show(fig)
            self.children = [individual, correlation]
        else:
            self.children = [individual]


def _create_tabs(plot_class, dataframe, cols, target_col=None):
    if isinstance(cols, str):
        cols = [cols]

    plots = Tab(children=[plot_class(dataframe, col, target_col) for col in cols])
    for i, title in enumerate(cols):
        plots.set_title(i, title)
    return plots


def num_cat_tabs(dataframe, cols, target_col=None):
    return _create_tabs(NumVsCat, dataframe, cols, target_col)


def cat_cat_tabs(dataframe, cols, target_col=None):
    return _create_tabs(CatVsCat, dataframe, cols, target_col)


def bool_cat_tabs(dataframe, cols, target_col=None):
    return _create_tabs(BoolVsCat, dataframe, cols, target_col)


def ord_cat_tabs(dataframe, cols, target_col=None):
    return _create_tabs(OrdVsCat, dataframe, cols, target_col)


def num_num_tabs(dataframe, cols, target_col=None):
    return _create_tabs(NumVsNum, dataframe, cols, target_col)


def cat_num_tabs(dataframe, cols, target_col=None):
    return _create_tabs(CatVsNum, dataframe, cols, target_col)
