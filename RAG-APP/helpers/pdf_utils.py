import os
import re
import PyPDF2
from .embedding_utils import generate_embeddings

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

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

            vault_path = os.path.join(BASE_DIR, 'vault.txt')
            with open(vault_path, "a", encoding="utf-8") as vault_file:
                for chunk in chunks:
                    vault_file.write(chunk.strip() + "\n")

            generate_embeddings()
            return True, "PDF processed successfully"
    except Exception as e:
        return False, str(e)