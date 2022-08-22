"""

TrainModelCommand class
==============================

"""


from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from functools import partial

from textattack import CommandLineTrainingArgs, Trainer
from textattack.commands import TextAttackCommand

from lineage.utils import compute_classification_metric
from datasets import Dataset, load_metric, load_dataset


class TrainModelCommand(TextAttackCommand):
    """The TextAttack train module:

    A command line parser to train a model from user specifications.
    """

    def run(self, args):
        metric = load_metric("accuracy")
        metric_fn = partial(compute_classification_metric, metric)


        train_dataset = Dataset.from_pandas(test_revert_df)
        eval_dataset = Dataset.from_pandas(glue_sst2)

        train_dataset = train_dataset.class_encode_column('label')
        eval_dataset = eval_dataset.class_encode_column('label')

        training_args = CommandLineTrainingArgs(**vars(args))
        model_wrapper = CommandLineTrainingArgs._create_model_from_args(training_args)
        train_dataset, eval_dataset = CommandLineTrainingArgs._create_dataset_from_args(
            training_args
        )
        attack = CommandLineTrainingArgs._create_attack_from_args(
            training_args, model_wrapper
        )
        trainer = Trainer(
            model_wrapper,
            training_args.task_type,
            attack,
            train_dataset,
            eval_dataset,
            training_args,
        )
        trainer.train()

    @staticmethod
    def register_subcommand(main_parser: ArgumentParser):
        parser = main_parser.add_parser(
            "train",
            help="train a model for sequence classification",
            formatter_class=ArgumentDefaultsHelpFormatter,
        )
        parser = CommandLineTrainingArgs._add_parser_args(parser)
        parser.set_defaults(func=TrainModelCommand())
