from lib2to3.pgen2 import token
from typing import List
from lineage.le_text import LeText
import numpy as np
import nltk
from collections import OrderedDict

import difflib
import itertools

from .logger import TransformationLogger, TextLogger


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

        self._le_text = None

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
            new_text = self.generate_new_record(output_text.text)
            output_text._le_text = new_text

            transformation_type = transformation.__class__.__name__
            
            new_le_attrs = {
                "transformation_history": self.le_attrs["transformation_history"] + [f"<{transformation_type}: {indices_to_modify}>"],
                "previous": self 
            }
            output_text.le_attrs = new_le_attrs

            modified_inds = (indices_to_modify, output_text.attack_attrs["newly_modified_indices"])

            LeRecord.transform_logger.log_transformation(self.id, output_text.id, transformation_type, modified_inds)

        LeRecord.text_logger.flush()
        LeRecord.transform_logger.flush()
        return transformed_texts


    def generate_new_record(self, output_text: str):
        #print(self.le_text)
        return self.le_text.generate_new_text(output_text)


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
    def le_text(self):
        cur_text = LeText.SPLIT_TOKEN.join(self._text_input.values())
        if self._le_text is None:
            self._le_text = LeText(cur_text, le_attrs={'src': True})

        return self._le_text


    @property
    def words(self):
        if not self._words:
            self._words = list(map(lambda i: self.tokens[i], self.token_word_inds))
        return self._words

    def __str__(self):
        return self.text

    def __repr__(self):
        class_name = self.__class__.__name__
        return f'<{class_name} "{self.text}": le_attrs={self.le_attrs}>'
        