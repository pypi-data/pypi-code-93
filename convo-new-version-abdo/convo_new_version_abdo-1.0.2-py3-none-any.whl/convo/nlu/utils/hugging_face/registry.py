import logging

# Explicitly set logging level for this module before any import
# because otherwise it logs tensorflow/pytorch versions
logging.getLogger("transformers.file_utils").setLevel(logging.WARNING)

from transformers import (
    TFBertModel,
    TFOpenAIGPTModel,
    TFGPT2Model,
    TFXLNetModel,
    # TFXLMModel,
    TFDistilBertModel,
    TFRobertaModel,
    BertTokenizer,
    OpenAIGPTTokenizer,
    GPT2Tokenizer,
    XLNetTokenizer,
    # XLMTokenizer,
    DistilBertTokenizer,
    RobertaTokenizer,
)
from convo.nlu.utils.hugging_face.transformers_pre_post_processors import (
    bert_tkns_pre_processor,
    gpt_tkns_pre_processor,
    xlnet_tokens_pre_processor,
    roberta_tkns_preprocessor,
    post_processor_bert_embedding,
    post_processor_gpt_embedding,
    post_processor_xlnet_embedding,
    post_processor_roberta_embedding,
    bert_tkns_cleaner,
    openaigpt_tkns_cleaner,
    gpt2_tkns_cleaner,
    xlnet_tkns_cleaner,
)


model_class_dictionary = {
    "bert": TFBertModel,
    "gpt": TFOpenAIGPTModel,
    "gpt2": TFGPT2Model,
    "xlnet": TFXLNetModel,
    # "xlm": TFXLMModel, # Currently doesn't work because of a bug in transformers library https://github.com/huggingface/transformers/issues/2729
    "distilbert": TFDistilBertModel,
    "roberta": TFRobertaModel,
}
model_tokenizer_dictionary = {
    "bert": BertTokenizer,
    "gpt": OpenAIGPTTokenizer,
    "gpt2": GPT2Tokenizer,
    "xlnet": XLNetTokenizer,
    # "xlm": XLMTokenizer,
    "distilbert": DistilBertTokenizer,
    "roberta": RobertaTokenizer,
}
model_wt_defaults = {
    "bert": "bert-base-uncased",
    "gpt": "openai-gpt",
    "gpt2": "gpt2",
    "xlnet": "xlnet-base-cased",
    # "xlm": "xlm-mlm-enfr-1024",
    "distilbert": "distilbert-base-uncased",
    "roberta": "roberta-base",
}

model_special_tkns_pre_processors = {
    "bert": bert_tkns_pre_processor,
    "gpt": gpt_tkns_pre_processor,
    "gpt2": gpt_tkns_pre_processor,
    "xlnet": xlnet_tokens_pre_processor,
    # "xlm": xlm_tkns_preprocessor,
    "distilbert": bert_tkns_pre_processor,
    "roberta": roberta_tkns_preprocessor,
}

model_tkns_cleaner = {
    "bert": bert_tkns_cleaner,
    "gpt": openaigpt_tkns_cleaner,
    "gpt2": gpt2_tkns_cleaner,
    "xlnet": xlnet_tkns_cleaner,
    # "xlm": xlm_tkns_preprocessor,
    "distilbert": bert_tkns_cleaner,  # uses the same as BERT
    "roberta": gpt2_tkns_cleaner,  # Uses the same as GPT2
}

model_embeded_postprocessors = {
    "bert": post_processor_bert_embedding,
    "gpt": post_processor_gpt_embedding,
    "gpt2": post_processor_gpt_embedding,
    "xlnet": post_processor_xlnet_embedding,
    # "xlm": post_processor_xlm_embedding,
    "distilbert": post_processor_bert_embedding,
    "roberta": post_processor_roberta_embedding,
}
