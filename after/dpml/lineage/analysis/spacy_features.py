import spacy
from spacy.language import Language
from spacy.tokens import Token, Doc
from nltk.corpus import opinion_lexicon

@Language.factory("sentiment", default_config={"pos_list": set(opinion_lexicon.positive()), 
                                              "neg_list": set(opinion_lexicon.negative())})
def create_sentiment_component(nlp: Language, name: str, pos_list: set, neg_list: set):
    # component name. Print nlp.pipe_names to see the change reflected in the pipeline.
    return SentimentComponent(nlp, pos_list=pos_list, neg_list=neg_list)

class SentimentComponent:
    def __init__(self, nlp: Language, pos_list=None, neg_list=None):
        self.pos_list=set(opinion_lexicon.positive())
        self.neg_list=set(opinion_lexicon.negative())

        if not Token.has_extension("sentiment"):
            Token.set_extension("sentiment", default = 'exclude')

    def __call__(self, doc: Doc):
        for sp_token in doc:
          token = sp_token.lemma_
          if sp_token.is_stop:
              sp_token._.sentiment='exclude'
          elif token in self.pos_list:
              sp_token._.sentiment='pos'
          elif token in self.neg_list:
              sp_token._.sentiment='neg'
          else:
              sp_token._.sentiment='neutral'
        return doc


class SpacyFeatures:
    model = spacy.load("en_core_web_sm")
    model.add_pipe("sentiment")
    
    def __init__(self, texts, feature_names):
        self.feature_names = feature_names
        self.docs = [SpacyFeatures.model(t) for t in texts]
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
   