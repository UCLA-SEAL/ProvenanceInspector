import os.path as osp
import pandas as pd
import json

from datasets import Dataset, load_dataset
from .args import ARGS_SPLIT_TOKEN

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

def encode_dataset(dataset: Dataset, tokenizer, text_col='text', label_col='label'):
    dataset.class_encode_column(label_col)

    def tokenize_function(examples):
        return tokenizer(examples[text_col], padding="max_length", truncation=True)

    dataset = dataset.map(tokenize_function, batched=True)

    return dataset


def get_df_dataset_columns(df):
    input_column = None
    output_column = None
    for column in df.columns:
        if column in {'perturbed_text', 'reverted_text', 'sentence'}:
            input_column = column
        elif column in {'ground_truth_output', 'label'}:
            output_column = column

    return input_column, output_column


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


def map_dataset_columns(dataset):
    input_columns, output_column =  get_datasets_dataset_columns(dataset)

    column_texts = []
    for column in input_columns:
        column_texts.append(dataset[column])
    dataset.add_column('text', list(zip(*column_texts)))

    remove_columns = []
    for column in dataset.column_names:
        if column == output_column:
            dataset.class_encode_column(column)
        elif column in {'text', 'idx'}:
            pass
        else:
            remove_columns.append(column)
    dataset.remove_columns_(remove_columns)

    return dataset


def load_dataset_from_args(dataset_arg):
    eval_split = None
    if dataset_arg in HUGGINGFACE_DATASET_BY_MODEL:
        dataset_name, subset, split = HUGGINGFACE_DATASET_BY_MODEL[dataset_arg]

        dataset = load_dataset(dataset_name, subset)
        eval_split = split

    elif ARGS_SPLIT_TOKEN in dataset_arg:
        dataset_args = dataset_arg.split(ARGS_SPLIT_TOKEN)
        dataset = load_dataset(*dataset_args)

    elif osp.exists(dataset_arg):
        dataset = load_file_dataset(dataset_arg)                

    else:
        try:
            dataset = load_dataset(dataset_arg)
        except:
            raise ValueError(
                        f"Error: cannot load {dataset_arg} as a HuggingFace dataset"
                    )
    return dataset, eval_split


def load_file_dataset(file_pth, subset='sst2', text_column=None, label_column=None):
    if 'csv' in file_pth:
        df = pd.read_csv(file_pth)
    elif 'json' in file_pth:
        json_dict = json.load(open(file_pth))
        df = pd.DataFrame(json_dict[subset])
    else:
        raise ValueError(f'Cannot load dataset from file path: {file_pth}, only support json / csv file.')

    if text_column is None or label_column is None:
        text_column, label_column = get_df_dataset_columns(df)

    data_df = df[[text_column,  label_column]]

    data_df.rename(columns = {text_column:'text', 
        label_column:'label'}, inplace = True)

    dataset = Dataset.from_pandas(data_df)
    
    return dataset