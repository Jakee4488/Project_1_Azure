
import os
from openai import AzureOpenAI

# Update the UPLOAD_FOLDER configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

EMBEDDINGS_DIR = os.path.join(BASE_DIR, 'embeddings')
CHUNKS_DIR = os.path.join(BASE_DIR, 'chunks')

AZURE_APIKEY="2NCD4p44jNbxqVXEFl5cEjcIg5fbqrNi5INs3VvPwQGPnt6zGWPKJQQJ99AJACmepeSXJ3w3AAABACOGAHUq"
AZURE_API_ENDPOINT = "https://rag-chatapp.openai.azure.com/"
AZURE_API_MODEL="gpt-35-turbo-16k" 
AZURE_EMBEDDING_MODEL="text-embedding-ada-002"


MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

AZURE_CLIENT_CONFIG =AzureOpenAI(
            azure_endpoint=AZURE_API_ENDPOINT,
            api_key=AZURE_APIKEY,
            api_version="2024-05-01-preview",
        )



CHAT_COMPLETION_CONFIG = {
            "model": AZURE_API_MODEL,
            "max_tokens": 900,
            "temperature": 0.7,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }