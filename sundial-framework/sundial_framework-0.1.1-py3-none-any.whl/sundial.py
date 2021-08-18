import math
import numbers

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler

TOLERANCE_DP = 6
TOLERANCE = 10 ^ (-TOLERANCE_DP)
BIN_TOL = 0.001
DEFAULT_PRED_AT = "predicted_at"


# -----------------
# Binner Class
# -----------------
class Binner:
    """
    Binning class for use in time series bin-based classifier models of discrete distros

    Bins are defined as (], and the left hand bin is assumed to be inclusive. Thus bin edges = [0,4,7,10] gives three bins (-0.001,4], (4,7], (7,10]

    """

    def __init__(self, bin_edges, data=pd.Series([], dtype="float64"), name=None, inclusive=True):
        """
        Construct a data binner.
        The binner can then be used to transform a provided data series into binned data, as per the bins in the binner

        Note that you should provide some data to fit the binner to during initialisation. This helps us to ensure that the binner is wide enough to cope with the anticipated data we will be binning.

        data -> data to bin. 1-D Array-like object (list, series etc)
        bins -> list of bin (upper) edge values
        name -> base name for the series, to use when labeling the columns
        inclusive -> True - extend the fist and last bin edges to ensure all values in data are included, False results in error if data falls outside the bins

        """
        # init
        self._init_bin_edges = None  # bin upper bounds provided at init
        self._bin_edges = None  # bin upper bounds
        self._bins_cat = None  # Categorical object for the calculated bins and binned data
        # Q: is this needed? Have commented out
        # self._raw_data = None # original (raw) data

        # check parameters

        if not isinstance(bin_edges, list):
            msg = "List of bins expected"
            raise ValueError(msg)
        if not (isinstance(name, str) or name is None):
            msg = "Name should be a string or None"
            raise ValueError(msg)

        # store the initialised edges. Edges are sorted from low to high
        self._init_bin_edges = bin_edges.copy()
        self._init_bin_edges.sort()

        # Fit the binner
        self._bins_cat, self._bin_edges = self._fit(data, self._init_bin_edges, inclusive)
        self._name = name

    def _fit(self, data, edges, inclusive=True):
        """
        Fit the binner to the provided data
        data -> series-like object to bin
        edges -> edges defining the bins
        inclusive -> expand the bin edges to ensure all data is in the binner
        """

        if not isinstance(inclusive, bool):
            msg = "Inclusive parameter must be boolean. You've passed something else"
            raise ValueError(msg)

        # ensure data is now a pd.Series
        df = self._process_data(data)

        # ensure bins cover the data, or quit if not
        edges = edges.copy()
        if inclusive:
            edges = self._fit_bin_edges(data, edges)
        if df.min().min() < edges[0] or df.max().max() > edges[-1]:
            msg = "Data lies outside bin edges - try setting inclusive=True"
            raise ValueError(msg)

        # perform binning and return the cut and the edges
        return pd.cut(df, bins=edges, include_lowest=False), edges

    def transform(self, data, truncate=True):
        """
        Transform the series in data to a set of dummy variables, 1 for each of the binner's bins

        data -> series like object
        truncate -> boolean, True if data outside the lowest/highest bin is truncated to the lowest/highest bin respectively. If false, data outside the bins will cause an error
        """
        # ensure data is a pd.Series (or put it in one if able)
        df = self._process_data(data)

        # truncate by expanding low/high bin edges to fit the data.
        # we then ensure the dummy column labels match the _bins_cat
        edges = self._bin_edges.copy()
        if truncate:
            edges = self._fit_bin_edges(df, edges)
        # cut the data to categories given by the binner edges
        cat = pd.cut(df, edges, include_lowest=False)
        # return the dummys. Note column labels are set to the original _bins_cat labels
        # The labels from "cat" are not used (as first and last label may be "wrong" due to
        # the way we are doing the truncation, AND we want to augment the bin labels with the given name, so that we dont end up with many features with the same bins and hence the same labels) - so we need to replace with the binner's correct labels.
        # In this way we perform truncation without needing to alter the data...
        df_ret = pd.get_dummies(cat)
        df_ret.columns = self.bin_labels
        return df_ret

    def inverse_transform(self, data):
        """
        Inverse transform a binning to a value, one for each row in data.

        For example, lets say the binner has 5 bins. _data_ will have 5 columns, one for each bin, and value(row_z) = row_z * bin_mids
        """
        # first, make sure data is an array or dataframe, and convert to dataframe if required
        df = self._process_dataframe_like_data(data)
        # make sure num cols = num bins
        if len(df.columns) != self.bin_count:
            msg = "Data needs to have {} columns - but it has {}".format(self.bin_count, len(df.columns))
            raise ValueError(msg)
        df_res = (df * self.bin_mid).sum(axis=1)
        df_res.name = "value"
        # convert results back to a np array or list if data was passed as such
        if isinstance(data, np.ndarray):
            df_res = df_res.values.round(TOLERANCE_DP)
        if isinstance(data, list):
            df_res = df_res.values.round(TOLERANCE_DP).tolist()
        return df_res

    def cumulative_probs(self, data):
        """Calculate cumulative probabilities for bucketed values"""

        # first, make sure data is an array or dataframe, and convert to dataframe if required
        df = self._process_dataframe_like_data(data)
        # make sure num cols = num bins
        if len(df.columns) != self.bin_count:
            msg = "Data needs to have {} columns - but it has {}".format(self.bin_count, len(df.columns))
            raise ValueError(msg)

        # check the probs dont sum > 1 rowwise
        if df.sum(axis=1).max() > 1:
            msg = "Probabilities sum > 1 in at least one row - exiting, rather than guessing how to interpret this."
            raise ValueError(msg)
        # possible - warning if probs sum to < 1 row-wise??

        # calculate the cumulative probs
        # note: this assumes the bins (and thus labels) are in order - which they should be in the binner
        # the data is assumed to be in the same order as the bins
        df_cum_pred = df.copy()
        for b in range(1, len(df.columns)):
            df_cum_pred.iloc[:, b] = df_cum_pred.iloc[:, b - 1] + df.iloc[:, b]
        # convert results back to a np array or list if data was passed as such
        if isinstance(data, np.ndarray):
            df_cum_pred = df_cum_pred.values.round(TOLERANCE_DP)
        if isinstance(data, list):
            df_cum_pred = df_cum_pred.values.round(TOLERANCE_DP).tolist()
        return df_cum_pred

    def calc_quantiles(self, data, quantiles):
        """
        calculate quantiles

        data -> dataframe-like object (dataframe, np array, list) of bin probabilities
        quantiles -> list of quantiles to return

        Returns
        dataframe of quantiles

        """
        # check the quantiles
        if not (isinstance(quantiles, list) or isinstance(quantiles, np.ndarray) or isinstance(quantiles, pd.Series)):
            msg = "Expected quantiles to be list, np array or series"
            raise ValueError(msg)
        quantiles = np.array(quantiles)
        if len(quantiles.shape) > 1:
            msg = "Expected 1-D list-like object of quantiles - got something with shape {}".format(quantiles.shape)
            raise ValueError(msg)
        for x in quantiles:
            if x < 0 or x > 1:
                msg = "Quantiles need to be between 0 and 1 - got a quantile = {}".format(x)
                raise ValueError(msg)

        # first, process into cumulative probabilities, and pack into dataframe
        df_c = pd.DataFrame(self.cumulative_probs(data))
        df_quantile = pd.DataFrame(index=df_c.index)
        for quant in quantiles:
            df_quantile[str(quant)] = self._calc_quantile_values(df_c, quant)
        return df_quantile

    def _calc_quantile_values(self, df, quantile):
        """Calculate the value for the given quantile, for each row"""

        df_q = pd.DataFrame(None, index=df.index, columns=[quantile])

        for idx, row in df.iterrows():
            # note - the rows are in monotonically non-decreasing order
            # calculate the label for the bin the quantile is in. Remember bins are (] by definition
            rowtail = row[row >= quantile]

            if len(rowtail > 0):
                # we have found a cum prob >= quantile
                # get the index and cum prob of this bin
                bidx = rowtail.index[0]
                cumprob = row[bidx]
                # get the cum prob corresponding to the previous bin also
                if bidx > 0:
                    cumprob_prev = row[bidx - 1]
                else:
                    cumprob_prev = 0
                if cumprob > cumprob_prev:
                    # in a bin with a non-zero prob
                    weight = (quantile - cumprob_prev) / (cumprob - cumprob_prev)
                    val = weight * self.bin_right[bidx] + (1 - weight) * self.bin_left[bidx]
                else:
                    # in a bin with a 0 prob. Thus we set the val for teh quantile to be the bins mid
                    val = self.bin_mid[bidx]
            else:
                # quantile is > cum prob for the largest bin we have, so set val = largest val we have
                val = self.bin_right[-1]

            df_q.loc[idx] = val
        return df_q

    def _process_data(self, data):
        """
        Test that the data is a series-like object and put it into a pd.Series
        """
        df = data.copy()
        if isinstance(df, np.ndarray) or isinstance(df, list):
            df = pd.Series(np.array(df))  # will fail if not 1 dimensional
        if isinstance(df, pd.DataFrame):
            df = df.squeeze()  # squeeze will not work if > 1 columns
            if isinstance(df, pd.DataFrame):
                msg = "Expected dataframe with one column only - got multiple columns"
        if not isinstance(df, pd.Series):
            msg = "Data needs to be a 1-D dataframe, list or np array or 1-D series"
            raise ValueError(msg)
        return df

    def _process_dataframe_like_data(self, data):
        """
        Test that the data is a (max 2-D) dataframe-like object and put it into a pd.dataframe
        """
        df = data.copy()
        if isinstance(df, np.ndarray) or isinstance(df, list):
            df = pd.DataFrame(np.array(df))
        if isinstance(df, pd.Series):
            df = pd.DataFrame(df)
        if not isinstance(df, pd.DataFrame):
            msg = "Data needs to be a 1-D or 2-D dataframe, list or np array or 1-D series"
            raise ValueError(msg)
        if len(df.shape) > 2:
            msg = "Data dimensions must be <= 2"
            raise ValueError(msg)
        # finally, if the columns of the df match the bin labels, ensure the dataframe is in the same order as the bins
        # otherwise, we dont reorder, and assume the df is already in the same order
        if set(df.columns) == set(self.bin_labels):
            df = df[self.bin_labels]
        return df

    @property
    def bin_labels(self):
        """
        Extract bin (column) labels from the bins
        """
        labels = []
        # if isinstance(self._bin_obj, list):
        #    labels = [bin.label for bin in self._bin_obj]
        name = self._name
        if name is None:
            name = ""
        for cat in self._bins_cat.dtype.categories:
            labels.extend([name + "_" + str(cat)])
        return labels

    @property
    def bin_left(self):
        """
        Extract bin left hand edge from the bins
        """
        return list(self._bins_cat.dtype.categories.left)

    @property
    def bin_right(self):
        """
        Extract bin right hand edge from the bins
        """
        return list(self._bins_cat.dtype.categories.right)

    @property
    def bin_mid(self):
        """
        Extract bin midpoints from the bins
        """
        return list(self._bins_cat.dtype.categories.mid)

    @property
    def bin_count(self):
        """
        Number of bins
        """
        return len(self._bins_cat.dtype.categories)

    @property
    def bin_dummies(self):
        """return data used to fit the binner as dummy (0,1) columns
        Equivalently you could use
        df_dummies=binner.transform(fit_data, truncate=False)"""
        df_ret = pd.get_dummies(self._bins_cat)
        df_ret.columns = self.bin_labels
        return df_ret

    def _old_fit_bin_edges(self, data, bin_edges):
        """
        Extends bin edges to include all data if required
        """
        df = pd.DataFrame(data)
        edges = bin_edges.copy()
        if df.min().min() == edges[0]:
            edges[0] -= 0.001  # decrease lowest bin edge a bit so the lowest bin includes the min data value
            # rather than making a new bin just for that min value
        elif df.min().min() < edges[0]:
            edges.extend([df.min().min() - 0.001])
        if df.max().max() > edges[-1]:
            edges.extend([df.max().max()])
        edges.sort()  # go from smallest to largest
        return edges

    def _fit_bin_edges(self, data, bin_edges):
        """
        Extends outer bin edges to include all data if required
        """
        df = pd.DataFrame(data)
        edges = bin_edges.copy()
        if df.min().min() <= edges[0]:
            edges[0] = df.min().min() - BIN_TOL
        if df.max().max() >= edges[-1]:
            edges[-1] = df.max().max()
        edges.sort()  # go from smallest to largest
        return edges


# -----------------
# Scaler Wrapper
# -----------------


class ScalerWrapper:
    """
    Class to wrap the various scalers available to us, into one object type

    """

    sklearn_scalers = {
        "sklearn_robust": RobustScaler,
        "sklearn_minmax": MinMaxScaler,
        "sklearn_standard": StandardScaler,
    }
    all_scalers = sklearn_scalers

    def __init__(self, scaler, **parameters):
        """
        scaler -> string name identifying the desired scaler
        **parameters -> list of initialisation parameters for the scaler
        """
        if not isinstance(scaler, str):
            msg = "Expected scaler to be a string identifier for the desired scaler"
            raise ValueError(msg)
        self._all_scalers = ScalerWrapper.all_scalers
        self._sklearn_scalers = ScalerWrapper.sklearn_scalers
        if scaler.lower() not in self._all_scalers:
            msg = "Unknown scaler selected -> {}".format(scaler)
            raise ValueError(msg)

        self._scaler_id = scaler.lower()
        # set the scaler
        # if scaler.lower() == "sklearn_robust":
        #    self.scaler = RobustScaler(**parameters)
        # elif scaler.lower() == "sklearn_minmax":
        #    self.scaler = MinMaxScaler(**parameters)
        # elif scaler.lower() == "sklearn_standard":
        #    self.scaler = StandardScaler(**parameters)
        if self._scaler_id in list(self._all_scalers.keys()):
            self.scaler = self._all_scalers[self._scaler_id](**parameters)

    def fit(self, **parameters):
        """wrapper for fit"""
        # currently only sklearn scalers, so we have
        try:
            if self._scaler_id in list(self._sklearn_scalers.keys()):
                self.scaler = self.scaler.fit(**parameters)
                return self
        except:
            msg = "Unable to fit scaler"
            raise ValueError(msg)

    def transform(self, **parameters):
        """wrapper for transform"""
        # currently only sklearn scalers, so we have
        try:
            if self._scaler_id in list(self._sklearn_scalers.keys()):
                return self.scaler.transform(**parameters)
        except:
            msg = "Unable to transform with scaler"
            raise ValueError(msg)

    def fit_transform(self, **parameters):
        """wrapper for fit-transform"""
        # currently only sklearn scalers, so we have
        try:
            if self._scaler_id in list(self._sklearn_scalers.keys()):
                return self.scaler.fit_transform(**parameters)
        except:
            msg = "Unable to fit & transform with scaler"
            raise ValueError(msg)

    def inverse_transform(self, **parameters):
        """wrapper for inverse transform"""
        # currently only sklearn scalers, so we have
        try:
            if self._scaler_id in list(self._sklearn_scalers.keys()):
                return self.scaler.inverse_transform(**parameters)
        except:
            msg = "Unable to inverse transform with scaler"
            raise ValueError(msg)


# -----------------
# Model Data Class
# -----------------


class ModelData:
    """
    Use a ModelData object for
        - storing the raw model data
        - splitting raw data into train, validate and test data
        - transform the raw data
             - scaling/normalising and storing the scalers
             - binning selected data and storing the binners
        - accessing the raw and transformed training, validation and test data
        - transform other data (e.g. data you will predict) using the same transformers (scalers, binners)
        - inverse-transform to un-scale other data (e.g. data you have predicted)
        - converting train, validate and test data into data windows for use in modelling
        - converting other data into the same window structure, for use in predicting
    """

    def __init__(
        self, data, data_cut, fit_scalers=True, scalers=None, binners=None, drop_binned_features=False,
    ):
        """
        data -> dataframe with features as columns
        data_cut -> dict to split the data into train, val, test, with keys "train", "val", "test and items = fraction in each
        fit_scalers -> Boolean. True if scalers are to be fitted (false assumes they already are)
        scalers -> dict holding the scalers to use per feature. {feature: sklearn scaler}
        binners -> dict holding the binner edges or already fitted binners to use per feature
        drop_binned_features -> If True, drops the features that are binned from the dataframe. If false, they are kept (this is the default behaviour)
        """

        # test the supplied dataframes
        if not isinstance(data, pd.DataFrame):
            msg = "Expected data to be a dataframe"
            raise ValueError(msg)

        # test the drop_binned_features
        if not isinstance(drop_binned_features, bool):
            msg = "Expected drop_binned_features to be boolean"
            raise ValueError(msg)
        self._drop_binned_features = drop_binned_features

        # Test the cutting instructions
        if not isinstance(data_cut, dict):
            msg = "Expecting data_cut to be a dict"
            raise ValueError(msg)
        lowkeys = [k.lower() for k, v in data_cut.items()]
        lowkeys.sort()
        if lowkeys != ["test", "train", "val"]:
            msg = "Expected dict with keys 'train', 'val', 'test', got {}".format(data_cut.keys())
            raise ValueError(msg)
        if not all(isinstance(v, numbers.Number) for k, v in data_cut.items()):
            msg = "Data cut dict items need to be numbers"
            raise ValueError(msg)
        if not all(v >= 0.0 for k, v in data_cut.items()):
            msg = "Data cut dict items need to be >= 0"
            raise ValueError(msg)

        # cut the data
        train_cut = data_cut["train"]
        val_cut = train_cut + data_cut["val"]
        test_cut = val_cut + data_cut["test"]
        # ensure sum to 1
        if test_cut == 0:
            msg = "Data cuts sum to 0. They should really sum to 1..."
            raise ValueError(msg)

        train_cut = train_cut / test_cut
        val_cut = val_cut / test_cut
        n = len(data)
        self.train_df = data[0 : int(n * train_cut)]
        self.val_df = data[int(n * train_cut) : int(n * val_cut)]
        self.test_df = data[int(n * val_cut) :]

        # store columns
        self.init_data_columns = data.columns

        # Perform the scaling
        if isinstance(scalers, dict):
            # Note: we fit the scaler to the training data only!
            self.scalers = self._fit_scalers(self.train_df, fit_scalers, scalers)
            # scale all of the training, val and test data
            train_scaled = self.transform_scale(self.train_df)
            val_scaled = self.transform_scale(self.val_df)
            test_scaled = self.transform_scale(self.test_df)
        else:
            # unable to understand scaling instructions, so dont do any
            # TODO: warn here is scaler is anything else than None?
            self.scalers = None
            train_scaled = self.train_df.copy()
            val_scaled = self.val_df.copy()
            test_scaled = self.test_df.copy()

        # Perform the binning. We bin using teh raw data, NOT the scaled data
        if isinstance(binners, dict):
            # Note: we fit the binner to the training data only!
            self.binners = self._fit_binners(self.train_df, binners)
            # scale all of the training, val and test data
            train_binned = self.transform_bin(self.train_df)
            val_binned = self.transform_bin(self.val_df)
            test_binned = self.transform_bin(self.test_df)
        else:
            self.binners = None
            train_binned = self.train_df.copy()
            val_binned = self.val_df.copy()
            test_binned = self.test_df.copy()

        # combine the scaled and binned data
        self.train_transformed = self._combine_scaled_and_binned(train_binned, train_scaled)
        self.val_transformed = self._combine_scaled_and_binned(val_binned, val_scaled)
        self.test_transformed = self._combine_scaled_and_binned(test_binned, test_scaled)
        # store the transformed data columns
        self.transformed_data_columns = self.train_transformed.columns

    def _fit_scalers(self, df, do_fitting, scalers):
        """
        Fit the scalers to the dataframe df
        """
        # TODO: Throw warnings if unexpected columns or unknown scalers are passed. Currently we just ignore them
        cols = list(df.columns)
        fitted_scalers = dict()  # store the scalers by feature/column in a dict {feature: scaler}
        for c in cols:
            fitted_scalers[c] = None  # default no scaler
        # loop throught each scaler in scalers
        for feature, scaler in scalers.items():
            if feature in cols and isinstance(scaler, ScalerWrapper):
                # only scale if we have the feature in the df
                # only (re)-fit if the scaler is a ScalerWrapper class
                fitted_scalers[feature] = scaler
                if do_fitting:
                    fitted_scalers[feature] = scaler.fit(X=df[[feature]])
        return fitted_scalers

    def _fit_binners(self, data, binners):
        """
        Fit the binners to the dataframe df
        """
        # TODO: Throw warnings if unexpected columns passed in binners. Currently we just ignore them
        df = data.copy()
        cols = df.columns
        fitted_binners = dict()  # store the scalers by feature/column in a dict {feature: scaler}
        for c in cols:
            fitted_binners[c] = None  # default no binner
        # loop throught each binner in binners
        for feature, binner in binners.items():
            if feature in cols:
                if isinstance(binner, Binner):
                    # Binner already exists, so we just use that and dont make a new one
                    fitted_binners[feature] = binner
                elif isinstance(binner, list):
                    # assume a list of edges is provided.
                    # create a binner with these edges and fit it to the provided data
                    fitted_binners[feature] = Binner(
                        bin_edges=binner, data=data[feature], name=feature, inclusive=True,
                    )
                else:
                    msg = "Expected bin edges or pre-fitted binner to be provided for {}".format(feature)
                    raise ValueError(msg)
        return fitted_binners

    def _combine_scaled_and_binned(self, binned_data, scaled_data):
        """
        Combine the binned and scaled data, according to the following logic. In the new "transformed" dataframe, we have:
         - binned columns
         - scaled columns for those columns with a scaler
         - raw columns for those columns without a scaler
         - drop the raw/scaled columns for the binned columns if instructed

        """
        # default is the binned data
        df = binned_data.copy()
        # replace the column in the binned data if we find the column also in the scaled data
        # This way we overwrite the raw data with scaled data, and ignore those cols that we have binned and are asked to drop
        for col in binned_data.columns:
            if col in scaled_data.columns:
                df[col] = scaled_data[col]
        return df

    def transform_scale(self, data):
        """
        Perform a transform onthe data in df with the scalers
        Designed to be used to transform external data (eg. data to predict for)
        """
        # TODO: Throw warnings if unexpected columns or unknown scalers are passed. Currently we just ignore them
        df_scaled = data.copy()
        if self.scalers is not None:
            for feature, scaler in self.scalers.items():
                if feature in list(df_scaled.columns) and isinstance(scaler, ScalerWrapper):
                    # only scale if we have the feature in the df
                    # only fit if the scaler is a ScalerWrapper class
                    df_scaled[feature] = scaler.transform(X=df_scaled[[feature]])
        return df_scaled

    def transform_bin(self, data):
        """
        Bin the data using the binner for each feature
        If no binner, no transformation done.
        If binner is defined for a column, the column will be replaced with its binned version (multiple columns)
        """
        df_binned = data.copy()
        if self.binners is not None:
            for feature, binner in self.binners.items():
                if isinstance(binner, Binner):
                    # assume that the feature exists and the binner is a Binner object. This should be the case from the code logic
                    # store feature col in a series
                    srs = df_binned[feature]
                    # drop the feature col from df_binned
                    if self._drop_binned_features:
                        df_binned = df_binned.drop(columns=[feature])
                    # calculate the bins
                    binned_data = binner.transform(data=srs, truncate=True)
                    # concat the new binned data to the feature data
                    df_binned = pd.concat([df_binned, binned_data], axis=1)
        return df_binned

    def transform(self, data):
        """
        Perform a scaler and bin transformation on the data
        """
        df = data.copy()
        scaled = self.transform_scale(df)
        binned = self.transform_bin(df)
        df = self._combine_scaled_and_binned(binned, scaled)
        return df

    def generate_dataset(
        self,
        input_width,
        label_width,
        shift,
        shuffle=True,
        batch_size=32,
        label_columns=None,
        drop_labels_from_inputs=True,
    ):
        """
        Create a WindowGenerator object for the model data.
        The WindowGenerator object converts the data into dataset(s) for modelling
        input width ->
        label_width ->
        shift ->
        label_columns -> the "y" labels - i.e. the columns you are going to predict.
            List or Dict.
            List: columns to use as y labels. If the column has been binned, the binned version will be used automatically.
            Dict: {column_label: "binned" or "original"}. If "original", will use the non-binned as the label. If "binned" (or any other string) will use the binned version
        """
        # process the label columns so that if there are any binned columns, the label is replaced by all the correpsonding bin labels
        if not (isinstance(label_columns, list) or isinstance(label_columns, dict) or label_columns is None):
            msg = "Expected a list or dict of label columns or None"
            raise ValueError(msg)
        if isinstance(label_columns, list):
            # pack into a dict
            label_columns = {col: "binned" for col in label_columns}
        new_label_cols = label_columns
        if label_columns is not None and self.binners is not None:
            new_label_cols = []
            for col, instr in label_columns.items():
                # if col has been binned, and "original" is not specified, default
                # to using the binned data as labels. Otherwise use the orignal version
                if col in list(self.binners.keys()) and instr.lower() != "original":
                    # need to replace the column label with the binner labels
                    bin_labels = self.binners[col].bin_labels
                    new_label_cols.extend(bin_labels)
                else:
                    # make sure the label can be found
                    if col not in list(self.transformed_data_columns):
                        msg = "Cannot find {} in the data columns. One possibility - you are asking for a column that you have binned and instructed that the original be dropped."
                        raise ValueError(msg)
                    # just use the given label
                    new_label_cols.extend(col)

        return WindowGenerator(
            self.train_transformed,
            self.val_transformed,
            self.test_transformed,
            input_width,
            label_width,
            shift,
            shuffle,
            batch_size,
            new_label_cols,
            drop_labels_from_inputs,
        )


# -----------------
# Window Generator Class
# -----------------


class WindowGenerator:
    """
    From: https://www.tensorflow.org/tutorials/structured_data/time_series

    Start by creating the WindowGenerator class. The __init__ method includes all the necessary logic for the input and label indices.

    It also takes the train, eval, and test dataframes as input. These will be converted to tf.data.Datasets of windows later.

    Examples:

        >>> w1 = WindowGenerator(input_width=24, label_width=1, shift=24,
                 label_columns=['T (degC)'])
        >>> w1

            Total window size: 48
            Input indices: [ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23]
            Label indices: [47]
            Label column name(s): ['T (degC)']

        >>> w2 = WindowGenerator(input_width=6, label_width=1, shift=1,
                 label_columns=['T (degC)'])
        >>> w2

            Total window size: 7
            Input indices: [0 1 2 3 4 5]
            Label indices: [6]
            Label column name(s): ['T (degC)']
    """

    def __init__(
        self,
        df_train,
        df_val,
        df_test,
        input_width,
        label_width,
        shift,
        shuffle=True,
        batch_size=32,
        label_columns=None,
        drop_labels_from_inputs=True,
    ):

        # test the supplied dataframes
        if (
            not isinstance(df_train, pd.DataFrame)
            or not isinstance(df_test, pd.DataFrame)
            or not isinstance(df_val, pd.DataFrame)
        ):
            msg = "Expected df_train, df_val and df_test to be dataframes"
            raise ValueError(msg)

        # test the drop_labels_from_inputs instructions
        if not isinstance(drop_labels_from_inputs, bool):
            msg = "Expected drop_labels_from_inputs to be boolean"
            raise ValueError(msg)
        self._drop_labels_from_inputs = drop_labels_from_inputs

        # test the batch and shuffle instructions
        if not isinstance(shuffle, bool):
            msg = "Expected boolean shuffle instructions"
            raise ValueError(msg)
        if not isinstance(batch_size, numbers.Number):
            msg = "Expected numeric batch size"
            raise ValueError(msg)
        if batch_size != int(batch_size):
            msg = "Expected integer batch size"
            raise ValueError(msg)
        self._shuffle = shuffle
        self._batch_size = batch_size
        self._sequence_stride = 1  # default - may open this up to user input later

        # make sure they all have the same columns in the same order
        # This is strict - we can add some intelligence to this later perhaps, if/when we allow array-like data instead of just dataframes, or want to allow same cols but in different order.
        if not (df_test.columns.equals(df_train.columns) and df_val.columns.equals(df_train.columns)):
            msg = "Train, validation and test dataframes must have the same columns (feature labels) in the same order"
            raise ValueError(msg)

        # store the column indicies
        self.data_columns = df_test.columns
        self.column_indices = {name: i for i, name in enumerate(self.data_columns)}

        # store the data
        self.train_df = df_train
        self.val_df = df_val
        self.test_df = df_test

        # Work out the label column indices.
        self.label_columns = label_columns
        if label_columns is not None:
            if not (set(self.label_columns) <= set(self.data_columns)):
                msg = "Label columns must be a subset of all data columns"
                raise ValueError(msg)
            self.label_columns_indices = {name: i for i, name in enumerate(label_columns)}

        # Work out the window parameters.
        if not (
            isinstance(input_width, numbers.Integral)
            and isinstance(label_width, numbers.Integral)
            and isinstance(shift, numbers.Integral)
        ):
            msg = "Expected integral input width, label width and shift"
            raise ValueError(msg)
        if input_width < 1 or label_width < 0 or shift < 0:
            msg = "Expected input width >=1, and label width, shift >= 0"
        if label_width == 0 and label_columns is not None:
            # 0 width => cannot get labels
            msg = "You have supplied label columns but specified labels of 0 width - either require no labels ot specify a width > 0"
            raise ValueError(msg)
        if label_width > 0 and label_columns is None:
            # 0 width => cannot get labels
            msg = "You have supplied label columns = None but specified labels of >0 width - either specify labels or specify a width = 0"
            raise ValueError(msg)
        if shift < label_width:
            msg = "The label width and input width overlap. Shift must be >= label width"
            raise ValueError(msg)

        self.input_width = input_width
        self.label_width = label_width
        self.shift = shift

        self.total_window_size = input_width + shift

        self.input_slice = slice(0, input_width)
        self.input_indices = np.arange(self.total_window_size)[self.input_slice]

        if label_columns is not None:
            self.data_is_labeled = True
            self.label_start = self.total_window_size - self.label_width
            self.labels_slice = slice(self.label_start, None)
            self.label_indices = np.arange(self.total_window_size)[self.labels_slice]
        else:
            self.data_is_labeled = False
            self.label_start = None
            self.labels_slice = None
            self.label_indices = None

    def __repr__(self):
        return "\n".join(
            [
                f"Total window size: {self.total_window_size}",
                f"Input indices: {self.input_indices}",
                f"Label indices: {self.label_indices}",
                f"Label column name(s): {self.label_columns}",
            ]
        )

    def plot(self, model=None, plot_col=None, max_subplots=3):
        """Plot the split window"""
        inputs, labels = self.example
        plt.figure(figsize=(12, 8))
        plot_col_index = self.column_indices[plot_col]
        max_n = min(max_subplots, len(inputs))
        for n in range(max_n):
            plt.subplot(max_n, 1, n + 1)
            plt.ylabel(f"{plot_col}")
            plt.plot(
                self.input_indices, inputs[n, :, plot_col_index], label="Inputs", marker=".", zorder=-10,
            )

            if self.label_columns:
                label_col_index = self.label_columns_indices.get(plot_col, None)
            else:
                label_col_index = plot_col_index

            if label_col_index is None:
                continue

            plt.scatter(
                self.label_indices, labels[n, :, label_col_index], edgecolors="k", label="Labels", c="#2ca02c", s=64,
            )
            if model is not None:
                predictions = model(inputs)
                plt.scatter(
                    self.label_indices,
                    predictions[n, :, label_col_index],
                    marker="X",
                    edgecolors="k",
                    label="Predictions",
                    c="#ff7f0e",
                    s=64,
                )

            if n == 0:
                plt.legend()

        plt.xlabel("Time")

    def split_window_data(self, features):
        """
        Given a list consecutive inputs, the split_window method will convert them to a window of inputs and a window of labels.
        Ensures that the data columns are in the same order every time - i.e. the same order as for the train, val and test data provided.

        Note: we are only in this function if there is label and input data to split. Otherwise the code should not be here

        """

        # want all vals up to & including idx input_width-1
        inputs = features[:, self.input_slice, :]
        labels = features[:, self.labels_slice, :]

        # seperate out the label data, and also drop the label data from the input data if necessary.
        labels = tf.stack([labels[:, :, self.column_indices[name]] for name in self.label_columns], axis=-1,)
        if self._drop_labels_from_inputs:
            # drop the labels from the inputs
            inputs = tf.stack(
                [
                    inputs[:, :, self.column_indices[name]]
                    for name in self.data_columns
                    if name not in self.label_columns
                ],
                axis=-1,
            )

        # Slicing doesn't preserve static shape information, so set the shapes
        # manually. This way the `tf.data.Datasets` are easier to inspect.
        inputs.set_shape([None, self.input_width, None])
        labels.set_shape([None, self.label_width, None])
        return inputs, labels

    def split_window_index_input(self, features):
        """
        Split out the index for for the input row (the last row in each sequence of inputs)
        """
        inputs = features[:, slice(self.input_width - 1, self.input_width), :]
        inputs.set_shape([None, 1, None])
        return inputs

    def split_window_index_labels(self, features):
        """
        Split out the indexes for for the label rows. Only to be used if labels are defined for the train etc data AND if labels have been requested for the data being processed
        """
        labels = features[:, self.labels_slice, :]
        labels.set_shape([None, self.label_width, None])
        return labels

    def split_window_pad(self, features):
        """
        pad by adding a None
        """
        return features, None

    def _make_dataset(
        self, data, return_label_data=True, shuffle=None, batch_size=None, sequence_stride=None,
    ):
        """
        Return data as a timeseries dataset, in the dimensions matching this window generator.
        label_data -> if True, will return a label dataset and an input dataset. Otherwise it will return a single dataset only of inputs. Note - if there are no labels for the data, then specifying this = True does nothing - you will still get just a input dataset
        shuffle -> if True, the results will be shuffled EVERYTIME. This is important - useful for fitting some models, but not necessarily for batch predicting...as you will get predictions that are not in the order you expect
        batch_size -> Int or None. batch size for the resulting dataset.
        sequence_stride -> stride length for the sequence data. Int or None.

        Note -> None for shuffle, batch_size, sequence_stride results in the defaults set at initialisation for the window being used.
        """
        # make the dataset
        ds = self._make_ds(data, return_label_data, shuffle, batch_size, sequence_stride)
        if return_label_data and self.data_is_labeled:
            # split the ds tensor into input data and label data
            ds = ds.map(self.split_window_data)
        else:
            # put a None placeholder where labels would be
            ds = ds.map(self.split_window_pad)
        return ds

    def _make_ds(
        self, data, return_label_data=True, shuffle=None, batch_size=None, sequence_stride=None,
    ):
        """
        Return data as a timeseries dataset, prior to splitting, in the dimensions matching this window generator.
        return_label_data -> if True, will return a label dataset and an input dataset. Otherwise it will return a single dataset only of inputs. Note - if there are no labels for the data, then specifying this = True does nothing - you will still get just a input dataset
        shuffle -> if True, the results will be shuffled EVERYTIME. This is important - useful for fitting some models, but not necessarily for batch predicting...as you will get predictions that are not in the order you expect
        batch_size -> Int or None. batch size for the resulting dataset.
        sequence_stride -> stride length for the sequence data. Int or None.

        Note -> None for shuffle, batch_size, sequence_stride results in the defaults set at initialisation for the window being used.
        """

        # ensure data is a dataframe
        if not isinstance(data, pd.DataFrame):
            msg = "Data expected to be dataframe (so we can ensure feature fidelity)"
            raise ValueError(msg)

        # fix stride, batch, shuffle
        if shuffle is None:
            shuffle = self._shuffle
        if batch_size is None:
            batch_size = self._batch_size
        if sequence_stride is None:
            sequence_stride = self._sequence_stride

        # Calculate the window size for the data (i.e. number of time periods in a given sequence)
        if return_label_data and self.data_is_labeled:
            # note - the self_data_is_labeled here is a little supurflous - if it were false, then self.total_window_size woulld = self.input_width
            window_size = self.total_window_size
        else:
            window_size = self.input_width

        # data set must be at least 1 window size long
        if len(data) < window_size:
            msg = "Data length is too short. Expecting at least length {}, but data is only length {}".format(
                window_size, len(data)
            )
            raise ValueError(msg)

        # ensure that the features in data are in the same order as for teh training, test and val data passed to the window generator at initialisation. If not, then when we convert to np arrays things will get problematic as we will use the wrong data for each feature
        # only do this if we have a full dataset. Assume otherwise it is an index set
        try:
            if (
                len(data.columns) > 1
            ):  # if ==1 assume it is index data. If it isnt it does not matter as the order will always be correct by definition
                cols_ordered = [None for _ in data.columns]
                for col_name, col_idx in self.column_indices.items():
                    cols_ordered[col_idx] = col_name
                data = data[cols_ordered]
        except:
            msg = "Provided data does not have the expect columns"
            raise ValueError(msg)

        data = np.array(data)
        if len(data) > 1:
            # check that the columns in the dataframe match the
            ds = tf.keras.preprocessing.timeseries_dataset_from_array(
                data=data,
                targets=None,
                sequence_length=window_size,
                sequence_stride=sequence_stride,
                shuffle=shuffle,
                batch_size=batch_size,
            )

        else:
            # the timeseries_dataset_from_array fails for len()=1 data
            # so need to make the tensor ourselves
            # the data.shape will = (1, <features>)
            # need to make it (1,1,<features>)
            ds = tf.data.Dataset.from_tensors(np.expand_dims(data, axis=0))

        return ds

    def make_dataset(
        self, data, return_label_data=True, return_index=True, shuffle=None, batch_size=None, sequence_stride=None,
    ):
        """
        Return provided data as a timeseries dataset in the dimensions matching this window generator.

        return_label_data -> if True, will return a label dataset and an input dataset. Otherwise it will return a single dataset only of inputs. Note - if there are no labels for the data, then specifying this = True does nothing - you will still get just a input dataset
        return_index -> if True, will return a dataset containing string representations of the period datatimes for each input dataset sequence, and for each label (if label_data=True)
        shuffle -> if True, the results will be shuffled EVERYTIME. This is important - useful for fitting some models, but not necessarily for batch predicting...as you will get predictions that are not in the order you expect
        batch_size -> Int or None. batch size for the resulting dataset.
        sequence_stride -> stride length for the sequence data. Int or None.

        Note -> None for shuffle, batch_size, sequence_stride results in the defaults set at initialisation for the window being used.
        """
        if shuffle == True and return_index == True:
            msg = "Cannot shuffle and return the indexes, as shuffling the data makes me loose track."
            raise ValueError(msg)
        if shuffle == None and return_index == True:
            shuffle = False  # default to false

        # first the input data - process is the standard way
        ds = self._make_dataset(data, return_label_data, shuffle, batch_size, sequence_stride)

        # then the index if it is required
        if return_index:
            # extract the index
            df_idx = pd.DataFrame(index=data.index.copy()).reset_index()
            idx_data = df_idx.astype("str")  # tensors do not work with datetimes
            # idx_data = np.array(df_idx)
            # make the index dataset
            # Note: index for labels are will be returned in idx_ds only if the original data is labelled data AND return_label_data is true. If we get label indexes, we need to split into input indexes, label indexes.
            # pack the datetimes into a batch data set, in the same way as the input data
            idx_ds = self._make_ds(
                idx_data, return_label_data, shuffle=False, batch_size=batch_size, sequence_stride=sequence_stride,
            )
            # then extract the datetime corresponding to each sequence (tensor). This is the last datetime corresponding to the input data
            idx_inputs = idx_ds.map(self.split_window_index_input)
            if return_label_data and self.data_is_labeled:
                # extract out the label data (the last data in each tensor)
                idx_labels = idx_ds.map(self.split_window_index_labels)
                # zip into one dataset
                idx_ret = tf.data.Dataset.zip((idx_inputs, idx_labels))
            else:
                # pad the "labels" index with None
                idx_ret = idx_inputs.map(self.split_window_pad)
            # Calculate the datefame of predicted at and predicted to datetimes for the input tensors
            df_idx = self._index_to_dataframe(idx_ret, return_label_data)
            return ds, idx_ret, df_idx
        else:
            return ds, None, None

    def _index_to_dataframe(self, dataset, return_label_data=False):
        """
        Pack into a datafame the predicted at and predicted to datetimes for the input tensors

        This will assume the dataset tensors are of specific shapes - will return errors if not

        Note we also assume time periods/steps are of equal length. If they are not, then the predicted to datetimes will be wrong - and it will be up to the user to repair these

        """

        # Blank dataframe
        df_idx = pd.DataFrame()
        # iterate through the dataset
        df_inp = pd.DataFrame()
        df_lab = pd.DataFrame()
        # calcualte the headers for the predicted to periods
        if self.data_is_labeled:
            pds_ahead = list(range(self.shift - self.label_width + 1, self.shift + 1))
            headers = ["pds_ahead_{}".format(x) for x in pds_ahead]

        for inp_idx, lab_idx in dataset:
            # first the inputs
            if inp_idx is not None:
                z = inp_idx.shape[0]
                df_z = pd.DataFrame(inp_idx.numpy().reshape(z, 1), columns=[DEFAULT_PRED_AT])
                df_inp = pd.concat([df_inp, df_z], ignore_index=True)
            # then labels
            if lab_idx is not None and return_label_data and self.data_is_labeled:
                df_y = pd.DataFrame(lab_idx.numpy().reshape(lab_idx.shape[0], lab_idx.shape[1]), columns=headers,)
                df_lab = pd.concat([df_lab, df_y], ignore_index=True)
        # form the dataframe and recode to strings from byte
        df_idx = pd.concat([df_inp, df_lab], axis=1)
        df_idx = df_idx.stack().str.decode("utf-8").unstack()
        for col in df_idx.columns:
            df_idx[col] = pd.to_datetime(df_idx[col])

        # calculate the predicted to datetimes from first principles if they are not already calculated, and we have info we can use to figure out the labelling (i.e. we can use the shift and label width info for the window to figure it out)
        if return_label_data == False and self.data_is_labeled == True:
            # first calc the period size (hour, day, etc etc). Note this assumes periods are of equal length. If they are not, then the predicted_to labels will be wrong
            td = df_idx[DEFAULT_PRED_AT][1] - df_idx[DEFAULT_PRED_AT][0]
            for s in range(self.label_width):
                colname = headers[s]
                pd_ahead = pds_ahead[s]
                df_idx[colname] = pd_ahead * td + df_idx[DEFAULT_PRED_AT]

        return df_idx

    @property
    def train(self):
        # always use the predefined shuffle and batch size and sequence stride
        return self._make_dataset(
            self.train_df,
            return_label_data=True,
            shuffle=self._shuffle,
            batch_size=self._batch_size,
            sequence_stride=self._sequence_stride,
        )

    @property
    def train_index_df(self):
        # always use the predefined shuffle and batch size and sequence stride
        _, _, df = self.make_dataset(
            self.train_df,
            return_label_data=True,
            return_index=True,
            shuffle=self._shuffle,
            batch_size=self._batch_size,
            sequence_stride=self._sequence_stride,
        )
        return df

    @property
    def val(self):
        # always use the predefined shuffle and batch size and sequence stride
        return self._make_dataset(
            self.val_df,
            return_label_data=True,
            shuffle=self._shuffle,
            batch_size=self._batch_size,
            sequence_stride=self._sequence_stride,
        )

    @property
    def val_index_df(self):
        # always use the predefined shuffle and batch size and sequence stride
        _, _, df = self.make_dataset(
            self.val_df,
            return_label_data=True,
            return_index=True,
            shuffle=self._shuffle,
            batch_size=self._batch_size,
            sequence_stride=self._sequence_stride,
        )
        return df

    @property
    def test(self):
        # always use the predefined shuffle and batch size and sequence stride
        return self._make_dataset(
            self.test_df,
            return_label_data=True,
            shuffle=self._shuffle,
            batch_size=self._batch_size,
            sequence_stride=self._sequence_stride,
        )

    @property
    def test_index_df(self):
        # always use the predefined shuffle and batch size and sequence stride
        _, _, df = self.make_dataset(
            self.test_df,
            return_label_data=True,
            return_index=True,
            shuffle=self._shuffle,
            batch_size=self._batch_size,
            sequence_stride=self._sequence_stride,
        )
        return df

    @property
    def example(self):
        """Get and cache an example batch of `inputs, labels` for plotting."""
        result = getattr(self, "_example", None)
        if result is None:
            # No example batch was found, so get one from the `.train` dataset
            result = next(iter(self.train))
            # And cache it for next time
            self._example = result
        return result


# ----------------------------------------------------
#
# FUNCTIONS
#
# ----------------------------------------------------


def knit_label_data_and_indexes(data, df_idx, labelnames=None):
    """
    Knit label data with the indexes being predicted.

    "Label data" can be either the actual labels, or the predictions.

    "Indexes" are indexes corresponding to the label data. For timeseries forecasting, these should be datetimes.

    The data is expected to be  anumpy array with 3 dimensions (x,y,z) where:
        x = the number of data points
        y = the width of each sequence (label sequence). Thus, if your model is to predict for 3, 4 and 5 hours ahead, y = 3
        z = the number of labels per sequence (e.g. the model might predict price and volume, giving z=2)

    The df_idx dataframe should contain the indexes, and have x rows and y columns.

    y dataframes will be returned, each have x rows and z columns, and indexed by the appropriate column in df_idx.

    Note that the order of columns in df_idx is assumed to be the same order as the sequence. Thus, for a sequence of witdth 3 (y=3), the row_0 in the sequence will be combined with the index in df_idx.columns[0], row_1 with the index in df_idx.columns[1] etc.

    The dataframes will be returned in a dict, with the key being the value (name) of the corresponding column in df_idx.columns.

    Example:
        data = np.array([[[1, 2, 3, 4],
                [2, 4, 6, 8]],

                [[10, 20, 30, 40],
                    [20, 40, 60, 80]],
                ])

        df_idx = pd.DataFrame([["A", "B"], ["C", "D"]], columns=["p1", "p2"])
        labelnames = ["l1", "l2", "l3", "l4"]

        will be packed into 2 dataframes:

                l1	l2	l3	l4
            p1
            A	1	2	3	4
            C	10	20	30	40

                l1	l2	l3	l4
            p2
            B	2	4	6	8
            D	20	40	60	80

    Inputs:
    data -> numpy array of data, shape (x,y,z) (can also be a list)
    df_idx -> dataframe of indexes, rows=x, cols=y (can also be np array or list)
    labelnames -> list of z label names, to use to label the columns of each df

    Returns:
    dict -> {name_y: df_y}, where the df_y is the data for the yth element of each sequence. df_y has rows=x, cols=z


    """
    data = data.copy()
    df_idx = df_idx.copy()

    # error check the data
    if not (isinstance(data, np.ndarray) or isinstance(data, list)):
        msg = "Expecting data to be a numpy array or list, got a {}".format(type(data))
        raise ValueError(msg)
    if isinstance(data, list):
        # convert to np array
        data = np.array(data)
    if len(data.shape) != 3:
        msg = "Expected data to have 3 dimensional shape (x,y,z). Got {}".format(data.shape)
        raise ValueError(msg)

    # process and error check the df_idx
    if not (isinstance(df_idx, pd.DataFrame) or isinstance(df_idx, np.ndarray) or isinstance(df_idx, list)):
        msg = "Expecting df_idx to be a dataframe, numpy array or list, got a {}".format(type(df_idx))
        raise ValueError(msg)
    if not isinstance(df_idx, pd.DataFrame):
        # convert to data frame
        df_idx = pd.DataFrame(df_idx)
    # drop the [DEFAULT_PRED_AT] column if it exists
    if DEFAULT_PRED_AT in df_idx.columns:
        df_idx = df_idx.drop(columns=[DEFAULT_PRED_AT])
    if len(df_idx.values.shape) != 2:
        msg = "Expected df_idx to have 2 dimensional shape (x,y). Got {}".format(df_idx.values.shape)
        raise ValueError(msg)
    if len(df_idx) != data.shape[0]:
        msg = "Inputs data and df_idx should have the same number of data points (rows). data has {}, df_idx has {} ".format(
            data.shape[0], len(df_idx)
        )
        raise ValueError(msg)
    if len(df_idx.columns) != data.shape[1]:
        msg = "Sequence width in data should = the number of columns in df_idx. Data has {}, df_idx has {} ".format(
            data.shape[1], len(df_idx.columns)
        )
        raise ValueError(msg)

    # error check labelnames, fix to default if none
    if not (isinstance(labelnames, list) or isinstance(labelnames, str) or labelnames == None):
        msg = "Expected string, list or None for label names"
        raise ValueError(msg)
    if isinstance(labelnames, str):
        labelnames = [labelnames]
    if labelnames is not None and (len(np.array(labelnames).shape) != 1 or len(labelnames) != data.shape[2]):
        msg = "Expected a 1-D list of names length {}, got something with shape {}".format(
            data.shape[2], np.array(labelnames).shape
        )
        raise ValueError(msg)
    if labelnames is None:
        labelnames = ["label_{}".format(z) for z in range(data.shape[2])]

    df_dict = dict()
    # Loop through each data_array item and convert numpy array into a dataframe
    for i in range(len(df_idx.columns)):
        colname = df_idx.columns[i]
        df_data = pd.DataFrame(data[:, i, :], columns=labelnames, index=df_idx.iloc[:, i])
        df_dict[colname] = df_data

    return df_dict


def dataset_to_dataframe(dataset, names=None):
    """
    Convert data in each element of the dataset to a dataframe, returning a dictionary of dfs.

    The data in each element is expected to have a shape of 3 dimensions (x,y,z) where:
        x = the number of data points
        y = the width of the sequence (input sequence or label sequence)
        z = the number of features (for inputs) or labels (labels)

    Data in multiple batches will be sewen together in the first (x) dimension

    The dataframes returned will have x rows and y*z columns.

    Each column will be named indicating width and feature. Thus, for a width of 2, features= 3, the column names will be:
    width_0_feature_0, width_0_feature_1, ... , width_1_feature_2

    Note that, if the data is in time order, width_0 occurs 1 period before width_1 and so forth.

    Example:
        array([[[1, 2, 3, 4],
                [2, 4, 6, 8]],

                [[10, 20, 30, 40],
                    [20, 40, 60, 80]],
                ])

        will be packed into:

        width_0_feature_0	width_0_feature_1	width_0_feature_2	width_0_feature_3	width_1_feature_0	width_1_feature_1	width_1_feature_2	width_1_feature_3
        0	1	2	3	4	2	4	6	8
        1	10	20	30	40	20	40	60	80

    Inputs:
    dataset -> tensorflow dataset
    names -> string or list of strings, one for each element in the dataset

    Returns:
    dict -> {name: df}, where the df is the converted data in the dataset element


    """

    # Firstly, extract the data in the dataset into numpy arrays of dim (mx+c, y, z)
    data_arrays = extract_numpy_from_mapdataset(dataset, names)
    df_dict = dict()
    # Loop through each data_array item and convert numpy array into a dataframe
    for n, data in data_arrays.items():
        if len(data.shape) != 3:
            msg = "Expected data of 3 dimensional shape. Data {} has shape {}".format(n, data.shape)
            raise ValueError(msg)
        shaped_data = data.reshape(data.shape[0], data.shape[1] * data.shape[2])
        # name the columns by width and feature id.
        cols = ["width_{}_feature_{}".format(y, z) for y in range(data.shape[1]) for z in range(data.shape[2])]
        df = pd.DataFrame(shaped_data, columns=cols)
        df_dict[n] = df
    return df_dict


def extract_numpy_from_mapdataset(dataset, names=None):
    """
    Extract numpy arrays from a tensorflow dataset object

    Inputs:
    dataset -> tensorflow dataset
    names -> string or list of strings, one for each element in the dataset

    Returns:
    dict -> {name: np.ndarray}, where the ndarray is the converted data in the dataset element
    """

    # make sure it is a tf dataset
    if not isinstance(dataset, tf.data.Dataset):
        msg = "Expecting a dataset, got a {}".format(type(dataset))
        raise ValueError(msg)

    if not (isinstance(names, list) or isinstance(names, str) or names == None):
        msg = "Expected string, list or None for names"
        raise ValueError(msg)
    if isinstance(names, str):
        names = [names]
    if names is not None and len(np.array(names).shape) != 1:
        msg = "Expected a 1-D list of names, got something with shape {}".format(np.array(names).shape)
        raise ValueError(msg)

    # set some names if they dont already exist
    spec = dataset.element_spec
    if names is None:
        names = list(range(len(spec)))
        for id in range(len(spec)):
            el = spec[id]
            names[id] = "item_{}".format(str(id))
            if el.name is not None:
                names[id] = el.name

    d_ret = {x: None for x in names}

    # this extracts each batch and sews it to the "bottom" of the already extracted data. It should thus keep its shape in all dims other than the first. Thus, if each batch has a shape (x,y,z), the output will have a shape (mx+c,y,z) where m and c are constants
    # loop through the dataset
    for el in dataset:  # each batch
        for i in range(len(el)):  # each element
            name = names[i]
            if not (isinstance(d_ret[name], np.ndarray)):
                d_ret[name] = el[i].numpy()
            else:
                d_ret[name] = np.concatenate([d_ret[name], el[i].numpy()])
    return d_ret


def metrics(predictions, labeldata, return_errors=False):
    """
    Calculate metrics for the predictions.

    Inputs:
    predictions - array-like object of predictions
    labeldata - array-like object of label data (actuals)
    return_errors -> boolean

    Returns:
    metrics -> dataframe of metrics
    df_errors -> error dataframe if return_errors = True

    """
    predictions = predictions.copy()
    labeldata = labeldata.copy()
    # process and error check the predictions
    # first, make sure they are arrays and put them in dataframes
    if not (
        isinstance(predictions, pd.DataFrame) or isinstance(predictions, np.ndarray) or isinstance(predictions, list)
    ):
        msg = "Expecting predictions to be a dataframe, numpy array or list, got a {}".format(type(predictions))
        raise ValueError(msg)
    if not isinstance(predictions, pd.DataFrame):
        # convert to data frame
        predictions = pd.DataFrame(predictions)
    # check the shape is 2-d
    if len(predictions.values.shape) != 2:
        msg = "Expected df_idx to have 2 dimensional shape (x,y). Got {}".format(predictions.values.shape)
        raise ValueError(msg)

    # now for labeldata (the same checks...)
    if not (isinstance(labeldata, pd.DataFrame) or isinstance(labeldata, np.ndarray) or isinstance(labeldata, list)):
        msg = "Expecting labeldata to be a dataframe, numpy array or list, got a {}".format(type(labeldata))
        raise ValueError(msg)
    if not isinstance(labeldata, pd.DataFrame):
        # convert to data frame
        labeldata = pd.DataFrame(labeldata)
    # check the shape is 2-d
    if len(labeldata.values.shape) != 2:
        msg = "Expected df_idx to have 2 dimensional shape (x,y). Got {}".format(labeldata.values.shape)
        raise ValueError(msg)

    # ensure both have the same number of columns
    if len(predictions.columns) != len(labeldata.columns):
        msg = "Inputs predictions (num.cols={}) and labeldata (num.cols={}) need to have the same number of columns. ".format(
            len(predictions.columns), len(labeldata.columns)
        )
        raise ValueError(msg)

    # we dont check the number of rows or the indexes - if they dont match, then we will end up with Nans that we will just drop. So, for example, the labeldata could be longer than the predictions, and we will just get metrics for the period covered by the predictions.

    # now, if the columns are different in both dataframe, replace the labeldata cols with the prediction cols
    if set(predictions.columns) != set(labeldata.columns):
        # this of course assumes that the columns in each of the dataframes are in the same order (so I can compare col#x in predictions with col#x in labeldata)
        # if this is not the case the results will be rubbish
        labeldata.columns = predictions.columns.copy()

    # calculate the errors
    df_error = predictions.subtract(labeldata, axis="index").dropna(axis="index")

    # calculate the metrics on the erroradn return
    if return_errors:
        return _calc_metrics(df_error), df_error
    else:
        return _calc_metrics(df_error)


def _calc_metrics(df):
    """
    Calculate summary statistic metrics for the provided dataframe
    """
    return df.agg(
        [
            "count",
            "min",
            _renamer(lambda x: percentile(x, 25), "25%"),
            _renamer(lambda x: percentile(x, 50), "50%"),
            _renamer(lambda x: percentile(x, 75), "75%"),
            "max",
            "mean",
            mabs,
            "std",
            "skew",
            mse,
            rmse,
        ]
    )


def mabs(srs):
    """mean of absolute values of the series"""
    return srs.abs().mean()


def mse(srs):
    """mse for the provided series"""
    return np.square(srs.values).mean()


def rmse(srs):
    """root mse for the provided series"""
    return math.sqrt(np.square(srs.values).mean())


def percentile(srs, q=50):
    return np.percentile(srs.values, q)


def _renamer(base_function, desired_name):
    """Returns the function <base_function> results with the new name <desired_name>"""

    def return_func(x):
        return base_function(x)

    return_func.__name__ = desired_name
    return return_func


def quantile_test(df_quantiles, df_actual):
    """calculates percentage of observations the quantile series is >= actual series, for each quantile series"""
    greater = df_quantiles.sub(df_actual, axis=0) >= 0
    return greater.sum() / len(greater)
