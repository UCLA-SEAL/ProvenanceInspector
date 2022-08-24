"""

TrainModelCommand class
==============================

"""


from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from functools import partial

from lineage import TrainingArgs, ModelArgs, DatasetArgs, Trainer
from lineage.commands import LineageCommand

from datasets import Dataset, load_metric
from transformers import AutoModelForSequenceClassification

from lineage.utils import compute_classification_metric, get_class_attributes, encode_dataset
from ..training_args import TRAINING_ARGS_CONFIG, TRAINING_ARGS_MAPPING


class TrainCommand(LineageCommand):
    """The TextAttack train module:

    A command line parser to train a model from user specifications.
    """

    def run(self, args):
        metric = load_metric("accuracy")
        metric_fn = partial(compute_classification_metric, metric)

        model, tokenizer = ModelArgs._create_train_model_from_args(args)
        train_dataset, test_dataset, adv_datatset = DatasetArgs._create_dataset_from_args(args)

        train_dataset = encode_dataset(train_dataset, tokenizer, text_col='text', label_col='label')
        test_dataset = encode_dataset(train_dataset, tokenizer, text_col='text', label_col='label')

        training_args = {}
        train_arg_set = get_class_attributes(TrainingArgs)
        for k in args.__dict__:
            if args.__dict__[k] is not None and k in train_arg_set:
                arg_name = k
                if k in TRAINING_ARGS_MAPPING:
                    arg_name = TRAINING_ARGS_MAPPING[k]
                training_args[arg_name] = args.__dict__[k]
                if k in TRAINING_ARGS_CONFIG:
                    training_args.update(TRAINING_ARGS_CONFIG[k])

        trainer = Trainer(model, tokenizer)
        eval_result = trainer.train(train_dataset, test_dataset, metric_fn, **training_args)

        #self.model.save_pretrained('./models/filtered_a2t_word.8_sst2_test')

        print('Evaluation Results:')
        print(eval_result)

        #model=AutoModelForSequenceClassification.from_pretrained('./models/unfiltered_a2t_mlm_word.8_sst2')
        #trainer = Trainer(model, tokenizer)

        label_map_fn = lambda x: 0 if x['label'] == 'LABEL_0' else 1
        adv_result = trainer.eval(adv_datatset, metric, label_map_fn)

        print('Adversarial Set Results:')
        print(adv_result)


    @staticmethod
    def register_subcommand(main_parser: ArgumentParser):
        parser = main_parser.add_parser(
            "train",
            help="train a model for sequence classification",
            formatter_class=ArgumentDefaultsHelpFormatter,
        )
        parser = ModelArgs._add_parser_args(parser)
        parser = DatasetArgs._add_parser_args(parser)
        parser = TrainingArgs._add_parser_args(parser)
        parser.set_defaults(func=TrainCommand())