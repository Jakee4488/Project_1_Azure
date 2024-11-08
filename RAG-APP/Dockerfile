# Use a slim Debian-based image for compatibility with faiss-cpu
FROM python:3.12-slim

# Update pip to minimize dependency errors
RUN pip install --upgrade pip

# Define the working directory
WORKDIR /RAG-APP

# Copy the contents into the working directory
ADD . /RAG-APP

# Install system dependencies required for faiss-cpu
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    swig \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install -r requirements.txt

EXPOSE 5000

# Define the command to start the Flask app
CMD ["python", "app.py"]