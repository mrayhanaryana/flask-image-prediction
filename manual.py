# Python Script to list all the files in the given directory then do the prediction
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image
import numpy as np
import cv2
import json
import pandas as pd
from openpyxl import Workbook

# Environment variables
IMAGE_DIR = "FingerprintTestImage/"
MODEL_PATH = "fingerprintnew.h5"


def list_files(directory):
    files = []
    for filename in os.listdir(directory):
        files.append(IMAGE_DIR + filename)
    return files

# Function to do the prediction


def predict_images(image_path):
    print("Loading image: ", image_path)

    # Load Model
    model = load_model(MODEL_PATH)

    # resize image to 128, 128
    original_size = Image.open(image_path)
    resized_image = original_size.resize((128, 128))
    resized_image.save(image_path)

    # read image then convert it to numpy array
    img = cv2.imread(image_path)
    img = np.array(img)

    # reshape image from 3D to 4D
    img = np.reshape(img, (1, 128, 128, 3))
    print(img.shape)

    # Make the prediction using the loaded model
    prediction = model.predict(img)

    # Process the prediction result and return it to the user
    prediction_result = prediction[0].tolist()
    prediction_result = translate_prediction_result(prediction_result)
    return prediction_result


def translate_prediction_result(prediction_result):
    # Some notes:
    # ['Arch ', 'Left Loop', 'Right Loop', 'Tented Arch', 'Whirl']
    # prediction_result is a list of 5 numbers.

    # First, we need to find out which number is the highest.
    highest_number = max(prediction_result)

    # highest_number is a float between 0 and 1.
    # If the number is less then certain then return error message
    print("Highest number: ", highest_number)
    threshold = 0.3
    if highest_number < threshold:
        return {'Message': 'Mohon maaf, Sidik Jari tidak dapat diidentifikasi. Silahkan coba lagi dengan gambar yang lebih jelas.', 'accuracy': str(round(highest_number * 100, 1)) + '%'}

    # Second, we need to find out the index of the highest number.
    index_of_highest_number = prediction_result.index(highest_number)
    print("Highest number and its index: ",
          highest_number, index_of_highest_number)
    # Third, we need to translate the index to a human readable format.
    # For the mapping read from a list of JSON from data.json file

    # Load the JSON file
    with open('data.json') as json_file:
        data = json.load(json_file)

    # Get the model mapping
    model_mapping = data
    print(model_mapping)

    human_readable_prediction_result = model_mapping[index_of_highest_number]
    # Convert the highest number from float to percentage then add % at the end
    # Example: 0.2949999272823334 -> 29.5%
    accuracy = str(round(highest_number * 100, 1)) + '%'
    print("Accuracy: ", accuracy)
    print("Accuracy type: ", type(accuracy))
    print("Human readable prediction result type: ",
          type(human_readable_prediction_result))
    # Add the accuracy to the human readable prediction result as "accuracy: xx.x%"
    human_readable_prediction_result['accuracy'] = str(accuracy)

    print("Human readable prediction result: ",
          human_readable_prediction_result)
    # Finally, return the human readable prediction result.
    return human_readable_prediction_result


# Main function
# if __name__ == '__main__':
#     # List all the files in the directory
#     files = list_files(IMAGE_DIR)
#     print("List of files: ", files)

#     # Loop through the files and do the prediction
#     for file in files:
#         print("File: ", file)
#         prediction_result = predict_images(file)
#         print("Prediction result: ", prediction_result)

if __name__ == '__main__':
    # List all the files in the directory
    files = list_files(IMAGE_DIR)
    print("List of files: ", files)

    # Create an empty list to store the prediction results and file names
    all_prediction_results = []
    file_names = []

    # Loop through the files and do the prediction
    for file in files:
        print("File: ", file)
        prediction_result = predict_images(file)
        print("Prediction result: ", prediction_result)

        # Add the prediction result and file name to the lists
        all_prediction_results.append(prediction_result)
        file_names.append(os.path.basename(file))

    # Create a pandas DataFrame from the lists of prediction results and file names
    df = pd.DataFrame(all_prediction_results)
    df.insert(0, "Image File", file_names)  # Insert the "Image File" column at the beginning

    # Save the results to an Excel file
    excel_file = "prediction_results.xlsx"
    df.to_excel(excel_file, index=False)

    print("Prediction results saved to", excel_file)