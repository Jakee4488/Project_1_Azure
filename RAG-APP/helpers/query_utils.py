import os
import json
import faiss  # FAISS library
import numpy as np
import logging
from flask import jsonify
from openai import AzureOpenAI
from .embedding_utils import get_azure_embedding
from constants import EMBEDDINGS_DIR, CHUNKS_DIR, ALLOWED_EXTENSIONS, AZURE_API_ENDPOINT, AZURE_API_MODEL, AZURE_APIKEY,AZURE_CLIENT_CONFIG

# Set up constants and configurations
subscription_key = AZURE_APIKEY
endpoint = AZURE_API_ENDPOINT
deployment = AZURE_API_MODEL

# Paths and directories
embeddings_dir = EMBEDDINGS_DIR
chunks_dir = CHUNKS_DIR
allowed_extensions = ALLOWED_EXTENSIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

    
def load_chunks_and_embeddings(chunks_path, embeddings_path):
    """Loads chunk text and embeddings from specified file paths."""
    try:
        with open(chunks_path, 'r', encoding='utf-8') as chunks_file:
            chunks = chunks_file.readlines()
        with open(embeddings_path, 'r', encoding='utf-8') as embeddings_file:
            embeddings = json.load(embeddings_file)
    except (FileNotFoundError, IOError) as e:
        logger.error(f"File not found: {e}")
        return None, None, f"File not found: {e.filename}"
    except IOError as e:
        logger.error(f"I/O error: {e}")
        return None, None, f"I/O error: {str(e)}"
    
    return chunks, np.array(embeddings, dtype=np.float32), None



def get_top_indices(user_query, embeddings, filename, k=10):
    """Finds the top k relevant indices based on cosine similarity using FAISS."""
    embedding_dim = embeddings.shape[1]
    faiss.normalize_L2(embeddings)  # Normalize embeddings once
    
    # Initialize and populate FAISS index
    index = faiss.IndexFlatL2(embedding_dim)
    index.add(embeddings)

    # Save the index to a file
    if not os.path.exists('vector_store'):
        os.makedirs('vector_store')
    
    # Check if the index is already stored in the vector store
    index_path = f'vector_store/{filename}_vector_store.index'
    if os.path.exists(index_path):
        index = faiss.read_index(index_path)
    else:
        faiss.write_index(index, index_path)

    # Obtain and normalize query embedding
    query_embedding = np.array(get_azure_embedding(user_query), dtype=np.float32).reshape(1, -1)
    faiss.normalize_L2(query_embedding)

    # Perform the search using FAISS
    _, indices = index.search(query_embedding, k)
    return indices[0]

def document_relevent_context(user_query, filename=None):
    """
    Processes user query by fetching relevant context if a filename is provided
    and querying Azure OpenAI. Provides general responses when no context is available.
    """
    relevant_context = []

    if filename:
        chunks_path = os.path.join(chunks_dir, f'{filename}_vault.txt')
        embeddings_path = os.path.join(embeddings_dir, f'{filename}_embeddings.json')

        # Load chunks and embeddings
        chunks, embeddings, load_error = load_chunks_and_embeddings(chunks_path, embeddings_path)
        if load_error:
            logger.error(f"Error loading files: {load_error}")
            return jsonify({'error': f'File load error: {load_error}'}), 500
        if embeddings is None or chunks is None:
            logger.error('Chunks or embeddings file is missing')
            return jsonify({'error': 'Chunks or embeddings file is missing'}), 404

        # Extract relevant context based on top indices
        top_indices = get_top_indices(user_query, embeddings,filename)
        relevant_context = [chunks[idx].strip() for idx in top_indices if idx < len(chunks)]
        logger.info(f"Contextualizing query with filename: {filename}")
    else:
        logger.info("No filename provided. Proceeding with general response.")

    return relevant_context



def query_documents_helper(user_query, filename=None):

    document_context = document_relevent_context(user_query, filename)

    chat_prompt = [
        {"role": "system", "content": "You are an AI assistant that helps people find information."},
        {"role": "user", "content": user_query}
    ]


    if document_context:
        # Incorporate the context into the user message
        combined_query = f"{user_query}\n\nContext:\n" + "\n".join(document_context)
        chat_prompt[-1]["content"] = combined_query
        logger.info("Added contextual information to the prompt.")
    else:
        logger.info("No contextual information added to the prompt.")
   

    # Request completion from the Azure OpenAI client
    try:
        llm = AZURE_CLIENT_CONFIG
        

        aimessage =llm.invoke(chat_prompt)
        
        response_content = aimessage.content

    except Exception as e:
        return jsonify({'error': f'Azure API call failed: {str(e)}'}), 500

    # Return the response and context
    return jsonify({
        'response': response_content,
        'context': document_context
    }), 200