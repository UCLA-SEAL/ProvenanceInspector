from lib2to3.pgen2 import token
from typing import List
import numpy as np
import nltk
from collections import OrderedDict
import copy

import difflib
import itertools

import textattack
from .utils.text import diff_text
from .utils import device, tokens_from_text
from .transformation_logger import TransformationLogger
from .text_logger import TextLogger


class LeRecord:
    """
    A helper class that represents a string that can be transformed, 
    tracking the transformations made to it.

    Modifying ``LeText`` instances results in the generation of new ``LeText`` 
    instances with a reference pointer (``le_attrs["previous"]``), so that 
    the full chain of transforms might be reconstructed by using this key to 
    form a linked list.

    Args:
       text (string): The string that this ``LeText`` represents
       granularity (string): Specifies the default level at which 
            lineage should be tracked. Value must be in:
                ['paragraph', 'sentence', 'word', 'character']
       le_attrs (dict): Dictionary of various attributes stored while 
            transforming the underlying text. 
    """
    id_iter = itertools.count()
    sent_tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer()
    SPLIT_TOKEN = "<SPLIT>"
    transform_logger = TransformationLogger(dirname='../results/')
    text_logger = TextLogger(dirname='../results/')

    def __init__(self, text_input, le_attrs=None):
        self._id = None

        # Read in ``text_input`` as a string or OrderedDict.
        if isinstance(text_input, str):
            self._text_input = OrderedDict([("text", text_input)])
        elif isinstance(text_input, OrderedDict):
            self._text_input = text_input
        else:
            raise TypeError(
                f"Invalid text_input type {type(text_input)} (required str or OrderedDict)"
            )
            
        # Format text inputs.
        if le_attrs is None:
            self.le_attrs = dict()
        elif isinstance(le_attrs, dict):
            self.le_attrs = le_attrs
        else:
            raise TypeError(f"Invalid type for le_attrs: {type(le_attrs)}")

        self._tokens = None
        self._token_word_inds = None

        self.le_attrs.setdefault("transformation_history", [])
        self.le_attrs.setdefault("previous", None)


    def __eq__(self, other):
        """Compares two LeText instances, making sure that they also share
        the same lineage attributes.

        Since some elements stored in ``self.le_attrs`` may be numpy
        arrays, we have to take special care when comparing them.
        """
        if not (self.text == other.text):
            return False
        if len(self.le_attrs) != len(other.le_attrs):
            return False
        for key in self.le_attrs:
            if key not in other.le_attrs:
                return False
            elif isinstance(self.le_attrs[key], np.ndarray):
                if not (self.le_attrs[key].shape == other.le_attrs[key].shape):
                    return False
                elif not (self.le_attrs[key] == other.le_attrs[key]).all():
                    return False
            else:
                if not self.le_attrs[key] == other.le_attrs[key]:
                    return False
        return True

    def __hash__(self):
        return hash(self.text)

    def apply(self, transformation, indices_to_modify=None, granularity="words"):
        """
        Applies fn(self.text), tracking the transformation info and output as
        a new LeText instance with a reference back to the source LeText.
        """

        # apply the provided function to the text stored in LeText
        transformed_texts = transformation._get_transformations(self, indices_to_modify)

        for output_text in transformed_texts:
            new_tokens, changes = self.generate_new_record(output_text.text)
            output_text._tokens = new_tokens

            transformation_type = transformation.__class__.__name__
            
            new_le_attrs = {
                "transformation_history": self.le_attrs["transformation_history"] + [f"<{transformation_type}: {indices_to_modify}>"],
                "previous": self 
            }
            output_text.le_attrs = new_le_attrs

            modified_inds = (indices_to_modify, output_text.attack_attrs["newly_modified_indices"])

            LeRecord.transform_logger.log_transformation(self.id, output_text.id, transformation_type, modified_inds, changes)

        LeRecord.text_logger.flush()
        LeRecord.transform_logger.flush()
        return transformed_texts


    def generate_new_record(self, output_text: str):
        # find changes between self.text and output_text
        old_tokens, new_tokens, changes = diff_text(self.text, output_text, tokenizer=tokens_from_text)

        for (tag, i1, i2, j1, j2) in changes:
            if tag == 'equal' and (j2 - j1) == (i2 - i1):
                for offset in range(0, j2 - j1):
                    new_tokens[j1 + offset].le_attrs = copy.deepcopy(self.tokens[i1 + offset].le_attrs)
            elif tag == 'replace' and (j2 - j1) == (i2 - i1):
                for offset in range(0, j2 - j1):
                    new_tokens[j1 + offset].le_attrs = copy.deepcopy(self.tokens[i1 + offset].le_attrs)
                    new_tokens[j1 + offset].le_attrs['ops'].append('replace')
            elif tag == 'insert':
                for j in range(j1, j2):
                    new_tokens[j].le_attrs['ops'] = ['insert']
            elif tag == 'delete':
                for i in range(i1, i2):
                    self.tokens[i].le_attrs['ops'].append('delete')
    
        return new_tokens, changes


    @property
    def column_labels(self):
        """Returns the labels for this text's columns.

        For single-sequence inputs, this simply returns ['text'].
        """
        return list(self._text_input.keys())

    @property
    def id(self):
        if not self._id:
            self._id = next(LeRecord.id_iter)
            LeRecord.text_logger.log_text(self._id, self.printable_text(), self.le_attrs)
            #LeRecord.text_logger.flush()
        return self._id


    @property
    def num_texts(self):
        return 0
        

    @property
    def text(self):
        """Represents full text input.

        Multiply inputs are joined with a line break.
        """
        return "\n".join(self._text_input.values())


    @property
    def words(self):
        if not self._words:
            self._words = list(map(lambda i: self.tokens[i], self.token_word_inds))
        return self._words


    @property
    def token_word_inds(self):
        if self.tokens and not self._token_word_inds:
            self._token_word_inds =  [ i for i in range(len(self.tokens)) if self.tokens[i].le_attrs['is_word']]

        return self._token_word_inds

    @property
    def tokens(self):
        if not self._tokens:
            cur_text = LeRecord.SPLIT_TOKEN.join(self._text_input.values())

            self._tokens = tokens_from_text(cur_text)
            self._token_word_inds = [ i for i in range(len(self._tokens)) if self._tokens[i].le_attrs['is_word']]

            self.attack_attrs["src"] = True

        return self._tokens

    def printable_tokens(self, key_color="bold", key_color_method=None):

        token_strings = list(map(str, self.tokens))

        # For single-sequence inputs, don't show a prefix.
        if len(self._text_input) == 1:
            return "".join(token_strings)
        # For multiple-sequence inputs, show a prefix and a colon. Optionally,
        # color the key.
        else:
            if key_color_method:

                def ck(k):
                    return textattack.shared.utils.color_text(
                        k, key_color, key_color_method
                    )

            else:

                def ck(k):
                    return k

            text_values = "".join(token_strings).split(LeRecord.SPLIT_TOKEN)

            return f"ID: {self.id}" + "\n".join(
                f"{ck(key.capitalize())}: {value}"
                for key, value in zip(self._text_input.keys(), text_values)
            )

    def __str__(self):
        return f'<"{self.text}" ({self.le_attrs})>'

    def __repr__(self):
        class_name = self.__class__.__name__
        return f'<{class_name} "{self.text}">'
        