import numpy as np
from textattack.shared.attacked_text import AttackedText

def text_word_diff(src_text, transformed_text, indices_to_modify):
    src_idx_modified = src_text.attack_attrs["modified_indices"]
    transformed_idx_modified = transformed_text.attack_attrs["modified_indices"]

    indices_unchanged = []
    for i in range(len(src_text.words)):
        if i not in indices_to_modify:
            indices_unchanged.append(i)
    
    if len(indices_unchanged) == 0:
        return (indices_to_modify, np.arange(len(transformed_text.words)))

    unchanged_sequence = np.array(src_text.words)[indices_unchanged]
    
    idx = 0
    modified_inds = []
    for i in range(len(transformed_text.words)):
        if idx < len(unchanged_sequence) and unchanged_sequence[idx] == transformed_text.words[i]:
            idx += 1
        else:
            modified_inds.append(i)

    return (indices_to_modify, np.array(modified_inds))
    '''
    lcs = lcs(src_text.words, transformed_text.words) # list of common subseuqence words    

    src_idx_modified = src_text.attack_attrs["original_index_map"]
    transformed_idx_modified = transformed_text.attack_attrs["original_index_map"]

    assert len(src_idx_modified.keys()) == len(transformed_idx_modified.keys())

    new_indices = []
    cur_text = transformed_text
    while "last_transformation" not in cur_text and "previous_attacked_text" in cur_text.attack_attrs:
        new_indices.append(cur_text['newly_modified_indices'])        

        cur_text = transformed_text["previous_attacked_text"]

    modified_id_mappings = 
    for n_idx in new_indices:

    

    for original_i in src_idx_map.keys():
        if src_idx_map[original_i] != transformed_idx_map[original_i]:

    
    

    '''

def lcs(X, Y):
    m = len(X)
    n = len(Y)

    L = [[0 for i in range(n+1)] for j in range(m+1)]
 
    # Following steps build L[m+1][n+1] in bottom up fashion. Note
    # that L[i][j] contains length of LCS of X[0..i-1] and Y[0..j-1]
    for i in range(m+1):
        for j in range(n+1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif X[i-1] == Y[j-1]:
                L[i][j] = L[i-1][j-1] + 1
            else:
                L[i][j] = max(L[i-1][j], L[i][j-1])
 
        # Create a string variable to store the lcs string
    lcs = []
 
    # Start from the right-most-bottom-most corner and
    # one by one store characters in lcs[]
    i = m
    j = n
    while i > 0 and j > 0:
 
        # If current character in X[] and Y are same, then
        # current character is part of LCS
        if X[i-1] == Y[j-1]:
            lcs.append(X[i-1])
            i -= 1
            j -= 1
 
        # If not same, then find the larger of two and
        # go in the direction of larger value
        elif L[i-1][j] > L[i][j-1]:
            i -= 1
             
        else:
            j -= 1
 
    # We traversed the table in reverse order
    # LCS is the reverse of what we got
    lcs = lcs[::-1]
    return lcs

def is_subseq(s: AttackedText, t: AttackedText) -> bool:
    LEFT_BOUND, RIGHT_BOUND = len(s), len(t)

    def rec_is_subseq(left_index, right_index):
        # base cases
        if left_index == LEFT_BOUND:
            return True
        if right_index == RIGHT_BOUND:
            return False
        # consume both strings or just the target string
        if s[left_index] == t[right_index]:
            left_index += 1
        right_index += 1

        return rec_is_subseq(left_index, right_index)

    return rec_is_subseq(0, 0)