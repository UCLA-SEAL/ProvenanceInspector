# 🔥 Learning Interpretability Tool (LIT)

The Learning Interpretability Tool (🔥LIT, formerly known as the Language
Interpretability Tool) is a visual, interactive ML model-understanding tool that
supports text, image, and tabular data. It can be run as a standalone server, or
inside of notebook environments such as Colab, Jupyter, and Google Cloud Vertex
AI notebooks.

LIT has a [website](https://pair-code.github.io/lit) with live demos, tutorials,
a setup guide and more.

For a broader overview, check out [the paper](https://arxiv.org/abs/2008.05122) and the
[user guide](https://github.com/PAIR-code/lit/wiki/ui_guide.md).

## Documentation

*   [Documentation index](https://github.com/PAIR-code/lit/wiki)
*   [FAQ](https://github.com/PAIR-code/lit/wiki/faq.md)
*   [Release notes](./RELEASE.md)

## Download and Installation

LIT can be installed via `pip` or built from source. Building from source is
necessary if you update any of the front-end or core back-end code.

### Install from source

Clone the repo and set up a Python environment:

```sh
git clone https://github.com/PAIR-code/lit.git ~/lit

# Set up Python environment
cd ~/lit
conda env create -f environment.yml
conda activate lit-nlp
conda install cudnn cupti  # optional, for GPU support
conda install -c pytorch pytorch  # optional, for PyTorch

# Build the frontend
(cd lit_nlp; yarn && yarn build)
```

Note: if you see [an error](https://github.com/yarnpkg/yarn/issues/2821)
running `yarn` on Ubuntu/Debian, be sure you have the
[correct version installed](https://yarnpkg.com/en/docs/install#linux-tab).

### pip installation

```sh
pip install lit-nlp
```

The `pip` installation will install all necessary prerequisite packages for use
of the core LIT package.

It **does not** install the prerequisites for the provided demos, so you need to
install those yourself. See [environment.yml](./environment.yml) for the list of
packages required to run the demos.

## Running LIT

Explore a collection of hosted demos on the
[LIT website demos page](https://pair-code.github.io/lit/demos).

### Quick-start: classification and regression

To explore classification and regression models tasks from the popular
[GLUE benchmark](https://gluebenchmark.com/):

```sh
python -m lit_nlp.examples.glue_demo --port=5432 --quickstart
```

Navigate to http://localhost:5432 to access the LIT UI.

Your default view will be a
[small BERT-based model](https://arxiv.org/abs/1908.08962) fine-tuned on the
[Stanford Sentiment Treebank](https://nlp.stanford.edu/sentiment/treebank.html),
but you can switch to
[STS-B](http://ixa2.si.ehu.es/stswiki/index.php/STSbenchmark) or
[MultiNLI](https://cims.nyu.edu/~sbowman/multinli/) using the toolbar or the
gear icon in the upper right.

### Quick-start: language modeling

To explore predictions from a pre-trained language model (BERT or GPT-2), run:

```sh
python -m lit_nlp.examples.lm_demo --models=bert-base-uncased --port=5432
```

And navigate to http://localhost:5432 for the UI.

### Notebook usage

Colab notebooks showing the use of LIT inside of notebooks can be found at
google3/third_party/py/lit_nlp/examples/notebooks.

We provide a simple
[Colab demo](https://colab.research.google.com/github/PAIR-code/lit/blob/main/lit_nlp/examples/notebooks/LIT_sentiment_classifier.ipynb).
Run all the cells to see LIT on an example classification model in the notebook.

### More Examples

See [lit_nlp/examples](./lit_nlp/examples). Run similarly to the above:

```sh
python -m lit_nlp.examples.<example_name> --port=5432 [optional --args]
```

## User Guide

To learn about LIT's features, check out the [user guide](https://github.com/PAIR-code/lit/wiki/ui_guide.md), or
watch this [video](https://www.youtube.com/watch?v=CuRI_VK83dU).

## Adding your own models or data

You can easily run LIT with your own model by creating a custom `demo.py`
launcher, similar to those in [lit_nlp/examples](./lit_nlp/examples). The
basic steps are:

*   Write a data loader which follows the [`Dataset` API](https://github.com/PAIR-code/lit/wiki/api.md#datasets)
*   Write a model wrapper which follows the [`Model` API](https://github.com/PAIR-code/lit/wiki/api.md#models)
*   Pass models, datasets, and any additional
    [components](https://github.com/PAIR-code/lit/wiki/api.md#interpretation-components) to the LIT server class

For a full walkthrough, see
[adding models and data](https://github.com/PAIR-code/lit/wiki/api.md#adding-models-and-data).

## Extending LIT with new components

LIT is easy to extend with new interpretability components, generators, and
more, both on the frontend or the backend. See our [documentation](https://github.com/PAIR-code/lit/wiki) to get
started.

## Citation

https://arxiv.org/abs/2008.05122

```
@misc{tenney2020language,
    title={The Language Interpretability Tool: Extensible, Interactive Visualizations and Analysis for {NLP} Models},
    author={Ian Tenney and James Wexler and Jasmijn Bastings and Tolga Bolukbasi and Andy Coenen and Sebastian Gehrmann and Ellen Jiang and Mahima Pushkarna and Carey Radebaugh and Emily Reif and Ann Yuan},
    booktitle = "Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing: System Demonstrations",
    year = "2020",
    publisher = "Association for Computational Linguistics",
    pages = "107--118",
    url = "https://www.aclweb.org/anthology/2020.emnlp-demos.15",
}
```
