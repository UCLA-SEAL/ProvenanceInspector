from abc import ABC, abstractmethod
import functools

class LazyCloneableProvenance(ABC):
    def __init__(self) -> None:
        self.safeToMerge = True  
    
    def cloneProvenance(self):
        self.safeToMerge = False
        return self
  
    # the non-lazy implementation
    @abstractmethod
    def _cloneProvenance(self):
        raise NotImplementedError()

    @abstractmethod
    def add_provenance(self):
        raise NotImplementedError()

    # Merges two provenance instances (in place), returning the current instance after merging.
    def merge(self, others):

        base = self if self.safeToMerge else self._cloneProvenance()
        base._merge(others)

        return base

    # merge assuming the input is non-lazy
    @abstractmethod
    def _merge(self, other):
        raise NotImplementedError()
