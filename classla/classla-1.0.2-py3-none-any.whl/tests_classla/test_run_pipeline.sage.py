import os
import re
from datetime import datetime

import pytest
import classla
from classla import Document
from classla.models.common.conll import CoNLLFile
from tests_classla import *

DOWNLOAD_TEST_DIR = f'{TEST_WORKING_DIR}/download'

RUN_PIPELINE_TEST_MODELS = [SL_SHORTHAND, SL_JOS_SHORTHAND, SL_NS_SHORTHAND]

def test_all_treebanks():
    for lang_treebanks in RUN_PIPELINE_TEST_MODELS:
        run_pipeline_for_lang(lang_treebanks)


def run_pipeline_for_lang(lang_treebanks):
    input_file = f'{TEST_WORKING_DIR}/in/{lang_treebanks}.test.txt'
    output_file = f'{TEST_WORKING_DIR}/out/{lang_treebanks}.test.txt.out'
    gold_output_file = f'{TEST_WORKING_DIR}/out/{lang_treebanks}.test.txt.out.gold'
    models_download_dir = f'{DOWNLOAD_TEST_DIR}/{lang_treebanks}_models'

    assert os.path.exists(input_file), f'Missing test input file: {input_file}'

    safe_rm(output_file)
    safe_rm(models_download_dir)

    classla.download(lang_treebanks)

    nlp = classla.Pipeline(treebank=lang_treebanks, tokenize_pretokenized=True, models_dir=DOWNLOAD_TEST_DIR)

    # Because we already have CoNLL-U formated input, we need to skip the tokenization step.
    # This is currently done by setting the Documents text parameter as None. After that we also
    # have to manually create a CoNLLFile instance and append it to the Document.
    doc = Document(text=None)
    conll_file = CoNLLFile(filename=input_file)
    doc.conll_file = conll_file

    # Start processing.
    res = nlp(doc)

    # Save result to output CoNLL-U file.
    res.conll_file.write_conll(output_file)

    if os.path.exists(output_file):
        curr_timestamp = re.sub(' ', '-', str(datetime.now()))
        os.rename(output_file, f'{output_file}-{curr_timestamp}')

    safe_rm(models_download_dir)
    assert open(gold_output_file).read() == open(f'{output_file}-{curr_timestamp}').read(), \
        f'Test failure: output does not match gold'
