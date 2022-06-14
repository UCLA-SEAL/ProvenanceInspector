import textattack
import transformers

model = transformers.AutoModelForSequenceClassification.from_pretrained("textattack/bert-base-uncased-SST-2")
tokenizer = transformers.AutoTokenizer.from_pretrained("textattack/bert-base-uncased-SST-2", use_fast=True)
model_wrapper = textattack.models.wrappers.HuggingFaceModelWrapper(model, tokenizer)

attack = textattack.attack_recipes.A2TYoo2021.build(model_wrapper)
dataset = textattack.datasets.HuggingFaceDataset("glue", "sst2", split="validation")

# Attack 20 samples with CSV logging and checkpoint saved every 5 interval
attack_args = textattack.AttackArgs(
    num_examples=20,
    csv_coloring_style="plain",
    log_to_csv="../results/log.csv",
    checkpoint_interval=5,
    disable_stdout=True
)

attacker = textattack.Attacker(attack, dataset, attack_args)
results = attacker.attack_dataset()
#for result in results:
#    print(result)