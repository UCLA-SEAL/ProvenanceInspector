from collections import defaultdict
import difflib
import numpy as np
import pandas as pd
import re

from .spacy_features import SpacyFeatures
from ..utils import compute_suspicious_score

def get_softlabel_class(pos_val, class_n=5):
    if pos_val in {0,1}:
        return pos_val

    intervals = np.arange(0, 1, 1 / class_n) + (.5 / class_n)
    interval_id = np.argmin(np.abs(intervals - pos_val))
    return intervals[interval_id]

def filter_nonnumeric_char(text):
    return re.sub("[^0-9.]", "", text)

class TransformStats:
    def __init__(self, feature_names=["morph", "lemma_", "pos_", "dep_", "static_sentiment"]):
        self.feature_names = feature_names
        self.original_spacy_docs = None
        self.transformed_spacy_docs = None
        self.gt_labels = {}
        self.size = 0
        self.edits = {}
        self.change_freqs = {}
        self.texts = {}
        self.total_pass = defaultdict(int)
        self.total_fail = defaultdict(int)
        self.misclassify = False
        self.stats_df = {}

    def add_edit(self, feature_name, op, from_feat, to_feat, label_pair, edit_info, changed, human_label=None):
        if human_label == 'Positive':
            self.total_pass[feature_name] += 1
            human_label = 1
        elif human_label == 'Negative':
            self.total_fail[feature_name] += 1
            human_label = 0
        else:
            human_label = None
            
        if feature_name not in self.change_freqs:
            self.change_freqs[feature_name] = defaultdict(int)
        if (op, from_feat, to_feat) not in self.change_freqs[feature_name] and changed:
            self.change_freqs[feature_name][(op, from_feat, to_feat)] += 1

        if feature_name not in self.edits:
            self.edits[feature_name] = defaultdict(dict)
        if (op, from_feat, to_feat) not in self.edits[feature_name]:
            self.edits[feature_name][(op, from_feat, to_feat)] = defaultdict(list)

        if label_pair is not None:
            self.edits[feature_name][(op, from_feat, to_feat)][label_pair].append(edit_info)
        
        self.edits[feature_name][(op, from_feat, to_feat)][human_label].append(edit_info)


    def add_transform(self, label_pair, transform_hist, edit_info, changed, human_label=None):
        if human_label == 'Positive':
            self.total_pass['transform'] += 1
            self.total_pass['transform_label'] += 1
            human_label = 1
        elif human_label == 'Negative':
            self.total_fail['transform'] += 1
            self.total_fail['transform_label'] += 1
            human_label = 0
        else:
            human_label = None
            
        
        if 'transform' not in self.change_freqs:
            self.change_freqs['transform'] = defaultdict(int)
        for transform in transform_hist:
            if changed:
                self.change_freqs['transform'][transform] += 1

        if 'transform' not in self.edits:
            self.edits['transform'] = defaultdict(dict)
            self.edits['transform_label'] = defaultdict(dict)
        for transform in transform_hist:
            transform_label = (transform, *label_pair)
            if transform not in self.edits['transform']:
                self.edits['transform'][transform] = defaultdict(list)
            if transform_label not in self.edits['transform_label']:
                self.edits['transform_label'][transform_label] = defaultdict(list)

            if label_pair is not None:
                self.edits['transform'][transform][label_pair].append(edit_info)
                self.edits['transform_label'][transform_label][label_pair].append(edit_info)

            self.edits['transform'][transform][human_label].append(edit_info)
            self.edits['transform_label'][transform_label][human_label].append(edit_info)
            


    def populate_edits_with_df(self, df):

        original_texts = df['original_text'].values.tolist()
        perturbed_texts = df['perturbed_text'].values.tolist()

        print('generating original spacy docs...')
        self.original_spacy_docs = SpacyFeatures(original_texts, self.feature_names)
        from_tokens, from_features_dict = self.original_spacy_docs.extract_token_tags()

        print('generating transformed spacy docs...')
        self.transformed_spacy_docs = SpacyFeatures(perturbed_texts, self.feature_names)
        to_tokens, to_features_dict = self.transformed_spacy_docs.extract_token_tags()

        self.size = len(self.transformed_spacy_docs.docs)

        for i in range(len(to_tokens)):

            label_pair = None
            self.misclassify = False
            if 'original_output' in df.columns and 'perturbed_output' in df.columns:
                original_label = df.loc[i]['original_output']
                perturbed_label = df.loc[i]['perturbed_output']
                label_pair = (original_label, perturbed_label)

                self.misclassify = True

            elif 'original_label' in df.columns and 'transformed_label' in df.columns:
                original_label = float(df.loc[i]['original_label'])
                try:
                    transformed_label = eval(df.loc[i]['transformed_label'])
                    if isinstance(transformed_label, list):
                        transformed_label = transformed_label[-1]
                except:
                    transformed_label = float(df.loc[i]['transformed_label'].split()[1][:-1])
                transformed_label = get_softlabel_class(transformed_label)
                label_pair = (original_label, transformed_label)

                self.misclassify = False


            gt_label = None
            if 'ground_truth_output' in df.columns:
                gt_label = df.loc[i]['ground_truth_output']
            elif 'transformed_label' in df.columns:
                try:
                    gt_label = eval(df.loc[i]['transformed_label'])
                    if isinstance(gt_label, list):
                        gt_label = gt_label[-1]
                except:
                    gt_label = [float(filter_nonnumeric_char(x)) for x in df.loc[i]['transformed_label'].split()][-1]
            self.gt_labels[i] = int(gt_label)

            if 'human' in df.columns:
                human_label = df.loc[i]['human']
            else:
                human_label = None
                
            changed = from_tokens[i] == to_tokens[i]

            transform_hist = None
            if 'transform' in df.columns:
                transform_hist = eval(df.loc[i]['transform'])
                self.add_transform(label_pair, transform_hist, (i, (0, len(self.original_spacy_docs.docs[i])), 
                    (0, len(self.transformed_spacy_docs.docs[i])), gt_label), changed,
                                   human_label=human_label)

            if 'result_type' in df.columns and df.loc[i]['result_type'] == 'Skipped':
                continue

            seq = difflib.SequenceMatcher(None, from_tokens[i], to_tokens[i])
            edits = seq.get_opcodes()
            
            for op, from_start, from_end, to_start, to_end in edits:
                if from_end < from_start:
                    continue
                if op == 'replace' or op == 'insert' or op == 'delete':
                    from_span = (from_start, from_end)
                    to_span = (to_start, to_end)

                    for feature in self.feature_names:
                        
                        from_feat = tuple(from_features_dict[feature][i][
                                                from_start:from_end]) 
                        to_feat = tuple(to_features_dict[feature][i][
                                                to_start:to_end])
                        
                        self.add_edit(feature, op, from_feat, to_feat, 
                                        label_pair,
                                        (i, from_span, to_span, gt_label), changed, human_label)
        if 'transform' in df.columns:
            self.feature_names += ['transform', 'transform_label']
            

    def get_stats(self):
        feature_sus_scores = {}
        misclassify_probs = {}
        total_freq = {}
        label_ratio = {}
        impact_ratio = {}
        pass_nums = {}
        fail_nums = {}
        
        for feature in self.edits.keys():
            feature_sus_scores[feature] = {}
            total_freq[feature] = {}
            label_ratio[feature] = {}
            impact_ratio[feature] = {}
            pass_nums[feature] = {}
            fail_nums[feature] = {}
            if self.misclassify:
                misclassify_probs[feature] = {}

        for feature in self.edits.keys():
            for edit in self.edits[feature].keys():
                total_pred_label_count = 0
                diff_pred_label_count = 0
                
                # Laplace smoothing 
                fail_num = 1
                pass_num = 1
                
                for label_pair in self.edits[feature][edit].keys():
                    freq = len(self.edits[feature][edit][label_pair])
                    if isinstance(label_pair, tuple):
                        old_label, new_label = label_pair
                        total_pred_label_count += freq
                        if new_label != old_label:
                            diff_pred_label_count += freq
                    elif label_pair == 1:
                        pass_num += freq
                    elif label_pair == 0:
                        fail_num += freq
                    elif label_pair is None:
                        pass
                    else:
                        raise ValueError('unsupported label addition')
                
                total_freq[feature][edit] = total_pred_label_count
                label_ratio[feature][edit] = (fail_num + pass_num - 2) / total_pred_label_count
                impact_ratio[feature][edit] = self.change_freqs[feature][edit] / total_pred_label_count
                misclassify_probs[feature][edit] = diff_pred_label_count / total_pred_label_count
                feature_sus_scores[feature][edit] = compute_suspicious_score(fail_num, pass_num, 
                                                                self.total_fail[feature], self.total_pass[feature])
                pass_nums[feature][edit] = pass_num - 1
                fail_nums[feature][edit] = fail_num - 1
        
        self.feature_sus_scores = feature_sus_scores
        self.total_freq = total_freq
        self.label_ratio = label_ratio
        self.impact_ratio = impact_ratio
        self.pass_nums = pass_nums
        self.fail_nums = fail_nums
        
        if len(misclassify_probs) != 0:
            self.misclassify_probs = misclassify_probs
        else:
            self.misclassify_probs = misclassify_probs = None
            

        for feature in self.edits.keys():
            transform_index_list = list(self.edits[feature].keys())
        
            stats_dict = {'transform': [str(t) for t in transform_index_list],
                         'total_freq': [total_freq[feature][t] for t in transform_index_list],
                         'label_ratio': [label_ratio[feature][t] for t in transform_index_list],
                         'impact_ratio': [impact_ratio[feature][t] for t in transform_index_list],
                         'fail_num': [fail_nums[feature][t] for t in transform_index_list],
                         'pass_num': [pass_nums[feature][t] for t in transform_index_list],
                         'sus_score': [feature_sus_scores[feature][t] for t in transform_index_list]}

            if misclassify_probs is not None:
                stats_dict.update({'misclassify_prob': [misclassify_probs[feature][t] for t in transform_index_list]})
            self.stats_df[feature] = pd.DataFrame.from_dict(stats_dict).set_index('transform')

        return self.stats_df
    
    def update_human_label(self, index, new_label):
        for feature in self.edits.keys():
            for edit in self.edits[feature].keys():
                self._update_human_label(index, feature, edit, new_label)
        return self.stats_df
        
        
    def _update_human_label(self, index, feature, edit, new_label):
        for old_label in list(self.edits[feature][edit].keys()):
            if old_label == new_label:
                continue
            if not isinstance(old_label, tuple):
                move_set = set()
                for edit_info in self.edits[feature][edit][old_label]:
                    edit_row_num = edit_info[0]
                    if edit_row_num == index:
                        move_set.add(edit_info)
                self.edits[feature][edit][old_label] = \
                    list(set(self.edits[feature][edit][old_label]) - move_set)
                self.edits[feature][edit][new_label] = \
                    list(set(self.edits[feature][edit][new_label]) | move_set)
                
        total_pred_label_count = self.total_freq[feature][edit]

        # Laplace smoothing 
        fail_num = 1 + len(self.edits[feature][edit][0])
        pass_num = 1 + len(self.edits[feature][edit][1])
        
        self.label_ratio[feature][edit] = (fail_num + pass_num - 2) / total_pred_label_count
        self.feature_sus_scores[feature][edit] = compute_suspicious_score(fail_num, pass_num, 
                                                        self.total_fail[feature], self.total_pass[feature])
        self.fail_nums[feature][edit] = fail_num - 1
        self.pass_nums[feature][edit] = pass_num - 1
        
        edit_str = str(edit)
        self.stats_df[feature].at[edit_str,'label_ratio'] = self.label_ratio[feature][edit]
        self.stats_df[feature].at[edit_str,'sus_score'] = self.feature_sus_scores[feature][edit]
        self.stats_df[feature].at[edit_str,'fail_num'] = self.fail_nums[feature][edit]
        self.stats_df[feature].at[edit_str,'pass_num'] = self.pass_nums[feature][edit]

        return self.stats_df
        

    def get_top_edits(self, top_n=5, reverse=False, verbose=False):
        extracted_transforms = {}
        for feature_name in self.edits.keys():
            extracted_transforms[feature_name] = {}

            if verbose:
                print(feature_name)
            sus_dict = self.feature_sus_scores[feature_name]
            least_sus = list(sorted(sus_dict.items(), key=lambda item: item[1], reverse=reverse))[:top_n]

            for i in range(len(least_sus)):
                if reverse and least_sus[i][1] < 50:
                    least_sus = least_sus[:i]
                    break
                if not reverse and least_sus[i][1] > 50:
                    least_sus = least_sus[:i]
                    break
            extracted_transforms[feature_name]['sus'] ={x[0] for x in least_sus}

            if verbose:
                if reverse:
                    print("most_sus")
                else:
                    print("least_sus:")
                for edit in least_sus:
                    print(edit)

            if self.misclassify_probs is not None:
                prob_dict = self.misclassify_probs[feature_name]

                most_succesful_attack = list(sorted(prob_dict.items(), key=lambda item: item[1], reverse=not reverse))[:top_n]

                for i in range(len(most_succesful_attack)):
                    if reverse and most_succesful_attack[i][1] > 25:
                        most_succesful_attack = most_succesful_attack[:i]
                        break

                    if not reverse and most_succesful_attack[i][1] < 25:
                        most_succesful_attack = most_succesful_attack[:i]
                        break
            
                extracted_transforms[feature_name]['misclassify'] = {x[0] for x in most_succesful_attack}

            
                if verbose:
                    if reverse:
                        print("least_successful_attack:")
                    else:
                        print("most_succuessful_attack:")
                    for edit in most_succesful_attack:
                        print(edit)

            if verbose:
                print()

        if reverse:
            self.extracted_worst_transforms = extracted_transforms
        else:
            self.extracted_top_transforms = extracted_transforms

        return extracted_transforms