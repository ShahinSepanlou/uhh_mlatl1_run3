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


def readFromAnomalyBackgroundh5(inputfile):
    # TODO: implement

    raise Exception("readFromAnomalyBackgroundh5 is not implemented yet!")


def readFromL1Ntuple(inputpath):
    # TODO: implement
    # this most likely will specify an input path where multiple root files are located
    # we could also use some xml file containing info on the files to load instead

    raise Exception("readFromL1Ntuple is not implemented yet!")


def readFromNanoAOD(inputpath):
    # TODO: implement
    # this most likely will specify an input path where multiple root files are located
    # we could also use some xml file containing info on the files to load instead

    raise Exception("readFromNanoAOD is not implemented yet!")