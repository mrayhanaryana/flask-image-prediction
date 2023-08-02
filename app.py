from flask import Flask, render_template, request, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image
import numpy as np
import cv2
import json
from datetime import datetime
import pickle
import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

app = Flask(__name__)

# ENVIRONMENT VARIABLES
IMAGE_DUMP_PATH = 'dump/'
MODEL_PATH = 'fingerprintnew.h5'

@app.route('/predict', methods=['POST'])
def predict_fingerprint():
    try:
        #folder_id = request.get_json()['folder_id']
        folder_id = '1GsFyJUj5s247D0QFNFTQfbyUd_KbU_H-'
        user_id = request.get_json()['user_id']
        output_dir = f"./gdrive_file/{user_id}/"
        creds = authenticate()

        if(download_files_drive(user_id, folder_id, output_dir, creds)):
            prediction_results = []
            # List all files in the folder
            image_files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
            # Load Model
            model = load_model(MODEL_PATH)

            for image_file in image_files:
                image_path = os.path.join(output_dir, image_file)

                # Preprocess the uploaded image
                original_size = Image.open(image_path)
                resized_image = original_size.resize((128, 128))
                resized_image.save(image_path)

                # Read image then convert it to a numpy array
                img = cv2.imread(image_path)
                img = np.array(img)

                # Reshape image from 3D to 4D
                img = np.reshape(img, (1, 128, 128, 3))

                # Make the prediction using the loaded model
                prediction = model.predict(img)

                # Process the prediction result and append it to the list
                prediction_result = prediction[0].tolist()
                prediction_result = translate_prediction_result(prediction_result)
                prediction_result['image'] = image_file.split('.')[0]
                print(f"Prediction result for {image_file}: {prediction_result}")
                prediction_results.append(prediction_result)
            return jsonify({'prediction_results': prediction_results})
        else:
            return jsonify({'error': 'Error downloading files from Google Drive'})
    except Exception as e:
        return jsonify({'error': 'Error processing the request', 'message': str(e)})
def authenticate():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/drive.metadata',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file'
            ]
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds
def download_files_drive(user_id, folder_id, output_dir, creds):
    drive_service = build('drive', 'v3', credentials=creds)
    result = False
    files_in_folder = list_files_in_folder(folder_id, creds)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_info in files_in_folder:
        try:
            user_id_compare = file_info['name'].split('_')[0]
            if(user_id == user_id_compare):
                file_id = file_info['id']
                filename = file_info['name']
                request = drive_service.files().get_media(fileId=file_id)
                file_path = os.path.join(output_dir, filename)

                with open(file_path, 'wb') as fh:
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                        print(f"Downloading {filename}... {int(status.progress() * 100)}%")
                print(f"{filename} downloaded successfully!")
                result = True
        except Exception as e:
            print(f"Error downloading {filename}: {str(e)}")
    return result
def list_files_in_folder(folder_id, creds):
    drive_service = build('drive', 'v3', credentials=creds)

    results = []
    page_token = None
    while True:
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            response = drive_service.files().list(q=query, spaces='drive', fields='nextPageToken, files(id, name)', pageToken=page_token).execute()
            items = response.get('files', [])
            results.extend(items)
            page_token = response.get('nextPageToken', None)
            if not page_token:
                break
        except Exception as e:
            print(f"Error listing files in the folder: {str(e)}")
            break

    return results

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        f = request.files['file']
        # Save the uploaded file to a directory
        image_name = f.filename
        print("Received image File name : ", image_name)
        # If there is a / in the file name, split it and get the last part
        if '/' in image_name:
            image_name = image_name.split('/')[-1]
            # Add the extension at the end based on the file type
            if '.jpg' not in image_name:
                image_name = image_name + '.jpg'
        # Add date and time for uniqueness
        image_name = datetime.now().strftime("%Y%m%d-%H%M%S") + image_name
        image_path = IMAGE_DUMP_PATH + image_name
        f.save(image_path)

        # Get the image size
        # original_size = Image.open(image_path)
        # img_width, img_height = img.size

        # Load Model
        model = load_model(MODEL_PATH)

        # Preprocess the uploaded image
        # img = image.load_img(image_path, target_size=(img_width, img_height))
        # img = image.img_to_array(img)

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
        print("Prediction result: ", prediction_result)
        return jsonify({'prediction_result': prediction_result})

    return render_template('index.html')
# Function to translate the prediction result to a human readable format
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
    human_readable_prediction_result['similarity'] = str(accuracy)

    print("Human readable prediction result: ",
          human_readable_prediction_result)
    # Finally, return the human readable prediction result.
    return human_readable_prediction_result

if __name__ == '__main__':
    app.run()
