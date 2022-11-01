## Overview
This repository hosts a small framework to compare and generalize our efforts on topo triggers and anomaly detection networks.

### Network storage format
To compare networks, we'll need a format in which these, as well as all required information on them, is stored. This has to be the following:

- the network itself (potentialy multiples from kfold)
- information on the input variables & shapes
- any preprocessing (sklearn StandardScaler)

### Features
We'll need a few modules to achieve the goals:

#### Data reading
For a given test dataset, we need a module to open and read all required information. This should be a model-independent, generic set of information that we can use to make model performance studies later.

Ideally, we build two versions of this, one that is working on the anomaly teams h5 files, and one that is running directly on L1 ntuples (and maybe later even one for NanoAOD).

#### Data proprocessing
Based on the output of the "data reading" module, a preprocession module is needed to create NN inputs in the needed format. This is model(type)-specific, we might be able to implement two relatively generic modules with the same I/O that handle this, one for topo and one for anomaly.

#### Inference
Using the preprocessed data, the inference can be run. Assuming that the input data and model have been loaded, the module itself should be independent of the specific DNN module used here.

#### Result comparison
Network outputs interpretation and all plotting happens here. Assuming that we only have models that output a single variable that we cut on (output score or loss), this can be rather generic as well.


### MISC
For later reference: these are the energy sum labels:

| type | ID |
| kTotalEt | 0 |
| kTotalEtEm | 16 |
| kTotalHt | 1 |
| kMissingEt | 2 |
| kMissingHt | 3 |