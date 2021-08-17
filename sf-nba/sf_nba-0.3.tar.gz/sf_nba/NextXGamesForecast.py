class NextXGamesForecast():
  def __init__(self, player_name, stat = 'PTS'):
    import pandas as pd
    import numpy as np
    df  = pd.read_csv('https://github.com/tarsur909/SF_NBA/blob/main/data/final_player_tables.csv?raw=true')
    self.df = df

    #store input data
    self.player_name = player_name
    player_df = df[df.Player == player_name]
    self.player_df = player_df
    self.stat = stat




  def simulate(self, next_n_games, epochs = 100, verbose = 0, test_loss = False, loss_curve = False):
    import numpy as np
    import numpy
    import pandas as pd
    #preprocessing
    self.data_array = np.asarray(self.player_df[self.stat]).reshape(-1,1)

    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(self.data_array)
    train = dataset[:round(0.8 * len(dataset))]
    test = dataset[round(0.8 * len(dataset)):len(dataset)]
    def create_dataset(dataset, look_back=1):
	    dataX, dataY = [], []
	    for i in range(len(dataset)-look_back-1):
		    a = dataset[i:(i+look_back), 0]
		    dataX.append(a)
		    dataY.append(dataset[i + look_back, 0])
	    return numpy.array(dataX), numpy.array(dataY)
    look_back = 60
    trainX, trainY = create_dataset(train, look_back)
    trainX = numpy.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
    
    testX, testY = create_dataset(test, look_back)
    testX = numpy.reshape(testX, (testX.shape[0], 1, testX.shape[1]))

    dataX, dataY = create_dataset(dataset, look_back)
    dataX = numpy.reshape(dataX, (dataX.shape[0], 1, dataX.shape[1]))

    

    #import modules 
    from keras.models import Sequential
    from keras.layers import Dense
    from keras.layers import LSTM
    from keras.layers import Dropout
    from keras.layers import Bidirectional
    import numpy as np
    import numpy
    import tensorflow as tf
    import matplotlib.pyplot as plt



    # create and fit the LSTM network
    self.model = Sequential()
    self.model.add(Bidirectional(LSTM(4, input_shape=(1, look_back))))
    #self.model.add(LSTM(4, activation='relu'))
    self.model.add(Dense(1))
    self.model.compile(loss='mean_squared_error', optimizer='adam')
    history = self.model.fit(trainX, trainY, epochs = epochs, batch_size=1, verbose = verbose)

    

    #evaluate model
    eval = self.model.evaluate(testX, testY)

    # make predictions
    dataPredict = self.model.predict(dataX)

    # invert predictions
    self.dataPredict = scaler.inverse_transform(dataPredict)

    self.model.save('nextxgamessimulator.h5')

    #future
    def predict(num_prediction, model):
      prediction_list = dataset[-look_back:]
    
      for _ in range(num_prediction):
        x = prediction_list[-look_back:]
        x = x.reshape((1, 1, look_back))
        out = self.model.predict(x)[0][0]
        prediction_list = np.append(prediction_list, out)
      prediction_list = prediction_list[look_back-1:]
        
      return prediction_list
    
    def predict_dates(num_prediction):
      last_date = self.player_df['Date'].values[-1]
      prediction_dates = pd.date_range(last_date, periods=num_prediction+1, freq = '2D').tolist()
      return prediction_dates[1:]

    num_prediction = next_n_games
    forecast = predict(num_prediction, self.model)
    self.forecast = scaler.inverse_transform(forecast.reshape(-1,1))
    self.forecast = np.around(self.forecast)
    self.forecast = self.forecast.astype('int')
    self.forecast_dates = predict_dates(num_prediction)
    

    if loss_curve is True and test_loss is True:
      plt.plot(history.history['loss'])
      plt.title('model loss')
      plt.ylabel('loss')
      plt.xlabel('epoch')
      return eval, plt.show()
    elif test_loss is True:
      return eval

  def results(self, table = 'dataframe', viz_type = 'standard'):
    import pandas as pd
    if table is 'dataframe':
      data = enumerate(self.forecast.flatten())
      predictions_df = pd.DataFrame(data, columns = ['Next N Game', self.stat])
      return predictions_df[1:]
    
    elif table is 'plotly':

      if viz_type is 'standard':

        import plotly
        import plotly.graph_objects as go
        prediction = self.dataPredict.flatten()
        date_train = self.player_df['Date']
        self.data_array = self.data_array.flatten()


        trace1 = go.Scatter(
          x = date_train,
          y = self.data_array,
          mode = 'lines',
          name = 'Data'
        )
        trace3 = go.Scatter(
        x = self.forecast_dates,
        y = self.forecast.flatten(),
        mode='lines',
        name = 'Future Prediction'
        )
        layout = go.Layout(
          title = self.stat + " Forecasting For " + self.player_name,
          xaxis = {'title' : "Date"},
          yaxis = {'title' : self.stat}
        )
        fig = go.Figure(data=[trace1, trace3], layout=layout)
        fig.show()
      elif viz_type is 'future':
        import plotly
        import plotly.graph_objects as go
        prediction = self.dataPredict.flatten()
        date_train = self.player_df['Date']
        self.data_array = self.data_array.flatten()



        trace3 = go.Scatter(
        x = self.forecast_dates,
        y = self.forecast.flatten(),
        mode='lines',
        name = 'Future Prediction'
        )
        layout = go.Layout(
          title = self.stat +  " Forecasting For " + self.player_name,
          xaxis = {'title' : "Date"},
          yaxis = {'title' : self.stat}
        )
        fig = go.Figure(data=[trace3], layout=layout)
        fig.show()

      elif viz_type is 'validate':
        import plotly
        import plotly.graph_objects as go
        prediction = self.dataPredict.flatten()
        date_train = self.player_df['Date']
        self.data_array = self.data_array.flatten()


        trace1 = go.Scatter(
          x = date_train,
          y = self.data_array,
          mode = 'lines',
          name = 'Data'
        )
        trace2 = go.Scatter(
          x = date_train,
          y = prediction,
          mode = 'lines',
          name = 'Prediction'
        )
        trace3 = go.Scatter(
        x = self.forecast_dates,
        y = self.forecast.flatten(),
        mode='lines',
        name = 'Future Prediction'
        )
        layout = go.Layout(
          title = self.stat + " Forecasting For " + self.player_name,
          xaxis = {'title' : "Date"},
          yaxis = {'title' : self.stat}
        )
        fig = go.Figure(data=[trace1, trace2, trace3], layout=layout)
        fig.show()
