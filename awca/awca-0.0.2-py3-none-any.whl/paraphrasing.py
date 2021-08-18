import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


def get_p_model():
    model = AutoModelForSeq2SeqLM.from_pretrained('Vamsi/T5_Paraphrase_Paws')
    return model

def get_p_tokenizer():
    tokenizer = AutoTokenizer.from_pretrained('Vamsi/T5_Paraphrase_Paws')
    return tokenizer

p_tokenizer = get_p_tokenizer()
p_model = get_p_model()


def paraphrase(texts):
    texts1 = texts.split("\n")
    #texts1 = [texts[n * 512 : (n + 1) * 512] for n in range(len(texts) // 512)]
    lines = ""
    for texts2 in texts1:
        
        texts2 =  "paraphrase: " + texts2

        encoding = p_tokenizer.encode_plus(texts2,padding='max_length', return_tensors="pt")
        input_ids, attention_masks = encoding["input_ids"], encoding["attention_mask"]

        outputs = p_model.generate(
            input_ids=input_ids, attention_mask=attention_masks,
            max_length=10000,
            do_sample=True,
            top_k=120,
            top_p=0.95,
            early_stopping=True,
            num_return_sequences=1
        )
    
        line = p_tokenizer.decode(outputs[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
        line += "\n\n"
        lines += line
    return lines
