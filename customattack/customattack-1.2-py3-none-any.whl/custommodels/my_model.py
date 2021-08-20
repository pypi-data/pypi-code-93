import transformers
from customattack.models.wrappers import HuggingFaceModelWrapper

model = transformers.AutoModelForSequenceClassification.from_pretrained("textattack/bert-base-uncased-ag-news")
tokenizer = transformers.AutoTokenizer.from_pretrained("textattack/bert-base-uncased-ag-news")

model_wrapper = HuggingFaceModelWrapper(model, tokenizer)

# attack_args = customattack.AttackArgs(
#     num_examples=20,
#     log_to_csv="log.csv",
#     checkpoint_interval=5,
#     checkpoint_dir="checkpoints",
#     disable_stdout=True
# )
#
# attacker = customattack.Attacker(attack, dataset, attack_args)
# attacker.attack_dataset()