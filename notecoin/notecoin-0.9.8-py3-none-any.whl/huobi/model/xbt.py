import xgboost as xgb
from notecoin.huobi.model import BaseModel

from sklearn.multioutput import MultiOutputRegressor


class XgboostModel(BaseModel):
    def __init__(self, windows=-15, *args, **kwargs):
        super(XgboostModel, self).__init__(*args, **kwargs)
        self.model = None
        self.windows = windows

    def solve(self, df, train=True):
        df2 = df.copy()
        df2 = df2.sort_values(['id'])
        df2 = df2.reset_index(drop=True)

        def ma_n(n):
            df2['MA' + str(n)] = df2['open'].rolling(window=n).mean()

        def shift_n(name, n):
            df2[name + '_' + str(n)] = df2[name].shift(n)

        [ma_n(i) for i in (2, 3, 4, 5, 10, 15, 20, 25, 30)]
        cols = [col for col in df2.columns]
        [[shift_n(name, n) for name in cols if (name in ('MA5', 'open') or 'MA' in name)] for n in
         (1, 2, 3, 4, 5, 10, 15, 30)]

        df2['label'] = df2['open'].shift(self.windows)
        del df2['symbol'], df2['id']

        if train:
            df2.dropna(axis=0, how='any', inplace=True)
            x = df2[df2.columns[1:-1]].values
            y = df2['label'].values
            return x, y
        else:
            del df2['label']
            df2.dropna(axis=0, how='any', inplace=True)
            x = df2[df2.columns[1:]].values
            return x

    def train(self, df, *args, **kwargs):
        x, y = self.solve(df)
        self.model = xgb.XGBRegressor(n_jobs=1).fit(x, y)

    def predict(self, df, *args, **kwargs):
        x = self.solve(df, train=False)
        return self.model.predict(x)


class MultiXgboostModel(BaseModel):
    def __init__(self, windows=None, *args, **kwargs):
        super(MultiXgboostModel, self).__init__(*args, **kwargs)

        if windows is None:
            windows = [-5, -10, -15]
        self.model = None
        self.windows = windows

    def solve(self, df, train=True):
        df2 = df.copy()
        df2 = df2.sort_values(['id'])
        df2 = df2.reset_index(drop=True)

        def ma_n(n):
            df2['MA' + str(n)] = df2['open'].rolling(window=n).mean()

        def shift_n(name, n):
            df2[name + '_' + str(n)] = df2[name].shift(n)

        [ma_n(i) for i in (2, 3, 4, 5, 10, 15, 20, 25, 30)]
        cols = [col for col in df2.columns]
        [[shift_n(name, n) for name in cols if (name in ('MA5', 'open') or 'MA' in name)] for n in
         (1, 2, 3, 4, 5, 10, 15, 30)]

        del df2['symbol'], df2['id']

        if train:
            cols = []
            for window in self.windows:
                col = f'label{window}'
                df2[col] = df2['open'].shift(window)
                cols.append(col)

            df2.dropna(axis=0, how='any', inplace=True)
            x = df2[df2.columns[1:-len(cols)]].values
            y = df2[cols].values
            return x, y
        else:
            df2.dropna(axis=0, how='any', inplace=True)
            x = df2[df2.columns[1:]].values
            return x

    def train(self, df, *args, **kwargs):
        x, y = self.solve(df)
        other_params = {'learning_rate': 0.1, 'n_estimators': 300, 'max_depth': 5, 'min_child_weight': 1, 'seed': 0,
                        'subsample': 0.8, 'colsample_bytree': 0.8, 'gamma': 0, 'reg_alpha': 0, 'reg_lambda': 1}

        self.model = MultiOutputRegressor(xgb.XGBRegressor(objective='reg:squarederror', **other_params)).fit(x, y)

    def predict(self, df, *args, **kwargs):
        x = self.solve(df, train=False)
        return self.model.predict(x)
