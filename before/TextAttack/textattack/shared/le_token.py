from matplotlib.pyplot import text
import numpy as np
from .le_text import LeText

class LeToken(LeText):
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
        super().__init__(text_token, le_attrs=le_attrs)

        self.le_attrs.setdefault("ops", [])
