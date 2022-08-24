"""
AnalysisArgs Class
===================
"""

from yaml import load
import transformers

from dataclasses import dataclass
from .utils.file_dataset import load_dataset_from_args, map_dataset_columns

@dataclass
class DatasetArgs:
    """Arguments for creating a dataset.
    """

    dataset: str = "textattack/bert-base-uncased-SST-2"
    eval_dataset: str = None
    adv_dataset: str = None
    dataset_train_split: str = None
    dataset_eval_split: str = None
    filter_train_by_labels: list = None
    filter_eval_by_labels: list = None

    @classmethod
    def _create_dataset_from_args(cls, args):
        adv_dataset = None

        if hasattr(args, "model"):
            if not args.dataset:
                args.dataset = args.model
            if not args.eval_dataset:
                args.eval_dataset = args.model
        if args.dataset:
            train_dataset, eval_split = load_dataset_from_args(args.dataset)
        if args.eval_dataset:
            eval_dataset, eval_split = load_dataset_from_args(args.eval_dataset)
            if not hasattr(args,'dataset_eval_split'):
                args.dataset_eval_split = eval_split
        if args.adv_dataset:
            adv_dataset, split = load_dataset_from_args(args.eval_dataset)
            adv_dataset = adv_dataset[split]
        if args.dataset_train_split:
            train_dataset = train_dataset[args.dataset_train_split]
        else:
            try:
                train_dataset = train_dataset["train"]
                args.dataset_train_split = "train"
            except KeyError:
                pass
                #raise KeyError(
                #    f"Error: no `train` split found in `{args.dataset}` dataset"
                #)

        if args.dataset_eval_split:
            eval_dataset = eval_dataset[args.dataset_eval_split]
        else:
            # try common dev split names
            try:
                eval_dataset = eval_dataset["dev"]
                args.dataset_eval_split = "dev"
            except KeyError:
                try:
                    eval_dataset = eval_dataset["eval"]
                    args.dataset_eval_split = "eval"
                except KeyError:
                    try:
                        eval_dataset = eval_dataset["validation"]
                        args.dataset_eval_split = "validation"
                    except KeyError:
                        try:
                            eval_dataset = eval_dataset["test"]
                            args.dataset_eval_split = "test"
                        except KeyError:
                            pass
                            #raise KeyError(
                            #    f"Could not find `dev`, `eval`, `validation`, or `test` split in dataset {args.dataset}."
                            #)

        if args.filter_train_by_labels:
            train_dataset.filter_by_labels_(args.filter_train_by_labels)
        if args.filter_eval_by_labels:
            eval_dataset.filter_by_labels_(args.filter_eval_by_labels)


        train_dataset = map_dataset_columns(train_dataset)
        eval_dataset = map_dataset_columns(eval_dataset)
        if adv_dataset is not None:
            adv_dataset = map_dataset_columns(adv_dataset)
        

        return train_dataset, eval_dataset, adv_dataset


    @classmethod
    def _add_parser_args(cls, parser):

        parser.add_argument(
            "--dataset",
            type=str,
            required=True,
            default="yelp",
            help="dataset for training; will be loaded from "
            "`datasets` library. if dataset has a subset, separate with `^`. "
            " ex: `glue^sst2`",
        )
        parser.add_argument(
            "--eval-dataset",
            type=str,
            required=False,
            default=None,
            help="dataset for evaluation; will be loaded from "
            "`datasets` library. if dataset has a subset, separate with `^`. "
            " ex: `glue^sst2`",
        )
        parser.add_argument(
            "--adv-dataset",
            type=str,
            required=False,
            default=None,
            help="dataset for evaluation; will be loaded from "
            "`datasets` library. if dataset has a subset, separate with `^`. "
            " ex: `glue^sst2`",
        )
        parser.add_argument(
            "--dataset-train-split",
            type=str,
            required=False,
            default="",
            help="train dataset split, if non-standard "
            "(can automatically detect 'train'",
        )
        parser.add_argument(
            "--dataset-eval-split",
            type=str,
            required=False,
            default="",
            help="val dataset split, if non-standard "
            "(can automatically detect 'dev', 'eval', 'validation')",
        )
        parser.add_argument(
            "--filter-train-by-labels",
            nargs="+",
            type=int,
            required=False,
            default=None,
            help="List of labels to keep in the train dataset and discard all others.",
        )
        parser.add_argument(
            "--filter-eval-by-labels",
            nargs="+",
            type=int,
            required=False,
            default=None,
            help="List of labels to keep in the eval dataset and discard all others.",
        )


        return parser