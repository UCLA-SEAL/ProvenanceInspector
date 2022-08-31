import os.path as osp
import pandas as pd

from .transform_stats import TransformStats
from .transform_revert import TransformReversion


class Reverter:
    def __init__(self, input_dir, pred_model):
        self.pred_model = pred_model
        self.collate_fn = lambda x: 0 if x['label'] == 'LABEL_0' else 1

        self.test_dir_pth = input_dir
        self.train_dir_pth = self.test_dir_pth + '_train'
        self.test_df = pd.read_csv(osp.join(self.test_dir_pth, 'out_human.csv'))

        self.test_edit_summary = TransformStats(feature_names=["morph", "pos_", "dep_", "contextual_sentiment"])
        self.test_edit_summary.populate_edits_with_df(self.test_df)
        self.test_edit_summary.get_stats()
        self.test_edit_summary.save_stats_df(osp.join(self.test_dir_pth, 'stats/'))
        
        if osp.exists(osp.join(self.train_dir_pth, 'log.csv')):
            self.train_df = pd.read_csv(osp.join(self.train_dir_pth, 'log.csv'))[
                        ['original_text', 'perturbed_text', 'original_output',
                        'perturbed_output', 'ground_truth_output',
                        'result_type']]
        
            self.train_edit_summary = TransformStats(feature_names=["morph", "pos_", "dep_", "contextual_sentiment"])
            self.train_edit_summary.populate_edits_with_df(self.train_df)
            self.train_edit_summary.get_stats()
            self.train_edit_summary.save_stats_df(osp.join(self.train_dir_pth, 'stats/'))
        else:
            self.train_edit_summary = None


    def revert(self, top_n_number=10, worst=False, pred_same_constraint=False):

        exctracted_edits = self.test_edit_summary.get_top_edits(top_n=top_n_number, reverse=worst, verbose=True)

        file_name = 'reverted_text.csv'

        if pred_same_constraint:
            file_name = 'false_' + file_name

        if worst:
            file_name = 'worst_' + file_name
        

        test_reversion = TransformReversion(self.test_edit_summary)

        if worst:
            selected_edits = test_reversion.revert_worst_edits()
        else:
            selected_edits = test_reversion.revert_nontop_edits()

        test_reversion.model_prediction_change_check(self.pred_model, self.collate_fn, no_result_changing=pred_same_constraint)
        test_reversion.save_reverted_texts(osp.join(self.test_dir_pth, file_name))

        
        if self.train_edit_summary is not None:
            train_reversion = TransformReversion(self.train_edit_summary)

            if worst:
                train_reversion.revert_exclude_transforms(selected_edits)
            else:
                train_reversion.revert_include_transforms(selected_edits)
            train_reversion.model_prediction_change_check(self.pred_model, self.collate_fn, no_result_changing=pred_same_constraint)

            train_reversion.save_reverted_texts(osp.join(self.train_dir_pth, file_name))