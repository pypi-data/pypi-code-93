# Encoders which should always work
from jaison.encoder.base import BaseEncoder
from jaison.encoder.datetime.datetime import DatetimeEncoder
from jaison.encoder.image.img_2_vec import Img2VecEncoder
from jaison.encoder.numeric.numeric import NumericEncoder
from jaison.encoder.numeric.ts_numeric import TsNumericEncoder
from jaison.encoder.numeric.ts_array_numeric import TsArrayNumericEncoder
from jaison.encoder.text.short import ShortTextEncoder
from jaison.encoder.text.vocab import VocabularyEncoder
from jaison.encoder.text.rnn import RnnEncoder as TextRnnEncoder
from jaison.encoder.categorical.onehot import OneHotEncoder
from jaison.encoder.categorical.binary import BinaryEncoder
from jaison.encoder.categorical.autoencoder import CategoricalAutoEncoder
from jaison.encoder.time_series.rnn import TimeSeriesEncoder
from jaison.encoder.time_series.plain import TimeSeriesPlainEncoder
from jaison.encoder.categorical.multihot import MultiHotEncoder
from jaison.encoder.text.pretrained import PretrainedLangEncoder
from jaison.encoder.type_encoder_maps import (Array, Binary, Categorical, Date, Datetime, Float, Image, Integer,
                                              Quantity, Rich_Text, Short_Text, Tags)


# Encoders that depend on optiona dependencies
try:
    from jaison.encoder.audio.amplitude_ts import AmplitudeTsEncoder
except Exception:
    AmplitudeTsEncoder = None


__ts_encoders__ = [TsNumericEncoder, TimeSeriesEncoder, TimeSeriesPlainEncoder]
__all__ = ['BaseEncoder', 'DatetimeEncoder', 'Img2VecEncoder', 'NumericEncoder', 'TsNumericEncoder',
           'TsArrayNumericEncoder', 'ShortTextEncoder', 'VocabularyEncoder', 'TextRnnEncoder', 'OneHotEncoder',
           'CategoricalAutoEncoder', 'TimeSeriesEncoder', 'TimeSeriesPlainEncoder', 'MultiHotEncoder',
           'PretrainedLangEncoder', 'AmplitudeTsEncoder', 'BinaryEncoder', 'Array', 'Binary', 'Categorical', 'Date',
           'Datetime', 'Float', 'Image', 'Integer', 'Quantity', 'Rich_Text', 'Short_Text', 'Tags']
