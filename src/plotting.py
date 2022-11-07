import numpy as np
import awkward as ak
import matplotlib
import matplotlib.pyplot as plt
import mplhep as hep
plt.style.use(hep.style.ROOT)

# a collection of plotting functions

# helper function to have a central definition of the total L1 rate
def totalMinBiasRate():
    
    LHCfreq = 11245.6 
    nCollBunch = 2760

    return LHCfreq * nCollBunch / 1e3 # in kHz


# a plotting function for one parameter of one object before and after the trigger application
# only doing leading one for this quick test
def plotSculpting(data, triggerBit):
    
    assert(len(data) == len(triggerBit))
    
    # first, get data before and after trigger bit
    np_data_beforeBit = ak.flatten( data ).to_numpy()
    np_triggerBit = triggerBit.to_numpy().flatten()
    np_data_afterBit = ak.flatten( data[np_triggerBit] ).to_numpy()
    
    # creating histograms
    before_hist, bins = np.histogram( np_data_beforeBit )
    after_hist, bins = np.histogram( np_data_afterBit, bins=bins )
    
    # plotting
    hep.histplot(before_hist, bins)
    hep.histplot(after_hist, bins)
    
    plt.yscale("log")
    
def plot_hist(data, ax = None, bins = 10, interval = None, logy = False, logx = False,
              info = None, density = False, leading = False):
## Die Funktion kann Histogramme plotten wo eigenes Binning und Density angegeben werden kann. 
## Ausserdem koennen mehrere Plots in eine Figure gemacht werden und die Achsen logarithmisch gemacht werden
    if ax == None:
        fig, ax = plt.subplots()
        print("new axis is defined")
    if info == None:
        info = {"input" : "There is no further Information"}
    
    #Converts Awkward Array to Numpy Array
    new_data = ak.flatten(data).to_numpy()
    
    #Suche nur die Leading Teilchen raus
    if leading == True:    
        newer_data = []
        for i in data:
            newer_data.append(ak.max(i)) 
        new_data = [i for i in newer_data if i is not None]
    
    #Create a Histogram
    hist, hist_edges = np.histogram(new_data, bins, interval, density = density)
    
    #plot Histogram
    hep.histplot(hist,hist_edges,ax = ax, label = str(info["input"]))
    if logy == True:
        plt.yscale("log")
    if logx == True:
        plt.xscale("log")