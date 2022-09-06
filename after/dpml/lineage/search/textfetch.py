import numpy as np
from textdiversity import (
    DocumentSemanticDiversity,
    POSSequenceDiversity,
    RhythmicDiversity,
    DependencyDiversity,
)

class TextFetch:
    def __init__(self, texts: list) -> None:
        self.texts = texts

        # featurizers
        self.semantic_featurizer = DocumentSemanticDiversity()
        self.syntactic_featurizer = DependencyDiversity()
        self.morphological_featurizer = POSSequenceDiversity()
        self.phonological_featurizer = RhythmicDiversity()

        # pre-computed features
        self.semantic_features = None
        self.syntactic_features = None
        self.morphological_features = None
        self.phonological_features = None

        # pre-computed text parses
        self.semantic_text = None
        self.syntactic_text = None
        self.morphological_text = None
        self.phonological_features = None

    def compute_semantic_features(self) -> None:
        features, texts = self.semantic_featurizer(self.texts)
        self.semantic_features = features
        self.semantic_text = texts

    def compute_syntactic_features(self) -> None:
        features, texts = self.syntactic_featurizer(self.texts)
        self.syntactic_features = features
        self.syntactic_text = texts

    def compute_morphological_features(self) -> None:
        features, texts = self.morphological_featurizer(self.texts)
        self.morphological_features = features
        self.morphological_text = texts

    def compute_phonological_features(self) -> None:
        features, texts = self.phonological_featurizer(self.texts)
        self.phonological_features = features
        self.phonological_features = texts

    def compute_features(self) -> None:
        self.compute_semantic_features()
        self.compute_syntactic_features()
        self.compute_morphological_features()
        # self.compute_phonological_features()


    def search(self, query: str, linguistic_type: str = "semantic", top_n: int = 1):
        if "semantic" in linguistic_type:
            ranker = self.semantic_featurizer
            t_feats = self.semantic_features
            t_texts = self.semantic_text
        elif "syntactic" in linguistic_type:
            ranker = self.syntactic_featurizer
            t_feats = self.syntactic_features
            t_texts = self.syntactic_text
        elif "morphological" in linguistic_type:
            ranker = self.morphological_featurizer
            t_feats = self.morphological_features
            t_texts = self.morphological_text
        elif "phonological" in linguistic_type:
            ranker = self.phonological_featurizer
            t_feats = self.phonological_features
            t_texts = self.phonological_text
        else:
            raise ValueError("Invalid linguistic_type provided.")

        if top_n == -1:
            top_n = len(t_texts)

        q_feats, q_texts = self.extract_features(query)

        z = ranker.calculate_similarity_vector(q_feats, t_feats)

        # rank based on similarity
        rank_idx = np.argsort(z)[::-1]

        ranking = np.array(t_texts)[rank_idx].tolist()
        scores = z[rank_idx]

        return ranking[:top_n], scores[:top_n]

if __name__ == "__main__":

    import numpy as np
    from time import perf_counter
    from datasets import load_dataset

    dataset = load_dataset("glue", "sst2", split="test[:100]")
    dataset = dataset.rename_column("sentence", "text")
    texts = dataset['text']
    print(len(texts))
    text_fetcher = TextFetch(texts)

    start_time = perf_counter()
    text_fetcher.compute_features()
    print(f"precomputation took {round(perf_counter() - start_time, 2)} seconds")

    query = "I cannot believe how dumb this movie is"

    linguistic_features = ["semantic", "syntactic", "morphological"] #, "phonological"]

    for lf in linguistic_features:
        start_time = perf_counter()
        ranking, scores = text_fetcher.search(query, lf, top_n=3)
        print(f"{lf} search took {round(perf_counter() - start_time, 2)} seconds")
        for text, score in zip(ranking, scores):
            print(f"score: {round(score, 2)} | text: {text}")
        