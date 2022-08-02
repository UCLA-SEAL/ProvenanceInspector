import functools
import inspect

from .le_record import LeRecord
from .le_text import LeText
from .le_target import LeTarget
from .storage import TransformLogger

import hydra

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

class LeBatch:

    transform_logger = None
    hydra.core.global_hydra.GlobalHydra.instance().clear()
    with hydra.initialize(version_base=None, config_path="config"):
        cfg = hydra.compose(config_name="config")

    def __init__(self, original_batch):
        self.original_batch = original_batch
        self.transformed_batch = None
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
        if LeBatch.cfg.use_log and not LeBatch.transform_logger:
            LeBatch.transform_logger = TransformLogger()

    def __enter__(self):
        if LeBatch.transform_logger.replay_only:
            LeBatch.transform_logger.log_originals(self.texts, self.targets)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if LeBatch.transform_logger.replay_only and self.transformed_batch:
            tran_history = [x.le_attrs['transformation_provenance'].history for x in self.transformed_batch]
            tran_history = [[x[1] for x in sorted(th, key=lambda x: x[0])] for th in tran_history]
            LeBatch.transform_logger.log_transform_provs(tran_history)
            LeBatch.transform_logger.flush()


    def apply(self, batch=None, transform_callable=None, *args, **kwargs):
        if batch:
            self.__init__(batch)
        self.transform_callable = transform_callable
        new_texts, new_targets = transform_callable((self.texts, self.targets), *args, **kwargs)
        self.new_texts = new_texts
        self.new_targets = new_targets

        new_records = []
        for le_record, text2, target2 in zip(self.le_records,
                                                  self.new_texts,
                                                  self.new_targets):

            transformation = transform_callable
            if hasattr(transformation, '__self__'):
                transformation = transformation.__self__

            new_le_attrs = {
                "transformation_provenance": le_record.le_attrs["transformation_provenance"].add_provenance(transformation),
                "prev": le_record
            }


            new_le_text, new_le_target = le_record.generate_new_record(LeText(text2), new_target=LeTarget(target2),
                                            new_le_attrs=new_le_attrs, granularity='word')

            output_record = LeRecord(new_le_text, le_target=new_le_target, le_attrs=new_le_attrs)

            if LeBatch.cfg.use_log and not LeBatch.cfg.replay_only:
                LeBatch.transform_logger.log(le_record, output_record)

            new_records.append(output_record)

        if LeBatch.cfg.use_log and not LeBatch.cfg.replay_only:
            LeBatch.transform_logger.flush()

        self.transformed_batch = new_records
        
        return new_records