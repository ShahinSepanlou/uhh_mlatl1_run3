import h5py
import vector
import uproot
import pandas as pd
import numpy as np
import awkward as ak
from glob import glob
import re
vector.register_awkward()

# Functions to load data from various sources and output it in a format usable by our networks
# This will implement multiple functions that all give the same outputs
# 
# Expected output:
# - A dict with misc. information: sample name...
# - L1 muons (awkward array of pt, eta, phi and more)
# - L1 egammas (awkward array of pt, eta, phi and more)
# - L1 jets (awkward array of pt, eta, phi and more)
# - L1 energy sums ((awkward array of pt, eta, phi and more))
# - L1 bits of cutbased triggers, and total L1 bit (pandas dataframe)
# all of these should have then same length!
# maybe we should store the output in a dict to make everything a bit less lengthy

# I created two functions for h5s, as the signal one contains multiple signals that we (might) want to load individually

def readFromAnomalySignalh5(inputfile, process, moreInfo=None, verbosity = 0):

    if(verbosity > 0): print("Reading anomaly team preprocessed signal file at " + inputfile + " for process " + process + ".")
    
    # constructing the information dict
    # some things will be automatically filled here
    # the input "moreInfo" can be used to pass more information
    # this information will have priority over automatically set entries
    infoDict = {}
    infoDict["input"] = inputfile
    
    # preparing lists to store L1 bit info
    L1bits_labels = []
    L1bits = []
    
    # reading the intput file
    if(verbosity > 0): print("Starting to read input file...")
    with h5py.File(inputfile, 'r') as h5f2:

        for key in h5f2.keys():
            
            if key.startswith(process + "_L1_"):
                L1bits_labels.append(key.replace(process+"_", ""))
                L1bits.append(np.array(h5f2[key]))
            elif key == process + "_l1bit":
                L1bit = np.array(h5f2[key])

            # doing this should remove all trigger things, and leave a single entry with the data
            if len(h5f2[key].shape) < 3: continue
            if key == process: data = h5f2[key][:,:,:].astype("float")
    
    # splitting objects
    np_energysums = data[:,0,:].reshape( (data.shape[0], 1, 3) ) # reshape is needed to keep dimensionality
    np_egammas = data[:,1:4,:]
    np_muons = data[:,5:8,:]
    np_jets = data[:,9:19,:]
    
    # converting to awkward (thanks Artur for the code)
    ak_egammas = ak.zip( {key:ak.from_regular(np_egammas[:,:,i], axis = 1) for i,key in enumerate(["pt","eta","phi"])}, with_name = "Momentum4D")
    ak_muons = ak.zip( {key:ak.from_regular(np_muons[:,:,i], axis = 1) for i,key in enumerate(["pt","eta","phi"])}, with_name = "Momentum4D")
    ak_jets = ak.zip( {key:ak.from_regular(np_jets[:,:,i], axis = 1) for i,key in enumerate(["pt","eta","phi"])}, with_name = "Momentum4D")
    
    # energy sums are handled a bit differently
    ak_energysums = ak.zip( {key:ak.from_regular(np_energysums[:,:,2*i], axis = 1) for i, key in enumerate(["pt","phi"])}, with_name = "Momentum4D")
    ak_energysums["Type"] = [2] * len(ak_energysums) # MET should have Type 2
    
    # removing empty entries (not needed for energy sums)
    ak_egammas = ak_egammas[ak_egammas.pt > 0]
    ak_muons = ak_muons[ak_muons.pt > 0]
    ak_jets = ak_jets[ak_jets.pt > 0]
    
    infoDict["nEvents"] = len(ak_muons)
    
    # formating the L1 bits
    df_total_L1 = pd.DataFrame( {"total L1": L1bit} )
    df_trigger_bits = pd.DataFrame(np.asarray(L1bits).T, columns=L1bits_labels)
    df_bits = df_total_L1.join(df_trigger_bits)
    
    # after everything else: add moreInfo
    if moreInfo: infoDict = {**infoDict, **moreInfo}
        
    if(verbosity > 0): print("Done!")
        
    # we'll output the data as a dict, makes it easier later
    dataDict = {}
    dataDict["muons"] = ak_muons
    dataDict["egammas"] = ak_egammas
    dataDict["jets"] = ak_jets
    dataDict["energysums"] = ak_energysums
    
    return infoDict, dataDict, df_bits


def readFromAnomalyBackgroundh5(inputfile, moreInfo=None, verbosity = 0):
    
    if(verbosity > 0): print("Reading anomaly team preprocessed background file at " + inputfile + ".")
        
    # constructing the information dict
    # some things will be automatically filled here
    # the input "moreInfo" can be used to pass more information
    # this information will have priority over automatically set entries
    infoDict = {}
    infoDict["input"] = inputfile
    
    # preparing lists to store L1 bit info
    L1bits_labels = []
    L1bits = []

    # reading the intput file
    if(verbosity > 0): print("Starting to read input file...")
    with h5py.File(inputfile, 'r') as h5f2:

        for key in h5f2.keys():

            if key[:3] == "L1_":
                L1bits_labels.append(key)
                L1bits.append(np.array(h5f2[key]))
            elif key == "L1bit":
                L1bit = np.array(h5f2[key])

            if len(h5f2[key].shape) < 3: continue
            if key == "full_data_cyl":
                data = h5f2[key][:,:,:].astype("float")

    # we have 57 variables, but they do not have labels yet. Lets assign them based on the info in
    # https://gitlab.cern.ch/cms-l1-ad/l1_anomaly_ae/-/blob/master/in/prep_data.py
    # I assume that we have MET, 4 electrons, 4 muons and 10 jets
    # These are 19 objects, times 3 parameters -> 57 vars
    # From line 27 I think the order is as I listed it: MET, egammas, muons, jets
        
    # splitting objects
    np_energysums = data[:,0,:].reshape( (data.shape[0], 1, 3) ) # reshape is needed to keep dimensionality
    np_egammas = data[:,1:4,:]
    np_muons = data[:,5:8,:]
    np_jets = data[:,9:19,:]
    
    # converting to awkward (thanks Artur for the code)
    ak_egammas = ak.zip( {key:ak.from_regular(np_egammas[:,:,i], axis = 1) for i,key in enumerate(["pt","eta","phi"])}, with_name = "Momentum4D")
    ak_muons = ak.zip( {key:ak.from_regular(np_muons[:,:,i], axis = 1) for i,key in enumerate(["pt","eta","phi"])}, with_name = "Momentum4D")
    ak_jets = ak.zip( {key:ak.from_regular(np_jets[:,:,i], axis = 1) for i,key in enumerate(["pt","eta","phi"])}, with_name = "Momentum4D")
    
    # energy sums are handled a bit differently
    ak_energysums = ak.zip( {key:ak.from_regular(np_energysums[:,:,2*i], axis = 1) for i, key in enumerate(["pt","phi"])}, with_name = "Momentum4D")
    ak_energysums["Type"] = [2] * len(ak_energysums) # MET should have Type 2
    
    # removing empty entries (not needed for energy sums)
    ak_egammas = ak_egammas[ak_egammas.pt > 0]
    ak_muons = ak_muons[ak_muons.pt > 0]
    ak_jets = ak_jets[ak_jets.pt > 0]
    
    infoDict["nEvents"] = len(ak_muons)
    
    # formating the L1 bits
    df_total_L1 = pd.DataFrame( {"total L1": L1bit} )
    df_trigger_bits = pd.DataFrame(np.asarray(L1bits).T, columns=L1bits_labels)
    df_bits = df_total_L1.join(df_trigger_bits)
    
    # after everything else: add moreInfo
    if moreInfo: infoDict = {**infoDict, **moreInfo}
        
    if(verbosity > 0): print("Done!")
        
    # we'll output the data as a dict, makes it easier later
    dataDict = {}
    dataDict["muons"] = ak_muons
    dataDict["egammas"] = ak_egammas
    dataDict["jets"] = ak_jets
    dataDict["energysums"] = ak_energysums
    
    return infoDict, dataDict, df_bits
    


def readFromL1Ntuple(inputpath, prescale_file_name, eventTree="l1UpgradeEmuTree/L1UpgradeTree", L1bitTree="l1uGTTree/L1uGTTree", moreInfo=None, verbosity=0):
    
    if(verbosity > 0): print("Reading from L1 ntuples in " + inputpath + ".")
    
    # constructing the information dict
    # some things will be automatically filled here
    # the input "moreInfo" can be used to pass more information
    # this information will have priority over automatically set entries
    infoDict = {}
    infoDict["input"] = inputpath
    infoDict["eventtree"] = eventTree
    infoDict["L1bittree"] = L1bitTree
    
    # reading the particles
    filepaths = glob(inputpath + "/*.root")
    if(verbosity > 0): print("Found %i files." % len(filepaths))
    infoDict["nFiles"] = len(filepaths)

    trees = []
    L1bittrees = []
    for filepath in filepaths:
        file = uproot.open(filepath)
        trees.append( file[eventTree] )
        L1bittrees.append( file[L1bitTree] )
    
    if(verbosity > 0): print("Starting to read objects...")
        
    particle_fields = ["Et", "Eta", "Phi"]
    energysum_fields = ["Type", "Et", "Phi"]
    
    muons = []
    egammas = []
    jets = []
    energysums = []
            
    for tree in trees:
        muons.append(tree.arrays(filter_name = ["muon" + f for f in particle_fields]))
        egammas.append(tree.arrays(filter_name = ["eg" + f for f in particle_fields]))
        jets.append(tree.arrays(filter_name = ["jet" + f for f in particle_fields]))
        energysums.append(tree.arrays(filter_name = ["sum" + f for f in energysum_fields]))
        
    muons = ak.concatenate(muons, axis = 0)
    egammas = ak.concatenate(egammas, axis = 0)
    jets = ak.concatenate(jets, axis = 0)
    energysums = ak.concatenate(energysums, axis = 0)
        
    # using Momentum4D to get pt, eta and phi
    muons = ak.zip({key.replace("muon","").replace("Eta","eta").replace("Phi","phi").replace("Et","pt"):muons[key] for key in muons.fields}, with_name = "Momentum4D")
    egammas = ak.zip({key.replace("eg","").replace("Eta","eta").replace("Phi","phi").replace("Et","pt"):egammas[key] for key in egammas.fields}, with_name = "Momentum4D")
    jets = ak.zip({key.replace("jet","").replace("Eta","eta").replace("Phi","phi").replace("Et","pt"):jets[key] for key in jets.fields}, with_name = "Momentum4D")
    energysums = ak.zip({key.replace("sum","").replace("Phi","phi").replace("Et","pt"):energysums[key] for key in energysums.fields})
    
    infoDict["nEvents"] = len(muons)
    
    if(verbosity > 0): print("Starting to read L1 trigger bits...")
    # reading the L1 trigger results
    # for this, we need to use the aliases in l1uGTTree/L1uGTTree   
    bits_part = []
    for tree in L1bittrees:
        
        # we need to make sure to apply prescales properly!
        # as the anomaly team does it, we only use un-prescaled paths
        with open(prescale_file_name) as prescale_file:
            wanted_keys = [line.split(',')[1] for line in prescale_file if line.split(',')[4] == "1"]
        
        decisions = tree["L1uGT/m_algoDecisionFinal"].array()
        
        resultdict = {}
        
        aliases = tree.aliases
        for alias in aliases:
            if alias in wanted_keys:
                decision_index_string = aliases[alias]
                decision_position = int(re.match(r"L1uGT\.m_algoDecisionInitial\[([0-9]+)\]", decision_index_string).group(1))

                resultdict[alias] = decisions[:,decision_position]
        
        # calculating the total L1 bis, as the one stored in L1 ntuples also consideres prescaled paths
        # (as a L1_AlwaysTrue is contained, the total L1 bit is just true everywhere)
        total_L1_bit = np.any( np.asarray(  list(resultdict.values()) ) , axis=0 ).flatten()
                
        df_total_L1 = pd.DataFrame( {"total L1": total_L1_bit} )
        df_trigger_bits = pd.DataFrame(resultdict)
        df_bits = df_total_L1.join(df_trigger_bits)
        bits_part.append(df_bits)
    
    bits = pd.concat(bits_part)
    
    # after everything else: add moreInfo
    if moreInfo: infoDict = {**infoDict, **moreInfo}
        
    if(verbosity > 0): print("Done!")
        
    # we'll output the data as a dict, makes it easier later
    dataDict = {}
    dataDict["muons"] = muons
    dataDict["egammas"] = egammas
    dataDict["jets"] = jets
    dataDict["energysums"] = energysums
    
    return infoDict, dataDict, bits


def readFromNanoAOD(inputpath):
    # TODO: implement
    # this most likely will specify an input path where multiple root files are located
    # we could also use some xml file containing info on the files to load instead

    raise Exception("readFromNanoAOD is not implemented yet!")