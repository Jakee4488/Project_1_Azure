from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv

import json

from helpers.file_utils import handle_file_upload
from helpers.pdf_utils import process_uploaded_pdf
from helpers.query_utils import query_documents_helper

# Load environment variables from .env file
load_dotenv()

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

app = Flask(__name__)
CORS(app)

# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    return handle_file_upload(file)

@app.route('/api/query', methods=['POST'])
def query_documents():
    data = request.json
    user_query = data.get('query')
    filename = data.get('filename')  # This can now be None

    if not user_query:
        return jsonify({'error': 'No query provided'}), 400

    # Removed enforcement of filename
    # if not filename:
    #     return jsonify({'error': 'Filename is required'}), 400

    try:
        response = query_documents_helper(user_query, filename)
        return response
    except Exception as e:
        logger.exception("An unexpected error occurred while processing the query.")
        return jsonify({'error': 'An unexpected error occurred.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
