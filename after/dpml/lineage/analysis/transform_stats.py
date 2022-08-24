from collections import defaultdict
import difflib

from .spacy_features import SpacyFeatures
from ..utils import compute_suspicious_score


class TransformStats:
    def __init__(self, feature_names=["morph", "lemma_", "pos_", "dep_", "static_sentiment"]):
        self.feature_names = feature_names
        self.original_spacy_docs = None
        self.transformed_spacy_docs = None
        self.edits = {}
        self.texts = {}
        self.total_pass = 0
        self.total_fail = 0
        self.misclassify = False

    def add_edit(self, feature_name, op, from_feat, to_feat, label_pair, edit_info, human_label=None):
        if human_label == 'Positive':
            self.total_pass += 1
            human_label = 1
        elif human_label == 'Negative':
            self.total_fail += 1
            human_label = 0
        else:
            human_label = None

        if feature_name not in self.edits:
            self.edits[feature_name] = defaultdict(dict)
        if (op, from_feat, to_feat) not in self.edits[feature_name]:
            self.edits[feature_name][(op, from_feat, to_feat)] = defaultdict(list)

        if label_pair is not None:
            self.edits[feature_name][(op, from_feat, to_feat)][label_pair].append(edit_info)
        if human_label is not None:
            self.edits[feature_name][(op, from_feat, to_feat)][human_label].append(edit_info)

    def populate_edits_with_df(self, df):

        original_texts = df['original_text'].values.tolist()
        perturbed_texts = df['perturbed_text'].values.tolist()

        self.original_spacy_docs = SpacyFeatures(original_texts, self.feature_names)
        from_tokens, from_features_dict = self.original_spacy_docs.extract_token_tags()

        self.transformed_spacy_docs = SpacyFeatures(perturbed_texts, self.feature_names)
        to_tokens, to_features_dict = self.transformed_spacy_docs.extract_token_tags()

        for i in range(len(to_tokens)):
            if 'result_type' in df.columns and df.loc[i]['result_type'] == 'Skipped':
                continue

            seq = difflib.SequenceMatcher(None, from_tokens[i], to_tokens[i])
            edits = seq.get_opcodes()

            label_pair = None
            self.misclassify = False
            if 'original_output' in df.columns and 'perturbed_output' in df.columns:
                original_label = eval(df.loc[i]['original_output'])
                perturbed_label = eval(df.loc[i]['perturbed_output'])
                label_pair = (original_label, perturbed_label)

                self.misclassify = True                    

            gt_label = df.loc[i]['ground_truth_output']
            if 'human' in df.columns:
                human_label = df.loc[i]['human']
            else:
                human_label = None

            for op, from_start, from_end, to_start, to_end in edits:
                if from_end <= from_start:
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
                                        (i, from_span, to_span, gt_label), human_label)

    def get_edit_freqs(self):
        self.edit_freqs = {}
        for feature in self.edits.keys():
            for edit in self.edits[feature].keys():
                for label_pair in self.edits[feature][edit].keys():
                    if feature not in self.edit_freqs:
                        self.edit_freqs[feature] = defaultdict(list)
                    self.edit_freqs[feature][label_pair].append( \
                        (len(self.edits[feature][edit][label_pair]), edit)
                        )
    
        return self.edit_freqs

    def print_edit_freqs(self):
        for feature in self.edit_freqs.keys():
            print(feature)
        for label_pair in self.edit_freqs[feature].keys():
            print(label_pair)
            self.edit_freqs[feature][label_pair] = sorted(
                self.edit_freqs[feature][label_pair], key=lambda x: x[0], reverse=True)
            for edit in self.edit_freqs[feature][label_pair]:
                if edit[0] >= 10:
                    print(f"\t{edit}")
        print()

    def get_stats(self):
        label_percentage = {}
        feature_sus_scores = {}
        misclassify_probs = {}
        for feature in self.edit_freqs.keys():
            label_percentage[feature] = {}
            feature_sus_scores[feature] = {}
            if self.misclassify:
                misclassify_probs[feature] = {}

            for label_pair in self.edit_freqs[feature].keys():
                edits_dict = {}
                for edit in self.edit_freqs[feature][label_pair]:
                    edits_dict[edit[1]] = edit[0]              

                label_percentage[feature][label_pair] = edits_dict
              
        for feature in label_percentage.keys():
            
            for label_pair in label_percentage[feature].keys():
                if isinstance(label_pair, tuple) and label_pair[0] != label_pair[1]:
                    original_pair = (label_pair[0], label_pair[0])
                    
                    for edit in label_percentage[feature][label_pair].keys():
                        cur_percent = label_percentage[feature][label_pair][edit]
                        if edit in label_percentage[feature][original_pair]:
                            original_percent = label_percentage[feature][original_pair][edit]
                            misclassify_succsess_prob = cur_percent / (original_percent + cur_percent) * 100

                            #if misclassify_succsess_prob > 50:
                            #    print(f"\t{edit}, misclassify_prob = {cur_percent}/{original_percent + cur_percent} = {misclassify_succsess_prob:.2f}%")
                            misclassify_probs[feature][edit] = misclassify_succsess_prob
                elif label_pair == 1:

                    for edit in label_percentage[feature][label_pair].keys():
                        if 0 in label_percentage[feature] and edit in label_percentage[feature][0]:
                            fail_num = label_percentage[feature][0][edit]
                        else:
                            fail_num = 0
                            
                        pass_num = label_percentage[feature][1][edit]

                        sus_score = compute_suspicious_score(fail_num, pass_num, 
                                                            self.total_fail, self.total_pass)
                        #if sus_score < 50:
                        #  print(f"\t{edit}, {fail_num}/{self.total_fail}:{pass_num}/{self.total_pass}: sus_score = {sus_score:.2f}%")
                        feature_sus_scores[feature][edit] = sus_score

                elif label_pair == 0:

                    for edit in label_percentage[feature][label_pair].keys():
                        if 1 in label_percentage[feature] and edit in label_percentage[feature][1]:
                            pass_num = label_percentage[feature][1][edit]
                        else:
                            pass_num = 0
                            
                        fail_num = label_percentage[feature][0][edit]

                        sus_score = compute_suspicious_score(fail_num, pass_num, 
                                                            self.total_fail, self.total_pass)
                        #if sus_score < 50:
                        #  print(f"\t{edit}, {fail_num}/{self.total_fail}:{pass_num}/{self.total_pass}: sus_score = {sus_score:.2f}%")
                        feature_sus_scores[feature][edit] = sus_score

        self.feature_sus_scores = feature_sus_scores
        if len(misclassify_probs) != 0:
            self.misclassify_probs = misclassify_probs
        else:
            self.misclassify_probs = misclassify_probs = None

        return feature_sus_scores, misclassify_probs

    def get_top_edits(self, top_n=5, reverse=False, verbose=False):
        extracted_transforms = {}
        for feature_name in self.feature_names:
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