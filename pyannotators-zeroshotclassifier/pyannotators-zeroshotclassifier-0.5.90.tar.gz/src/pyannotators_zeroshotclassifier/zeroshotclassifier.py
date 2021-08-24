import os
import re
from enum import Enum
from functools import lru_cache
from typing import Type, List, cast, Optional

import icu as icu
from pydantic import BaseModel, Field
from pymultirole_plugins.v1.annotator import AnnotatorParameters, AnnotatorBase
from pymultirole_plugins.v1.schema import Document, Category, Sentence
from transformers import pipeline, ZeroShotClassificationPipeline

_home = os.path.expanduser('~')
xdg_cache_home = os.environ.get('XDG_CACHE_HOME') or os.path.join(_home, '.cache')


class TrfModel(str, Enum):
    distilbert_base_uncased_mnli = 'typeform/distilbert-base-uncased-mnli'
    camembert_base_xnli = 'BaptisteDoyen/camembert-base-xnli'


class ProcessingUnit(str, Enum):
    document = 'document'
    segment = 'segment'


class ZeroShotClassifierParameters(AnnotatorParameters):
    model: TrfModel = Field(TrfModel.distilbert_base_uncased_mnli,
                            description="""Which [Transformers model)(
                            https://huggingface.co/models?pipeline_tag=zero-shot-classification) fine-tuned
                            for Zero-shot classification to use, can be one of:<br/>
                            <li>`typeform/distilbert-base-uncased-mnli`: This is the uncased DistilBERT model
                            fine-tuned on Multi-Genre Natural Language Inference (MNLI) dataset for the
                            zero-shot classification task. The model is not case-sensitive, i.e., it does not
                            make a difference between "english" and "English".
                            <li>`BaptisteDoyen/camembert-base-xnli`: Camembert-base model fine-tuned on french
                            part of XNLI dataset.""")
    processing_unit: ProcessingUnit = Field(ProcessingUnit.document,
                                            description="""The processing unit to apply the classification in the input
                                            documents, can be one of:<br/>
                                            <li>`document`
                                            <li>`segment`""")
    candidate_labels: List[str] = Field([],
                                        description="The set of possible class labels to classify each sequence into. "
                                                    "For example `[\"sport\",\"politics\",\"science\"]`")
    multi_label: bool = Field(False, description="Whether or not multiple candidate labels can be true.")
    multi_label_threshold: float = Field(0.5,
                                         description="If multi-label you can set the threshold to make predictions.")
    hypothesis_template: Optional[str] = Field(None,
                                               description="""The template used to turn each label into an NLI-style
                                               hypothesis. This template must include a {} for the
                                               candidate label to be inserted into the template. For
                                               example, the default template in english is
                                               `\"This example is {}.\"`""")


class ZeroShotClassifierAnnotator(AnnotatorBase):
    """[🤗 Transformers](https://huggingface.co/transformers/index.html) Zero-shot classifier.
    """

    # cache_dir = os.path.join(xdg_cache_home, 'trankit')

    def annotate(self, documents: List[Document], parameters: AnnotatorParameters) \
            -> List[Document]:
        params: ZeroShotClassifierParameters = \
            cast(ZeroShotClassifierParameters, parameters)
        if params.hypothesis_template is None:
            if params.model == TrfModel.distilbert_base_uncased_mnli:
                params.hypothesis_template = "This example is {}."
            elif params.model == TrfModel.camembert_base_xnli:
                params.hypothesis_template = "Ce texte parle de {}."
        # Create cached pipeline context with model
        p: ZeroShotClassificationPipeline = get_pipeline(params.model)

        for document in documents:
            if params.processing_unit == ProcessingUnit.document:
                result = p(document.text, params.candidate_labels, hypothesis_template=params.hypothesis_template)
                document.categories = compute_categories(result, params.multi_label_threshold, params.multi_label)
            elif params.processing_unit == ProcessingUnit.segment:
                if not document.sentences:
                    document.sentences = [Sentence(start=0, end=len(document.text))]
                stexts = [document.text[s.start:s.end] for s in document.sentences]
                results = p(stexts, params.candidate_labels, hypothesis_template=params.hypothesis_template)
                for sent, result in zip(document.sentences, results):
                    sent.categories = compute_categories(result, params.multi_label_threshold, params.multi_label)
        return documents

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return ZeroShotClassifierParameters


def compute_categories(result: dict, multi_label_threshold, multi_label=False) -> List[Category]:
    cats: List[Category] = []
    for label, score in zip(result['labels'], result['scores']):
        if score > multi_label_threshold:
            cats.append(Category(label=label, labelName=sanitize_label(label), score=score))
            if not multi_label:
                break
    return cats


@lru_cache(maxsize=None)
def get_pipeline(model):
    p = pipeline("zero-shot-classification", model=model.value)
    return p


nonAlphanum = re.compile(r'[\W]+', flags=re.ASCII)
underscores = re.compile("_{2,}", flags=re.ASCII)
trailingAndLeadingUnderscores = re.compile(r"^_+|_+\$", flags=re.ASCII)
# see http://userguide.icu-project.org/transforms/general
transliterator = icu.Transliterator.createInstance(
    "Any-Latin; NFD; [:Nonspacing Mark:] Remove; NFC; Latin-ASCII; Lower;", icu.UTransDirection.FORWARD)


def sanitize_label(string):
    result = transliterator.transliterate(string)
    result = re.sub(nonAlphanum, "_", result)
    result = re.sub(underscores, "_", result)
    result = re.sub(trailingAndLeadingUnderscores, "", result)
    return result
