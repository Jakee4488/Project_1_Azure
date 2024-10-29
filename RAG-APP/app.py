import os
import requests
import re
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import PyPDF2
import torch
import ollama
from openai import AzureOpenAI

app = Flask(__name__)
CORS(app)

# Configuration and setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}
os.makedirs(UPLOAD_FOLDER, mode=0o777, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Azure OpenAI configuration
ENDPOINT = "https://rag-react.openai.azure.com/openai/deployments/gpt-35-turbo-16k/chat/completions?api-version=2024-08-01-preview"
API_KEY = "5maY2n0mnFiWBjxGx2Kt6PYSv94xj53wZ8lw50OeckTNe1h4ipsAJQQJ99AJACYeBjFXJ3w3AAABACOGmeVH"
HEADERS = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_uploaded_pdf(file_path):
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ' '.join([page.extract_text() or "" for page in pdf_reader.pages])
            text = re.sub(r'\s+', ' ', text).strip()

            sentences = re.split(r'(?<=[.!?]) +', text)
            chunks, current_chunk = [], ""
            
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
            
            success, message = generate_embeddings()
            if not success:
                return False, message
            return True, "PDF processed successfully"
    except Exception as e:
        return False, f"Error processing PDF: {str(e)}"
    

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_pdf():
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

            success, message = process_uploaded_pdf(file_path)
            if not success:
                return jsonify({'error': f'Failed to process PDF: {message}'}), 500

            return jsonify({
                'message': 'PDF uploaded and processed successfully',
                'filename': filename,
                'path': file_path
            }), 200
        except Exception as save_error:
            return jsonify({'error': f'Failed to save file: {str(save_error)}'}), 500
    else:
        return jsonify({'error': 'File type not allowed'}), 400

def generate_embeddings():
    try:
        vault_path = os.path.join(BASE_DIR, 'vault.txt')
        if not os.path.exists(vault_path):
            return False, "Vault file does not exist"

        with open(vault_path, "r", encoding='utf-8') as vault_file:
            vault_content = vault_file.readlines()

        vault_embeddings = []
        for content in vault_content:
            response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
            vault_embeddings.append(response.get("embedding", []))

        vault_embeddings_tensor = torch.tensor(vault_embeddings)
        embeddings_path = os.path.join(BASE_DIR, 'embeddings.pt')
        torch.save(vault_embeddings_tensor, embeddings_path)
        
        return True, "Embeddings generated successfully"
    except Exception as e:
        return False, f"Error generating embeddings: {str(e)}"

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

    query_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=user_query).get("embedding", [])
    cos_scores = torch.cosine_similarity(torch.tensor(query_embedding).unsqueeze(0), vault_embeddings)
    top_k = min(3, len(cos_scores))
    top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
    relevant_context = [vault_content[idx].strip() for idx in top_indices]

    messages = [
        {"role": "system", "content": "You are an AI assistant that helps people find information."},
        {"role": "user", "content": f"{user_query}\n\nRelevant Context:\n{'\n'.join(relevant_context)}"}
    ]

    payload = {
        "messages": messages,
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 9000
    }

    try:
        response = requests.post(ENDPOINT, headers=HEADERS, json=payload)
        response.raise_for_status()
        return jsonify(response.json()), 200
    except requests.RequestException as e:
        return jsonify({'error': f"Failed to make the request. Error: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
