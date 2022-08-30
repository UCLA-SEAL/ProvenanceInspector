import spacy
from .components import *
from tqdm import tqdm

class SpacyFeatures:
    model = spacy.load("en_core_web_sm")
    model.add_pipe("static_sentiment")
    model.add_pipe("contextual_sentiment")
    
    def __init__(self, texts, feature_names):
        self.feature_names = feature_names
        for i,t in enumerate(texts):
          try:
            self.model(t)
          except:
            print(i, t)
            raise
        self.docs = list(self.model.pipe(texts))
        self._tokens = None
        self._features = None

    @property
    def features(self):
        if self._features is None:
          self._features = {}
          for feature_name in self.feature_names:
            self._features[feature_name] = []

          for d in self.docs:
            for feature_name in self.feature_names:
              self._features[feature_name].append([])
            for token in d:
                for feature_name in self.feature_names:
                  if hasattr(token, '_') and hasattr(getattr(token, '_'), feature_name):
                    self._features[feature_name][-1].append(getattr(getattr(token, '_'), feature_name))
                  elif hasattr(token, feature_name):
                    self._features[feature_name][-1].append(getattr(token, feature_name))
                  
          for feature_name in self.feature_names:
            setattr(self, feature_name, self._features[feature_name])
            self._features[feature_name] = getattr(self, feature_name)

        return self._features

    @property
    def tokens(self):
        if self._tokens is None:
            self._tokens = []
            for d in self.docs:
                self._tokens.append([])
                for token in d:
                    self._tokens[-1].append(token.text)
        return self._tokens

    def extract_token_tags(self, feature_names=None):
        if not feature_names:
            return self.tokens, self.features

        feature_dict = {}
        for feature_name in feature_names:
            feature_dict[feature_name] = self.features[feature_name]
        return self.tokens, feature_dict
    
    """
    def extract_span_tags(self, feature="ents"):
        for d in self.docs:
          for span in getattr(doc,feature):
            print(span.text, span.start_char, ent.end_char, ent.label_)
    """

if __name__ == "__main__":

    texts = ["Wicked kickflip my dude!"]
    features = ["static_sentiment", "contextual_sentiment"]

    sf = SpacyFeatures(texts, features)

    for feature_name, features in sf.features.items():
        print(feature_name)
        for toks, feats in zip(sf.tokens, features):
            print(list(zip(toks,feats)))
