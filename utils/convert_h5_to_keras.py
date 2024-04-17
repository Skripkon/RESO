import tensorflow as tf


# If you saved your model as a set of the following files:
# PATH_TO_THE_FOLDER /
#                   ├── config.json
#                   ├── metadata.json
#                   └── model.weights.h5
#
# then you can use this converted to get a .keras file

PATH_TO_THE_FOLDER = "reso_backup/cp_400"
NAME_OF_THE_KERAS_FILE = "CHOPIN_SL100_BS64_400.keras"

# Load model architecture from config.json
with open(PATH_TO_THE_FOLDER + "/config.json", 'r') as json_file:
    loaded_model_json = json_file.read()
    loaded_model = tf.keras.models.model_from_json(loaded_model_json)

# Load model weights from model.weights.h5
loaded_model.load_weights(PATH_TO_THE_FOLDER + "/model.weights.h5")

# Save the model in .keras format
loaded_model.save(NAME_OF_THE_KERAS_FILE)
