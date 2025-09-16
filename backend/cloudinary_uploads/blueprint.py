import os
import requests
from flask import Blueprint, request, jsonify

cloudinary_upload = Blueprint('cloudinary_upload', __name__)

CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', 'dur4aqnh6')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY', '')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', '')

@cloudinary_upload.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'Brak pliku w żądaniu'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nie wybrano pliku'}), 400
    url = f'https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/image/upload'
    data = {
        'upload_preset': 'ml_default',  # domyślny preset Cloudinary
    }
    files = {'file': (file.filename, file.stream, file.mimetype)}
    auth = (CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET)
    response = requests.post(url, data=data, files=files, auth=auth)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Błąd uploadu', 'details': response.text}), 500
