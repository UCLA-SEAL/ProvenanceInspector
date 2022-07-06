from lineage.le_target import LeTarget
import nltk
from collections import OrderedDict

from lineage.le_text import LeText
from .logger import TransformationLogger
from .provenance import ProvenanceFactory

from .config import *

class LeRecord:
    """
    A container class that contains a pair of LeText and LeTarget object, which is
    same as a single row/instance in the dataset.

    Args:
       text (string): The string that this ``LeText`` represents
       granularity (string): Specifies the default level at which 
            lineage should be tracked. Value must be in:
                ['paragraph', 'sentence', 'word', 'character']
       le_attrs (dict): Dictionary of various attributes stored while 
            transforming the underlying text. 
    """
    sent_tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer()
    SPLIT_TOKEN = "<SPLIT>"
    transform_logger = None

    def __init__(self, text_input, le_target=None, le_attrs=None):
        self._id = None

        self._le_text = None
        self._le_target = None
        self._target = None
        self._text_input = None

        # Read in ``text_input`` as a string or OrderedDict.
        if isinstance(text_input, LeText):
            self._le_text = text_input
        elif isinstance(text_input, (str,OrderedDict)):
            self._text_input = text_input
        else:
            raise TypeError(
                f"Invalid text_input type {type(text_input)} (required LeText, str or OrderedDict)"
            )

        if le_target is None or isinstance(le_target, LeTarget):
            self._le_target = le_target
        else:
            self._target = le_target
            
        # Format text inputs.
        if le_attrs is None:
            self.le_attrs = dict()
        elif isinstance(le_attrs, dict):
            self.le_attrs = le_attrs
        else:
            raise TypeError(f"Invalid type for le_attrs: {type(le_attrs)}")

        if USE_LOG and not LeRecord.transform_logger:
            LeRecord.transform_logger = TransformationLogger(dirname='../results/')

        self.le_attrs.setdefault("transformation_provenance", ProvenanceFactory.get_provenance('transformation'))
        self.le_attrs.setdefault("feature_provenance", ProvenanceFactory.get_provenance('feature', feature_name="edit_seq"))
        self.le_attrs.setdefault("prev", None)
    


    def __eq__(self, other):
        """Compares two LeRecord instances, making sure that they also share
        the same lineage attributes.
        """
        if self.text != other.text and self.target != other.target:
            return False
        if self.le_attrs != other.le_attrs:
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

        for output_record in transformed_texts:

            transformation_type = transformation.__class__.__name__
            
            new_le_attrs = {
                "transformation_provenance": self.le_attrs["transformation_provenance"].add_provenance(transformation),
                "prev": self
            }

            new_text, new_target = self.generate_new_record(output_record.le_text, new_le_attrs=new_le_attrs)
            output_record._le_text = new_text
            output_record.le_attrs = new_le_attrs

            output_record._le_target = new_target

            if USE_LOG:
                LeRecord.transform_logger.log_transformation(self, output_record)

        if USE_LOG:
            LeText.text_logger.flush()
            if LeTarget.label_logger:
                LeTarget.label_logger.flush()
            LeRecord.transform_logger.flush()
        return transformed_texts


    def generate_new_record(self, new_text, new_target=None, new_le_attrs=None, granularity=None):
        #print(self.le_text)
        new_text = self.le_text.generate_new_text(new_text, new_le_attrs=new_le_attrs, granularity=granularity)
        if not self.le_target:
            new_target = None
        else:
            new_target = self.le_target.generate_new_target(new_target, new_le_attrs=new_le_attrs) 
        return (new_text, new_target)


    @property
    def text_id(self):
        if self.le_text:
            return self.le_text.id
        else:
            return -1


    @property
    def target_id(self):
        if self.le_target:
            return self.le_target.id
        else:
            return -1


    @property
    def text(self):
        return self.le_text.text


    @property
    def target(self):
        return self.le_target.target


    @property
    def le_text(self):
        if self._le_text is None:
            self._le_text = LeText(self._text_input, le_attrs={'src': True})

        return self._le_text


    @property
    def le_target(self):
        if self._le_target is None:
            if self._target is None:
                return None
            else:
                self._le_target = LeTarget(self._target, le_attrs={'src': True})

        return self._le_target


    @property
    def num_texts(self):
        return 0


    @property
    def words(self):
        if not self._words:
            self._words = list(map(lambda i: self.tokens[i], self.token_word_inds))
        return self._words


    def __getattr__(self, attr):
        if attr in self.le_attrs:
            return self.le_attrs[attr]
        else:
            return self.__getattribute__(attr)

    def __str__(self):
        return self.text

    def __repr__(self):
        class_name = self.__class__.__name__
        return f'<{class_name}:\n\t text="{self.text}",\n\t target="{self.target}",\n\t le_attrs={self.le_attrs}>'
        