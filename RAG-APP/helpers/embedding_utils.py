import os
import torch
import ollama

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

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