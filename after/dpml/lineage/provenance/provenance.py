from .transformation_provenance import TransformationProvenance
from .feature_provenance import FeatureProvenance
from .lazy_cloneable_provenance import LazyCloneableProvenance

class ProvenanceFactory:
    def get_provenance(self, format, *args, **kwargs):
        if format == 'transformation':
            return TransformationProvenance(args, kwargs)
        elif format == 'feature':
            return FeatureProvenance(args, kwargs)
        else:
            raise ValueError(format)

'''
class ProvenanceObject:
    def __init__(self, factory):
        self.factory = factory

    def add_provenance(self, to_add, provenance_type):
        provenance = self.factory.get_provenance(provenance_type)
        
        return provenance.add_provenance(to_add)


    def merge(self, to_merge, provenance_type):
        provenance = self.factory.get_provenance(provenance_type)
        
        return provenance.add_provenance(to_add)
'''
