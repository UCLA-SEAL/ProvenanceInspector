from.lazy_cloneable_provenance import LazyCloneableProvenance
from collections import OrderedDict
from lineage.utils import add_branch_prefix


class FeatureProvenance(LazyCloneableProvenance):
    def __init__(self, feature_name, history=None, store_type='Set'):
        super().__init__()
        self.name = feature_name
        self.store_type = store_type

        if history:
            self.history = history
        else:
            if store_type =='Set':
                self.history = set()
            #elif store_type == 'OrderedDict':
            #    self.history = OrderedDict()
            else:
                raise ValueError(f"{store_type} is not supported for FeatureProvenance creation")

    def _cloneProvenance(self):
        return FeatureProvenance(self.name, history=self.history.copy(), store_type=self.store_type)


    def get_tags(self):
        return [record[2] for record in self.history]

        
    def add_provenance(self, feature_span, feature_tag):
        feature_order = len(self.history)

        new_provenance = self._cloneProvenance()
        new_provenance.history.add((feature_order, feature_span, feature_tag))
        return new_provenance


    def _merge(self, others):
        cur_hist = add_branch_prefix(self.history, 0)
        # append '#' to all provenance order numbers
        for i,other in enumerate(others):
            cur_hist.add(add_branch_prefix(other.history, i+1))
        
        self.history = cur_hist

        return self 

    def _sub(self, other):
        self.history -= other.history
        return self

    def __eq__(self, other):
        if self.name != other.name:
            return False

        if self.history != other.history:
            return False
            
        return True

    def __str__(self):
        return f'{self.name}={self.history}'

    def __repr__(self):
        return f'<FeatureProvenance[{self.name}] {self.history}>'
