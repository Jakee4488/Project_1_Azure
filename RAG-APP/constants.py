from werkzeug.utils import secure_filename
import os


# Update the UPLOAD_FOLDER configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

EMBEDDINGS_DIR = os.path.join(BASE_DIR, 'embeddings')
CHUNKS_DIR = os.path.join(BASE_DIR, 'chunks')


AZURE_API_ENDPOINT = "https://rag-chatapp.openai.azure.com/"
AZURE_API_MODEL="gpt-35-turbo-16k" 


MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
