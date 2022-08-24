from collections import defaultdict
import pandas as pd
import os.path as osp

from .spacy_features import SpacyFeatures

class bcolors:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class TransformReversion:
    def __init__(self, edit_summary):
        self.edit_summary = edit_summary
        self.size = self.edit_summary.size
        self.revert_docs = {} # reversed_texts
        self._revert_texts = None
        self._original_texts = None # final_texts
        self._labels = None

    @property
    def revert_texts(self):
        if self._revert_texts is None:
            self._revert_texts = []
            for i in range(self.size):
                if i in self.revert_docs:
                    self._revert_texts.append(self.revert_docs[i].text)
                else:
                    self._revert_texts.append(self.edit_summary.transformed_spacy_docs.docs[i].text)
        return self._revert_texts

    @property
    def original_texts(self):
        if self._original_texts is None:
            self._original_texts = []
            for i in range(self.size):
                self._original_texts.append(self.edit_summary.transformed_spacy_docs.docs[i].text)
        return self._original_texts

    @property
    def labels(self):
        if self._labels is None:
            self._labels = []
            for i in range(self.size):
                self._labels.append(self.edit_summary.gt_labels[i])
        return self._labels
    
    # need self.edit_summary to be populated
    def revert_transform_types(self, feature_name, exclude_transforms=None, include_transforms=None, verbose=False):
        for transform in self.edit_summary.edits[feature_name].keys():
            if exclude_transforms is not None and transform not in exclude_transforms:
                continue
            if include_transforms is not None and transform in include_transforms:
                continue

            for label_pair in self.edit_summary.edits[feature_name][transform].keys():
                if isinstance(label_pair, int):
                    continue
                
                # TODO: need to have lineage to make this reversion actually sorted
                for (i, from_span, to_span, gt_label) in sorted(
                    self.edit_summary.edits[feature_name][transform][label_pair], 
                    key=lambda x: (x[0], x[2]), reverse=True):
                    before_text = self.edit_summary.original_spacy_docs.docs[i]
                    left1 = from_span[0]
                    right1 = from_span[1]
                    
                    if verbose:
                        original_highlight_text = before_text[:left1].text_with_ws + \
                            bcolors.GREEN + before_text[left1:right1].text_with_ws +bcolors.ENDC + \
                            before_text[right1:].text
                        print(original_highlight_text)

                    after_text = self.edit_summary.transformed_spacy_docs.docs[i]
                    left2 = to_span[0]
                    right2 = to_span[1]
                    
                    if verbose:
                        after_highlight_text = after_text[:left2].text_with_ws + \
                            bcolors.RED + after_text[left2:right2].text_with_ws +bcolors.ENDC + \
                            after_text[right2:].text
                        print(after_highlight_text)
                        print()

                    if i not in self.revert_docs:
                        self.revert_docs[i] = after_text
                        self.original_texts[i] = after_text.text

                    self.revert_docs[i] = SpacyFeatures.model.make_doc(
                        self.revert_docs[i][:left2].text_with_ws + before_text[left1:right1].text_with_ws + \
                        self.revert_docs[i][right2:].text)
            
    def revert_nontop_edits(self):
        self.revert_include_transforms(self.edit_summary.extracted_top_transforms)
        return self.edit_summary.extracted_top_transforms

    def revert_worst_edits(self):
        self.revert_exclude_transforms(self.edit_summary.extracted_worst_transforms)
        return self.edit_summary.extracted_worst_transforms

    def revert_exclude_transforms(self, exclude_transforms):
        for feature_name in exclude_transforms.keys():
            for stat_type in exclude_transforms[feature_name].keys():
                self.revert_transform_types(feature_name, exclude_transforms=exclude_transforms[feature_name][stat_type])

    def revert_include_transforms(self, include_transforms):
        for feature_name in include_transforms.keys():
            for stat_type in include_transforms[feature_name].keys():
                self.revert_transform_types(feature_name, include_transforms=include_transforms[feature_name][stat_type])


    def model_prediction_change_check(self, pipeline, label_map_func, no_result_changing=False):
        new_results = pipeline(self.revert_texts)
        self.new_results = list(map(label_map_func, new_results))

        self.comp_result_indices = defaultdict(list)

        for i, (old, new) in enumerate(zip(self.labels, self.new_results)):
            self.comp_result_indices[(old, new)].append(i)

        comp_result_freqs = {}
        
        for result_pair in self.comp_result_indices.keys():
            comp_result_freqs[result_pair] = len(self.comp_result_indices[result_pair])

            if result_pair[0] != result_pair[1] and no_result_changing:
                for id in self.comp_result_indices[result_pair]:
                    self.revert_texts[id] = self.original_texts[id]

        print('transformed labels vs new predictions')
        print(comp_result_freqs)
        return comp_result_freqs

    def save_reverted_texts(self, save_pth):
        pd.DataFrame({'reverted_text':self.revert_texts, 
            'label': self.labels}).to_csv(osp.join(save_pth), \
            mode='w', index=False)