from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import torch
import ollama
from openai import OpenAI
import json

from helpers.file_utils import allowed_file
from helpers.pdf_utils import process_uploaded_pdf

app = Flask(__name__)
CORS(app)

# Update the UPLOAD_FOLDER configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

EMBEDDINGS_DIR = os.path.join(BASE_DIR, 'embeddings')
CHUNKS_DIR = os.path.join(BASE_DIR, 'chunks')

# Create upload folder with proper permissions
os.makedirs(UPLOAD_FOLDER, mode=0o777, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
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

@app.route('/api/query', methods=['POST'])
def query_documents():
    data = request.json
    user_query = data.get('query')
    filename = data.get('filename')


    #filename = 'Attention'
    """need to get filename form the state and loop through all the relevnt documents if need creating the embeddings if not been created 
    and then query the documents and return the response"""

    if not user_query:
        return jsonify({'error': 'No query provided'}), 400
    

    if not filename:
        return jsonify({'error': 'Filename is required'}), 400

    chunks_path = os.path.join(CHUNKS_DIR, f'{filename}_vault.txt')
    embeddings_path = os.path.join(EMBEDDINGS_DIR, f'{filename}_embeddings.txt')

    if not os.path.exists(chunks_path) or not os.path.exists(embeddings_path):
        return jsonify({'error': 'Chunks or embeddings file not found'}), 404

    with open(chunks_path, 'r', encoding='utf-8') as chunks_file:
        chunks = chunks_file.readlines()

    with open(embeddings_path, 'r', encoding='utf-8') as embeddings_file:
        embeddings = [eval(line.strip()) for line in embeddings_file]

    query_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=user_query)["embedding"]
    cos_scores = torch.cosine_similarity(torch.tensor(query_embedding).unsqueeze(0), torch.tensor(embeddings))
    top_k = min(3, len(cos_scores))
    top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
    relevant_context = [chunks[idx].strip() for idx in top_indices]

    client = OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='llama3.1:8b'
    )

    system_message = "You are a helpful assistant expert in extracting useful information from text and providing additional relevant information."
    context_str = "\n".join(relevant_context)

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"{user_query}\n\nRelevant Context:\n{context_str}"}
    ]

    response = client.chat.completions.create(
        model="llama3.1:8b",
        messages=messages,
        max_tokens=2000,
    )

    return jsonify({
        'response': response.choices[0].message.content,
        'context': relevant_context
    }), 200

if __name__ == '__main__':
    app.run(debug=True)