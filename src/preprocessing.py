# Functions for data preprocessing.
# prepareData is the main function, which determines from the passed model what kind of preparation is needed


def prepareData(model_dir, data):
    # Expected input:
    # - a model. I would propose just passing a path to a directory containing all info
    # - everything from loadData
    #
    # Expected output:
    # - NN input variables (x_test), numpy array
    # - Labels (y_test), numpy array

    # Implementation: determine from the info in model_dir what kind of model is needed
    # Then call one of the specialized functions from below

    raise Exception("prepareData is not implemented yet!")


# we could also import these from somewhere, if we want to keep the model-dependent parts separated
def prepareDataTopotrigger(model_dir, data):

    raise Exception("prepareDataTopotrigger is not implemented yet!")


def prepareDataAnomaly(model_dir, data):

    raise Exception("prepareDataAnomaly is not implemented yet!")