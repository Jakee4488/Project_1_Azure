# RAG Chat Application

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Implementation Details](#implementation-details)
4. [Setup Guide](#setup-guide)
5. [API Reference](#api-reference)
6. [Development](#development)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

## Project Overview
The RAG (Retrieval-Augmented Generation) Chat Application is a sophisticated web application that combines document processing, vector embeddings, and natural language processing to provide intelligent responses based on uploaded documents   .

### Key Features
- Document processing (PDF, TXT, DOC, DOCX)
- Azure OpenAI integration for intelligent responses
- Real-time chat with conversation history
- Dark/Light theme support
- Voice input capabilities
- Document preview
- Session management
- Responsive design

## Architecture

### System Components
1. **Frontend**
   - HTML5/CSS3 with Bootstrap 5
   - Vanilla JavaScript
   - Responsive mobile-first design
   - WebSocket for real-time chat

2. **Backend**
   - Flask web server
   - Azure OpenAI API integration
   - FAISS vector database
   - Document processing pipeline
   - WebSocket server

3. **Storage**
   - File system for documents
   - Vector embeddings store
   - Session data store

### Data Flow
1. Document Upload → Processing → Vector Storage
2. User Query → Context Retrieval → AI Response
3. Real-time Updates → WebSocket → UI Refresh

## Implementation Details

### Core Services

#### Document Processor
- File validation and sanitization
- Text extraction (PDF, DOC, TXT)
- Content chunking
- Vector embedding generation
- FAISS indexing

#### Query Engine
- Context retrieval
- Prompt engineering
- Azure OpenAI integration
- Response generation

#### Chat Manager
- Session handling
- Message history
- Real-time updates
- Voice processing

## Setup Guide

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker
- Azure OpenAI API access
- 8GB+ RAM
- 10GB+ storage

### Installation
1. Clone repository
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```
4. Initialize database
   ```bash
   python init_db.py
   ```

### Configuration
Required environment variables:
