import numpy as np
import nltk
import difflib
from .utils.text import diff_text
import itertools

class LeText:
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

    def __init__(self, text_input, granularity="word", le_attrs=None):
        self._id = None

        # Read in ``text_input`` as a string .
        if isinstance(text_input, str):
            self._text= text_input
        else:
            raise TypeError(
                f"Invalid text_input type {type(text_input)} (required str)"
            )

        if granularity in ['paragraph', 'sentence', 'word', 'character']:
          
            self.granularity = granularity
        else:
            raise TypeError(
                f"Invalid granularity {granularity} (must be one of the \
                following: ['paragraph', 'sentence', 'word', 'character'])"
            )
        # Process input lazily.
        self._chars = None
        self._words = None
        self._sents = None
        self._paras = None
        # Format text inputs.
        if le_attrs is None:
            self.le_attrs = dict()
        elif isinstance(le_attrs, dict):
            self.le_attrs = le_attrs
        else:
            raise TypeError(f"Invalid type for le_attrs: {type(le_attrs)}")

        # Lineage Attributes
        self.le_attrs.setdefault("granularity", self.granularity)

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

    def apply(self, fn, granularity="word"):
        """
        Applies fn(self.text), tracking the transformation info and output as
        a new LeText instance with a reference back to the source LeText.
        """

        # apply the provided function to the text stored in LeText
        output_text = fn(self.text)

        # find changes between self.text and output_text
        parsed_a, parsed_b, changes = diff_text(self.text, output_text, granularity)

        new_le_attrs = {
            "granularity": self.granularity,
            "changes": changes,
            "transformation": fn,
            "previous": self # current LeText
        }
        
        output_LeText = LeText(output_text, 
                               granularity=granularity,
                               le_attrs=new_le_attrs)
        
        return output_LeText

    def parse_text(self):
        if self.granularity == "paragraph":
            parsed_text = self.text.split('\n')
        elif self.granularity == "sentence":
            parsed_text = self.sent_tokenizer.tokenize(self.text)
        elif self.granularity == "word":
            parsed_text = self.text.split()
        elif self.granularity == "character":
            parsed_text = list(self.text)
        return parsed_text

    @property
    def column_labels(self):
        """Returns the labels for this text's columns.

        For single-sequence inputs, this simply returns ['text'].
        """
        return list(self._text_input.keys())

    @property
    def id(self):
        if not self._id:
            self._id = next(LeText.id_iter)

        return self._id

    @property
    def chars(self):
        if not self._chars:
            self._chars = list(self.text)
        return self._chars

    @property
    def words(self):
        if not self._words:
            self._words = self.text.split()
        return self._words

    @property
    def sents(self):
        if not self._sents:
            self._sents = self.sent_tokenizer(self.text)
        return self._sents

    @property
    def paras(self):
        if not self._paras:
            self._paras = self.text.split("\n")
        return self._paras

    @property
    def num_chars(self):
        """Returns the number of characters in the text."""
        return len(self.chars)

    @property
    def num_words(self):
        """Returns the number of words in the text."""
        return len(self.words)

    @property
    def num_sents(self):
        """Returns the number of sentences in the text."""
        return len(self.sents)

    @property
    def num_paras(self):
        """Returns the number of paragraphs in the text."""
        return len(self.paras)

    @property
    def num_units(self):
        """Returns the number of "units" of text given the default granularity."""
        if self.granularity == "paragraph":
            return self.num_paras
        elif self.granularity == "sentence":
            return self.num_sents
        elif self.granularity == "word":
            return self.num_words
        elif self.granularity == "character":
            return self.num_chars

    @property
    def text(self):
        """Represents full text input.

        Multiply inputs are joined with a line break.
        """
        return self._text

    def __str__(self):
        return self.text

    def __repr__(self):
        class_name = self.__class__.__name__
        return f'<{class_name} "{self.text}": le_attrs={self.le_attrs}>'