"""Dataset manipulation scripts."""

import json
import logging
import os
import pickle
import shutil
import sys
import warnings
from copy import deepcopy
from glob import glob
from typing import List
from urllib.error import HTTPError
from urllib.request import urlretrieve

import click
import pandas as pd
import torch
from tqdm import tqdm  # type: ignore
from transformers import MarianMTModel, MarianTokenizer  # type: ignore

import stanza  # type: ignore

logger = logging.getLogger(__name__)

FEATURE_TEXT = "text_raw"
FEATURE_STANZA = "stanza"
FEATURE_CONSTITUENTS = "constituencies"
LANGUAGE_COLUMN = "language"
DATASET_CSV = "dataset.csv"
HF_URL = "https://s3.amazonaws.com/models.huggingface.co/bert/Helsinki-NLP"
FILES = [
    "config.json",
    "pytorch_model.bin",
    "source.spm",
    "target.spm",
    "tokenizer_config.json",
    "vocab.json",
]
MODEL_DIR = "translation_data"


@click.command(
    help="transforms corpora created with the reddit script to the dataframe format."
)
@click.argument("input_directory")
def reddit_to_common(input_directory: str) -> None:
    """
    Transform corpora created with reddit scripts into dataframe format.

    This script is meant to be called via CLI. It will read a directory that
    contains a nested directory structure and produces a common dataset format
    using DataFrames. The result is a meta-information file called dataset.csv
    and a directory 'text_raw' which contains the raw text files.

    Args:
        input_directory: The directory that contains the topmost target
            directories (often, authors).

    Returns: Nothing.

    """
    records = []

    text_directory = os.path.join(input_directory, FEATURE_TEXT)
    if not os.path.isdir(text_directory):
        os.makedirs(text_directory)

    old_directory = os.path.join(input_directory, "old")
    if not os.path.isdir(old_directory):
        os.makedirs(old_directory)

    meta_file = os.path.join(input_directory, DATASET_CSV)

    authors = sorted(os.listdir(input_directory))
    for author in tqdm(authors):

        # don't process these "authors" that might be existing from previous
        # calls to this script:
        if author in [os.path.basename(text_directory), os.path.basename(meta_file)]:
            continue

        author_dir = os.path.join(input_directory, author)
        if not os.path.isdir(author_dir):
            logger.warning("not an author directory: %s", author_dir)
            continue
        languages = os.listdir(author_dir)
        for language in languages:
            language_dir = os.path.join(author_dir, language)
            if not os.path.isdir(language_dir):
                logger.warning("not a language directory: %s", language_dir)
                continue
            json_files = glob(language_dir + "/*.json")
            for json_file in json_files:
                name_ext = os.path.basename(json_file)
                name = os.path.splitext(name_ext)[0]
                text_name = f"{author}_{language}_{name}.txt"
                text_file = os.path.join(FEATURE_TEXT, text_name)
                full_text_file = os.path.join(input_directory, text_file)
                with open(json_file) as i_f, open(full_text_file, "w") as o_f:
                    js = json.load(i_f)
                    o_f.write(js["body_clean"])
                    del js["body"]
                    del js["body_clean"]
                    js[FEATURE_TEXT] = text_file
                    js["group_field"] = language  # important for deepl_...
                    records.append(js)

        # move old author dir
        shutil.move(author_dir, old_directory)

    df = pd.DataFrame.from_records(records)
    df.to_csv(meta_file, index=False)


@click.command(help="Reads dataset.csv + column name to produce stanza dir")
@click.argument("input-directory")
@click.option("-t", "--text-column-name", default=FEATURE_TEXT)
@click.option("-l", "--language-column-name", default=LANGUAGE_COLUMN)
@click.option("-o", "--overwrite", default=False)
@click.option("-out", "--output-column-name", default=FEATURE_STANZA)
def parse_dependency(
    input_directory: str,
    text_column_name: str,
    language_column_name: str,
    overwrite: bool,
    output_column_name: str,
) -> None:
    """
    Parse text files using the stanza parser.

    Args:
        input_directory: Directory containing the dataset.csv file, and a
            directory named <text_column_name>
        text_column_name: name of the column containing the raw text data.
            defaults to 'text_raw'.
        language_column_name:  name of the column where the language is saved.
            defaults to 'language'.
        overwrite: whether to re-parse existing files. If this is not set, this
            script will leave already parsed files untouched and won't parse
            the appropriate inputs.
        output_column_name: name of the output column in the meta-data file.
            defaults to 'stanza'.

    Returns: Nothing, this is a cli script.

    """
    warnings.simplefilter("ignore")  # stanza is very 'loud'.
    main_dataset_file = os.path.join(input_directory, DATASET_CSV)
    df = pd.read_csv(main_dataset_file)

    # check output directory
    out_dir = os.path.join(input_directory, output_column_name)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    df[output_column_name] = [
        os.path.join(
            output_column_name, os.path.splitext(os.path.basename(f))[0] + ".pckl"
        )
        for f in df[text_column_name]
    ]

    def should_write(f: str) -> bool:
        if overwrite:
            return True
        if os.path.isfile(f):
            return os.path.getsize(f) == 0
        else:
            return True

    tuples = [
        (in_file, out_file, language)
        for (in_file, out_file, language) in zip(
            df[text_column_name], df[output_column_name], df[language_column_name]
        )
        if should_write(os.path.join(input_directory, out_file))
    ]
    if not tuples:
        logger.warning("no files remaining, skipping calculation")
        return

    parsers = {}
    for in_file, out_file, language in tqdm(tuples):
        if language.endswith("_to_en"):
            language = "en"
        if language not in parsers:
            parsers[language] = stanza.Pipeline(lang=language, use_gpu=False)
        parser = parsers[language]

        full_path = os.path.join(input_directory, in_file)
        with open(full_path) as in_fh:
            content = in_fh.read()
            try:
                parsed = parser(content)
            except RuntimeError as e:
                logger.error("error on parsing", full_path)
                logger.error(content)
                raise e
            with open(os.path.join(input_directory, out_file), "wb") as out_fh:
                pickle.dump(parsed, out_fh)
    logger.info("writing %s", main_dataset_file)
    df.to_csv(main_dataset_file, index=False)


@click.command(help="reads dataset.csv, produces constituencies directory")
@click.argument("input-directory")
@click.option("-t", "--text-column-name", default=FEATURE_TEXT)
@click.option("-l", "--language-column-name", default=LANGUAGE_COLUMN)
def parse_constituency(
        input_directory: str,
        text_column_name: str,
        language_column_name: str
) -> None:
    """
    Ignore this method for the time being.

    This is no longer working unless the common file transformers are replaced.
    """
    print(input_directory, text_column_name, language_column_name)
    pass
    # meta = os.path.join(input_directory, DATASET_CSV)
    #
    # df = pd.read_csv(meta)
    #
    # out_dir = os.path.join(input_directory, FEATURE_CONSTITUENTS)
    # if not os.path.isdir(out_dir):
    #     os.makedirs(out_dir)
    #
    # sub_dfs = {}
    #
    # columns = [text_column_name, language_column_name]
    # for language, sub_df in df[columns].groupby(language_column_name):
    #     logger.info('parsing %s', language)
    #
    #     infiles = list(sub_df[text_column_name].values)
    #     # the path to the text file points to a subfolder
    #     outfiles = PathTransformer('../' + FEATURE_CONSTITUENTS,
    #                                '.json').transform(infiles)
    #     pairs = [(i_f, o_f) for (i_f, o_f) in zip(infiles, outfiles)
    #              if not os.path.isfile(o_f)]
    #     if not pairs:
    #         logger.warning('no files remaining, skipping calculation')
    #         return
    #
    #     input_filenames, output_filenames = list(zip(*pairs))
    #
    #
    #
    #     make_pipeline(
    #         FileReader(),
    #         CoreNLPTreeTransformer(
    #             language=language,
    #             port=CORENLP_PORT,
    #             model_dir=CORENLP_MODELS,
    #             properties_dir=CORENLP_PROPERTIES),
    #         FileWriter(output_filenames, writemode='json'),
    #     ).transform(input_filenames)
    #
    #     sub_df[FEATURE_CONSTITUENTS] = output_filenames
    #     sub_dfs[language] = sub_df
    #
    # pd.concat(sub_dfs, axis=0).to_csv(DATASET_CSV + '2', index=False)


class Translator:
    """Simple translator wrapper for Hugging Face models."""

    def __init__(
        self,
        source_language: str,
        target_language: str,
        model_dir: str = "translation_models",
        force_download: bool = False,
    ):
        """
        Initialize the translator.

        Args:
            source_language: two-letter code for the source language
            target_language: two-letter code for the target language
            model_dir: directory where to store the cached translation models
            force_download: if true, overwrite existing cached models
        """
        self.source_language = source_language
        self.target_language = target_language
        self.model_dir = model_dir
        self.force_download = force_download

        self.model_name = f"opus-mt-{self.source_language}-" f"{self.target_language}"
        self.model_dir = os.path.join(self.model_dir, self.model_name)

        if not os.path.isdir(self.model_dir) or self.force_download:
            self._download_language_model()

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info("running on device: %s", self.device)

        self.model = MarianMTModel.from_pretrained(self.model_dir).to(
            torch.device(self.device)
        )
        self.tokenizer = MarianTokenizer.from_pretrained(self.model_dir)

    def _download_language_model(self) -> None:
        if os.path.isdir(self.model_dir):
            shutil.rmtree(self.model_dir)
        os.makedirs(self.model_dir)
        for f in FILES:
            file_url = os.path.join(HF_URL, self.model_name, f)
            file_path = os.path.join(self.model_dir, f)
            try:
                logger.info("downloading %s", file_url)
                urlretrieve(file_url, file_path)
            except HTTPError as e:
                logger.error(
                    "Error retrieving model from url."
                    "Please confirm model exists: %s",
                    e,
                )
                sys.exit(1)

    def translate(self, sentences: List[str]) -> List[str]:
        """
        Translate sentences for source to target language.

        Args:
            sentences: list of strings to translate. Each sentence will be
                translated separately for memory reasons.

        Returns: list of translated sentences.

        """
        result = []
        for sentence in tqdm(sentences, leave=False):
            batch = self.tokenizer.prepare_seq2seq_batch(
                src_texts=[sentence], return_tensors="pt"
            )
            translated = self.model.generate(**batch.to(self.device))
            result += self.tokenizer.batch_decode(translated, skip_special_tokens=True)
        return result


@click.command(help="translates data")
@click.argument("input-dir")
@click.argument("source")
@click.argument("target")
def translate(
        input_dir: str,
        source: str,
        target: str,
) -> None:
    """
    Translate common datafrarme corpora.

    The corpora that is to be translated should already contain the 'stanza'
    column of parsed sentences, as this will have better sentence segmentation.

    Args:
        input_dir: directory containing the dataset.csv file.
        source: two-letter source language code
        target: two-letter target language code

    Returns: Nothing, this is a CLI script.

    """
    key = f"marianmt_{source}_to_{target}"
    df = pd.read_csv(os.path.join(input_dir, "dataset.csv"))
    df = df.drop(columns=[c for c in df.columns if c.startswith("Unnamed: 0")])
    sub_df = df[df["language"] == source]

    logger.info("loading translation model")
    translator = Translator(source, target)

    new_rows = []

    for index, row in tqdm(sub_df.iterrows(), total=sub_df.shape[0]):
        new_row = deepcopy(row)
        old_path = os.path.join(input_dir, row["stanza"])
        old_name = os.path.splitext(os.path.basename(old_path))[0]
        new_name = old_name + "__" + key
        new_path_part = os.path.join("text_raw", new_name + ".txt")
        new_path = os.path.join(input_dir, new_path_part)
        new_row["text_raw"] = new_path_part
        new_row["stanza"] = None
        new_row["language"] = key

        new_dir = os.path.dirname(new_path)
        if not os.path.isdir(new_dir):
            os.makedirs(new_dir)

        # sometimes, empty files are created when interrupting a process
        if os.path.isfile(new_path) and os.stat(new_path).st_size == 0:
            os.unlink(new_path)

        # don't re-compute stuff we already have
        if os.path.isfile(new_path):
            continue

        with open(old_path, "rb") as i_f, open(new_path, "w") as o_f:
            document = pickle.load(i_f)
            sentences = [sentence.text for sentence in document.sentences]
            translations = translator.translate(sentences)
            o_f.write("\n".join(translations))

        new_rows.append(new_row)

    df2 = pd.DataFrame.from_records(new_rows)
    df3 = pd.concat([df, df2])
    df3.to_csv(os.path.join(input_dir, "dataset.csv"), index=False)
