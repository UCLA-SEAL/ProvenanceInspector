# general imports
from spacy.language import Language
from spacy.tokens import Token, Doc
import unicodedata
import difflib

# static sentiment imports
from nltk.corpus import opinion_lexicon

# contextual sentiment imports
import numpy as np
import torch 
from transformers_interpret import SequenceClassificationExplainer
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)

def strip_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn')

@Language.factory("static_sentiment", default_config={"pos_list": set(opinion_lexicon.positive()), 
                                                      "neg_list": set(opinion_lexicon.negative())})
def create_static_sentiment_component(nlp: Language, name: str, pos_list: set, neg_list: set):
    if not Token.has_extension("static_sentiment"):
        Token.set_extension("static_sentiment", default = 'unknown')
    return StaticSentimentComponent(nlp, pos_list=pos_list, neg_list=neg_list)

class StaticSentimentComponent:
    def __init__(self, nlp: Language, pos_list=None, neg_list=None):
        self.pos_list=set(opinion_lexicon.positive())
        self.neg_list=set(opinion_lexicon.negative())
    def __call__(self, doc: Doc):
        for sp_token in doc:
            token = sp_token.lemma_
            if sp_token.is_stop:
                sp_token._.static_sentiment='exclude'
            elif token in self.pos_list:
                sp_token._.static_sentiment='pos'
            elif token in self.neg_list:
                sp_token._.static_sentiment='neg'
            else:
                sp_token._.static_sentiment='neutral'
        return doc

@Language.factory("contextual_sentiment", 
                  default_config={
                    "model_name": "distilbert-base-uncased-finetuned-sst-2-english",
                    "dataset": None,
                    "device": "cuda"
                })
def create_contextual_sentiment_component(nlp: Language,
                                          name: str,
                                          model_name: str = None,
                                          dataset: str = None, 
                                          device: str = None):
    if not Token.has_extension("contextual_sentiment"):
        Token.set_extension("contextual_sentiment", default = 'unknown')
    return ContextualSentimentComponent(model_name=model_name,
                                        dataset=dataset,
                                        device=device)

class ContextualSentimentComponent:
    def __init__(self, 
                 model_name=None,
                 dataset=None, 
                 device='cuda'):
      
        self.dataset = dataset
        self.model_name = model_name
        self.device = 'cuda' if torch.cuda.is_available() and 'cuda' in device else 'cpu'

        if self.model_name:
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name).to(self.device)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        else:
            # find huggingface model to provide rationalized output
            from huggingface_hub import HfApi

            api = HfApi()
            modelIds = api.list_models(filter=("pytorch", "dataset:" + dataset, "sibyl"))
            if modelIds:
                modelId = getattr(modelIds[0], 'modelId')
                print('Using ' + modelId + ' to rationalize keyphrase selections.')
                self.model = AutoModelForSequenceClassification.from_pretrained(modelId).to(self.device)
                self.tokenizer = AutoTokenizer.from_pretrained(modelId)
            else: 
                raise "No model found. Please provide one via `model_name`."
        self.interpreter = SequenceClassificationExplainer(self.model, self.tokenizer)

    def __call__(self, doc: Doc):   

        # get sentiment attributions
        attributions = self.interpreter(text=doc.text)[1:-1]
        doc_is_negative = 1 if not self.interpreter.predicted_class_index else 0
        tokens, weights = zip(*attributions)
        words, weights = merge_bpe(tokens, weights)

        weights = align_tokens([strip_accents(t.text).lower() for t in doc], words, weights.tolist())
        weights *= -1 if doc_is_negative else 1
            
        assert len(doc) == len(weights)
        
        # add attributions to doc
        for sp_token, weight in zip(doc, weights):
            if sp_token.is_stop:
                sp_token._.contextual_sentiment = "exclude"
            else:
                sp_token._.contextual_sentiment = stringify_sentiment(weight)

        return doc

def merge_bpe(tok, boe, chars="##"):
    len_chars = len(chars)

    new_tok = []
    new_boe = []

    emb = []
    append = ""
    for t, e in zip(tok[::-1], boe[::-1]):
        t += append
        emb.append(e)
        if t.startswith(chars):
            append = t[len_chars:]
        else:
            append = ""
            new_tok.append(t)
            new_boe.append(np.stack(emb).mean(axis=0))
            emb = []  
    new_tok = np.array(new_tok)[::-1]
    new_boe = np.array(new_boe)[::-1]
    return new_tok, new_boe


def align_tokens(doc_tok, tok, boe):

    new_embs = []
    
    seq = difflib.SequenceMatcher(None, doc_tok, tok)
    edits = seq.get_opcodes()
    
    for i, (op, from_start, from_end, to_start, to_end) in enumerate(edits):
        if op == 'equal':
            new_embs += boe[to_start:to_end]
        elif op == 'insert':
            cur_embs = boe[to_start:to_end]

            end = from_end 
            start = end
            
            k = max(i - 1, 0)

            while k >= 0:
                if edits[k][0] != 'equal':
                    start = edits[k][1]
                    break
                k -= 1
            cur_embs += new_embs[start:end]
            avg_emb = np.stack(cur_embs).mean(axis=0)
            new_embs[start:end] = [avg_emb] * (end - start)
            
        elif op == 'replace':
            avg_emb = np.stack(boe[to_start:to_end]).mean(axis=0)
            for j in range(from_start, from_end):
                new_embs.append(avg_emb)
        elif op == 'delete':
            for j in range(from_start,from_end):
                new_embs.append(0)

    return np.array(new_embs)


def stringify_sentiment(weight):
    ranges = {
        (-1.0, -0.33): "neg",
        (-0.33, 0.33): "neutral",
        (0.33,  1.0 ): "pos"
    }
    for (lower_bound, upper_bound), value in ranges.items():
        if lower_bound <= weight < upper_bound:
            return value
    return "NA"