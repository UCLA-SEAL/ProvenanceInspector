import numpy as np
import pandas as pd
import os.path as osp
import json
from datasets import Dataset, load_metric, load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer, pipeline

from .utils import compute_classification_metric

class Trainer:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def train(self, train_dataset, eval_dataset, metric_fn, save_last=False, **training_args):
        training_args = TrainingArguments(**training_args)
    
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            compute_metrics=metric_fn,
        )

        trainer.train()

        return trainer.evaluate()

    def eval(self, eval_dataset, metric, label_map_fn):

        model=AutoModelForSequenceClassification.from_pretrained('./models/finetune_filtered_a2t_word.8_sst2')

        self.model.eval()
        sentiment_model = pipeline("sentiment-analysis", model=self.model, 
                                tokenizer=self.tokenizer, device=0)

        pred = sentiment_model(eval_dataset['text'])
        pred_labels = [label_map_fn(x) for x in pred]

        result = metric.compute(predictions=pred_labels, references=eval_dataset['label'])[metric.name]

        return result