import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration, T5Config

def get_sum_model():
    model = T5ForConditionalGeneration.from_pretrained('t5-small')
    return model

def get_sum_tokenizer():
    tokenizer = T5Tokenizer.from_pretrained('t5-small')
    return tokenizer

tokenizer = get_sum_tokenizer()
model = get_sum_model()

def preprocess(texts):
    preprocess_texts = texts.strip().replace("\n", "")
    texts1 = [preprocess_texts[n*512: (n+1)*512] for n in range(len(preprocess_texts) // 512)]
    tokens=[]
    for text in texts1:
        t5_prepared_Text = "summarize: "+ text
        #print ("original text preprocessed: \n", text)
        tokenized_text = tokenizer.encode(t5_prepared_Text, return_tensors="pt")
        tokens.append(tokenized_text)
    return tokens

def get_summarization(tokenized_texts, min_length=10, max_length=45):
    outputs = ""
    for text in tokenized_texts:
        summary_ids = model.generate(text,
                                    num_beams=4,
                                    no_repeat_ngram_size=2,
                                    min_length=min_length,
                                    max_length=max_length,
                                    early_stopping=True)
        output = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        outputs += output
    return outputs

def summarize(texts, min_length=10, max_length=45):
    tokenized = preprocess(texts)
    return get_summarization(tokenized, min_length, max_length)