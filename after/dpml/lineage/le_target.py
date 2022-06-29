from .logger import LabelLogger
from .config import *

class LeTarget:
    """
    A helper class that represents target data (e.g. most likely a label in the 
    case of classification, but could also be text or some other arbitary
    data structure for other tasks). This target can be transformed, as with 
    sibylvariant augmentations, and this class tracks changes to the target.

    Modifying ``LeTarget`` instances results in the generation of new ``LeTarget`` 
    instances with a reference pointer (``le_attrs["previous"]``), so that 
    the full chain of transforms might be reconstructed by using this key to 
    form a linked list.

    Args:
       target (any): The data which may be transformed
       le_attrs (dict): Dictionary of various attributes stored while 
            transforming the underlying data. 

    TODO:
        - type check target:
            - if isinstance(target, int):   e.g. classification
            - if isinstance(target, float): e.g. regression
            - if ifinstance(target, str):   e.g. seq2seq (save as LeText?)
            - if ifinstance(target, list):  e.g. multi-label classification, soft-label
            - if ifinstance(target, dict):  e.g. pose detection
        - determine how to do diff-ing for other data types
    """

    label_logger = None

    def __init__(self, target, le_attrs=None):
        self._id = None

        self.target = target
        self.target_type = type(target)
        
        # create le_attrs if none exists
        if le_attrs is None:
            self.le_attrs = dict()
        elif isinstance(le_attrs, dict):
            self.le_attrs = le_attrs
        else:
            raise TypeError(f"Non-dict provided for le_attrs: {type(le_attrs)}.")

        if USE_LOG and not LeTarget.label_logger:
            LeTarget.label_logger = LabelLogger(dirname='../results/')

    def __eq__(self, other):
        """Compares two LeTarget instances, making sure that they also share
        the same lineage attributes.

        Since some elements stored in ``self.le_attrs`` may be numpy
        arrays, we have to take special care when comparing them.
        """
        if not (self.target == other.target):
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
        return hash(self.target)

    '''
    def apply(self, fn):
        """
        Applies fn(self.target), tracking the transformation info and output as
        a new LeTarget instance with a reference back to the source LeTarget.
        """

        # apply the provided function to the target stored in LeTarget
        output_target = fn(self.target)

        # diff 
        # changes = ???

        new_le_attrs = {
            "transformation": fn,
            # "changes": changes, 
            "previous": self # current LeTarget
        }
        
        output_LeTarget = LeTarget(output_target, 
                               le_attrs=new_le_attrs)
        
        return output_LeTarget
    '''

    def generate_new_target(self, output_le_target, new_le_attrs=None):

        new_target = LeTarget(output_le_target.target, le_attrs=new_le_attrs)
    
        return new_target

    @property
    def id(self):
        if USE_LOG and not self._id:
            self._id = LeTarget.label_logger.log_label(self.target)

        return self._id

    def __getattr__(self, attr):
        if attr in self.le_attrs:
            return self.le_attrs[attr]
        else:
            try:
                return self.__getattribute__(attr)
            except:
                return self.text.__getattribute__(attr)


    def __str__(self):
        return self.target


    def __repr__(self):
        return f'<LeTarget "{self.target}">'