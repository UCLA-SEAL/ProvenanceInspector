"""
TrainingArgs Class
==================
"""

from dataclasses import dataclass, field
import datetime
import os
from typing import Union


TRANING_ARGS_CONFIG = {
    'checkpoint_interval_steps': {'save_strategy': "steps"},
    'checkpoint_on_epoch': {'save_strategy': "epoch"},
    'logging_interval_step': {'logging_strategy': "steps"},
    'save_last': {'save_last': True} # not HUGGINGFACE

}
TRAINING_ARGS_MAPPING = {
    'num_epochs': 'num_train_epochs',
    'num_warmup_steps': 'warmup_steps',
    'random_seed': 'seed',
    'checkpoint_interval_steps': 'save_steps', 
    'log_dir': 'logging_dir',
    'logging_interval_step': 'logging_steps',

}

def default_output_dir():
    return os.path.join(
        "./outputs", datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
    )


@dataclass
class TrainingArgs:
    """Arguments for ``Trainer`` class that is used for adversarial training.

    Args:
        num_epochs (:obj:`int`, `optional`, defaults to :obj:`3`):
            Total number of epochs for training.
        learning_rate (:obj:`float`, `optional`, defaults to :obj:`5e-5`):
            Learning rate for optimizer.
        num_warmup_steps (:obj:`int` or :obj:`float`, `optional`, defaults to :obj:`500`):
            The number of steps for the warmup phase of linear scheduler.
            If :obj:`num_warmup_steps` is a :obj:`float` between 0 and 1, the number of warmup steps will be :obj:`math.ceil(num_training_steps * num_warmup_steps)`.
        weight_decay (:obj:`float`, `optional`, defaults to :obj:`0.01`):
            Weight decay (L2 penalty).
        per_device_train_batch_size (:obj:`int`, `optional`, defaults to :obj:`8`):
            The batch size per GPU/CPU for training.
        per_device_eval_batch_size (:obj:`int`, `optional`, defaults to :obj:`32`):
            The batch size per GPU/CPU for evaluation.
        gradient_accumulation_steps (:obj:`int`, `optional`, defaults to :obj:`1`):
            Number of updates steps to accumulate the gradients before performing a backward/update pass.
        random_seed (:obj:`int`, `optional`, defaults to :obj:`786`):
            Random seed for reproducibility.
        load_best_model_at_end (:obj:`bool`, `optional`, defaults to :obj:`False`):
            If :obj:`True`, keep track of the best model across training and load it at the end.
        output_dir (:obj:`str`, `optional`):
            Directory to output training logs and checkpoints. Defaults to :obj:`./outputs/%Y-%m-%d-%H-%M-%S-%f` format.
        checkpoint_interval_steps (:obj:`int`, `optional`, defaults to :obj:`None`):
            If set, save model checkpoint after every `N` updates to the model.
        checkpoint_on_epoch (:obj:`bool`, `optional`, defaults to :obj: False):
            If set, save model checkpoint after every `N` epochs.
        save_last (:obj:`bool`, `optional`, defaults to :obj:`True`):
            If :obj:`True`, save the model at end of training. Can be used with :obj:`load_best_model_at_end` to save the best model at the end.
        log_dir (:obj:`str`, `optional`, defaults to :obj:`"./runs"`):
            Path of Tensorboard log directory.
        logging_interval_step (:obj:`int`, `optional`, defaults to :obj:`1`):
            Log to Tensorboard/Wandb every `N` training steps.
    """

    num_epochs: int = 3
    attack_epoch_interval: int = 1
    learning_rate: float = 5e-5
    num_warmup_steps: Union[int, float] = 500
    weight_decay: float = 0.01
    per_device_train_batch_size: int = 8
    per_device_eval_batch_size: int = 32
    gradient_accumulation_steps: int = 1
    random_seed: int = 786
    load_best_model_at_end: bool = False
    output_dir: str = field(default_factory=default_output_dir)
    checkpoint_interval_steps: int = None
    checkpoint_on_epoch: bool = False
    save_last: bool = True
    log_dir: str = None
    logging_interval_step: int = 1

    def __post_init__(self):
        assert self.num_epochs > 0, "`num_epochs` must be greater than 0."
        
        if self.attack_epoch_interval is not None:
            assert (
                self.attack_epoch_interval > 0
            ), "`attack_epoch_interval` must be greater than 0."
        assert (
            self.num_warmup_steps >= 0
        ), "`num_warmup_steps` must be greater than or equal to 0."
        assert (
            self.gradient_accumulation_steps > 0
        ), "`gradient_accumulation_steps` must be greater than 0."
        

    @classmethod
    def _add_parser_args(cls, parser):
        """Add listed args to command line parser."""
        default_obj = cls()

        def int_or_float(v):
            try:
                return int(v)
            except ValueError:
                return float(v)

        parser.add_argument(
            "--num-epochs",
            "--epochs",
            type=int,
            default=default_obj.num_epochs,
            help="Total number of epochs for training.",
        )
        parser.add_argument(
            "--learning-rate",
            "--lr",
            type=float,
            default=default_obj.learning_rate,
            help="Learning rate for Adam Optimization.",
        )
        parser.add_argument(
            "--num-warmup-steps",
            type=int_or_float,
            default=default_obj.num_warmup_steps,
            help="The number of steps for the warmup phase of linear scheduler.",
        )
        parser.add_argument(
            "--weight-decay",
            type=float,
            default=default_obj.weight_decay,
            help="Weight decay (L2 penalty).",
        )
        parser.add_argument(
            "--per-device-train-batch-size",
            type=int,
            default=default_obj.per_device_train_batch_size,
            help="The batch size per GPU/CPU for training.",
        )
        parser.add_argument(
            "--per-device-eval-batch-size",
            type=int,
            default=default_obj.per_device_eval_batch_size,
            help="The batch size per GPU/CPU for evaluation.",
        )
        parser.add_argument(
            "--gradient-accumulation-steps",
            type=int,
            default=default_obj.gradient_accumulation_steps,
            help="Number of updates steps to accumulate the gradients for, before performing a backward/update pass.",
        )
        parser.add_argument(
            "--random-seed",
            type=int,
            default=default_obj.random_seed,
            help="Random seed.",
        )
        parser.add_argument(
            "--load-best-model-at-end",
            action="store_true",
            default=default_obj.load_best_model_at_end,
            help="If set, keep track of the best model across training and load it at the end.",
        )
        parser.add_argument(
            "--output-dir",
            type=str,
            default=default_output_dir(),
            help="Directory to output training logs and checkpoints.",
        )
        parser.add_argument(
            "--checkpoint-interval-steps",
            type=int,
            default=default_obj.checkpoint_interval_steps,
            help="Save model checkpoint after every N updates to the model.",
        )
        parser.add_argument(
            "--checkpoint-on-epoch",
            action="store_true",
            default=default_obj.checkpoint_on_epoch,
            help="Save model checkpoint after every epoch.",
        )
        parser.add_argument(
            "--save-last",
            action="store_true",
            default=default_obj.save_last,
            help="If set, save the model at end of training. Can be used with `--load-best-model-at-end` to save the best model at the end.",
        )
        parser.add_argument(
            "--log-dir",
            type=str,
            default=default_obj.log_dir,
            help="Path of Tensorboard log directory.",
        )
        parser.add_argument(
            "--logging-interval-step",
            type=int,
            default=default_obj.logging_interval_step,
            help="Log to Tensorboard/Wandb every N steps.",
        )

        return parser
