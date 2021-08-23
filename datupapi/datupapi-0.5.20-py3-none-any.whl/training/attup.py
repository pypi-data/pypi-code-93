import boto3
import datetime
import itertools
import numpy as np
import openpyxl
import os
import pandas as pd
import tensorflow as tf
import tensorflow.keras.backend as K
import time
from matplotlib import pyplot as plt
from datetime import datetime
from datetime import date, timedelta
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.utils import plot_model
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed, Input, BatchNormalization
from tensorflow.keras.layers import multiply, concatenate, Flatten, Activation, dot, Dropout
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.activations import softmax
from dateutil.relativedelta import relativedelta
from tensorflow.python.framework import indexed_slices
from tensorflow.python.keras.callbacks import LearningRateScheduler
from causalnex.structure.notears import from_pandas

from datupapi.configure.config import Config


class Attup(Config):

    def __init__(self, config_file, logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path

    def transform_with_loc_to_matrix(self, df):
        """
        Returns a dataframe in matrix form in order to be trained by the attention model

        :param df: Dataframe with columns: timestamp, item_id, demand and location
        :return df_out: Output dataframe with each item as a column
        >>> df =
                Date        item_id  Demand  Location
                2021-16-05     sku1      23     1
                2021-16-05     sku2     543     2
                2021-16-05     sku3     123     3
        >>> df = transform_to_matrix(df)
        >>> df =
                      Date           sku1    sku2     sku3 ......... skuN
                idx1  2021-16-05      23      543      123 ......... 234
        """
        n_features_list = []
        frames = []
        locations = df.location.unique()
        for i in range(len(locations)):
            data_aux = df[df['location'] == locations[i]].iloc[:, :3].sort_values(by='timestamp')
            n_features_list.append(len(data_aux.item_id.unique()))
            data_aux = data_aux.pivot(index='timestamp', columns='item_id', values='demand')
            frames.append(data_aux)
        df_out = pd.concat(frames, axis=1).fillna(0).reset_index()
        df_out = df_out.rename(columns={'index': 'Date'})

        for_loc = []
        for i in range(len(locations)):
            aux_for = np.repeat(locations[i], n_features_list[i] * self.n_steps_out)
            for_loc.append(aux_for)
        for_loc = np.concatenate(for_loc)

        return df_out, for_loc

    def transform_to_matrix(self, df, value=None, method=None):
        """
        Returns a dataframe in matrix form in order to be trained by the attention model

        :param df: Dataframe with columns: timestamp, item_id and demand
        :return df_out: Output dataframe with each item as a column
        >>> df =
                Date        item_id  Demand
                2021-16-05     sku1      23
                2021-16-05     sku2     543
                2021-16-05     sku3     123
        >>> df = transform_to_matrix(df)
        >>> df =
                      Date           sku1    sku2     sku3 ......... skuN
                idx1  2021-16-05      23      543      123 ......... 234
        """
        df_out = df.sort_values(by='timestamp')
        df_out = df_out.reset_index()
        df_out = df_out.iloc[:, 1:]
        df_out = df_out.pivot(index='timestamp', columns='item_id', values='demand').reset_index()
        df_out = df_out.fillna(value=value, method=method)
        df_out = df_out.rename(columns={'timestamp': 'Date'})
        df_out = df_out.set_index("Date")
        df_out = df_out.reindex(sorted(df_out.columns), axis=1)
        df_out = df_out.reset_index()
        for_loc = []
        return df_out, for_loc

    def fill_dates(self, df, freq='W', value=None, method=None):
        """
        Returns a dataframe in matrix form with a row for each week between the start and end date
        defined in the df input dataframe. The NaN values are filled by the value.

        :param df: Dataframe in matrix form with the data as first column and each SKU as the next columns.
        :param freq: Aggregation type for time dimension. Default W.
        :param value: Value to fill incomplete records.
        :param method: Filling method for incomplete intermediate records.
        :return df: Output dataframe with each week between the start and end date as a row.
        >>> df =
                        Date           sku1    sku2 ......... skuN
                idx1    2021-16-05     543      123 ......... 234
                idx2    2021-30-05     250      140 ......... 200
        >>> df =fill_dates(df)
        >>> df =
                        Date           sku1    sku2 ......... skuN
                idx1    2021-16-05     543      123 ......... 234
                idx2    2021-23-05      0        0  ......... 0
                idx3    2021-30-05     250      140 ......... 200
        """
        df = df.sort_values(by='Date', ascending=True)
        sdate = datetime.strptime(df['Date'].iloc[0], '%Y-%m-%d').date()
        # start date
        edate = datetime.strptime(df['Date'].iloc[len(df) - 1], '%Y-%m-%d').date()
        # sdate = date(2017,1,2)   # start date
        # edate = date(2021,5,12)   # end date
        dates = pd.date_range(sdate, edate, freq='d')
        if freq == 'W':
            dates = dates[::7]
        dates = dates.strftime("%Y-%m-%d")
        dates_df = df.sort_values(by='Date').Date.values

        n_dates = []
        for j in range(len(dates)):
            if np.isin(dates[j], dates_df) == False:
                n_dates.append(dates[j])

        if n_dates:
            df2 = pd.DataFrame(n_dates)
            df2.columns = ['Date']
            df = df.append(df2, ignore_index=True)
            df['Date'] = pd.to_datetime(df.Date, format='%Y-%m-%d')

            df = df.sort_values(by='Date', ascending=True)
            df = df.reset_index().iloc[:, 1:]
            df = df.fillna(value=value, method=method)
            return df
        else:
            df['Date'] = pd.to_datetime(df.Date, format='%Y-%m-%d')
            return df

    def add_dates(self, data_date, data, predict, n_features, for_loc):
        """
        Add the timestamp, backtesting intervals and target to the predictions dataframe based on each rows index and Qprep.

        :param data_date (df): Original Qprep dataframe.
        :param data (df): training data without dates.
        :param predict (df): Dataframe with the neural network output.
        :param n_features (int): Number of features or items that were predicted.
        :param n_backtests (int): Number of backtests. 5 by default.
        :param n_steps_out (int): Number of weeks predicted. 4 by default

        :return predict (df): Prediction dataframe with the target values, timestamp and backtesting intervals.
        """

        # Take the start date of the data
        # startdate = data_date['Date'].iloc[0]
        # startdate=datetime.datetime.strptime(startdate, '%Y-%m-%d').date()
        # Define a list with all the dates by week between the startdate and the enddate
        # listaDates = list(data_date['Date'].unique())
        # dates = [startdate + timedelta(weeks=i) for i in range(0, len(listaDates) + self.n_steps_out + 1)]
        edate = data_date['Date'].iloc[len(data_date) - 1]
        edate = datetime.strptime(edate, '%Y-%m-%d').date()
        if self.dataset_frequency == "W":
            dates = [edate + relativedelta(weeks=+i) for i in range(1, self.n_steps_out + 1)]
        elif self.dataset_frequency == "M":
            dates = [edate + relativedelta(months=+i) for i in range(1, self.n_steps_out + 1)]

        size = len(data)
        print(size)
        target = {}

        predict[0].insert(2, column='date', value=np.tile(dates, (n_features)))
        # Take the target column from the data dataframe and add it to the Predict dataframe.
        for i in range(1, self.n_backtests + 1):
            target[i] = data.iloc[size - i * self.n_steps_out:size - (i - 1) * self.n_steps_out].to_numpy()
            print(len(target[i]))
            target[i] = np.reshape(target[i], (n_features * self.n_steps_out, 1), order='F')
            predict[i].insert(3, "target_value", target[i], allow_duplicates=False)

        # Add the dates column to the forecast dataframe based on the respective time_idx of each row and drop the time_idx column.

        predict[0] = predict[0].drop(columns='time_idx')

        # Reorder the forecast columns according to the order defined in datupapi.
        column_names = ["item_id", "date", "p5", "p20", "p40", "p50", "p60", "p80", "p95"]
        predict[0] = predict[0].reindex(columns=column_names)

        ##Add the dates, backtest start time and backtest end time column to each backtest dataframe based on the respective time_idx of each row
        timestamp = {}
        for j in range(1, self.n_backtests + 1):
            aux_d = data_date["Date"].iloc[size - j * self.n_steps_out:size - (j - 1) * self.n_steps_out].to_numpy()
            timestamp[j] = np.tile(aux_d, (n_features))
            timestamp[j] = np.reshape(timestamp[j], (n_features * self.n_steps_out, 1), order='F')
            predict[j].insert(2, "timestamp", timestamp[j], allow_duplicates=False)

            startdate = []
            enddate = []
            for i in range(len(predict[j].index)):
                startdate.append(timestamp[j][0][0])
                enddate.append(timestamp[j][self.n_steps_out - 1][0])

            # predict[j].insert(2,column='timestamp',value=timestamp)
            predict[j].insert(3, column='backtestwindow_start_time', value=startdate)
            predict[j].insert(4, column='backtestwindow_end_time', value=enddate)
            predict[j] = predict[j].drop(columns='time_idx')

            # Reorder the backtest columns according to the order defined in datupapi.
            column_names = ["item_id", "timestamp", "target_value", "backtestwindow_start_time",
                            "backtestwindow_end_time", "p5", "p20", "p40", "p50", "p60", "p80", "p95"]
            predict[j] = predict[j].reindex(columns=column_names)

        return predict

    def clean_negatives(self, df):
        """
        Replace negative values with zeros.

        :param noneg (df): Dataframe with the negative values to be replaces.
        :param n_backtests (int): Number of backtests. 5 by default.

        :return noneg (df): Dataframe without negative values.
        """
        inter = ["p95", "p5", "p60", "p40", "p80", "p20", "p50"]
        for i in range(1, self.n_backtests + 1):
            df[i]['target_value'] = df[i]['target_value'].map(lambda x: 0 if x < 0 else x)

        for i in inter:
            for j in range(self.n_backtests + 1):
                df[j][i] = df[j][i].map(lambda x: 0 if x < 0 else x)

        return df

    def split_sequences(self, sequences, n_steps_in, n_steps_out):
        """
        Split a multivariate sequence into samples to use the sequences as a supervised learning model.

        :param sequences(df): Dataframe use to train the model in matrix form.
        :param n_steps_out (int): Number of weeks  to be predicted. 4 by default.
        :param n_steps_in (int): Input window size. Number of weeks used to make the prediction.

        :return X (numpy_array): Input values for training the model.
        :return y (numpy_array): Output values for training the model.
        """
        X, y = list(), list()
        for i in range(len(sequences)):
            # find the end of this pattern
            end_ix = i + n_steps_in
            out_end_ix = end_ix + n_steps_out
            # check if we are beyond the dataset
            if out_end_ix > len(sequences):
                break
            # gather input and output parts of the pattern
            seq_x, seq_y = sequences[i:end_ix, :], sequences[end_ix:out_end_ix, :]
            X.append(seq_x)
            y.append(seq_y)
        return np.array(X), np.array(y)

    def predict_with_uncertainty(self, f, x, n_iter, n_steps_out, n_features):
        """
        Predicts with the trained model with dropout.

        :param f: Model with dropout during testing
        :param x: Input data used to make the predictions.
        :param n_iter: Number of iterations through the model.
        :param n_steps_out: Output size. Number of weeks to predict.
        :param n_features: Number of features to predict.

        :return predictions: Array with the predictions for each feature.

        """
        predictions = []
        for i in range(n_iter):
            predictions.append(f([x, 1]))
            # prediction = result.mean(axis=0)
        predictions = np.array(predictions).reshape(n_iter, n_steps_out * n_features).T
        # uncertainty = result.std(axis=0)
        return predictions

    def min_max_scaler(self, data):
        """
        Scales the data with a Min Max scaler.

        :param data: Input dataframe used to train the models predictions.

        :return scalers: Array with the scalers for each feature.
        :return data_train: Normalized input dataframe.

        """
        scalers = {}
        # data_train=data.iloc[:,n_features:].copy()
        data_train = data.copy()
        for j in data_train.columns:
            #   scaler= StandardScaler()
            scaler = MinMaxScaler(feature_range=(-1, 1))
            s_s = scaler.fit_transform(data_train[j].values.reshape(-1, 1))
            s_s = np.reshape(s_s, len(s_s))
            scalers['scaler_' + j] = scaler
            data_train[j] = s_s
        return scalers, data_train

    def training(self, data_m, n_features):
        """
        Train models for backtesting and forecasting.

        :param data_m (df): Dataframe with the historical data ordered by date, where each columns represents a feature.
        :param n_features: Number of features to predict.

        :return data (df): Dataframe with the historical data ordered by date, where each columns represents a feature.
        :return models: List of models trained for backtesting and forecasting.
        :return data_train_list: List of arrays used to train the models.
        :return scalers_list: List of scalers used for data normalization.
        """

        models = [None] * (self.n_backtests + 1)
        data_train_list = {}
        scalers_list = {}

        # Train and predict forecast and backtests models
        for i in range(self.n_backtests + 1):
            scalers = {}
            data_train = pd.DataFrame()
            data_train = data_m.copy()
            size = len(data_m.index)
            data_train = data_train.head(size - (i) * self.n_steps_out)
            if self.normalization:
                # -------------------------------scaler----------------------------------
                # for j in data_train.columns:
                # scaler= StandardScaler()
                # scaler = MinMaxScaler(feature_range=(-1,1))
                # s_s = scaler.fit_transform(data_train[j].values.reshape(-1,1))
                # s_s=np.reshape(s_s,len(s_s))
                # scalers['scaler_'+ j] = scaler
                # data_train[j]=s_s
                scalers, data_train = self.min_max_scaler(data_train)
                # -----------------------------------------------------------

            # convert into input/output
            X, y = self.split_sequences(data_train.to_numpy(), self.n_steps_in, self.n_steps_out)
            # ....................................................................
            # if params["trdata"]:
            #    X=X[:,:,params["train_columns"]:]
            y = y[:, :, 0:n_features]
            # Xval,yval=split_sequences(dfvaln, n_steps_in, n_steps_out)
            # the dataset knows the number of features, e.g. 2
            n_features = y.shape[2]

            # X = tf.expand_dims(X, axis=-1)
            # y = tf.expand_dims(y, axis=-1)
            # modellll seq
            print(X.shape)
            print(y.shape)
            # X = tf.squeeze(train_labels, axis=-1)
            # y = tf.squeeze(y, axis=-1)
            print(y.shape)
            # tf.keras.backend.clear_session()

            # model = tf.keras.models.Sequential([
            #    tf.keras.layers.LSTM(72, activation='relu', input_shape=(X.shape[1], X.shape[2]), return_sequences=True),
            #    tf.keras.layers.LSTM(48, activation='relu', return_sequences=False),
            #    tf.keras.layers.Flatten(),
            #    tf.keras.layers.Dropout(0.3),
            #    tf.keras.layers.Dense(128, activation='relu'),
            #    tf.keras.layers.Dropout(0.3),
            #    tf.keras.layers.Dense(self.n_steps_out)
            # ], name='lstm')

            # tf.keras.backend.clear_session()

            # model = tf.keras.models.Sequential([
            #    tf.keras.layers.Conv1D(64, kernel_size=6, activation='relu', input_shape=(X.shape[1], X.shape[2]))),
            #    tf.keras.layers.MaxPooling1D(2),
            #    tf.keras.layers.Conv1D(64, kernel_size=3, activation='relu'),
            # tf.keras.layers.MaxPooling1D(2),
            #    tf.keras.layers.LSTM(72, activation='relu', return_sequences=True),
            #    tf.keras.layers.LSTM(48, activation='relu', return_sequences=False),
            #    tf.keras.layers.Flatten(),
            #    tf.keras.layers.Dropout(0.3),
            #    tf.keras.layers.Dense(128),
            #    tf.keras.layers.Dropout(0.3),
            #    tf.keras.layers.Dense(self.n_steps_out)
            # ], name="lstm_cnn")

            # loss = tf.keras.losses.Huber()
            # optimizer = tf.keras.optimizers.Adam(lr=lr)

            # model.compile(loss=loss, optimizer='adam', metrics=['mae'])

            # ------------------------------Define the model---------------------------------------------------
            n_hidden = self.units
            input_train = Input(shape=(X.shape[1], X.shape[2]))
            output_train = Input(shape=(y.shape[1], y.shape[2]))

            encoder_stack_h, encoder_last_h, encoder_last_c = LSTM(n_hidden, activation='relu',
                                                                   dropout=self.dropout_train,
                                                                   recurrent_dropout=self.dropout_train,
                                                                   return_state=True, return_sequences=True)(
                input_train)

            encoder_last_h = BatchNormalization(momentum=self.momentum)(encoder_last_h)
            encoder_last_c = BatchNormalization(momentum=self.momentum)(encoder_last_c)
            decoder_input = RepeatVector(y.shape[1])(encoder_last_h)
            decoder_stack_h = LSTM(n_hidden, activation='relu', return_state=False, return_sequences=True)(
                decoder_input, initial_state=[encoder_last_h, encoder_last_c])
            attention = dot([decoder_stack_h, encoder_stack_h], axes=[2, 2])
            attention = Activation('softmax')(attention)
            context = dot([attention, encoder_stack_h], axes=[2, 1])
            context = BatchNormalization(momentum=self.momentum)(context)
            decoder_combined_context = concatenate([context, decoder_stack_h])
            out = TimeDistributed(Dense(y.shape[2]))(decoder_combined_context)
            model = Model(inputs=input_train, outputs=out)
            # ---------------------------------------------------------------------------------

            model.summary()
            lr = self.lr
            adam = Adam(lr)
            # Compile model
            model.compile(optimizer=adam, loss='mean_squared_error', metrics=['accuracy'])

            # fit model
            def scheduler(epoch, lr):
                if epoch < self.epochs / 2:
                    return self.lr
                elif epoch < int(self.epochs * 2 / 3):
                    return self.lr / 2
                elif epoch < int(self.epochs * 3 / 4):
                    return self.lr / 4
                else:
                    return self.lr / 8

            LearningScheduler = tf.keras.callbacks.LearningRateScheduler(scheduler, verbose=2)
            checkpoint_best_path = '../tmp/model' + str(i) + '.h5'
            checkpoint_best = ModelCheckpoint(filepath=checkpoint_best_path, save_weights_only=False, save_freq="epoch",
                                              monitor="accuracy", save_best_only=True, verbose=2)

            if self.lrS:
                history = model.fit(X, y, epochs=self.epochs, verbose=2, batch_size=self.batch_size,
                                    callbacks=[checkpoint_best, LearningScheduler])
            else:
                history = model.fit(X, y, epochs=self.epochs, verbose=2, batch_size=self.batch_size,
                                    callbacks=[checkpoint_best])
            print(history.history.keys())
            # print(history.history())
            # Plot the model accuracy and loss
            plt.plot(history.history['accuracy'])
            plt.title('model accuracy')
            plt.ylabel('accuracy')
            plt.xlabel('epoch')
            plt.legend(['train'], loc='upper left')
            plt.show()

            plt.plot(history.history['loss'])
            plt.title('model loss')
            plt.ylabel('loss')
            plt.xlabel('epoch')
            plt.legend(['train'], loc='upper left')
            plt.show()
            scalers_list[i] = scalers
            data_train_list[i] = data_train
            models[i] = model
            if self.save_last_epoch:
                model.save('../tmp/model' + str(i) + '.h5')
        # --------------------------------------------------------
        return models, data_train_list, scalers_list, n_features

    def prediction(self, data, models, data_train_list, scalers_list, n_features):
        """
        Takes the models trained and predicts the values for backtesting and forecasting.

        :param data (df): Dataframe with the historical data ordered by date, where each columns represents a feature.
        :param models: List of models trained for backtesting and forecasting.
        :param data_train_list: List of arrays used to train the models.
        :param scalers_list: List of scalers used for data normalization.

        :return predict (list(df)): Dataframe with the forecasted values of n_steps_out for each item in n_features.
        :return models (list(models)): List with the (n_backtests+1) models trained for backtesting and forecasting.
        :return intervals (list(arrays)): List with arrays of the predictions using dropout in order to find the confidence intervales.
                                Each array has a size of (n_iter, n_steps_out*n_features).
                                models,data_train_list, scalers_list, n_features
        """
        tf.compat.v1.disable_eager_execution()
        intervals = {}
        predict = {}
        for i in range(self.n_backtests + 1):
            lista = []
            lista = list(data_train_list[i].columns)[0:n_features]
            listan = list(itertools.chain.from_iterable(itertools.repeat(x, self.n_steps_out) for x in lista))
            size = len(data.index)

            # if params["trdata"]:
            #    predict_input =data_train_list[i].iloc[:,params["train_columns"]:].tail(n_steps_in)
            # else:
            predict_input = data_train_list[i].tail(self.n_steps_in)
            # ......................................................................
            predict_input = predict_input.to_numpy()[0:self.n_steps_in]
            model = tf.keras.models.load_model('../tmp/model' + str(i) + '.h5')
            # model=models[i]
            # -------Add dropout to the model used during training to make the predictions---------------------------
            dropout = self.dropout
            n_iter = self.n_iter
            conf = model.get_config()
            # Add the specified dropout to all layers

            for layer in conf['layers']:
                # Dropout layers
                if layer["class_name"] == "Dropout":
                    layer["config"]["rate"] = dropout
                # Recurrent layers with dropout
                elif "dropout" in layer["config"].keys():
                    layer["config"]["dropout"] = dropout
            # Create a new model with specified dropout
            if type(model) == Sequential:
                # Sequential
                model_dropout = Sequential.from_config(conf)
            else:
                # Functional
                model_dropout = Model.from_config(conf)
            model_dropout.set_weights(model.get_weights())

            # Define the new model with dropout
            predict_with_dropout = K.function([model_dropout.layers[0].input, K.learning_phase()],
                                              [model_dropout.layers[-1].output])

            input_data = predict_input.copy()
            input_data = input_data[None, ...]
            # num_samples = input_data.shape[0]
            # fill the intervals list with the n_iter outputs for each point.
            intervals[i] = self.predict_with_uncertainty(f=predict_with_dropout, x=input_data, n_iter=self.n_iter,
                                                         n_steps_out=self.n_steps_out, n_features=n_features)
            # -----------------------------------------------------------------------------------
            # Make predictions without dropout to compare the results
            # .......................................................................................
            # if params["trdata"]:
            #    predict_input =predict_input.reshape((1, n_steps_in, len(data_train_list[i].iloc[:,params["train_columns"]:].columns)))
            # else:
            predict_input = predict_input.reshape((1, self.n_steps_in, len(data_train_list[i].columns)))
            predict_out = model.predict(predict_input, verbose=0)
            print(predict_out.shape)

            # ---------------------Invert normalization----------------------------
            if self.normalization:
                for index, k in enumerate(data_train_list[i].iloc[:, :n_features].columns):
                    scaler = scalers_list[i]['scaler_' + k]
                    predict_out[:, :, index] = scaler.inverse_transform(predict_out[:, :, index])
                    for j in range(self.n_steps_out):
                        intervals[i][j * n_features + index, :] = scaler.inverse_transform(
                            intervals[i][j * n_features + index, :].reshape(-1, 1))[:, 0]
            # ------------------------inverse transform-----------------------

            # Reshape predictions
            predict_out = np.reshape(predict_out, (n_features * self.n_steps_out, 1), order='F')
            predict[i] = pd.DataFrame(predict_out)
            idxa = np.arange(size - i * self.n_steps_out, size - (i - 1) * self.n_steps_out)
            idx = idxa
            for k in range(n_features - 1):
                idx = np.append(idx, idxa)
            predict[i].insert(0, "item_id", np.array(listan), True)
            predict[i].insert(0, "time_idx", idx.T, True)

        return predict, models, intervals

    def gradient_importance(self, seq, model):
        """
        Finds the importance of each feature for a model.

        :param seq: Normalized input data used to find the importance of each feature.
        :param model: Model trained.

        :return grads: Importance of each varaible.

        """

        seq = tf.Variable(seq[np.newaxis, :, :], dtype=tf.float32)

        with tf.GradientTape() as tape:
            predictions = model(seq)

        grads = tape.gradient(predictions, seq)
        grads = tf.reduce_mean(grads, axis=1).numpy()[0]

        return grads

    def relative_importance(self, data, n_columns=0, list_columns=[]):
        """
        Finds the relative importance of each variable using the backtesting and forecasting models

        :param data: Normalized input data used to find the importance of each feature.
        :param n_columns: Number of features used in the input data.
        :param list_columns: List of features defined to find their relative importance.

        :return df_importancia_r: Importance of each varaible.

        """

        df_importancia = {}
        df_importancia_mean = {}
        df_importancia_r = pd.DataFrame()

        for i in range(self.n_backtests + 1):

            scalers = {}
            # data_train=data.iloc[:,n_features:].copy()
            data_train = data.copy()
            size = len(data_train)
            data_train = data_train.head(size - (i) * self.n_steps_out)

            if self.normalization:
                scalers, data_train = self.min_max_scaler(data_train)

            # convert into input/output
            X, y = self.split_sequences(data_train.to_numpy(), self.n_steps_in, self.n_steps_out)
            # y=y[:,:,0:n_features]

            att = tf.keras.models.load_model('../tmp/model' + str(i) + '.h5')
            grad_imp = []
            columns = data_train.iloc[:, :].columns

            for k in range(X.shape[0]):
                grad_imp = np.append(grad_imp, self.gradient_importance(X[k], att))

            grad_imp = grad_imp.reshape(X.shape[0], X.shape[2])

            strings = ["median", "mean"]
            # plt.figure(figsize=(35,25))
            # plt.bar(range(len(mean_grad_imp[:])), mean_grad_imp[:])
            # plt.xticks(range(len(columns)), columns, rotation=90)
            # plt.ylabel('gradients')
            # plt.title("Importancia de variables andercol")
            # plt.savefig('fig3.png')
            # plt.show()
            median_grad_imp = np.median(grad_imp, axis=0)
            if i == 0:
                df_importancia[i] = pd.DataFrame(median_grad_imp, index=list(data_train.columns)).applymap(
                    lambda x: x * 1e3) \
                    .reset_index(drop=False) \
                    .rename(columns={'index': 'SKU', 0: 'Importancia_median_0'})
            else:
                df_importancia[i] = pd.DataFrame(median_grad_imp, index=list(data_train.columns)).applymap(
                    lambda x: x * 1e3) \
                    .reset_index(drop=False) \
                    .rename(columns={0: 'Importancia_median_' + str(i)})

            mean_grad_imp = np.mean(grad_imp, axis=0)
            if i == 0:
                df_importancia_mean[i] = pd.DataFrame(mean_grad_imp, index=list(data_train.columns)).applymap(
                    lambda x: x * 1e3) \
                    .reset_index(drop=False) \
                    .rename(columns={'index': 'SKU', 0: 'Importancia_median_0'})
            else:
                df_importancia_mean[i] = pd.DataFrame(mean_grad_imp, index=list(data_train.columns)).applymap(
                    lambda x: x * 1e3) \
                    .reset_index(drop=False) \
                    .rename(columns={0: 'Importancia_median_' + str(i)})

        df_importancia_f = pd.concat(df_importancia, axis=1)
        df_importancia_f.columns = df_importancia_f.columns.droplevel()

        def sum_imp(row):
            sum = 0
            idx_sum = 0
            for k in range(self.n_backtests + 1):
                idx_sum = idx_sum + 6 - k
                sum = sum + row["Importancia_median_" + str(k)] * (6 - k)
                # print(sum)
                # print(idx_sum)
            mean = sum / idx_sum
            # mean=row["Importancia_median_"+str(0)]
            return mean

        df_importancia_f["Total_importancia_median"] = df_importancia_f.apply(sum_imp, axis=1)

        # df_importancia_f["Total_importancia_median"]=df_importancia_f.apply(lambda row: 1*row["Importancia_median_5"]+2*row["Importancia_median_4"]+3*row["Importancia_median_3"]+4*row["Importancia_median_2"]+5*row["Importancia_median_1"]+6*row["Importancia_median_0"] ,axis=1)
        df_importancia_f = df_importancia_f[["SKU", "Total_importancia_median"]].sort_values(
            by="Total_importancia_median", ascending=False)
        df_importancia_f = df_importancia_f.reset_index().iloc[:, 1:]
        total_positive = df_importancia_f[df_importancia_f['Total_importancia_median'] >= 0][
            'Total_importancia_median'].sum()
        total_negative = df_importancia_f[df_importancia_f['Total_importancia_median'] < 0][
            'Total_importancia_median'].sum()

        df_importancia_r["SKU_" + str(strings[0])] = df_importancia_f["SKU"]
        df_importancia_r['Importancia_relativa_' + str(strings[0])] = df_importancia_f.apply(
            lambda row: (row['Total_importancia_median'] * 100 / total_positive) if row[
                                                                                        'Total_importancia_median'] >= 0 else (
                        -row['Total_importancia_median'] * 100 / total_negative), axis=1)

        # df_importancia_mean_f=pd.concat(df_importancia_mean, axis=1)
        # df_importancia_mean_f.columns=df_importancia_mean_f.columns.droplevel()
        # df_importancia_mean_f["Total_importancia_median"]=df_importancia_mean_f.apply(lambda row: 1*row["Importancia_median_5"]+2*row["Importancia_median_4"]+3*row["Importancia_median_3"]+4*row["Importancia_median_2"]+5*row["Importancia_median_1"]+6*row["Importancia_median"] ,axis=1)
        # df_importancia_mean_f=df_importancia_mean_f[["SKU","Total_importancia_median"]].sort_values(by="Total_importancia_median", ascending=False)
        # df_importancia_mean_f=df_importancia_mean_f.reset_index().iloc[:,1:]
        # total_positive_mean=df_importancia_mean_f[df_importancia_mean_f['Total_importancia_median']>=0]['Total_importancia_median'].sum()
        # total_negative_mean=df_importancia_mean_f[df_importancia_mean_f['Total_importancia_median']<0]['Total_importancia_median'].sum()

        # df_importancia_r["SKU_"+str(strings[1])]=df_importancia_mean_f["SKU"]
        # df_importancia_r['Importancia_relativa_'+str(strings[1])]=df_importancia_mean_f.apply(lambda row: (row['Total_importancia_median']*100/total_positive_mean) if row['Total_importancia_median']>=0 else (-row['Total_importancia_median']*100/total_negative_mean) , axis=1)

        if n_columns == 0:
            if len(list_columns) == 0:
                return df_importancia_r
            else:
                return df_importancia_r[(df_importancia_r["SKU_median"].isin(list_columns))]
        else:
            return df_importancia_r[(df_importancia_r["SKU_median"].isin(data_train.columns[0:n_columns]))]

    def correlation(self, data, n_columns=0, list_columns=[]):
        """
        Finds the correlation between the selected variables.

        :param data: Normalized input data used to find the correlation of each feature.
        :param n_columns: Number of features used in the input data.
        :param list_columns: List of features defined to find their correlation.

        :return correlation_matrix: Dataframe with the correlation between the selected variables.

        """
        # if n_columns==0:
        #    if len(list_columns)==0:
        #      data=data
        #    else:
        #      data=data[list_columns]
        # else:
        #  data=data.iloc[:,:n_columns]

        scalers, data_train = self.min_max_scaler(data)
        heatdata = data_train.corr()
        correlation_matrix = pd.DataFrame()

        if n_columns == 0:
            if len(list_columns) == 0:
                for col in data_train.columns:
                    col_heat = heatdata[[col]].sort_values(by=col, ascending=False)
                    correlation_matrix = pd.concat([correlation_matrix, col_heat.reset_index()], axis=1)
                return correlation_matrix
            else:
                for col in list_columns:
                    col_heat = heatdata[[col]].sort_values(by=col, ascending=False)
                    correlation_matrix = pd.concat([correlation_matrix, col_heat.reset_index()], axis=1)
                return correlation_matrix
        else:
            for col in data_train[0:n_columns].columns:
                col_heat = heatdata[[col]].sort_values(by=col, ascending=False)
                correlation_matrix = pd.concat([correlation_matrix, col_heat.reset_index()], axis=1)
            return correlation_matrix

    def causality(self, data, threshold=0.7, max_iter=100, list_columns=[]):
        """
        Finds the causality between the selected variables.

        :param data: Normalized input data used to find the causality of each feature.
        :param threshold: Minimum causality value.
        :param max_iter: Number of iterations used to converge the model.

        :return affects: Dataframe with the features that are affected by the column name variable.
        :return Var_affected: Dataframe with the features that affects the column name variable.

        """
        scalers, data_train = self.min_max_scaler(data)
        sm = from_pandas(data_train, max_iter=max_iter, w_threshold=threshold)
        len(sm.edges)

        # affects
        d = np.array(sm.edges)
        df = pd.DataFrame(d)
        df.columns = ["affected by", "Var affected"]
        uni = df['affected by'].unique()

        lista = []
        for i in range(len(uni)):
            lista_aux = []
            df_aux = df[df['affected by'] == uni[i]]
            lista_aux.append(uni[i])
            for j in range(len(df_aux)):
                lista_aux.append(df_aux["Var affected"].iloc[j])
            lista.append(lista_aux)
        affects = pd.DataFrame(lista).T
        affects = affects.rename(columns=affects.iloc[0])
        affects = affects[1:]

        table = str.maketrans(dict.fromkeys("()"))
        n_col = []
        for i in range(len(affects.columns)):
            n_col.append(affects.columns[i].translate(table))
        affects.columns = n_col

        # Var affected by
        uni_aff = df['Var affected'].unique()
        lista_aff = []
        for i in range(len(uni_aff)):
            lista_aux = []
            df_aux = df[df['Var affected'] == uni_aff[i]]
            lista_aux.append(uni_aff[i])
            for j in range(len(df_aux)):
                lista_aux.append(df_aux["affected by"].iloc[j])
            lista_aff.append(lista_aux)

        Var_affected = pd.DataFrame(lista_aff).T
        Var_affected = Var_affected.rename(columns=Var_affected.iloc[0])
        Var_affected = Var_affected[1:]

        n_col = []
        for i in range(len(Var_affected.columns)):
            n_col.append(Var_affected.columns[i].translate(table))
        Var_affected.columns = n_col

        # affected=Var_affected[list_columns].values
        # Qcausal2=pd.DataFrame()
        # Qcausal2["item_id"]=data.columns
        # Qcausal2["Causality"]=Qcausal2.apply(lambda row: row["item_id"] in affected, axis=1)
        # Qcausal2=Qcausal2.sort_values(by="Causality", ascending=False)
        # Qcausal2["Causality"] = Qcausal2["Causality"].astype(int)

        return Var_affected

    def intervals(self, data, predict, predictions, n_features, mult=[1.3, 1.2, 1.1]):
        """
        Define confidence intervals using the ['p50','p95','p5','p60','p40','p80','p20'] percentils with the predictions data
        found using dropout and simulation path during the prediction.

        :param data (df): Qprep data in matrix form.
        :param predict (df): Dataframe with the predicted values during prediction.
        :param predictions (df): predictions using dropout with size (n_iter, n_steps_out*n_features).
        :param n_features (int): Number of features or items to be predicted.

        :return predict (df): Dataframe with the confidence intervals for each product in each of the backtests and forecast.
        """
        interv = ['p50', 'p95', 'p5', 'p60', 'p40', 'p80', 'p20']
        columns = ["time_idx", "item_id"]
        size = len(data)
        # n_features_old=10
        for i in range(self.n_backtests + 1):
            predict[i] = predict[i].iloc[:, :2]
            p = np.zeros((self.n_steps_out * n_features, len(interv)))
            predict[i].columns = columns
            for j in range(n_features):
                for k in range(self.n_steps_out):
                    ci = 0
                    p[j * self.n_steps_out + k][0] = np.quantile(predictions[i][n_features * k + j, :], 0.5)
                    ci = 0.95
                    p[j * self.n_steps_out + k][1] = np.quantile(predictions[i][n_features * k + j, :],
                                                                 0.5 + ci / 2) * (mult[0])
                    p[j * self.n_steps_out + k][2] = np.quantile(predictions[i][n_features * k + j, :],
                                                                 0.5 - ci / 2) / (mult[0])
                    ci = 0.8
                    p[j * self.n_steps_out + k][3] = np.quantile(predictions[i][n_features * k + j, :],
                                                                 0.5 + ci / 2) * (mult[1])
                    p[j * self.n_steps_out + k][4] = np.quantile(predictions[i][n_features * k + j, :],
                                                                 0.5 - ci / 2) / (mult[1])
                    ci = 0.6
                    p[j * self.n_steps_out + k][5] = np.quantile(predictions[i][n_features * k + j, :],
                                                                 0.5 + ci / 2) * (mult[2])
                    p[j * self.n_steps_out + k][6] = np.quantile(predictions[i][n_features * k + j, :],
                                                                 0.5 - ci / 2) / (mult[2])
            predict[i].insert(2, "p50", p[:, 0], allow_duplicates=False)
            predict[i].insert(3, "p95", p[:, 1], allow_duplicates=False)
            predict[i].insert(4, "p5", p[:, 2], allow_duplicates=False)
            predict[i].insert(5, "p80", p[:, 3], allow_duplicates=False)
            predict[i].insert(6, "p20", p[:, 4], allow_duplicates=False)
            predict[i].insert(7, "p60", p[:, 5], allow_duplicates=False)
            predict[i].insert(8, "p40", p[:, 6], allow_duplicates=False)
        return predict

    def intervals(self, data, predict, predictions, n_features, mult=[1.3, 1.2, 1.1]):

        """Define confidence intervals using the ['p50','p95','p5','p60','p40','p80','p20'] percentils with the predictions data
            found using dropout and simulation path during the prediction.

        Args:
            data (df): Qprep data in matrix form.
            predict (df): Dataframe with the predicted values during prediction.
            predictions (df): predictions using dropout with size (n_iter, n_steps_out*n_features).
            n_features (int): Number of features or items to be predicted.
            n_backtests (int): Number of backtests to use during training.
            n_steps_in (int): Input window size. 8 weeks by default.
            n_steps_out (int): Number of weeks to be predicted. 4 by default

        Returns:
            predict (df): Dataframe with the confidence intervals for each product in each of the backtests and forecast.
        """

        interv = ['p50', 'p95', 'p5', 'p60', 'p40', 'p80', 'p20']
        columns = ["time_idx", "item_id", "predict_orig"]
        size = len(data)
        # n_features_old=10
        for i in range(self.n_backtests + 1):
            # predict[i]=predict[i].iloc[:,:2]
            p = np.zeros((self.n_steps_out * n_features, len(interv)))
            predict[i].columns = columns
            for j in range(n_features):
                for k in range(self.n_steps_out):
                    ci = 0
                    p50 = np.quantile(predictions[i][n_features * k + j, :], 0.5)
                    p[j * self.n_steps_out + k][0] = p50
                    ci = 0.95
                    p[j * self.n_steps_out + k][1] = (np.quantile(predictions[i][n_features * k + j, :],
                                                                  0.5 + ci / 2) - p50) * mult[0]
                    p[j * self.n_steps_out + k][2] = (np.quantile(predictions[i][n_features * k + j, :],
                                                                  0.5 - ci / 2) - p50) * mult[0]
                    ci = 0.6
                    p[j * self.n_steps_out + k][3] = (np.quantile(predictions[i][n_features * k + j, :],
                                                                  0.5 + ci / 2) - p50) * mult[2]
                    p[j * self.n_steps_out + k][4] = (np.quantile(predictions[i][n_features * k + j, :],
                                                                  0.5 - ci / 2) - p50) * mult[2]
                    ci = 0.8
                    p[j * self.n_steps_out + k][5] = (np.quantile(predictions[i][n_features * k + j, :],
                                                                  0.5 + ci / 2) - p50) * mult[1]
                    p[j * self.n_steps_out + k][6] = (np.quantile(predictions[i][n_features * k + j, :],
                                                                  0.5 - ci / 2) - p50) * mult[1]

                    # ci = 0
                    # p[j*n_steps_out+k][0] = np.quantile(predictions[i][n_features*k+j,:], 0.5)
                    # ci = 0.95
                    # p[j*n_steps_out+k][1]=np.quantile(predictions[i][n_features*k+j,:], 0.5+ci/2)
                    # p[j*n_steps_out+k][2]=np.quantile(predictions[i][n_features*k+j,:], 0.5-ci/2)
                    # ci=0.6
                    # p[j*n_steps_out+k][3]=np.quantile(predictions[i][n_features*k+j,:], 0.5+ci/2)
                    # p[j*n_steps_out+k][4]=np.quantile(predictions[i][n_features*k+j,:], 0.5-ci/2)
                    # ci=0.8
                    # p[j*n_steps_out+k][5]=np.quantile(predictions[i][n_features*k+j,:], 0.5+ci/2)
                    # p[j*n_steps_out+k][6]=np.quantile(predictions[i][n_features*k+j,:], 0.5-ci/2)

            predict[i].insert(2, "p50a", p[:, 0], allow_duplicates=False)
            predict[i].insert(3, "p95a", p[:, 1], allow_duplicates=False)
            predict[i].insert(4, "p5a", p[:, 2], allow_duplicates=False)
            predict[i].insert(5, "p60a", p[:, 3], allow_duplicates=False)
            predict[i].insert(6, "p40a", p[:, 4], allow_duplicates=False)
            predict[i].insert(7, "p80a", p[:, 5], allow_duplicates=False)
            predict[i].insert(8, "p20a", p[:, 6], allow_duplicates=False)

            predict[i]["p50"] = predict[i].apply(lambda row: row["predict_orig"], axis=1)
            predict[i]["p95"] = predict[i].apply(lambda row: row["predict_orig"] + row["p95a"], axis=1)
            predict[i]["p5"] = predict[i].apply(lambda row: row["predict_orig"] + row["p5a"], axis=1)
            predict[i]["p60"] = predict[i].apply(lambda row: row["predict_orig"] + row["p60a"], axis=1)
            predict[i]["p40"] = predict[i].apply(lambda row: row["predict_orig"] + row["p40a"], axis=1)
            predict[i]["p80"] = predict[i].apply(lambda row: row["predict_orig"] + row["p80a"], axis=1)
            predict[i]["p20"] = predict[i].apply(lambda row: row["predict_orig"] + row["p20a"], axis=1)
        return predict

    def intervals(self, data, predict, predictions, n_features, mult):

        """Define confidence intervals using the ['p50','p95','p5','p60','p40','p80','p20'] percentils with the predictions data
            found using dropout and simulation path during the prediction.

        Args:
            data (df): Qprep data in matrix form.
            predict (df): Dataframe with the predicted values during prediction.
            predictions (df): predictions using dropout with size (n_iter, n_steps_out*n_features).
            n_features (int): Number of features or items to be predicted.
            n_backtests (int): Number of backtests to use during training.
            n_steps_in (int): Input window size. 8 weeks by default.
            n_steps_out (int): Number of weeks to be predicted. 4 by default

        Returns:
            predict (df): Dataframe with the confidence intervals for each product in each of the backtests and forecast.
        """

        interv = ['p50', 'p95', 'p5', 'p60', 'p40', 'p80', 'p20']
        columns = ["time_idx", "item_id", "predict_orig"]
        size = len(data)
        # n_features_old=10
        for i in range(self.n_backtests + 1):
            # predict[i]=predict[i].iloc[:,:2]
            p = np.zeros((self.n_steps_out * n_features, len(interv)))
            predict[i].columns = columns
            for j in range(n_features):
                for k in range(self.n_steps_out):
                    ci = 0
                    p50 = np.quantile(predictions[i][n_features * k + j, :], 0.5)
                    p[j * self.n_steps_out + k][0] = p50
                    ci = 0.95
                    p[j * self.n_steps_out + k][1] = (np.quantile(predictions[i][n_features * k + j, :],
                                                                  0.5 + ci / 2) - p50) * mult[j][0]
                    p[j * self.n_steps_out + k][2] = (np.quantile(predictions[i][n_features * k + j, :],
                                                                  0.5 - ci / 2) - p50) * mult[j][0]
                    ci = 0.6
                    p[j * self.n_steps_out + k][3] = (np.quantile(predictions[i][n_features * k + j, :],
                                                                  0.5 + ci / 2) - p50) * mult[j][2]
                    p[j * self.n_steps_out + k][4] = (np.quantile(predictions[i][n_features * k + j, :],
                                                                  0.5 - ci / 2) - p50) * mult[j][2]
                    ci = 0.8
                    p[j * self.n_steps_out + k][5] = (np.quantile(predictions[i][n_features * k + j, :],
                                                                  0.5 + ci / 2) - p50) * mult[j][1]
                    p[j * self.n_steps_out + k][6] = (np.quantile(predictions[i][n_features * k + j, :],
                                                                  0.5 - ci / 2) - p50) * mult[j][1]

                    # ci = 0
                    # p[j*n_steps_out+k][0] = np.quantile(predictions[i][n_features*k+j,:], 0.5)
                    # ci = 0.95
                    # p[j*n_steps_out+k][1]=np.quantile(predictions[i][n_features*k+j,:], 0.5+ci/2)
                    # p[j*n_steps_out+k][2]=np.quantile(predictions[i][n_features*k+j,:], 0.5-ci/2)
                    # ci=0.6
                    # p[j*n_steps_out+k][3]=np.quantile(predictions[i][n_features*k+j,:], 0.5+ci/2)
                    # p[j*n_steps_out+k][4]=np.quantile(predictions[i][n_features*k+j,:], 0.5-ci/2)
                    # ci=0.8
                    # p[j*n_steps_out+k][5]=np.quantile(predictions[i][n_features*k+j,:], 0.5+ci/2)
                    # p[j*n_steps_out+k][6]=np.quantile(predictions[i][n_features*k+j,:], 0.5-ci/2)

            predict[i].insert(2, "p50a", p[:, 0], allow_duplicates=False)
            predict[i].insert(3, "p95a", p[:, 1], allow_duplicates=False)
            predict[i].insert(4, "p5a", p[:, 2], allow_duplicates=False)
            predict[i].insert(5, "p60a", p[:, 3], allow_duplicates=False)
            predict[i].insert(6, "p40a", p[:, 4], allow_duplicates=False)
            predict[i].insert(7, "p80a", p[:, 5], allow_duplicates=False)
            predict[i].insert(8, "p20a", p[:, 6], allow_duplicates=False)

            predict[i]["p50"] = predict[i].apply(lambda row: row["predict_orig"], axis=1)
            predict[i]["p95"] = predict[i].apply(lambda row: row["predict_orig"] + row["p95a"], axis=1)
            predict[i]["p5"] = predict[i].apply(lambda row: row["predict_orig"] + row["p5a"], axis=1)
            predict[i]["p60"] = predict[i].apply(lambda row: row["predict_orig"] + row["p60a"], axis=1)
            predict[i]["p40"] = predict[i].apply(lambda row: row["predict_orig"] + row["p40a"], axis=1)
            predict[i]["p80"] = predict[i].apply(lambda row: row["predict_orig"] + row["p80a"], axis=1)
            predict[i]["p20"] = predict[i].apply(lambda row: row["predict_orig"] + row["p20a"], axis=1)
        return predict