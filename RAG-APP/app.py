from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import PyPDF2
import re
from pathlib import Path
import torch
import ollama
from openai import OpenAI
import json

app = Flask(__name__)
CORS(app)

# Update the UPLOAD_FOLDER configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

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

    if not user_query:
        return jsonify({'error': 'No query provided'}), 400

    embeddings_path = os.path.join(BASE_DIR, 'embeddings.pt')
    vault_path = os.path.join(BASE_DIR, 'vault.txt')

    if not os.path.exists(embeddings_path) or not os.path.exists(vault_path):
        return jsonify({'error': 'No documents have been processed yet'}), 400

    vault_embeddings = torch.load(embeddings_path)
    with open(vault_path, 'r', encoding='utf-8') as f:
        vault_content = f.readlines()

    query_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=user_query)["embedding"]
    cos_scores = torch.cosine_similarity(torch.tensor(query_embedding).unsqueeze(0), vault_embeddings)
    top_k = min(3, len(cos_scores))
    top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
    relevant_context = [vault_content[idx].strip() for idx in top_indices]

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

# Functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_uploaded_pdf(file_path):
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
            text = ''
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + " " if page.extract_text() else ""

            text = re.sub(r'\s+', ' ', text).strip()
            sentences = re.split(r'(?<=[.!?]) +', text)
            chunks = []
            current_chunk = ""

            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 1 < 1000:
                    current_chunk += (sentence + " ").strip()
                else:
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "

            if current_chunk:
                chunks.append(current_chunk)

            vault_path = os.path.join(BASE_DIR, 'vault.txt')
            with open(vault_path, "a", encoding="utf-8") as vault_file:
                for chunk in chunks:
                    vault_file.write(chunk.strip() + "\n")

            generate_embeddings()
            return True, "PDF processed successfully"
    except Exception as e:
        return False, str(e)

def generate_embeddings():
    try:
        vault_content = []
        vault_path = os.path.join(BASE_DIR, 'vault.txt')
        if os.path.exists(vault_path):
            with open(vault_path, "r", encoding='utf-8') as vault_file:
                vault_content = vault_file.readlines()

        vault_embeddings = []
        for content in vault_content:
            response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
            vault_embeddings.append(response["embedding"])

        vault_embeddings_tensor = torch.tensor(vault_embeddings)
        embeddings_path = os.path.join(BASE_DIR, 'embeddings.pt')
        torch.save(vault_embeddings_tensor, embeddings_path)

        return True, "Embeddings generated successfully"
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    app.run(debug=True)