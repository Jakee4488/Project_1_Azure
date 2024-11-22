### Points to Implement in the New Project

1. **Integrate Vision LLaMA**:
   - Add a **vision processing module** to handle images.
   - Extract metadata from images and perform OCR scans using `pytesseract`.
   - Install necessary dependencies:
     ```bash
     pip install pytesseract
     sudo apt-get install tesseract-ocr  # Ensure Tesseract is installed system-wide
     ```
   - Design a pipeline to:
     - Analyze images for metadata (e.g., size, resolution, format).
     - Extract text using OCR and add to the chunking and embedding process.
   - Use Vision LLaMA or similar models to enhance the image understanding capabilities.

2. **Explore and Integrate Lightweight LLMs**:
   - Incorporate **Imperial LLM** or other lightweight models for resource-efficient text generation.
   - Evaluate potential models for smaller memory footprints while maintaining high accuracy.
   - Implement a fallback mechanism to switch between lightweight and Azure OpenAI models based on query complexity or system load.

3. **Access Vector Database by Full Indexing**:
   - Implement a comprehensive indexing strategy for the vector database:
     - Store the vector database as a persistent FAISS index on disk.
     - Include metadata linking FAISS indices to the original documents or image data.
   - Dynamically update the index when new data (text or images) is added to the system.
   - Develop APIs to:
     - Query the entire database efficiently.
     - Perform advanced filtering, such as querying only specific document types (e.g., PDFs, images).

4. **Unified Data Pipeline**:
   - Combine text, image, and metadata embeddings into a single vector database.
   - Standardize the chunking process for both text and image OCR outputs.
   - Ensure embeddings are normalized for consistent FAISS querying.

5. **End-to-End System Deployment**:
   - Enable dynamic document uploads (text, PDFs, images) and automated processing.
   - Integrate Vision LLaMA and lightweight LLMs into the query pipeline to handle multimodal inputs.
   - Build a robust REST API for interacting with the system.

6. **Evaluation and Optimization**:
   - Test performance with mixed datasets (text and images).
   - Optimize FAISS queries and embeddings for speed and accuracy.
   - Experiment with hybrid LLM and lightweight LLM responses to balance cost and performance.
