"""
AnalysisArgs Class
===================
"""


from dataclasses import dataclass

from .model_args import ModelArgs

EXTRACTION_STRATEGY_NAMES = {
    "top_n":  {"worst": False},
    "worst_n": {"worst": True},
}


@dataclass
class AnalysisArgs:
    """Arguments for performing transformation lineage analysis.
    """

    input_dir: str
    extraction_strategy: str = "top_n"
    top_n_number: int = 5
    prediction_same_constraint: bool = True
    

    @classmethod
    def _add_parser_args(cls, parser):
        parser.add_argument(
            "--input-dir",
            type=str,
            help="Path of input CSV file to analysis.",
        )
        parser.add_argument(
            "--extraction-strategy",
            help="Strategy to extract transforms from test data",
            type=str,
            default="top-n",
            choices=EXTRACTION_STRATEGY_NAMES.keys(),
        )
        parser.add_argument(
            "--top-n-number",
            help="Number of top/worst N transforms to be extracted",
            type=int,
            default=5,
        )
        parser.add_argument(
            "--pred-same-constraint",
            default=False,
            action="store_true",
            help="Only perform reversion that won't change model predictions for perturbed texts",
        )

        parser = ModelArgs._add_parser_args(parser)


        return parser