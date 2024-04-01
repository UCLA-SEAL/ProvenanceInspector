# Inspector

Human-in-the-Loop Synthetic Text Data Inspection
with Provenance Tracking

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
