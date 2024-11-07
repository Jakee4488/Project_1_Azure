import os
import json
import faiss  # FAISS library
import numpy as np
from flask import jsonify
from openai import AzureOpenAI
from .embedding_utils import get_azure_embedding
from constants import EMBEDDINGS_DIR, CHUNKS_DIR, BASE_DIR, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, AZURE_API_ENDPOINT, AZURE_API_MODEL

# Set up constants and configurations
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
    # Define paths for chunks and embeddings
    chunks_path = os.path.join(chunks_dir, f'{filename}_vault.txt')
    embeddings_path = os.path.join(embeddings_dir, f'{filename}_embeddings.json')

    # Check if the necessary files exist
    if not os.path.exists(chunks_path) or not os.path.exists(embeddings_path):
        return jsonify({'error': 'Chunks or embeddings file not found'}), 404

    # Read chunks and embeddings data
    with open(chunks_path, 'r', encoding='utf-8') as chunks_file:
        chunks = chunks_file.readlines()

    with open(embeddings_path, 'r', encoding='utf-8') as embeddings_file:
        embeddings = json.load(embeddings_file)

    # Convert embeddings to a NumPy array
    embeddings = np.array(embeddings, dtype=np.float32) # Shape: (num_chunks, embedding_dim)
    embedding_dim = embeddings.shape[1]

    # Initialize and populate FAISS index
    index = faiss.IndexFlatL2(embedding_dim)  # L2 distance for FAISS, approximates cosine with normalization
    index.add(embeddings)

    # Obtain query embedding
    query_embedding = get_azure_embedding(user_query)
    query_embedding = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
    query_embedding = np.ascontiguousarray(query_embedding)
    
    # Normalize embeddings and query to use cosine similarity approximation
    faiss.normalize_L2(embeddings)       # Normalize the document embeddings
    faiss.normalize_L2(query_embedding)  # Normalize the query embedding

    # Perform the search using FAISS
    k = 10  # Number of top results
    distances, indices = index.search(query_embedding, k)

    # Extract relevant context based on top indices
    top_indices = indices[0]
    relevant_context = [chunks[idx].strip() for idx in top_indices if idx < len(chunks)]

    if not relevant_context:  # Handle case where no context is found
        return jsonify({'error': 'No relevant context found'}), 404

    # Set up the Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=subscription_key,
        api_version="2024-05-01-preview",
    )

    # Prepare the prompt with the user query and relevant context
    chat_prompt = [
        {"role": "system", "content": "You are an AI assistant that helps people find information."},
        {"role": "user", "content": user_query + " " + relevant_context[0]}
    ]

    # Request completion from the Azure OpenAI client
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

    # Extract the response content
    response_contents = completion.choices[0].message.content

    # Return the response and context
    return jsonify({
        'response': response_contents,
        'context': relevant_context
    }), 200
