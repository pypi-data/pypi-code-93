# import spacy
# @spacy.registry.tokenizers("whitespace_tokenizer")def create_whitespace_tokenizer():
#     def create_tokenizer(nlp):
#         return WhitespaceTokenizer(nlp.vocab)
#
#     return create_tokenizer