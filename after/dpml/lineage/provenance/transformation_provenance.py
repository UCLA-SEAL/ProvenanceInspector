from inspect import signature
from.lazy_cloneable_provenance import LazyCloneableProvenance
from lineage.utils import add_branch_prefix

class TransformationProvenance(LazyCloneableProvenance):
    def __init__(self, history=None, store_type='Set'):
        super().__init__()
        self.store_type = store_type
        if history:
            self.history = history
        else:
            if store_type=='Set':
                self.history = set()
            else:
                raise ValueError(f"{store_type} is not supported for TransformationProvenance creation")

    def _cloneProvenance(self):
        return TransformationProvenance(history=self.history.copy(), store_type=self.store_type)
        
    def add_provenance(self, transformation):
        transformation_order = len(self.history)
        #transformation_info = dir(transformation)
        transformation_info = {"class": transformation.__class__.__name__}
        sig = signature(transformation.__init__)
        for arg_name in sig.parameters.keys():
            if arg_name not in {'self', 'args', 'kwargs'}:
                transformation_info[arg_name] = getattr(transformation, arg_name)

        new_provenance = self._cloneProvenance()
        new_provenance.history.add((transformation_order, str(transformation_info)))
        return new_provenance

    def _merge(self, others):
        cur_hist = add_branch_prefix(self.history, 0)
        # append '#' to all provenance order numbers
        for i,other in enumerate(others):
            cur_hist.add(add_branch_prefix(other.history, i+1))
        
        self.history = cur_hist

        return self 

    def _sub(self, other):
        new_provenance = self._cloneProvenance()
        new_provenance.history = self.history - other.history
        return new_provenance


    def __eq__(self, other):
        if self.history != other.history:
            return False
            
        return True

    def __str__(self):
        return str(self.history)

    def __repr__(self):
        return f'<TransformationProvenance: {self.history}>'
    '''
    def containsAll(self, other):
        return other.history.issubset(self.history)
    '''
    

    
