"""
AnalysisArgs Class
===================
"""

import transformers

from dataclasses import dataclass

HUGGINGFACE_MODELS = {
    #
    # bert-base-uncased
    #
    "bert-base-uncased": "bert-base-uncased",
    "bert-base-uncased-ag-news": "textattack/bert-base-uncased-ag-news",
    "bert-base-uncased-cola": "textattack/bert-base-uncased-CoLA",
    "bert-base-uncased-imdb": "textattack/bert-base-uncased-imdb",
    "bert-base-uncased-mnli": "textattack/bert-base-uncased-MNLI",
    "bert-base-uncased-mrpc": "textattack/bert-base-uncased-MRPC",
    "bert-base-uncased-qnli": "textattack/bert-base-uncased-QNLI",
    "bert-base-uncased-qqp": "textattack/bert-base-uncased-QQP",
    "bert-base-uncased-rte": "textattack/bert-base-uncased-RTE",
    "bert-base-uncased-sst2": "textattack/bert-base-uncased-SST-2",
    "bert-base-uncased-stsb": "textattack/bert-base-uncased-STS-B",
    "bert-base-uncased-wnli": "textattack/bert-base-uncased-WNLI",
    "bert-base-uncased-mr": "textattack/bert-base-uncased-rotten-tomatoes",
    "bert-base-uncased-snli": "textattack/bert-base-uncased-snli",
    "bert-base-uncased-yelp": "textattack/bert-base-uncased-yelp-polarity",
    #
    # distilbert-base-cased
    #
    "distilbert-base-uncased": "distilbert-base-uncased",
    "distilbert-base-cased-cola": "textattack/distilbert-base-cased-CoLA",
    "distilbert-base-cased-mrpc": "textattack/distilbert-base-cased-MRPC",
    "distilbert-base-cased-qqp": "textattack/distilbert-base-cased-QQP",
    "distilbert-base-cased-snli": "textattack/distilbert-base-cased-snli",
    "distilbert-base-cased-sst2": "textattack/distilbert-base-cased-SST-2",
    "distilbert-base-cased-stsb": "textattack/distilbert-base-cased-STS-B",
    "distilbert-base-uncased-ag-news": "textattack/distilbert-base-uncased-ag-news",
    "distilbert-base-uncased-cola": "textattack/distilbert-base-cased-CoLA",
    "distilbert-base-uncased-imdb": "textattack/distilbert-base-uncased-imdb",
    "distilbert-base-uncased-mnli": "textattack/distilbert-base-uncased-MNLI",
    "distilbert-base-uncased-mr": "textattack/distilbert-base-uncased-rotten-tomatoes",
    "distilbert-base-uncased-mrpc": "textattack/distilbert-base-uncased-MRPC",
    "distilbert-base-uncased-qnli": "textattack/distilbert-base-uncased-QNLI",
    "distilbert-base-uncased-rte": "textattack/distilbert-base-uncased-RTE",
    "distilbert-base-uncased-wnli": "textattack/distilbert-base-uncased-WNLI",
    #
    # roberta-base (RoBERTa is cased by default)
    #
    "roberta-base": "roberta-base",
    "roberta-base-ag-news": "textattack/roberta-base-ag-news",
    "roberta-base-cola": "textattack/roberta-base-CoLA",
    "roberta-base-imdb": "textattack/roberta-base-imdb",
    "roberta-base-mr": "textattack/roberta-base-rotten-tomatoes",
    "roberta-base-mrpc": "textattack/roberta-base-MRPC",
    "roberta-base-qnli": "textattack/roberta-base-QNLI",
    "roberta-base-rte": "textattack/roberta-base-RTE",
    "roberta-base-sst2": "textattack/roberta-base-SST-2",
    "roberta-base-stsb": "textattack/roberta-base-STS-B",
    "roberta-base-wnli": "textattack/roberta-base-WNLI",
    #
    # albert-base-v2 (ALBERT is cased by default)
    #
    "albert-base-v2": "albert-base-v2",
    "albert-base-v2-ag-news": "textattack/albert-base-v2-ag-news",
    "albert-base-v2-cola": "textattack/albert-base-v2-CoLA",
    "albert-base-v2-imdb": "textattack/albert-base-v2-imdb",
    "albert-base-v2-mr": "textattack/albert-base-v2-rotten-tomatoes",
    "albert-base-v2-rte": "textattack/albert-base-v2-RTE",
    "albert-base-v2-qqp": "textattack/albert-base-v2-QQP",
    "albert-base-v2-snli": "textattack/albert-base-v2-snli",
    "albert-base-v2-sst2": "textattack/albert-base-v2-SST-2",
    "albert-base-v2-stsb": "textattack/albert-base-v2-STS-B",
    "albert-base-v2-wnli": "textattack/albert-base-v2-WNLI",
    "albert-base-v2-yelp": "textattack/albert-base-v2-yelp-polarity",
    #
    # xlnet-base-cased
    #
    "xlnet-base-cased": "xlnet-base-cased",
    "xlnet-base-cased-cola": "textattack/xlnet-base-cased-CoLA",
    "xlnet-base-cased-imdb": "textattack/xlnet-base-cased-imdb",
    "xlnet-base-cased-mr": "textattack/xlnet-base-cased-rotten-tomatoes",
    "xlnet-base-cased-mrpc": "textattack/xlnet-base-cased-MRPC",
    "xlnet-base-cased-rte": "textattack/xlnet-base-cased-RTE",
    "xlnet-base-cased-stsb": "textattack/xlnet-base-cased-STS-B",
    "xlnet-base-cased-wnli": "textattack/xlnet-base-cased-WNLI",
}



@dataclass
class ModelArgs:
    """Arguments for creating a model.
    """

    model: str = "textattack/bert-base-uncased-SST-2"
    task: str = "text-classification"
    model_max_length: int = None
    model_num_labels: int = None
    

    @classmethod
    def _create_eval_model_from_args(cls, args):

        if args.model in HUGGINGFACE_MODELS:
            # Support loading models automatically from the HuggingFace model hub.

            model_name = HUGGINGFACE_MODELS[args.model]

            max_seq_len = args.model_max_length if args.model_max_length else 512
            num_labels = args.model_num_labels if args.model_num_labels else 2

            config = transformers.AutoConfig.from_pretrained(
                model_name,
                num_labels=num_labels,
            )

            model = transformers.AutoModelForSequenceClassification.from_pretrained(
                model_name,
                config=config
            )

            tokenizer = transformers.AutoTokenizer.from_pretrained(
                model_name, model_max_length=max_seq_len,
                use_fast=True
            )

            pred_model = transformers.pipeline(args.task, model=model, tokenizer=tokenizer, device=0)
      
        else:
            raise ValueError(f"Error: unsupported Lineage model {args.model}")            

        return pred_model

    
    @classmethod
    def _create_train_model_from_args(cls, args):

        if args.model in HUGGINGFACE_MODELS:
            # Support loading models automatically from the HuggingFace model hub.

            model_name = HUGGINGFACE_MODELS[args.model]

            max_seq_len = args.model_max_length if args.model_max_length else 512
            num_labels = args.model_num_labels if args.model_num_labels else 2

            config = transformers.AutoConfig.from_pretrained(
                model_name,
                num_labels=num_labels,
            )

            model = transformers.AutoModelForSequenceClassification.from_pretrained(
                model_name,
                config=config
            )

            tokenizer = transformers.AutoTokenizer.from_pretrained(
                model_name, model_max_length=max_seq_len,
                use_fast=True
            )

      
        else:
            raise ValueError(f"Error: unsupported Lineage model {args.model}")            

        return model, tokenizer


    @classmethod
    def _add_parser_args(cls, parser):
        parser.add_argument(
            "--model",
            help="Name or path of target HuggingFace model for prediction",
            type=str,
            default="bert-base-uncased-sst2",
            choices=HUGGINGFACE_MODELS.keys(),
        )
        parser.add_argument(
            "--task",
            help="Type of task  model is supposed to perform",
            type=str,
            default="text-classification"
        )

        parser.add_argument(
            "--model-max-length",
            type=int,
            default=None,
            help="The maximum sequence length of the model.",
        )
        parser.add_argument(
            "--model-num-labels",
            type=int,
            default=None,
            help="The number of labels for classification.",
        )

        return parser