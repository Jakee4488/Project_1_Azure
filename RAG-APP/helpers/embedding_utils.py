import os
import torch
import ollama
from openai import OpenAI, AzureOpenAI

from constants import BASE_DIR, EMBEDDINGS_DIR , CHUNKS_DIR, AZURE_EMBEDDING_MODEL, AZURE_API_ENDPOINT

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
EMBEDDINGS_DIR = os.path.join(BASE_DIR, 'embeddings')
CHUNKS_DIR = os.path.join(BASE_DIR, 'chunks')

os.makedirs(EMBEDDINGS_DIR, exist_ok=True)



def generate_embeddings(filename):
    try:
        vault_content = []
        vault_path = os.path.join(CHUNKS_DIR, f'{filename}_vault.txt')
        if os.path.exists(vault_path):
            with open(vault_path, "r", encoding='utf-8') as vault_file:
                vault_content = vault_file.readlines()

        vault_embeddings = []
        for content in vault_content:
            response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
            vault_embeddings.append(response["embedding"])

        embeddings_path = os.path.join(EMBEDDINGS_DIR, f'{filename}_embeddings.txt')
        with open(embeddings_path, "w", encoding='utf-8') as embeddings_file:
            for embedding in vault_embeddings:
                embeddings_file.write(f"{embedding}\n")
    except Exception as e:
        print(f"Error generating embeddings: {e}")