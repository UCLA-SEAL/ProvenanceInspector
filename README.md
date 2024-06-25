# Inspector

[Human-in-the-Loop Synthetic Text Data Inspection with Provenance Tracking](https://aclanthology.org/2024.findings-naacl.197)

## About
Inspector extends and builds on the Learning Interpretability Tool: https://github.com/PAIR-code/lit
It provides an interface for human inspection of synthetically generated texts produced by data augmentation techniques. 
Inspector allows users to group related texts by their transformation provenance, i.e., the transformations
applied to the original text, or feature provenance, the linguistic features of the original
text. 
For assistive labeling, INSPECTOR computes metrics that approximate data quality, and
allows users to compare the corresponding label of each text against the predictions of a large language model.



## Setup

### environment
```
- ensure conda is installed
  - https://conda.io/projects/conda/en/latest/user-guide/install/linux.html#installing-on-linux 

  - check with `conda info`

- create a conda environmenmt
  - conda env create -f lit/environment.yml
  - check with `conda env list`

- always ensure this environment is activated
  - conda activate lit-nlp
  - check with `conda info`

- ensure node.js is installed
  - directly via linux binary
    - https://github.com/nodejs/help/wiki/Installation#how-to-install-nodejs-via-binary-archive-on-linux

  - alternatively, via conda
    - https://anaconda.org/conda-forge/nodejs
  
  - check with `node -v`
  
  - ensure npm, npx, yarn all are available
    - check with `npm -v`
    - check with `npx -v`
    - check with `yarn -v`

- ngrok installation recommended
  - for demo deployments
  - refer https://ngrok.com/download
```


### build
```
- ensure the conda env is activated, as noted above

- lit backend
  
  - cd into ProvenanceInspector/after/dpml
  - run `pip install -e .`
  - install additional packages
    - pip install nltk
    - pip install spacy SQLAlchemy SQLAlchemy-Utils transformers-interpret==0.8.1
    - python -m spacy download en_core_web_sm

      python3 -m pip install -e <path to ProvenanceInspector>/after/dpml  

  - optional
    - conda install cudnn cupti  # optional, for GPU support
    - conda install -c pytorch pytorch  # optional, for PyTorch


- lit fronted
  - cd into ProvenanceInspector/lit/lit_nlp/
  - run `yarn && yarn build`
  - alternatively run `yarn && yarn watch`
```


## Run
```
- cd into dpml/lit
- run `python -m lit_nlp.examples.dpml_demo --port=5432`
- parallelly, run `ngrok http 5432` to expose localhost:5432 to a public url
```

## Cite

```
@inproceedings{kang-etal-2024-human,
    title = "Human-in-the-Loop Synthetic Text Data Inspection with Provenance Tracking",
    author = "Kang, Hong Jin  and
      Harel-Canada, Fabrice  and
      Gulzar, Muhammad Ali  and
      Peng, Nanyun  and
      Kim, Miryung",
    editor = "Duh, Kevin  and
      Gomez, Helena  and
      Bethard, Steven",
    booktitle = "Findings of the Association for Computational Linguistics: NAACL 2024",
    month = jun,
    year = "2024",
    address = "Mexico City, Mexico",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2024.findings-naacl.197",
    pages = "3118--3129",
    abstract = "Data augmentation techniques apply transformations to existing texts to generate additional data. The transformations may produce low-quality texts, where the meaning of the text is changed and the text may even be mangled beyond human comprehension. Analyzing the synthetically generated texts and their corresponding labels is slow and demanding. To winnow out texts with incorrect labels, we develop INSPECTOR, a human-in-the-loop data inspection technique. INSPECTOR combines the strengths of provenance tracking techniques with assistive labeling. INSPECTOR allows users to group related texts by their $\textit{transformation provenance}$, i.e., the transformations applied to the original text, or $\textit{feature provenance}$, the linguistic features of the original text. For assistive labeling, INSPECTOR computes metrics that approximate data quality, and allows users to compare the corresponding label of each text against the predictions of a large language model. In a user study, INSPECTOR increases the number of texts with correct labels identified by $3\times$ on a sentiment analysis task and by $4\times$ on a hate speech detection task. The participants found grouping the synthetically generated texts by their common transformation to be the most useful technique. Surprisingly, grouping texts by common linguistic features was perceived to be unhelpful. Contrary to prior work, our study finds that no single technique obviates the need for human inspection effort. This validates the design of INSPECTOR which combines both analysis of data provenance and assistive labeling to reduce human inspection effort.",
}
```
