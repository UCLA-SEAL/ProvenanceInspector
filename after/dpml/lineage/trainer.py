import numpy as np
import pandas as pd
import os.path as osp
import json

glue_dict = json.load(open("./adv_glue/dev.json"))
glue_sst2 = pd.DataFrame(glue_dict['sst2'])[['sentence', 'label']]

from datasets import Dataset, load_metric, load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer

from .utils import compute_classification_metric

class Trainer:
    def __init__(self, model):
        self.model = model

    def train(self, train_dataset, eval_dataset, metric_fn, **training_args):
        training_args = TrainingArguments(**training_args)

    
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            compute_metrics=metric_fn,
        )

        trainer.train()

        trainer.evaluate()

    def eval(self):
        # eval

        dataset = load_dataset("sst2")
        train_dataset = dataset['train']
        valid_dataset = dataset['validation']
        test_dataset = dataset['test']

        # Run inferences with your new model using Pipeline|
        from transformers import pipeline

        model.eval()
        sentiment_model = pipeline("sentiment-analysis", model=model, 
                                tokenizer=tokenizer, device=0)

        pred = sentiment_model(valid_dataset['sentence'])
        pred_labels = [0 if x['label'] == 'LABEL_0' else 1 for x in pred]

        metric = load_metric("accuracy")
        metric.compute(predictions=pred_labels, references=valid_dataset['label'])