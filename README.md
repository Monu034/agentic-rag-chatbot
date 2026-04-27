# Agentic RAG Chatbot with MCP 🤖

An agent-based Retrieval-Augmented Generation (RAG) chatbot that processes multiple document formats (PDF, PPTX, CSV, DOCX, TXT) and answers user questions based on the uploaded context. The system uses an agentic architecture with simulated Model Context Protocol (MCP) for structured message passing between components.

## 🌟 Features

- **Multi-Format Parsing**: Extracts text from PDF, PPTX, CSV, DOCX, and TXT files.
- **Agentic Architecture**: Uses distinct agents (Ingestion, Retrieval, LLM Response) to handle specific tasks.
- **Model Context Protocol (MCP)**: Agents communicate via structured JSON messages (`sender`, `receiver`, `type`, `trace_id`, `payload`).
- **Vector Search**: Uses `SentenceTransformers` and `FAISS` for fast, semantic retrieval.
- **LLM Integration**: Uses Google's Gemini Flash for generating accurate, context-aware answers.
- **Streamlit UI**: A clean, beginner-friendly web interface for document uploading, querying, and viewing MCP traces.

## 🏗️ System Architecture

1. **Streamlit UI (Coordinator)**: Acts as the frontend and orchestrator. It receives user inputs and routes tasks to the appropriate agents.
2. **Ingestion Agent**: Receives raw documents, parses them based on their format, and chunks the text into smaller segments.
3. **Retrieval Agent**: Receives text chunks, generates embeddings using `sentence-transformers`, and stores them in a `FAISS` vector index. During QA, it receives queries, searches the vector index, and returns the most relevant chunks.
4. **LLM Response Agent**: Receives the retrieved context and the user query. It formats a prompt and calls the Gemini LLM to generate the final response.

### MCP Message Flow Example

```json
{
  "sender": "RetrievalAgent",
  "receiver": "LLMResponseAgent",
  "type": "RETRIEVAL_RESULT",
  "trace_id": "e4f8d9b1-...",
  "payload": {
    "retrieved_context": ["[Source: data.pdf] Revenue increased by 20%..."],
    "query": "What was the revenue increase?"
  }
}
```

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.9 or higher
- Obtain a [Google Gemini API Key](https://aistudio.google.com/app/apikey).

### 2. Installation
Clone the repository and install the required dependencies:

```bash
git clone <your-repo-link>
cd Chatbot
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory and add your Gemini API key:
```ini
GEMINI_API_KEY=your_api_key_here
```

### 4. Run the Application
Start the Streamlit application:
```bash
streamlit run app.py
```

## 📂 Repository Structure

```
Chatbot/
├── agents/
│   ├── __init__.py
│   ├── ingestion_agent.py   # Parses and chunks documents
│   ├── llm_agent.py         # Generates LLM responses
│   ├── mcp.py               # Defines the MCP message structure
│   └── retrieval_agent.py   # Handles FAISS indexing and searching
├── utils/
│   └── document_parser.py   # Utility for extracting text from PDF, CSV, PPTX, etc.
├── vector_store/
│   └── store.py             # FAISS Vector DB implementation
├── app.py                   # Streamlit UI & Coordinator
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

## 💡 Best Practices Implemented

- **Modularity**: Code is split into agents and utils for clean separation of concerns.
- **Scalability**: FAISS can scale to handle many chunks efficiently.
- **Traceability**: All agent communications are logged with unique `trace_id`s, visible in the UI.

## 🎥 Presentation & Demo Video Suggestions

- **Slide 1 (Title)**: Project Title, Your Name.
- **Slide 2 (Architecture)**: Show the Streamlit Coordinator routing tasks between the Ingestion, Retrieval, and LLM Agents.
- **Slide 3 (MCP Flow)**: Show the JSON payload moving between agents, emphasizing how MCP standardizes context.
- **Slide 4 (Tech Stack)**: Streamlit, FAISS, Sentence-Transformers, Gemini Flash.
- **Slide 5 (Demo Video)**: 5 minutes covering app usage (2 min), architecture flow (2 min), and code walkthrough (1 min). Include uploading a tricky format like PPTX or CSV!
