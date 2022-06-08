from matplotlib.pyplot import text
import numpy as np
import difflib

class LeToken:
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

    def __init__(self, text_token, le_attrs=None):
        # Read in ``text_input`` as a string .
        if isinstance(text_token, str):
            self.text = text_token
        else:
            raise TypeError(
                f"Invalid text_token type {type(text_token)} (required str)"
            )
            
        # Format text inputs.
        if le_attrs is None:
            self.le_attrs = dict()
        elif isinstance(le_attrs, dict):
            self.le_attrs = le_attrs
        else:
            raise TypeError(f"Invalid type for le_attrs: {type(le_attrs)}")

    def get_le_attr(self, attr_name, default_val=None):
        if attr_name not in self.le_attrs:
            self.le_attrs[attr_name] = default_val

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


    def __repr__(self):
        return f'<LeToken "{self.text}">'

    def __getattr__(self, name): 
        return getattr(self.text, name)