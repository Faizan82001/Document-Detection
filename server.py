from flask import Flask, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from page_extractor import process_image
from small_image_extractor import scan
import cv2
import io
import tempfile

current_script_path = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1])
print("Current script path:", current_script_path)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = os.path.join(current_script_path, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part in the request', 400

    file = request.files['file']

    if file.filename == '':
        return 'No file selected', 400

    if file and allowed_file(file.filename):
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_filename = temp_file.name
            file.save(temp_filename)

        result_image_array = scan(temp_filename)
        # process_image(temp_filename)
        # extract_document(temp_filename)

        # Remove the temporary file
        os.remove(temp_filename)

        # Convert result image array to bytes
        result_image_bytes = cv2.imencode('.jpg', result_image_array)[1].tobytes()

        # Return the result image in the response
        return send_file(
            io.BytesIO(result_image_bytes),
            mimetype='image/jpeg'
        )
        # filename = secure_filename(file.filename)
        # image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # file.save(image_path)
        # result_image_array = scan(image_path)
        # result_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.jpg')
        # cv2.imwrite(result_image_path, result_image_array)

        # # Return the result image in the response
        # return send_file(result_image_path, mimetype='image/jpeg')

    return 'Invalid file', 400

if __name__ == '__main__':
    app.run()
