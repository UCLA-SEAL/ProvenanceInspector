# dpml
Data Provenance for Machine Learning

## software components

### **lineage**
```
- python package
- used by lit web-app interface for lineage / provenance information
```


### **textdiversity**
```
- python package
- used by lit web-app interface for fetching "similar" texts and feature visualization (e.g AMR)
```


### **Web-app Interface (powered by _Google LIT_: https://github.com/PAIR-code/lit)**
```
- backend
  - python based
  - barebones WSGI implementation
  - web api handlers can be easily interfaced with dpml packages
    - lineage
    - textdiversity

- frontend
  - single page typescript application
  - powered by Google's https://lit.dev web framework
  - uses https://mobx.js.org library for state management
```

 
## setup instructions

### environment
```
- ensure conda is installed
  - https://conda.io/projects/conda/en/latest/user-guide/install/linux.html#installing-on-linux 

  - check with `conda info`

- clone this repo
  - git clone git@github.com:fabriceyhc/dpml.git

- create a conda environmenmt
  - conda env create -f dpml/lit/environment.yml
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
  
  - cd into dpml/after/dpml
  - run `pip install -e .`
  - install additional packages
    - pip install nltk
    - pip install spacy SQLAlchemy SQLAlchemy-Utils transformers-interpret==0.8.1
    - python -m spacy download en_core_web_sm

  - check with `python -c "import lineage"`
  - also, check within `pip freeze | less`
      # Editable install with no version control (lineage==0.0)
      -e ....../dpml/after/dpml

  - optional
    - conda install cudnn cupti  # optional, for GPU support
    - conda install -c pytorch pytorch  # optional, for PyTorch


- lit fronted
  - cd into dpml/lit/lit_nlp/
  - run `yarn && yarn build`
  - alternatively run `yarn && yarn watch`
```


## run
```
- cd into dpml/lit
- run `python -m lit_nlp.examples.dpml_demo --port=5432`
- parallelly, run `ngrok http 5432` to expose localhost:5432 to a public url
```
