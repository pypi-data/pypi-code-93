import gdown
import pickle
import tensorflow as tf
from pathlib import Path
from keras.models import load_model
from keras_self_attention import SeqSelfAttention  # pip install keras-self-attention==0.42.0


MODELS_DIR = Path(__file__).resolve().parent.joinpath("models")


def load_bigru():
    bigru_path = Path(MODELS_DIR).joinpath("bigru.h5")
    new_model = load_model(bigru_path, custom_objects={"SeqSelfAttention": SeqSelfAttention})
    optimizer = tf.keras.optimizers.RMSprop(learning_rate=0.001, momentum=0.2)
    new_model.compile(loss='binary_crossentropy',
                      optimizer=optimizer,
                      metrics=['accuracy'])
    return new_model


def load_bert_with_edu():
    bertedu_path = Path(MODELS_DIR).joinpath("bertedu_1e-6lr.p")
    if not bertedu_path.exists():
        bertedu_pub_storage = "https://drive.google.com/uc?id=116pGILUWd9m4QFCbWJnlP8UdVBtCGVny"
        gdown.download(bertedu_pub_storage, str(bertedu_path), quiet=False)

    return pickle.load(open(bertedu_path, "rb"))


def load_bigbert():
    bigbert_path = Path(MODELS_DIR).joinpath("bigbert.h5")
    built_model = load_model(bigbert_path)
    optimizer = tf.keras.optimizers.RMSprop(learning_rate=0.001, momentum=0.2)
    built_model.compile(loss='binary_crossentropy',
                        optimizer=optimizer,
                        metrics=['accuracy'])
    return built_model
