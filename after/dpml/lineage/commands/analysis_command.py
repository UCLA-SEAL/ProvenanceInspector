"""

AnalysisCommand class
===========================

"""

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
import os.path as osp
import pandas as pd

from .lineage_command import LineageCommand

import lineage
from lineage.commands import LineageCommand
from lineage.analysis import Reverter
from lineage import AnalysisArgs, ModelArgs
from ..analysis_args import EXTRACTION_STRATEGY_NAMES

class AnalysisCommand(LineageCommand):
    """The TextAttack attack resume recipe module:

    A command line parser to resume a checkpointed attack from user
    specifications.
    """


    def run(self, args):
        if args.input_dir:

            model_wrapper = ModelArgs._create_eval_model_from_args(args)
            
            reversion_pipeline = Reverter(args.input_dir, model_wrapper)

            revert_args = {}
            if args.extraction_strategy:
                revert_args = EXTRACTION_STRATEGY_NAMES[args.extraction_strategy]

            if args.top_n_number:
                revert_args['top_n_number'] = args.top_n_number
            if args.pred_same_constraint:
                revert_args['pred_same_constraint'] = args.pred_same_constraint

            reversion_pipeline.revert(**revert_args)
        else:
            raise TypeError("Log directory was not provided.")



    @staticmethod
    def register_subcommand(main_parser: ArgumentParser):
        parser = main_parser.add_parser(
            "analysis",
            help="run analysis on lineage log",
            formatter_class=ArgumentDefaultsHelpFormatter,
        )
        parser = AnalysisArgs._add_parser_args(parser)
        parser.set_defaults(func=AnalysisCommand())
