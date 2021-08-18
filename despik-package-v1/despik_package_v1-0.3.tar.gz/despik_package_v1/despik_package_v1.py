import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


def ticker_upper(ticker):
    if type(ticker) == str:
        ticker = [ticker]
    return [x.upper() for x in ticker]


def get_info(ticker, param=None):
    """
    This function can give you all parametres of tickers. If you want download not all, you can chose
    your own list of parametrs
    :param ticker: string or list of strings, one ticker or list of tickers
    :param param: list or string. List of parametres
    :return: dataframe with all tickers and parametres.
    """
    ticker_upp = ticker_upper(ticker)
    for tick in ticker_upp:
        assert len(yf.Ticker(tick).info) != 2, 'Wrong {}. Please send right ticker code'.format(tick)
    all_parametrs = yf.Ticker(ticker_upp[0]).info.keys()
    if param is None:
        data = pd.DataFrame(index=ticker_upp, columns=all_parametrs)
        for i in ticker_upp:
            tick = yf.Ticker(i)
            for k in all_parametrs:
                data.loc[i, k] = tick.info[k]
    else:
        data = pd.DataFrame(index=ticker_upp, columns=param)
        for i in ticker_upp:
            tick = yf.Ticker(i)
            for k in param:
                data.loc[i, k] = tick.info[k]
    return data


def get_all_price(ticker, period='Max', interval="1d"):
    """
    :param ticker: string or list of strings.
    :param period: "Max"  # 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    :param interval: "1d"    # 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk
    :return: dataframe with prices
    """
    ticker_upp = ticker_upper(ticker)
    yf_price = yf.download(
        tickers=ticker_upp,  # tickers list or string as well
        period=period,  # optional, default is '1mo'
        interval=interval,  # fetch data by interval
        group_by='ticker',  # group by ticker
        auto_adjust=True,  # adjust all OHLC (open-high-low-close)
        prepost=True,  # download market hours data
        threads=True,  # threads for mass downloading
        proxy=None)
    return yf_price


def get_close_price(ticker, period='Max', interval='1d'):
    ticker_upp = ticker_upper(ticker)
    yf_price = get_all_price(ticker_upp, period, interval)
    if len(ticker_upp) == 1:
        yf_price.columns = pd.MultiIndex.from_product([ticker_upp, yf_price.columns])
    yf_price = yf_price.iloc[:, yf_price.columns.get_level_values(1) == 'Close']
    yf_price = round(yf_price[ticker_upp], 2)  # change order of columns
    yf_price.columns = yf_price.columns.droplevel(1)
    return yf_price


def close_price_percent(ticker, period='Max', interval='1d'):
    ticker_upp = ticker_upper(ticker)
    yf_price = get_close_price(ticker, period, interval)
    yf_percent = round(yf_price[ticker_upp].pct_change() * 100, 2)

    yf_percent['YR-MTH'] = pd.to_datetime(yf_percent.index).strftime("%Y-%m")

    # create dataframe
    perf_mth = pd.DataFrame()
    perf_mth['YR-MTH'] = yf_percent['YR-MTH'].sort_values().unique()

    #  calculate returns
    for x in ticker_upp:
        perf_mth[x] = yf_percent[x].groupby(yf_percent['YR-MTH']).sum().values
        perf_mth[x] = round(perf_mth[x], 2)
    return perf_mth


def plot_ticker(ticker, period='Max', interval="1d", perfomance=24):
    """
    period   = "Max"  # 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    interval = "1d"    # 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,
    :param ticker: string or list of strings.
    :param period:
    :param interval:
    :param perfomance: period of plot
    :return:
    """
    ticker_upp = ticker_upper(ticker)
    perf_mth = close_price_percent(ticker, period, interval)
    perf_mth = perf_mth.tail(perfomance)

    # col_name with max row_values
    perf_mth['maxSYM'] = perf_mth[ticker_upp].idxmax(axis=1)
    perf_mth['max'] = perf_mth[ticker_upp].max(axis=1)
    df_plot = perf_mth[ticker_upp].head(-1).tail(perfomance)
    df_plot['YR-MTH'] = perf_mth['YR-MTH'].head(-1).tail(perfomance)

    if len(ticker_upp) == 1:
        sns.lineplot(x=df_plot['YR-MTH'], y=df_plot[ticker_upp[0]])
        plt.legend([ticker_upp[0]], loc=2)  # top left
        plt.title('{}({} months)'.format(ticker_upp[0], perfomance), fontsize=14)
        plt.xlabel('')
        plt.ylabel('percent change')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.show()
    else:
        c = 3  # columns for subplot
        r = int((len(ticker_upp) + 1) / c)  # rows for subplot
        s = 1  # initialize subplot counter
        fig_y = (c + r) * 3  # multiple may need to be modified

        #  figure size
        plt.figure(figsize=(20, fig_y))

        #  subplot loop
        for i in ticker_upp:
            plt.subplot(r, c, s)
            sns.lineplot(x=df_plot['YR-MTH'], y=df_plot[i])

            plt.legend([i], loc=2)  # top left
            plt.title('{}({} months)'.format(i, perfomance), fontsize=14)
            plt.xlabel('')
            plt.ylabel('percent change')
            plt.xticks(rotation=90)
            s = s + 1  # increment subplot counter
        plt.tight_layout()
        plt.show()


def simple_regression(ticker, period='Max'):
    apl = yf.Ticker(ticker)
    data = apl.history(period=period)
    data.reset_index(inplace=True)
    data.columns = ['date', 'open', 'high', 'low', 'close', 'vol', 'divs', 'split']
    data.drop(columns=['divs', 'split'])
    data['date'] = pd.to_datetime(data.date)
    x = data[['open', 'high', 'low', 'vol']]
    y = data['close']
    train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.15,
                                                        shuffle=False, random_state=42)
    regression = LinearRegression()
    regression.fit(train_x, train_y)

    predicted = regression.predict(test_x)
    dfr = pd.DataFrame({'Actual_Price': test_y, 'Predicted_Price': predicted})

    plt.plot(dfr.Actual_Price, color='black')
    plt.plot(dfr.Predicted_Price, color='lightblue')
    plt.title("{} prediction chart".format(ticker))
    plt.show()
    return predicted




