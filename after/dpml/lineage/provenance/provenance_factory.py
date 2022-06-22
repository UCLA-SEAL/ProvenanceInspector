from .transformation_provenance import TransformationProvenance
from .feature_provenance import FeatureProvenance

class ProvenanceFactory:
    @classmethod
    def get_provenance(self, prov_type, *args, **kwargs):
        if prov_type == 'transformation':
            return TransformationProvenance(*args, **kwargs)
        elif prov_type == 'feature':
            return FeatureProvenance(*args, **kwargs)
        else:
            raise ValueError(prov_type)

'''
class ProvenanceObject:
    def __init__(self, factory):
        self.factory = factory

    def add_provenance(self, to_add, provenance_type):
        provenance = self.factory.get_provenance(provenance_type)
        
        return provenance.add_provenance(to_add)


    def merge(self, to_merge, provenance_type):
        provenance = self.factory.get_provenance(provenance_type)
        
        return provenance.merge(to_merge)
'''
