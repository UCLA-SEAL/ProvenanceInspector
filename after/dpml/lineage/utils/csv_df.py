from datasets import Dataset
import os.path as osp
import pandas as pd
from tokenizers import Tokenizer


def df_to_dataset(df, tokenizer, label_col='label'):

    dataset = Dataset.from_pandas(df)
    dataset.class_encode_column(label_col)

    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True)

    dataset = dataset.map(tokenize_function, batched=True)

    return dataset


def load_df(file_pth, text_column, label_column):
    #file_name = file_pth[file_pth.rfind('/')+1:]

    df = pd.read_csv(file_pth)
    data_df = df[[text_column,  label_column]]

    data_df.rename(columns = {text_column:'text', 
        label_column:'label'}, inplace = True)
    
    return data_df