# Doctor Appointment Bot - Project Documentation

## Overview
This is an AI-powered doctor appointment assistant built with FastAPI, LangChain, and Qdrant vector database. It helps users find doctors and book appointments through natural language conversations.

## Project Structure

### 📁 Root Files

#### `main.py`
- **Purpose**: Application entry point
- **Function**: Imports FastAPI app and runs the server
- **Usage**: `python main.py` or `uvicorn app:app --reload`

#### `requirements.txt`
- **Purpose**: Python dependencies
- **Contents**: All required packages (FastAPI, LangChain, Cohere, Qdrant, etc.)

#### `.env`
- **Purpose**: Environment variables
- **Required Variables**:
  - `GOOGLE_API_KEY` - For Gemini AI
  - `COHERE_API_KEY` - For text embeddings
  - `QDRANT_URL` - Vector database URL
  - `QDRANT_API_KEY` - Database authentication
  - `SECRET_KEY` - FastAPI sessions

#### `README.md`
- **Purpose**: Project documentation and setup instructions

### 📁 `app/` Directory

#### `app/__init__.py`
- **Purpose**: FastAPI application setup
- **Features**:
  - Creates FastAPI app with lifespan management
  - Sets up session middleware
  - Defines API routes:
    - `GET /` - Serves chat interface
    - `POST /api/chat` - Handles chat messages

#### `app/main.py`
- **Purpose**: Alternative entry point (currently minimal)

### 📁 `app/ai_agent/` Directory

#### `agent.py`
- **Purpose**: Main AI agent logic
- **Class**: `AppointmentAgent`
- **Features**:
  - Uses Google Gemini AI for conversations
  - Integrates with Qdrant vector database
  - Handles tool calling (appointment booking, doctor search)
  - Manages chat sessions

**Key Methods**:
- `__init__()` - Initialize with Gemini LLM and Qdrant
- `get_response()` - Process user messages and return AI responses

#### `qdrant.py`
- **Purpose**: Vector database operations
- **Class**: `QdrantIngestionService`
- **Features**:
  - Text embeddings using Cohere
  - Semantic text chunking
  - Doctor data storage and retrieval
  - Vector similarity search

**Key Methods**:
- `create_collection()` - Set up vector database
- `upsert()` - Add doctor data
- `search()` - Find relevant doctors

#### `tools.py`
- **Purpose**: Custom tools for the AI agent
- **Tools**:
  - `save_appointment()` - Book appointments
  - `get_docs()` - Search doctors in vector database

#### `prompts.py`
- **Purpose**: AI conversation prompts
- **Features**:
  - System prompt with doctor booking instructions
  - Chat template for structured conversations

#### `context.py`
- **Purpose**: Sample data for doctors and appointments
- **Contents**:
  - Doctor profiles (name, specialty, experience)
  - Existing appointments
  - Used for testing and initial data

#### `history_manager.py`
- **Purpose**: Chat session management
- **Class**: `SessionChatHistory`
- **Features**:
  - Store conversation history per user session
  - Retrieve chat history for context
  - Clear sessions when needed

### 📁 `static/` Directory

#### `static/chat.html`
- **Purpose**: Web chat interface
- **Features**:
  - HTMX for dynamic updates
  - Tailwind CSS styling
  - Real-time chat interface
  - Doctor appointment assistant UI

### 📁 `env/` Directory
- **Purpose**: Python virtual environment
- **Contents**: Isolated Python environment with all dependencies

## Key Technologies

### 🤖 AI & ML
- **Google Gemini**: Main conversational AI
- **Cohere**: Text embeddings for vector search
- **LangChain**: LLM orchestration framework

### 🗄️ Database & Storage
- **Qdrant**: Vector database for semantic search
- **JSON**: Simple appointment storage

### 🌐 Web Framework
- **FastAPI**: Modern Python web framework
- **HTMX**: Frontend interactions without JavaScript
- **Tailwind CSS**: Utility-first CSS framework

## How It Works

1. **User Input**: User types message in chat interface
2. **AI Processing**: Gemini AI processes message with doctor context
3. **Tool Calling**: AI may call tools for doctor search or appointment booking
4. **Vector Search**: Cohere embeddings used to find relevant doctors
5. **Response**: AI generates natural response with booking options
6. **Persistence**: Appointments saved to JSON file

## API Endpoints

- `GET /` - Chat interface
- `POST /api/chat` - Send chat message

## Development Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables in `.env`
3. Run server: `uvicorn app:app --reload`
4. Open browser: `http://127.0.0.1:8000`

## Data Flow

```
User Message → FastAPI → Gemini AI → Tool Calling → Qdrant Search → Response → HTML Update
```

## Future Improvements

- Add PostgreSQL for persistent storage
- Implement user authentication
- Add appointment conflict checking
- Deploy with Docker
- Add doctor registration interface
