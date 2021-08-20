from .load_model import load_bigru, load_bert_with_edu, load_bigbert
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import StratifiedKFold
from .util import *


class BiGBERT(object):
    def __init__(self):
        sym_spell, sym_spell1 = setup_symspell()
        self.embeddings_dict = setup_embeddings()
        self.word_segmenter = sym_spell
        self.spellchecker = sym_spell1
        self._bigru = load_bigru()
        self._bert_with_edu = load_bert_with_edu()
        self._bigbert = load_bigbert()

    def _preprocess_url(self, url):
        tokens = []
        for token in re.split(r'[.-\/-]', url):
            if token not in ['http', 'https', 'www', 'com', 'net']:
                if len(token) > 4:
                    segments = self.word_segmenter.word_segmentation(token).corrected_string.split()
                else:
                    segments = [token]
                for s in segments:
                    if s in self.embeddings_dict:
                        tokens.append(s)
                    else:
                        suggestions = self.spellchecker.lookup(s, Verbosity.CLOSEST, max_edit_distance=1)
                        if len(suggestions) > 0:
                            tokens.append(suggestions[0].term)
        return tokens

    def _data_prep(self, df, y=None):
        # Preprocessing
        df['tokens_new'] = df['url'].apply(lambda x: self._preprocess_url(x))
        df['text'] = df.apply(lambda x: ' '.join(x['tokens_new']), axis=1)
        texts = df['text'].values
        tokenizer = Tokenizer()
        tokenizer.fit_on_texts(texts)
        sequences = tokenizer.texts_to_sequences(texts)
        data = pad_sequences(sequences, maxlen=10, padding="post", truncating="post")
        df['url_sequences'] = data.tolist()
        if y is not None:
            df['target'] = y

        return df

    def fit(self, x, y, folds=5, **kwargs):
        epochs = kwargs.get("epochs", 50)
        batch_size = kwargs.get("batch_size", 128)
        df = self._data_prep(x, y)
        df = get_bert_embeddings(df, self._bert_with_edu, desc="BERT Vectors (fit)")

        df = df.sample(frac=1, random_state=0)
        skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)

        for train_index, test_index in skf.split(df, df['target']):
            # Set up pandas dataframes for train/test
            train = df.iloc[train_index]
            test = df.iloc[test_index]

            # Get training data
            x_train = np.array(train['url_sequences'].to_list())
            y_train = to_categorical(np.asarray(train['target'].values))
            x_val = np.array(test['url_sequences'].to_list())
            y_val = to_categorical(np.asarray(test['target'].values))

            # Get the biG URL vectors for our train and test
            big_train = self._bigru.predict(x_train)
            big_test = self._bigru.predict(x_val)

            # Get BERT vectors
            bert_train = np.array(train['bert_vector'].to_list())
            bert_test = np.array(test['bert_vector'].to_list())

            fit_input_x = [big_train, bert_train]
            fit_input_val = [big_test, bert_test]

            self._bigbert.fit(x=fit_input_x, y=y_train, validation_data=(fit_input_val, y_val),
                              epochs=epochs, batch_size=batch_size)

    def evaluate(self, x, y, score_fn):
        """
        Alias for `score()`
        :param kwargs:
        :return:
        """
        return self.score(x, y, score_fn)

    def predict(self, x):
        df = self._data_prep(x)
        df = get_bert_embeddings(df, self._bert_with_edu, desc="BERT Vectors (predict)")

        url_seq = np.array(df['url_sequences'].to_list())

        big_vec = self._bigru.predict(url_seq)
        bert_vec = np.array(df['bert_vector'].to_list())

        return self._bigbert.predict([big_vec, bert_vec])

    def score(self, x, y, score_fn):
        df = self._data_prep(x, y)
        df = get_bert_embeddings(df, self._bert_with_edu, desc="BERT Vectors (score)")
        url_seq = np.array(df["url_sequences"].to_list())
        features = [self._bigru.predict(url_seq), np.array(df["bert_vector"].to_list())]
        y_pred = self._bigbert.predict(features)
        y_cat = to_categorical(np.asarray(df['target'].values))
        y_true = y_cat[:, 1]
        return score_fn(y_true, np.argmax(y_pred, axis=1))
