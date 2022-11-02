import numpy as np
import awkward as ak
import pickle

# Functions for data preprocessing.
# prepareData is the main function, which determines from the passed model what kind of preparation is needed

def prepareData(model_dir, data, verbosity=0):
    # Expected input:
    # - a model. I would propose just passing a path to a directory containing all info
    # - data_*: this can be anything the concrete method needs, stored in a dict (or list, or array...)
    #
    # Expected output:
    # - NN input variables (x_test), numpy array
    # - Labels (y_test), numpy array

    # Implementation: determine from the info in model_dir what kind of model is needed
    # Then call one of the specialized functions from below

    # loading the info dict to determine the model type
    with open(model_dir+'network_info.pkl', 'rb') as f:
        infoDict = pickle.load(f)
    
    if(verbosity > 0): print("Preparing data for type " + infoDict["type"] + "...")
    if(infoDict["type"] == "topo"):
        return prepareDataTopotrigger(model_dir, data, verbosity = verbosity)
    else:
        raise Exception("Model type " + infoDict["type"] + " is not yet implemented.")
        

# we could also import these from somewhere, if we want to keep the model-dependent parts separated

def awkward_to_numpy(ak_array, maxN):
    # this is a bit ugly, but it works. Maybe we can improve later
    selected_arr = ak.fill_none( ak.pad_none( ak_array, maxN, clip=True, axis=-1), {"pt":0, "eta":0, "phi":0})
    np_arr = np.stack( (selected_arr.pt.to_numpy(), selected_arr.eta.to_numpy(), selected_arr.phi.to_numpy()), axis=2)
    return np_arr.reshape(np_arr.shape[0], np_arr.shape[1] * np_arr.shape[2])

def formatDataTopotrigger(infoDict, data, verbosity=0):
    # a helper function for the topo trigger that x_test outputs data in the desired format
    
    if(verbosity > 1): print("Formating data for topo trigger usage...")
    
    energysums = data["energysums"]
    jets = data["jets"]
    muons = data["muons"]
    egammas = data["egammas"]
    
    # first, lets get MET and MET phi
    np_MET = np.asarray( ak.to_numpy( energysums[energysums.Type == 2].pt).flatten() ).reshape( (len(energysums), 1) )
    np_MET_phi = np.asarray( ak.to_numpy(energysums[energysums.Type == 2].phi).flatten() ).reshape( (len(energysums), 1) )
    
    
    # now, lets add particles based on the info in the infoDict
    np_jets = awkward_to_numpy(jets, infoDict["nJets"])
    np_muons = awkward_to_numpy(muons, infoDict["nMuons"])
    np_egammas = awkward_to_numpy(egammas, infoDict["nEgammas"])
    
    x_test = np.concatenate( (np_MET, np_MET_phi, np_jets, np_muons, np_egammas), axis=1 )
    
    return x_test

def prepareDataTopotrigger(model_dir, data, verbosity = 0):
    
    # the implementation for the topo trigger expects up to two dicts of ak arrays
    # containing the following keys: energysums, muons, egammas, jets
    # if multiple dicts are passed, they are contained in a dict labelling "signal" or "background"
    
    # in the model_dir, multiple model files is expected (names: model_foldX.h5)
    # each model has a scaler: scaler_foldX.pkl
    
    # check whether any data is passed
    if not "signal" in data and not "background" in data:
        raise Exception("Please pass at least one of signal or background data!")
    
    # the info dict will be used to store some more info on the desired input variables
    with open(model_dir+'network_info.pkl', 'rb') as f:
        infoDict = pickle.load(f)
    
    # important! topo trigger networks will always used the following order of inputs:
    # energy sums, jets, muons, egammas
    
    x_tests = []
    y_tests = []
    
    if "signal" in data:
        if(verbosity > 0): print("Working on signal data...")
        data_signal = data["signal"]
        
        # creating the x_test according to the info stored in the infoDict
        x_data = formatDataTopotrigger(infoDict, data_signal, verbosity = verbosity)
        x_tests.append( x_data )
        
        # creating the needed part of y_test
        y_tests.append( np.ones( x_data.shape[0] ) )
        
    if "background" in data:
        if(verbosity > 0): print("Working on background data...")
        data_background = data["background"]
        
        # creating the x_test according to the info stored in the infoDict
        x_data = formatDataTopotrigger(infoDict, data_background, verbosity = verbosity)
        x_tests.append( x_data )
        
        # creating the needed part of y_test
        y_tests.append( np.zeroes( x_data.shape[0] ) )
        
    x_test = np.concatenate(x_tests)
    y_test = np.concatenate(y_tests)
    
    # finally, apply the StandardScaler to the test dataset
    # first, load the scalers. We'll determine the number of scalers from the infoDics
    scalers = []
    for i in range(infoDict["folds"]):
        with open(model_dir + "/scaler_fold" + str(i) + ".pkl", 'rb') as inp: scalers.append( pickle.load(inp) )
     
    x_test_scaled = []
    for scaler in scalers: x_test_scaled.append( scaler.transform(x_test) )
    
    # only returning the first one for the moment, need to have discussion on kFold later
    return x_test_scaled[0], y_test


def prepareDataAnomaly(model_dir, data):

    raise Exception("prepareDataAnomaly is not implemented yet!")