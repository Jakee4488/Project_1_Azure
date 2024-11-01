import os
from flask import jsonify
from werkzeug.utils import secure_filename
from helpers.pdf_utils import process_uploaded_pdf
from constants import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

upload_folder = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper function to handle file uploads
def handle_file_upload(file):
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            if filename.lower().endswith('.pdf'):
                success, message = process_uploaded_pdf(file_path)
                if not success:
                    return jsonify({'error': f'Failed to process PDF: {message}'}), 500

            return jsonify({
                'message': 'File uploaded and processed successfully',
                'filename': filename,
                'path': file_path
            }), 200

        except Exception as save_error:
            return jsonify({'error': f'Failed to save file: {str(save_error)}'}), 500
    else:
        return jsonify({'error': 'File type not allowed'}), 400