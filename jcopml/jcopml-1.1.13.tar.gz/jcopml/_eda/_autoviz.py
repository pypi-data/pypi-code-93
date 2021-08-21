from ipywidgets import Accordion

from ._template import bool_cat_tabs, ord_cat_tabs, cat_cat_tabs, num_cat_tabs, num_num_tabs, cat_num_tabs
from ._autocol import analyze_columns_type


def classification_eda(df, target_col, num_col="auto", cat_col="auto", bool_col="auto", ord_col="auto"):
    is_binary = df[target_col].nunique() == 2
    num_col, cat_col, bool_col, ord_col = _update_cols(df, target_col, num_col, cat_col, bool_col, ord_col)

    targets = bool_cat_tabs(df, target_col) if is_binary else cat_cat_tabs(df, target_col)
    numcat = num_cat_tabs(df, num_col, target_col)
    catcat = cat_cat_tabs(df, cat_col, target_col)
    ordcat = ord_cat_tabs(df, bool_col + ord_col, target_col)

    accordion = Accordion(children=[targets, numcat, catcat, ordcat])
    for i, title in enumerate(["Target", "Numerical  Input", "Categorical Input", "Boolean & Ordinal Input"]):
        accordion.set_title(i, title)
    accordion.selected_index = None
    return accordion


def regression_eda(df, target_col, num_col="auto", cat_col="auto", bool_col="auto", ord_col="auto"):
    num_col, cat_col, bool_col, ord_col = _update_cols(df, target_col, num_col, cat_col, bool_col, ord_col)

    targets = num_num_tabs(df, target_col)
    numnum = num_num_tabs(df, num_col, target_col)
    catnum = cat_num_tabs(df, cat_col, target_col)
    ordnum = cat_num_tabs(df, bool_col + ord_col, target_col)

    accordion = Accordion(children=[targets, numnum, catnum, ordnum])
    for i, title in enumerate(["Target", "Numerical  Input", "Categorical Input", "Boolean & Ordinal Input"]):
        accordion.set_title(i, title)
    accordion.selected_index = None
    return accordion


def _update_cols(df, target_col, num_col, cat_col, bool_col, ord_col):
    auto_cols = analyze_columns_type(df, target_col)
    if num_col == "auto":
        num_col = auto_cols[0]
    if cat_col == "auto":
        cat_col = auto_cols[1]
    if bool_col == "auto":
        bool_col = auto_cols[2]
    if ord_col == "auto":
        ord_col = auto_cols[3]
    return num_col, cat_col, bool_col, ord_col
