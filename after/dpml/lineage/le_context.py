import functools
import inspect

from .le_record import LeRecord
from .le_text import LeText
from .le_target import LeTarget
from .config import *


'''
def get_class_that_defined_method(meth):
    if isinstance(meth, functools.partial):
        return get_class_that_defined_method(meth.func)
    if inspect.ismethod(meth) or (inspect.isbuiltin(meth) and getattr(meth, '__self__', None) is not None and getattr(meth.__self__, '__class__', None)):
        for cls in inspect.getmro(meth.__self__.__class__):
            if meth.__name__ in cls.__dict__:
                return cls
        meth = getattr(meth, '__func__', meth)  # fallback to __qualname__ parsing
    if inspect.isfunction(meth):
        cls = getattr(inspect.getmodule(meth),
                      meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0],
                      None)
        if isinstance(cls, type):
            return cls
    return getattr(meth, '__objclass__', None)  # handle special descriptor objects

'''


class LeContext:

    def __init__(self, original_batch):
        self.original_batch = original_batch


        if isinstance(original_batch, tuple):
            self.texts, self.targets = self.original_batch
            self.le_records = []
            for text, target in zip(self.texts, self.targets):
                self.le_records.append(LeRecord(text, le_target=target, le_attrs=None))
        elif all(isinstance(item, LeRecord) for item in original_batch):
            self.le_records =  original_batch
            self.texts = []
            self.targets = []
            # extract text and targets for transformation
            for record in self.le_records:
                self.texts.append(record.text)
                self.targets.append(record.target)

        else:
            raise TypeError(
                f"Invalid original_batch type {type(original_batch)} (required tupel of texts and targets or list of LeRecord)"
            )

    
    def apply(self, transform_callable, *args, **kwargs):
        self.transform_callble = transform_callable
        new_texts, new_targets = transform_callable((self.texts, self.targets), *args, **kwargs)
        self.new_texts = new_texts
        self.new_targets = new_targets

        transformation = transform_callable
        if hasattr(transform_callable, '__self__'):
            transformation = transformation.__self__

        transformation_type = transformation.__class__.__name__

        new_records = []
        
        for le_record, text2, target2 in zip(self.le_records,
                                                  self.new_texts,
                                                  self.new_targets):


            new_le_attrs = {
                "transformation_provenance": le_record.le_attrs["transformation_provenance"].add_provenance(transformation),
            }


            new_le_text, new_le_target = le_record.generate_new_record(LeText(text2), new_target=LeTarget(target2),
                                            new_le_attrs=new_le_attrs, granularity='word')

            output_record = LeRecord(new_le_text, le_target=new_le_target, le_attrs=new_le_attrs)

            if USE_LOG:
                LeRecord.transform_logger.log_transformation(le_record, output_record, transformation_type)

            new_records.append(output_record)

        if USE_LOG:
            LeText.text_logger.flush()
            if LeTarget.label_logger:
                LeTarget.label_logger.flush()
            LeRecord.transform_logger.flush()
        
        return new_records


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if isinstance(exc_value, Exception):
            print(f"An exception occurred in your with block: {exc_type}")
            print(f"Exception message: {exc_value}")
            print(f"Traceback info: {exc_tb}")