import os
from flask import Flask, request, make_response, jsonify
from werkzeug.utils import secure_filename
import subprocess

UPLOAD_FOLDER = '/Users/oleandreashansen/Documents/vtl/uploads'
ALLOWED_EXTENSIONS = {'zip', 'tar', 'gz'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/software", methods=['POST'])
def post_software():
    if request.method == 'POST':
        if 'software' not in request.files:
            return make_response(jsonify({'error': 'No files foud'}), 502)
        file = request.files['software']

        if file.filename == '':
            return make_response(jsonify({'error': 'Not a valid filename'}), 502)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            replace_old_code()
            return make_response(jsonify({'status': 'File uploaded!'}), 200)
    return make_response(jsonify({'error': 'Wrong request type'}))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def replace_old_code():
    subprocess.call('./replace_code.sh')
    return


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)