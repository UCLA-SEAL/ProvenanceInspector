"""GLUE benchmark datasets, using TFDS.

See https://gluebenchmark.com/ and
https://www.tensorflow.org/datasets/catalog/glue

Note that this requires the TensorFlow Datasets package, but the resulting LIT
datasets just contain regular Python/NumPy data.
"""
from lit_nlp.api import dataset as lit_dataset
from lit_nlp.api import types as lit_types

from absl import logging

import tensorflow_datasets as tfds
import csv


def load_tfds(*args, do_sort=True, **kw):
  """Load from TFDS, with optional sorting."""
  # Materialize to NumPy arrays.
  # This also ensures compatibility with TF1.x non-eager mode, which doesn't
  # support direct iteration over a tf.data.Dataset.
  ret = list(tfds.as_numpy(tfds.load(*args, download=True, try_gcs=True, **kw)))
  if do_sort:
    # Recover original order, as if you loaded from a TSV file.
    ret.sort(key=lambda ex: ex['idx'])
  return ret


class CoLAData(lit_dataset.Dataset):
  """Corpus of Linguistic Acceptability.

  See
  https://www.tensorflow.org/datasets/catalog/glue#gluecola_default_config.
  """

  LABELS = ['0', '1']

  def __init__(self, split: str):
    self._examples = []
    for ex in load_tfds('glue/cola', split=split):
      self._examples.append({
          'sentence': ex['sentence'].decode('utf-8'),
          'label': self.LABELS[ex['label']],
      })

  def spec(self):
    return {
        'sentence': lit_types.TextSegment(),
        'label': lit_types.CategoryLabel(vocab=self.LABELS)
    }


class SST2Data(lit_dataset.Dataset):
  """Stanford Sentiment Treebank, binary version (SST-2).

  See https://www.tensorflow.org/datasets/catalog/glue#gluesst2.
  """

  LABELS = ['negative', 'positive']

  def __init__(self, split: str):
    self._examples = []
    for ex in load_tfds('glue/sst2', split=split):
      self._examples.append({
          'sentence': ex['sentence'].decode('utf-8'),
          'label': self.LABELS[ex['label']],
      })

  def spec(self):
    return {
        'sentence': lit_types.TextSegment(),
        'label': lit_types.CategoryLabel(vocab=self.LABELS)
    }

class RankedSST2Data(lit_dataset.Dataset):
  """Stanford Sentiment Treebank, binary version (SST-2).

  See https://www.tensorflow.org/datasets/catalog/glue#gluesst2.
  """

  LABELS = ['neg', 'pos']
  LLM_LABELS = ['neg', 'pos', 'neutral']
  CONSISTENCY = ['consistent', 'inconsistent']

  def __init__(self, split: str):
    self._examples = []
    # for ex in load_tfds('glue/sst2', split=split):

    filename = 'aug_dataset.csv' if split == 'train' else 'validation_aug_dataset.csv'
    with open(filename, 'r') as f:
      reader = csv.DictReader(f)
      
      for row in reader: 
        self._examples.append({
            'idx': int(row['idx']),
            'Sentence': row['text'],
            'Original label': self.LABELS[int(row['label'])],
            'label': self.LABELS[int(row['label'])],
            'LLM label': self.LLM_LABELS[int(row['llm_label'])],
            'LLM explanation': row['llm_explanation'],
            'label-LLM label consistency': self.CONSISTENCY[int(row['different_label'])],
            'features': row['features'],
            'transforms': row['transforms'],
            'Alignment': max(0, min(1, round(float(row['alignment_score']), 2))),
            'Fluency': max(0, min(1, round(float(row['fluency_score']), 2))),
            'Grammaticality': max(0, min(1, round(float(row['grammar_score']), 2))),
            'old_sentence': row['old_text'],
            'diff': row['diff_html']
        })
      logging.info('loaded Ranked SST2 dataset. Length of dataset is ' + str(len(self._examples)))
      logging.info('one row is ' + str(self._examples[0]))
    # logging.info('done init RankedSST2Data')

  def spec(self):
    return {
        'Sentence': lit_types.TextSegment(),
        # 'old_sentence': lit_types.TextSegment(),
        'Alignment': lit_types.Scalar(),
        'Fluency': lit_types.Scalar(),
        'Grammaticality': lit_types.Scalar(),
        'LLM label': lit_types.CategoryLabel(vocab=self.LLM_LABELS),
        'LLM explanation': lit_types.TextSegment(),
        'label-LLM label consistency': lit_types.CategoryLabel(vocab=self.CONSISTENCY),

        'label': lit_types.CategoryLabel(vocab=self.LABELS)
    }

class RankedHateSpeechData(lit_dataset.Dataset):
  """TweetEval

  See https://huggingface.co/datasets/tweet_eval/viewer/hate/validation.
  """

  LABELS = ['not hate', 'hate']
  LLM_LABELS = ['not hate', 'hate']
  CONSISTENCY = ['consistent', 'inconsistent']

  def __init__(self):
    self._examples = []
    # for ex in load_tfds('glue/sst2', split=split):

    filename = 'aug_hate_dataset.csv'
    with open(filename, 'r') as f:
      reader = csv.DictReader(f)
      
      for row in reader: 
        self._examples.append({
            'idx': int(row['idx']),
            'Sentence': row['text'],
            'Original label': self.LABELS[int(row['label'])],
            'label': self.LABELS[int(row['label'])],
            'LLM label': self.LLM_LABELS[int(row['llm_label'])],
            'LLM explanation': row['llm_explanation'],
            'label-LLM label consistency': self.CONSISTENCY[int(row['different_label'])],
            'features': row['features'],
            'transforms': row['transforms'],
            'Alignment': max(0, min(1, round(float(row['alignment_score']), 2))),
            'Fluency': max(0, min(1, round(float(row['fluency_score']), 2))),
            'Grammaticality': max(0, min(1, round(float(row['grammar_score']), 2))),
            'old_sentence': row['old_text'],
            'diff': row['diff_html']
        })
      logging.info('loaded TweetEval hate speech dataset. Length of dataset is ' + str(len(self._examples)))
      logging.info('one row is ' + str(self._examples[0]))
    # logging.info('done init RankedSST2Data')

  def spec(self):
    return {
        'Sentence': lit_types.TextSegment(),
        # 'old_sentence': lit_types.TextSegment(),
        'Alignment': lit_types.Scalar(),
        'Fluency': lit_types.Scalar(),
        'Grammaticality': lit_types.Scalar(),
        'LLM label': lit_types.CategoryLabel(vocab=self.LLM_LABELS),
        'LLM explanation': lit_types.TextSegment(),
        'label-LLM label consistency': lit_types.CategoryLabel(vocab=self.CONSISTENCY),

        'label': lit_types.CategoryLabel(vocab=self.LABELS)
    }

class MRPCData(lit_dataset.Dataset):
  """Microsoft Research Paraphrase Corpus.

  See https://www.tensorflow.org/datasets/catalog/glue#gluemrpc.
  """

  LABELS = ['positive', 'negative']

  def __init__(self, split: str):
    self._examples = []
    for ex in load_tfds('glue/mrpc', split=split):
      self._examples.append({
          'sentence1': ex['sentence1'].decode('utf-8'),
          'sentence2': ex['sentence2'].decode('utf-8'),
          'label': self.LABELS[ex['label']],
      })

  def spec(self):
    return {
        'sentence1': lit_types.TextSegment(),
        'sentence2': lit_types.TextSegment(),
        'label': lit_types.CategoryLabel(vocab=self.LABELS)
    }


class QQPData(lit_dataset.Dataset):
  """Quora Question Pairs.

  See https://www.tensorflow.org/datasets/catalog/glue#glueqqp.
  """

  LABELS = ['0', '1']

  def __init__(self, split: str):
    self._examples = []
    for ex in load_tfds('glue/qqp', split=split):
      self._examples.append({
          'question1': ex['question1'].decode('utf-8'),
          'question2': ex['question2'].decode('utf-8'),
          'label': self.LABELS[ex['label']],
      })

  def spec(self):
    return {
        'question1': lit_types.TextSegment(),
        'question2': lit_types.TextSegment(),
        'label': lit_types.CategoryLabel(vocab=self.LABELS)
    }


class STSBData(lit_dataset.Dataset):
  """Semantic Textual Similarity Benchmark (STS-B).

  Unlike the other GLUE tasks, this is formulated as a regression problem.

  See https://www.tensorflow.org/datasets/catalog/glue#gluestsb.
  """

  def __init__(self, split: str):
    self._examples = []
    for ex in load_tfds('glue/stsb', split=split):
      self._examples.append({
          'sentence1': ex['sentence1'].decode('utf-8'),
          'sentence2': ex['sentence2'].decode('utf-8'),
          'label': ex['label'],
      })

  def spec(self):
    return {
        'sentence1': lit_types.TextSegment(),
        'sentence2': lit_types.TextSegment(),
        'label': lit_types.RegressionScore(),
    }


class MNLIData(lit_dataset.Dataset):
  """MultiNLI dataset.

  See https://www.tensorflow.org/datasets/catalog/glue#gluemnli.
  """

  LABELS = ['entailment', 'neutral', 'contradiction']

  def __init__(self, split: str):
    self._examples = []
    for ex in load_tfds('glue/mnli', split=split):
      self._examples.append({
          'premise': ex['premise'].decode('utf-8'),
          'hypothesis': ex['hypothesis'].decode('utf-8'),
          'label': self.LABELS[ex['label']],
      })

  def spec(self):
    return {
        'premise': lit_types.TextSegment(),
        'hypothesis': lit_types.TextSegment(),
        'label': lit_types.CategoryLabel(vocab=self.LABELS)
    }


class QNLIData(lit_dataset.Dataset):
  """NLI examples derived from SQuAD.

  See https://www.tensorflow.org/datasets/catalog/glue#glueqnli.
  """

  LABELS = ['entailment', 'not_entailment']

  def __init__(self, split: str):
    self._examples = []
    for ex in load_tfds('glue/qnli', split=split):
      self._examples.append({
          'question': ex['question'].decode('utf-8'),
          'sentence': ex['sentence'].decode('utf-8'),
          'label': self.LABELS[ex['label']],
      })

  def spec(self):
    return {
        'question': lit_types.TextSegment(),
        'sentence': lit_types.TextSegment(),
        'label': lit_types.CategoryLabel(vocab=self.LABELS)
    }


class RTEData(lit_dataset.Dataset):
  """Recognizing Textual Entailment.

  See https://www.tensorflow.org/datasets/catalog/glue#gluerte.
  """

  LABELS = ['entailment', 'not_entailment']

  def __init__(self, split: str):
    self._examples = []
    for ex in load_tfds('glue/rte', split=split):
      self._examples.append({
          'sentence1': ex['sentence1'].decode('utf-8'),
          'sentence2': ex['sentence2'].decode('utf-8'),
          'label': self.LABELS[ex['label']],
      })

  def spec(self):
    return {
        'sentence1': lit_types.TextSegment(),
        'sentence2': lit_types.TextSegment(),
        'label': lit_types.CategoryLabel(vocab=self.LABELS)
    }


class WNLIData(lit_dataset.Dataset):
  """Winograd schema challenge.

  See https://www.tensorflow.org/datasets/catalog/glue#gluewnli.
  """

  LABELS = ['0', '1']

  def __init__(self, split: str):
    self._examples = []
    for ex in load_tfds('glue/wnli', split=split):
      self._examples.append({
          'sentence1': ex['sentence1'].decode('utf-8'),
          'sentence2': ex['sentence2'].decode('utf-8'),
          'label': self.LABELS[ex['label']],
      })

  def spec(self):
    return {
        'sentence1': lit_types.TextSegment(),
        'sentence2': lit_types.TextSegment(),
        'label': lit_types.CategoryLabel(vocab=self.LABELS)
    }


class DiagnosticNLIData(lit_dataset.Dataset):
  """NLI diagnostic set; use to evaluate models trained on MultiNLI.

  See https://www.tensorflow.org/datasets/catalog/glue#glueax.
  """

  LABELS = ['entailment', 'neutral', 'contradiction']

  def __init__(self, split: str):
    self._examples = []
    for ex in load_tfds('glue/ax', split=split):
      self._examples.append({
          'premise': ex['premise'].decode('utf-8'),
          'hypothesis': ex['hypothesis'].decode('utf-8'),
          'label': self.LABELS[ex['label']],
      })

  def spec(self):
    return {
        'premise': lit_types.TextSegment(),
        'hypothesis': lit_types.TextSegment(),
        'label': lit_types.CategoryLabel(vocab=self.LABELS)
    }
