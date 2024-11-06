import os
import torch
from flask import jsonify
import ollama
from openai import AzureOpenAI

from constants import EMBEDDINGS_DIR, CHUNKS_DIR , BASE_DIR, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, AZURE_API_ENDPOINT, AZURE_API_MODEL

subscription_key = os.getenv('AZURE_APIKEY')
embeddings_dir = EMBEDDINGS_DIR
chunks_dir = CHUNKS_DIR

base_dir = BASE_DIR
upload_folder = UPLOAD_FOLDER
allowed_extensions = ALLOWED_EXTENSIONS
endpoint = AZURE_API_ENDPOINT
deployment = AZURE_API_MODEL





# Helper function to query documents
def query_documents_helper(user_query, filename):
    chunks_path = os.path.join(chunks_dir, f'{filename}_vault.txt')
    embeddings_path = os.path.join(embeddings_dir, f'{filename}_embeddings.pt')

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

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=subscription_key,
        api_version="2024-05-01-preview",
    )

    chat_prompt = [
        {
            "role": "system",
            "content": "You are an AI assistant that helps people find information."
        },
        {
            "role": "user",
            "content": user_query + " " + relevant_context[0]
        }
    ]

    completion = client.chat.completions.create(
        model=deployment,
        messages=chat_prompt,
        max_tokens=900,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False
    )

    response_contents = completion.choices[0].message.content

    return jsonify({
        'response': response_contents,
        'context': relevant_context
    }), 200
