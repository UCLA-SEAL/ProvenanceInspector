"""
AnalysisArgs Class
===================
"""

import transformers

from dataclasses import dataclass
from datasets import load_dataset

from lineage.utils import ARGS_SPLIT_TOKEN



HUGGINGFACE_DATASET_BY_MODEL = {
    #
    # bert-base-uncased
    #
    "bert-base-uncased-ag-news": ("ag_news", None, "test"),
    "bert-base-uncased-cola": ("glue", "cola", "validation"),
    "bert-base-uncased-imdb": ("imdb", None, "test"),
    "bert-base-uncased-mrpc": ("glue", "mrpc", "validation"),
    "bert-base-uncased-qnli": ("glue", "qnli", "validation"),
    "bert-base-uncased-qqp": ("glue", "qqp", "validation"),
    "bert-base-uncased-rte": ("glue", "rte", "validation"),
    "bert-base-uncased-sst2": ("glue", "sst2", "validation"),
    "bert-base-uncased-wnli": ("glue", "wnli", "validation"),
    "bert-base-uncased-mr": ("rotten_tomatoes", None, "test"),
    "bert-base-uncased-yelp": ("yelp_polarity", None, "test"),
    #
    # distilbert-base-cased
    #
    "distilbert-base-cased-cola": ("glue", "cola", "validation"),
    "distilbert-base-cased-mrpc": ("glue", "mrpc", "validation"),
    "distilbert-base-cased-qqp": ("glue", "qqp", "validation"),
    "distilbert-base-cased-snli": ("snli", None, "test"),
    "distilbert-base-cased-sst2": ("glue", "sst2", "validation"),
    "distilbert-base-uncased-ag-news": ("ag_news", None, "test"),
    "distilbert-base-uncased-cola": ("glue", "cola", "validation"),
    "distilbert-base-uncased-imdb": ("imdb", None, "test"),
    "distilbert-base-uncased-mr": ("rotten_tomatoes", None, "test"),
    "distilbert-base-uncased-mrpc": ("glue", "mrpc", "validation"),
    "distilbert-base-uncased-qnli": ("glue", "qnli", "validation"),
    "distilbert-base-uncased-rte": ("glue", "rte", "validation"),
    "distilbert-base-uncased-wnli": ("glue", "wnli", "validation"),
    #
    # roberta-base (RoBERTa is cased by default)
    #
    "roberta-base-ag-news": ("ag_news", None, "test"),
    "roberta-base-cola": ("glue", "cola", "validation"),
    "roberta-base-imdb": ("imdb", None, "test"),
    "roberta-base-mr": ("rotten_tomatoes", None, "test"),
    "roberta-base-mrpc": ("glue", "mrpc", "validation"),
    "roberta-base-qnli": ("glue", "qnli", "validation"),
    "roberta-base-rte": ("glue", "rte", "validation"),
    "roberta-base-sst2": ("glue", "sst2", "validation"),
    "roberta-base-wnli": ("glue", "wnli", "validation"),
    #
    # albert-base-v2 (ALBERT is cased by default)
    #
    "albert-base-v2-ag-news": ("ag_news", None, "test"),
    "albert-base-v2-cola": ("glue", "cola", "validation"),
    "albert-base-v2-imdb": ("imdb", None, "test"),
    "albert-base-v2-mr": ("rotten_tomatoes", None, "test"),
    "albert-base-v2-rte": ("glue", "rte", "validation"),
    "albert-base-v2-qqp": ("glue", "qqp", "validation"),
    "albert-base-v2-snli": ("snli", None, "test"),
    "albert-base-v2-sst2": ("glue", "sst2", "validation"),
    "albert-base-v2-wnli": ("glue", "wnli", "validation"),
    "albert-base-v2-yelp": ("yelp_polarity", None, "test"),
    #
    # xlnet-base-cased
    #
    "xlnet-base-cased-cola": ("glue", "cola", "validation"),
    "xlnet-base-cased-imdb": ("imdb", None, "test"),
    "xlnet-base-cased-mr": ("rotten_tomatoes", None, "test"),
    "xlnet-base-cased-mrpc": ("glue", "mrpc", "validation"),
    "xlnet-base-cased-rte": ("glue", "rte", "validation"),
    "xlnet-base-cased-wnli": ("glue", "wnli", "validation"),
}

def get_datasets_dataset_columns(dataset):
    """Common schemas for datasets found in dataset hub."""
    schema = set(dataset.column_names)
    if {"premise", "hypothesis", "label"} <= schema:
        input_columns = ("premise", "hypothesis")
        output_column = "label"
    elif {"question", "sentence", "label"} <= schema:
        input_columns = ("question", "sentence")
        output_column = "label"
    elif {"sentence1", "sentence2", "label"} <= schema:
        input_columns = ("sentence1", "sentence2")
        output_column = "label"
    elif {"question1", "question2", "label"} <= schema:
        input_columns = ("question1", "question2")
        output_column = "label"
    elif {"question", "sentence", "label"} <= schema:
        input_columns = ("question", "sentence")
        output_column = "label"
    elif {"text", "label"} <= schema:
        input_columns = ("text",)
        output_column = "label"
    elif {"sentence", "label"} <= schema:
        input_columns = ("sentence",)
        output_column = "label"
    elif {"document", "summary"} <= schema:
        input_columns = ("document",)
        output_column = "summary"
    elif {"content", "summary"} <= schema:
        input_columns = ("content",)
        output_column = "summary"
    elif {"label", "review"} <= schema:
        input_columns = ("review",)
        output_column = "label"
    else:
        raise ValueError(
            f"Unsupported dataset schema {schema}. Try passing your own `dataset_columns` argument."
        )

    return input_columns, output_column

@dataclass
class DatasetArgs:
    """Arguments for creating a model.
    """

    dataset: str = "textattack/bert-base-uncased-SST-2"

    dataset_train_split: str = None
    dataset_eval_split: str = None
    filter_train_by_labels: list = None
    filter_eval_by_labels: list = None

    @classmethod
    def _create_dataset_from_args(cls, args):
        if hasattr(args, "model"):
            args.dataset = args.model
        
        if args.dataset in HUGGINGFACE_DATASET_BY_MODEL:
            dataset_name, subset, split = HUGGINGFACE_DATASET_BY_MODEL[args.dataset]

            dataset = load_dataset(dataset_name, subset)[split]

            input_columns, output_column =  get_datasets_dataset_columns(dataset)

            column_texts = []
            for column in input_columns:
                column_texts.append(dataset[column])
            dataset.add_column('text', list(zip(*column_texts))))
            dataset[input_columns]

            remove_columns = []
            for column in dataset.column_names:
                if column == output_column:
                    dataset.class_encode_column(column)
                elif column in {'text', 'idx'}:
                    pass
                else:
                    remove_columns.append(column)
            dataset.remove_columns_(remove_columns)


        elif ARGS_SPLIT_TOKEN in args.dataset:

            dataset_args = args.dataset.split(ARGS_SPLIT_TOKEN)
            # TODO `HuggingFaceDataset` -> `HuggingFaceDataset`
            if args.dataset_train_split:
                train_dataset = load_dataset(*dataset_args)[args.dataset_train_split]
            else:
                try:
                    train_dataset = load_dataset(*dataset_args)["train"]
                    args.dataset_train_split = "train"
                except KeyError:
                    raise KeyError(
                        f"Error: no `train` split found in `{args.dataset}` dataset"
                    )

            if args.dataset_eval_split:
                eval_dataset = load_dataset(*dataset_args)[args.dataset_eval_split]
            else:
                # try common dev split names
                try:
                    eval_dataset = load_dataset(*dataset_args)["dev"]
                    args.dataset_eval_split = "dev"
                except KeyError:
                    try:
                        eval_dataset = load_dataset(*dataset_args)["eval"]
                        args.dataset_eval_split = "eval"
                    except KeyError:
                        try:
                            eval_dataset = load_dataset(*dataset_args)["validation"]
                            args.dataset_eval_split = "validation"
                        except KeyError:
                            try:
                                eval_dataset = load_dataset(*dataset_args)["test"]
                                args.dataset_eval_split = "test"
                            except KeyError:
                                raise KeyError(
                                    f"Could not find `dev`, `eval`, `validation`, or `test` split in dataset {args.dataset}."
                                )

            if args.filter_train_by_labels:
                train_dataset.filter_by_labels_(args.filter_train_by_labels)
            if args.filter_eval_by_labels:
                eval_dataset.filter_by_labels_(args.filter_eval_by_labels)

            return train_dataset, eval_dataset


    @classmethod
    def _add_parser_args(cls, parser):

        parser.add_argument(
            "--dataset",
            type=str,
            required=True,
            default="yelp",
            help="dataset for training; will be loaded from "
            "`datasets` library. if dataset has a subset, separate with a colon. "
            " ex: `glue^sst2` or `rotten_tomatoes`",
        )
        parser.add_argument(
            "--dataset-train-split",
            type=str,
            default="",
            help="train dataset split, if non-standard "
            "(can automatically detect 'train'",
        )
        parser.add_argument(
            "--dataset-eval-split",
            type=str,
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