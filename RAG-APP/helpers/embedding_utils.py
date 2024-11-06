import os
import requests
import json
from constants import BASE_DIR, EMBEDDINGS_DIR, CHUNKS_DIR, AZURE_EMBEDDING_MODEL, AZURE_API_ENDPOINT, AZURE_API_KEY

# Define paths for embeddings and chunks
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
EMBEDDINGS_DIR = os.path.join(BASE_DIR, 'embeddings')
CHUNKS_DIR = os.path.join(BASE_DIR, 'chunks')

os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

# Function to get embeddings from Azure OpenAI
def get_azure_embedding(content):
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_API_KEY,
    }
    data = {
        "input": content
    }
    url = f"{AZURE_API_ENDPOINT}/openai/deployments/{AZURE_EMBEDDING_MODEL}/embeddings?api-version=2023-06-01-preview"
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()['data'][0]['embedding']
    else:
        raise Exception(f"Error from Azure OpenAI API: {response.status_code}, {response.text}")

def generate_embeddings(filename):
    try:
        # Check if embeddings already exist
        embeddings_path = os.path.join(EMBEDDINGS_DIR, f'{filename}_embeddings.json')
        if os.path.exists(embeddings_path):
            print(f"Embeddings for {filename} already exist.")
            return

        # Read vault content from chunks directory
        vault_content = []
        vault_path = os.path.join(CHUNKS_DIR, f'{filename}_vault.txt')
        if os.path.exists(vault_path):
            with open(vault_path, "r", encoding='utf-8') as vault_file:
                vault_content = vault_file.readlines()

        # Generate embeddings for each content chunk
        vault_embeddings = []
        for content in vault_content:
            embedding = get_azure_embedding(content)
            vault_embeddings.append(embedding)

        # Save embeddings to a file
        with open(embeddings_path, "w", encoding='utf-8') as embeddings_file:
            json.dump(vault_embeddings, embeddings_file)
    except Exception as e:
        print(f"An error occurred: {e}")