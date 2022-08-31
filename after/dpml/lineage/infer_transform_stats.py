import pandas as pd
import os.path as osp

from .analysis import TransformStats

test_dir_pth = "./results_a2t_mlm_word.8_n5_sst2/"

test_df = pd.read_csv(osp.join(test_dir_pth, 'out_human.csv'))



class InferTransformStats:
    def __init__(self, log_file_pth = '../results_a2t_sst2/log.csv', features = ["morph", "pos_", "dep_", "contextual_sentiment"]):
        self.test_df = pd.read_csv(log_file_pth)
        self.test_edit_summary = TransformStats(feature_names=features)
        self.test_edit_summary.populate_edits_with_df(self.test_df)
        self.test_edit_summary.get_stats()


    # add or update the human label of a datatable row
    def update_human_label_by_idx(self, index, new_label):
        return self.test_edit_summary.update_human_label(index, new_label)

    # get the transform stats dataframe of a feature (or all features when feature=None)
    def get_transform_df(self, feature_name=None):
        if feature_name is None:
            return self.test_edit_summary.stats_df
        else:
            return self.test_edit_summary.stats_df[feature_name]