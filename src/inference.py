import keras
import pandas as pd

# Functions to run the inference on the dataset
def runInference(model_file, x, verbosity = 0):
    # Expected input:
    # - path to the model file
    # - everything from preparedata
    #
    # Expected output:
    # - output scores (numpy array)
    
    if(verbosity > 0): print("Loading model from " + str(model_file) + "...")
    model = keras.models.load_model(model_file)

    if(verbosity > 0): print("Starting inference...")
        
    y_pred = model.predict(x)
    
    return y_pred


# quick method to define a trigger from a certain threshold
# this will return the "trigger bit" of this trigger as a dataframe
# other ways to define a trigger from a y_pred can be defined
def defineTriggerFromThreshold(y_pred, threshold, label = None, mode = "min", verbosity = 0):
    
    if label: label = label + "_"
    else: label = ""
    
    if mode == "min":
        if (verbosity > 0): print("Defining Trigger by requiring score > " + str(threshold) + ".")
        return pd.DataFrame( y_pred > threshold, columns=[label + mode + "_" + str(threshold).replace(".", "p")] )
    elif mode == "max":
        if (verbosity > 0): print("Defining Trigger by requiring score < " + str(threshold) + ".")  
        return pd.DataFrame( y_pred < threshold, columns=[label + mode + "_" + str(threshold).replace(".", "p")] )
    else:
        raise Exception("Mode " + mode + " not recognized.")
