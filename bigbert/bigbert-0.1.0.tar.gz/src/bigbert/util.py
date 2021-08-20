import gdown
import torch, re
import numpy as np
from flair.data import Sentence
from pathlib import Path
from symspellpy.symspellpy import SymSpell, Verbosity
from tqdm import tqdm


DATA_DIR = Path(__file__).resolve().parent.joinpath("data")


def bert_embed_sentence(sent, embeddings):
    # create a sentence
    sentence = Sentence(sent)
    # embed the sentence
    embeddings.embed(sentence)
    return sentence.get_embedding().cpu().detach().numpy()


def get_bert_embeddings(df, bert, desc):
    # Swap to GPU if it's available
    if torch.cuda.is_available():
        bert.cuda()

    tqdm.pandas(desc=desc)
    df['description'] = df['description'].progress_apply(lambda x: re.sub(r'[^A-Za-z0-9 ]+', '', x).lower())
    df['bert_vector'] = df['description'].progress_apply(lambda x: bert_embed_sentence(str(x), bert))

    return df


def pre_proc_url(url, embeddings_dict, segmenter, spellchecker):
    tokens = []
    for token in re.split(r'[.-\/-]', url):
        if token not in ['http', 'https', 'www', 'com', 'net']:
            if len(token) > 4:
                segments = segmenter.word_segmentation(token).corrected_string.split()
            else:
                segments = [token]
            for s in segments:
                if s in embeddings_dict:
                    tokens.append(s)
                else:
                    suggestions = spellchecker.lookup(s, Verbosity.CLOSEST, max_edit_distance=1)
                    if len(suggestions) > 0:
                        tokens.append(suggestions[0].term)
    return tokens


def setup_symspell():
    dictionary_path = Path(DATA_DIR).joinpath("frequency_dictionary_en_82_765.txt")
    sym_spell = SymSpell(max_dictionary_edit_distance=0, prefix_length=7)
    sym_spell.load_dictionary(str(dictionary_path), term_index=0, count_index=1)

    # SymSpell for spellchecking
    sym_spell1 = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
    sym_spell1.load_dictionary(str(dictionary_path), term_index=0, count_index=1)

    return sym_spell, sym_spell1


def setup_embeddings(embedding="edu2vec"):
    embeddings = {
        "edu2vec": str(Path(DATA_DIR).joinpath("edu2Vec.txt"))
    }

    if not Path(embeddings[embedding]).exists():
        edu2vec_pub_storage = "https://drive.google.com/uc?id=1pPIA8TBpJ41vjQ2WAwcZh212GMAhiu_i"
        gdown.download(edu2vec_pub_storage, embeddings[embedding], quiet=False)

    embeddings_dict = {}
    embedding_file = embeddings[embedding]
    with open(embedding_file, 'r', encoding="utf8") as f:
        for line in tqdm(f, desc="Generating embedding dictionary", unit='B', unit_scale=True, unit_divisor=1024):
            values = line.split()
            word = values[0]
            vector = np.asarray(values[1:], "float32")  # Shape of (300,)
            embeddings_dict[word] = vector

    return embeddings_dict
