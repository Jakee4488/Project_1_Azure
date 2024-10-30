import os
import re
import PyPDF2
from .embedding_utils import generate_embeddings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CHUNKS_DIR = os.path.join(BASE_DIR, 'chunks')

os.makedirs(CHUNKS_DIR, exist_ok=True)

def process_uploaded_pdf(file_path):
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
            text = ''
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + " " if page.extract_text() else ""

            text = re.sub(r'\s+', ' ', text).strip()
            sentences = re.split(r'(?<=[.!?]) +', text)
            chunks = []
            current_chunk = ""

            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 1 < 1000:
                    current_chunk += (sentence + " ").strip()
                else:
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "

            if current_chunk:
                chunks.append(current_chunk)

            filename = os.path.splitext(os.path.basename(file_path))[0]
            vault_path = os.path.join(CHUNKS_DIR, f'{filename}_vault.txt')
            with open(vault_path, "a", encoding="utf-8") as vault_file:
                for chunk in chunks:
                    vault_file.write(chunk.strip() + "\n")

            generate_embeddings(filename)
            return True, "PDF processed successfully"
    except Exception as e:
        return False, str(e)