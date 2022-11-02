import keras

# Function to run the inference on the dataset

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