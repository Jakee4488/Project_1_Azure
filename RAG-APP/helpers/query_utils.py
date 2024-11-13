import os
import json
import faiss  # FAISS library
import numpy as np
from flask import jsonify
from openai import AzureOpenAI
from .embedding_utils import get_azure_embedding
from constants import EMBEDDINGS_DIR, CHUNKS_DIR, ALLOWED_EXTENSIONS, AZURE_API_ENDPOINT, AZURE_API_MODEL, AZURE_APIKEY

# Set up constants and configurations
subscription_key = AZURE_APIKEY
endpoint = AZURE_API_ENDPOINT
deployment = AZURE_API_MODEL

# Paths and directories
embeddings_dir = EMBEDDINGS_DIR
chunks_dir = CHUNKS_DIR
allowed_extensions = ALLOWED_EXTENSIONS


def load_chunks_and_embeddings(chunks_path, embeddings_path):
    """Loads chunk text and embeddings from specified file paths."""
    try:
        with open(chunks_path, 'r', encoding='utf-8') as chunks_file:
            chunks = chunks_file.readlines()
        with open(embeddings_path, 'r', encoding='utf-8') as embeddings_file:
            embeddings = json.load(embeddings_file)
    except (FileNotFoundError, IOError) as e:
        return None, None, str(e)
    
    return chunks, np.array(embeddings, dtype=np.float32), None


def get_top_indices(user_query, embeddings, k=10):
    """Finds the top k relevant indices based on cosine similarity using FAISS."""
    embedding_dim = embeddings.shape[1]
    faiss.normalize_L2(embeddings)  # Normalize embeddings once
    
    # Initialize and populate FAISS index
    index = faiss.IndexFlatL2(embedding_dim)
    index.add(embeddings)

    # Obtain and normalize query embedding
    query_embedding = np.array(get_azure_embedding(user_query), dtype=np.float32).reshape(1, -1)
    faiss.normalize_L2(query_embedding)

    # Perform the search using FAISS
    _, indices = index.search(query_embedding, k)
    return indices[0]


def query_documents_helper(user_query, filename):
    """Processes user query by fetching relevant context and querying Azure OpenAI."""
    chunks_path = os.path.join(chunks_dir, f'{filename}_vault.txt')
    embeddings_path = os.path.join(embeddings_dir, f'{filename}_embeddings.json')

    # Load chunks and embeddings
    chunks, embeddings, load_error = load_chunks_and_embeddings(chunks_path, embeddings_path)
    if load_error:
        return jsonify({'error': f'File load error: {load_error}'}), 500
    if embeddings is None or chunks is None:
        return jsonify({'error': 'Chunks or embeddings file is missing'}), 404

    # Extract relevant context based on top indices
    top_indices = get_top_indices(user_query, embeddings)
    relevant_context = [chunks[idx].strip() for idx in top_indices if idx < len(chunks)]
    if not relevant_context:
        return jsonify({'error': 'No relevant context found'}), 404

    # Set up the Azure OpenAI client
    try:
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=subscription_key,
            api_version="2024-05-01-preview",
        )
    except Exception as e:
        return jsonify({'error': f'Azure client setup failed: {str(e)}'}), 500

    # Prepare the prompt with user query and context
    chat_prompt = [
        {"role": "system", "content": "You are an AI assistant that helps people find information."},
        {"role": "user", "content": f"{user_query} {relevant_context[0]}"}
    ]

    # Request completion from the Azure OpenAI client
    try:
        completion = client.chat.completions.create(
            model=deployment,
            messages=chat_prompt,
            max_tokens=900,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0
        )
        response_content = completion.choices[0].message.content
    except Exception as e:
        return jsonify({'error': f'Azure API call failed: {str(e)}'}), 500

    # Return the response and context
    return jsonify({
        'response': response_content,
        'context': relevant_context
    }), 200