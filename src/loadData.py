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

def readFromAnomalySignalh5(inputfile):
    # TODO: implement

    raise Exception("readFromAnomalySignalh5 is not implemented yet!")


def readFromAnomalyBackgroundh5(inputfile, verbosity = 0):
    # I quickly tried to implement this, but:
    # the anomaly h5 files are numpy array, that are 0-padded
    # doing the step numpy -> awkward and removing "empty" particles is surprisingly difficult
    # if anyone has an idea - please implement :)
    
    raise Exception("readFromAnomalyBackgroundh5 is not implemented yet!")


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
    egammas = ak.zip({key.replace("egammas","").replace("Eta","eta").replace("Phi","phi").replace("Et","pt"):egammas[key] for key in egammas.fields}, with_name = "Momentum4D")
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
    
    return infoDict, muons, egammas, jets, energysums, bits


def readFromNanoAOD(inputpath):
    # TODO: implement
    # this most likely will specify an input path where multiple root files are located
    # we could also use some xml file containing info on the files to load instead

    raise Exception("readFromNanoAOD is not implemented yet!")