from typing import List

import torch
import pandas as pd
from scipy.special import softmax
from sklearn.linear_model import LinearRegression

from jaison.helpers.log import log
from jaison.api.dtype import dtype
from jaison.model import BaseModel
from jaison.encoder.base import BaseEncoder
from jaison.data.encoded_ds import ConcatedEncodedDs, EncodedDs


class Regression(BaseModel):
    model: LinearRegression
    label_map: dict
    supports_proba: bool

    def __init__(self, stop_after: int, target_encoder: BaseEncoder, dtype_dict: dict, target: str):
        super().__init__(stop_after)
        self.target_encoder = target_encoder
        self.target_dtype = dtype_dict[target]
        self.supports_proba = self.target_dtype in [dtype.binary, dtype.categorical]
        self.label_map = {}
        self.stable = False

    def fit(self, ds_arr: List[EncodedDs]) -> None:
        if self.target_dtype not in (dtype.float, dtype.integer):
            raise Exception(f'Unspported {self.target_dtype} type for regression')
        log.info('Fitting Linear Regression model')
        X = []
        Y = []
        for x, y in ConcatedEncodedDs(ds_arr):
            X.append(x.tolist())
            Y.append(y.tolist())

        if self.supports_proba:
            self.label_map = self.target_encoder.rev_map

        self.model = LinearRegression().fit(X, Y)
        log.info(f'Regression based correlation of: {self.model.score(X, Y)}')

    def partial_fit(self, train_data: List[EncodedDs], dev_data: List[EncodedDs]) -> None:
        self.fit(train_data + dev_data)

    def __call__(self, ds: EncodedDs, predict_proba: bool = False) -> pd.DataFrame:
        X = []
        for x, _ in ds:
            X.append(x.tolist())

        Yh = self.model.predict(X)

        decoded_predictions = self.target_encoder.decode(torch.Tensor(Yh))

        ydf = pd.DataFrame({'prediction': decoded_predictions})

        if predict_proba and self.label_map:
            raw_predictions = softmax(Yh.squeeze(), axis=1)
            for idx, label in enumerate(self.target_encoder.rev_map.values()):
                ydf[f'__mdb_proba_{label}'] = raw_predictions[:, idx]

        return ydf
